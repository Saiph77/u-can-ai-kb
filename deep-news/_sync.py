#!/usr/bin/env python3
"""Sync Chinese Deep News articles from https://yage.ai/share/?lang=zh"""
from __future__ import annotations

import argparse
import html as htmlmod
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

from markdownify import markdownify as html_to_md

ROOT = Path(__file__).resolve().parent
ARTICLES = ROOT / "articles"
ASSETS = ROOT / "assets"
INDEX_URL = "https://yage.ai/share/?lang=zh"
BASE = "https://yage.ai/share/"
UA = "Mozilla/5.0 (compatible; u-can-ai-kb-sync/1.0)"

# Slow on purpose: one in-flight request, min gap between starts.
MIN_INTERVAL_SEC = 1.5
MAX_RETRIES = 6
SKIP_EXISTING = True

_rate_lock = threading.Lock()
_next_ok = 0.0


def _wait_slot() -> None:
    global _next_ok
    with _rate_lock:
        now = time.monotonic()
        wait = _next_ok - now
        if wait > 0:
            time.sleep(wait)
        _next_ok = time.monotonic() + MIN_INTERVAL_SEC


def fetch(url: str, retries: int = MAX_RETRIES) -> bytes:
    last: Exception | None = None
    for i in range(retries):
        _wait_slot()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            last = e
            retry_after = e.headers.get("Retry-After") if e.headers else None
            if e.code in (429, 503):
                extra = float(retry_after) if retry_after and retry_after.isdigit() else (8 * (i + 1))
                print(f"  rate-limited {e.code} {url} sleep {extra}s")
                time.sleep(extra)
                continue
            if e.code == 404:
                raise
            time.sleep(2 * (i + 1))
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (i + 1))
    raise last  # type: ignore[misc]


def parse_iso_date(value: str) -> date | None:
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(value[:10] if fmt == "%Y-%m-%d" else value[:8], fmt).date()
        except ValueError:
            continue
    return None


def local_latest_date() -> date | None:
    """Newest publish date already on disk (index.json, then article frontmatter)."""
    dates: list[date] = []
    index_path = ROOT / "index.json"
    if index_path.exists():
        try:
            rows = json.loads(index_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            rows = []
        for row in rows:
            d = parse_iso_date(str(row.get("date") or ""))
            if d:
                dates.append(d)
    if ARTICLES.exists():
        for path in ARTICLES.glob("*.md"):
            item = item_from_file(path)
            d = parse_iso_date(item.get("date") or "")
            if d:
                dates.append(d)
    return max(dates) if dates else None


def list_zh_articles() -> list[dict]:
    """Return [{name, date, title}, ...] from the zh listing, newest first as on the page."""
    html = fetch(INDEX_URL).decode("utf-8", "replace")
    items: list[dict] = []
    seen: set[str] = set()
    for m in re.finditer(r"<li([^>]*class=\"[^\"]*article-item[^\"]*\"[^>]*)>", html):
        attrs = m.group(1)
        lang = re.search(r'data-lang="([^"]*)"', attrs)
        if not lang or lang.group(1) != "zh":
            continue
        date_m = re.search(r'data-date="([^"]*)"', attrs)
        title_m = re.search(r'data-title="([^"]*)"', attrs)
        end = html.find("</li>", m.end())
        chunk = html[m.end() : end if end != -1 else m.end() + 4000]
        href_m = re.search(r'href="([^"]+\.html)"', chunk)
        if not href_m:
            continue
        name = href_m.group(1).split("/")[-1]
        if name in seen or name == "index.html":
            continue
        if "-en-" in name or name.endswith("-en.html"):
            continue
        seen.add(name)
        items.append(
            {
                "name": name,
                "date": date_m.group(1) if date_m else "",
                "title": htmlmod.unescape(title_m.group(1)) if title_m else name,
            }
        )
    if not items:
        # fallback: href-only, no listing dates
        for href in re.findall(r'href="([^"]+\.html)"', html):
            name = href.split("/")[-1]
            if name in seen or name == "index.html":
                continue
            if "-en-" in name or name.endswith("-en.html"):
                continue
            seen.add(name)
            items.append({"name": name, "date": "", "title": name})
    return items


def filter_incremental(cards: list[dict], since: date) -> list[dict]:
    """Keep cards on/after `since`. Same-day items still skip if the file exists."""
    kept = []
    for card in cards:
        card_d = parse_iso_date(card.get("date") or "")
        if card_d is None:
            slug_d = parse_iso_date(card["name"].rsplit(".", 1)[0][-8:])
            card_d = slug_d
        if card_d is None:
            kept.append(card)
            continue
        if card_d >= since:
            kept.append(card)
    return kept


class TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_title = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        if tag == "h1":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "h1":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def extract_body(html: str) -> tuple[str, str, str]:
    """Return (title, datetime, body_html from h1 to disqus)."""
    tp = TitleParser()
    tp.feed(html)
    title = tp.title.strip() or "untitled"
    m_time = re.search(r'<time datetime="([^"]+)"', html)
    dt = m_time.group(1) if m_time else ""
    start = html.find("<h1")
    if start < 0:
        start = html.find("<body")
        if start < 0:
            start = 0
    end_markers = [
        '<div id="disqus_thread"',
        "yage-share.disqus.com",
        "</body>",
    ]
    end = len(html)
    for mk in end_markers:
        i = html.find(mk, start)
        if i != -1:
            end = min(end, i)
    body = html[start:end]
    # drop header chrome after title block
    body = re.sub(r"</header>", "", body, count=1)
    return title, dt, body


def drop_data_uri_images(html: str) -> str:
    """Strip inlined base64 <img> tags; keep alt/aria-label as a caption."""

    def repl(m: re.Match[str]) -> str:
        tag = m.group(0)
        alt = re.search(r'\b(?:alt|aria-label)="([^"]*)"', tag)
        text = alt.group(1).strip() if alt else ""
        return f"<p>{text}</p>" if text else ""

    return re.sub(
        r"<img\b[^>]*src=\"data:image/[^\"]*\"[^>]*>",
        repl,
        html,
        flags=re.IGNORECASE,
    )


def rewrite_and_save_images(slug: str, body: str) -> str:
    body = drop_data_uri_images(body)
    dest = ASSETS / slug
    urls = re.findall(r'(?:src|srcset)="([^"]+)"', body)

    def abs_url(u: str) -> str:
        u = u.strip().split()[0]
        return urljoin(BASE, u)

    seen = {}
    for raw in urls:
        u = abs_url(raw)
        if u.startswith("data:"):
            continue
        path = urlparse(u).path
        fname = os.path.basename(path) or "image"
        # keep unique
        key = fname
        n = 1
        while key in seen.values() and seen.get(u) != key:
            stem, ext = os.path.splitext(fname)
            key = f"{stem}-{n}{ext}"
            n += 1
        seen[u] = key

    if seen:
        dest.mkdir(parents=True, exist_ok=True)
    for u, fname in seen.items():
        out = dest / fname
        if not out.exists():
            try:
                data = fetch(u)
                out.write_bytes(data)
            except Exception as e:  # noqa: BLE001
                print(f"  image fail {u}: {e}")
                continue
        rel = f"../assets/{slug}/{fname}"
        body = body.replace(u, rel)
        # also replace relative original
        orig_path = urlparse(u).path
        orig_name = os.path.basename(orig_path)
        body = re.sub(
            rf'(src|href)="(?:https://yage\.ai/share/)?{re.escape(orig_name)}"',
            rf'\1="{rel}"',
            body,
        )
    return body


def strip_md_data_images(md: str) -> str:
    md = re.sub(
        r"!\[([^\]]*)\]\(\s*data:image/[^)]+\)",
        lambda m: f"*{m.group(1).strip()}*" if m.group(1).strip() else "",
        md,
        flags=re.IGNORECASE,
    )
    return re.sub(r"\n{3,}", "\n\n", md)


def to_markdown(title: str, dt: str, slug: str, body_html: str, source: str) -> str:
    md = html_to_md(body_html, heading_style="ATX", bullets="-")
    md = strip_md_data_images(md).strip()
    if "查看原网页" not in md:
        md = re.sub(
            r"(发布于\s*\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)",
            rf"\1 · [查看原网页]({source})",
            md,
            count=1,
        )
    front = [
        "---",
        f"title: {json.dumps(title, ensure_ascii=False)}",
        f"date: {dt}" if dt else "date: ",
        f"source: {source}",
        f"slug: {slug}",
        "lang: zh",
        "---",
        "",
    ]
    return "\n".join(front) + md + "\n"


def process(name: str) -> dict:
    source = urljoin(BASE, name)
    slug = name[:-5] if name.endswith(".html") else name
    path = ARTICLES / f"{slug}.md"
    if SKIP_EXISTING and path.exists() and path.stat().st_size > 200:
        return {"slug": slug, "skipped": True, "file": str(path.relative_to(ROOT))}
    html = fetch(source).decode("utf-8", "replace")
    title, dt, body = extract_body(html)
    body = rewrite_and_save_images(slug, body)
    md = to_markdown(title, dt, slug, body, source)
    ARTICLES.mkdir(parents=True, exist_ok=True)
    path.write_text(md, encoding="utf-8")
    return {"slug": slug, "title": title, "date": dt, "source": source, "file": str(path.relative_to(ROOT))}


def item_from_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"')
    return {
        "slug": meta.get("slug") or path.stem,
        "title": meta.get("title") or path.stem,
        "date": meta.get("date") or "",
        "source": meta.get("source") or "",
        "file": str(path.relative_to(ROOT)),
    }


def write_index(items: list[dict]) -> None:
    items = sorted(items, key=lambda x: x.get("date") or "", reverse=True)
    lines = [
        "# Deep News（中文）",
        "",
        "来源：[https://yage.ai/share/?lang=zh](https://yage.ai/share/?lang=zh)",
        "",
        f"共 {len(items)} 篇。",
        "",
        "## 📖 结构化索引导航",
        "",
        "- 📅 **[按时间顺序演进索引](index-by-time.md)**：按月份划分 2026 年 3 月至 9 月的技术演进主线、月度重大事件与全量归档。",
        "- 🧭 **[按内容主题相关性索引](index-by-topic.md)**：按 6 大核心领域（智能体、AI 编程、模型架构、评测安全、硬件算力、商业经济）与 18 个专题重构知识树。",
        "",
        "---",
        "",
        "## 📜 全量文章列表",
        "",
    ]
    for it in items:
        date = it.get("date") or ""
        title = (it.get("title") or it["slug"]).replace("\n", " ").strip()
        rel = it["file"]
        source = it.get("source") or ""
        source_link = f" · [原网链接]({source})" if source else ""
        lines.append(f"- {date} [{title}]({rel}){source_link}")
    (ROOT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "index.json").write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sync Deep News zh articles from yage.ai/share")
    p.add_argument(
        "--incremental",
        "-i",
        action="store_true",
        help="Only fetch articles on/after the newest local publish date",
    )
    p.add_argument(
        "--since",
        metavar="YYYY-MM-DD",
        help="Only fetch articles on/after this date (overrides --incremental watermark)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cards = list_zh_articles()
    since: date | None = None
    if args.since:
        since = parse_iso_date(args.since)
        if since is None:
            raise SystemExit(f"invalid --since: {args.since}")
    elif args.incremental:
        since = local_latest_date()
        if since is None:
            print("incremental: no local articles, falling back to full sync")
        else:
            print(f"incremental: local latest date = {since.isoformat()}")
    if since is not None:
        before = len(cards)
        cards = filter_incremental(cards, since)
        print(f"listing {before} zh → {len(cards)} on/after {since.isoformat()}")
    else:
        print(f"found {len(cards)} zh articles")
    print(f"interval={MIN_INTERVAL_SEC}s sequential")
    ARTICLES.mkdir(parents=True, exist_ok=True)
    errors = []
    fetched = 0
    skipped = 0
    for i, card in enumerate(cards, 1):
        n = card["name"]
        try:
            result = process(n)
            if result.get("skipped"):
                skipped += 1
            else:
                fetched += 1
            if i % 20 == 0 or i == len(cards):
                print(f"  {i}/{len(cards)} fetched={fetched} skipped={skipped} {n}")
        except Exception as e:  # noqa: BLE001
            errors.append({"name": n, "error": str(e)})
            print(f"  FAIL {n}: {e}")
    items = [item_from_file(p) for p in ARTICLES.glob("*.md")]
    write_index(items)
    if errors:
        (ROOT / "sync-errors.json").write_text(json.dumps(errors, ensure_ascii=False, indent=2) + "\n")
    print(f"done files={len(items)} fetched={fetched} skipped={skipped} fail={len(errors)}")


if __name__ == "__main__":
    main()
