#!/usr/bin/env python3
"""生成自测卡片 cards.json。

分层抽样：
- deep-news: index-by-topic.md 六个领域各取 5 篇，优先掺入 daily-report 标过的文章
- lizheng-open-context: context/ 5 篇全取（校准项）+ videos 8 + community-posts 5 + community-comments 2
- 诱饵: 2 张不存在的卡，用于检验「看过」选项的诚实度
"""
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LZ = ROOT / "upstream" / "lizheng-open-context"
DN = ROOT / "deep-news"
SEED = 42

ROW = re.compile(
    r"^\| (\d{4}-\d{2}-\d{2}) \| \[([^\]]+)\]\(articles/([^)]+)\) "
    r"\| \[yage\.ai 原文\]\([^)]+\) \| (.+?) \|$"
)


def deep_news_cards(rng: random.Random) -> list[dict]:
    linked = set()
    for f in (DN / "daily-report").glob("*.md"):
        linked.update(re.findall(r"\.\./articles/([a-zA-Z0-9-]+\.md)", f.read_text()))

    domains: dict[str, list[dict]] = {}
    domain = ""
    for line in (DN / "index-by-topic.md").read_text().splitlines():
        m = re.match(r"^## (.+)", line)
        if m:
            domain = re.sub(r"^([一二三四五六])、(.+?)(?:\s*\(|$)", r"\2", m.group(1)).strip()
        r = ROW.match(line.strip())
        if r and domain:
            domains.setdefault(domain, []).append(
                {
                    "date": r.group(1),
                    "title": r.group(2),
                    "fname": r.group(3),
                    "snippet": r.group(4).strip(),
                    "daily_linked": r.group(3) in linked,
                }
            )

    cards = []
    for domain, arts in domains.items():
        linked_arts = [a for a in arts if a["daily_linked"]]
        plain_arts = [a for a in arts if not a["daily_linked"]]
        rng.shuffle(linked_arts)
        rng.shuffle(plain_arts)
        pick = linked_arts[:2] + plain_arts[: 5 - min(2, len(linked_arts))]
        for a in pick:
            cards.append(
                {
                    "id": f"dn:{a['fname'][:-3]}",
                    "corpus": "deep-news",
                    "domain": domain,
                    "title": a["title"],
                    "date": a["date"],
                    "snippet": a["snippet"][:110],
                    "path": f"deep-news/articles/{a['fname']}",
                }
            )
    return cards


def first_paragraph(path: Path) -> str:
    text = path.read_text()
    body = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    for para in re.split(r"\n\s*\n", body):
        p = para.strip()
        if len(p) < 30 or p.startswith(("#", ">", "!", "-", "|", "[")):
            continue
        # 跳过主要由链接/时间戳构成的段落（逐字稿 cue）
        stripped = re.sub(r"\[[^\]]*\]\([^)]*\)", "", p)
        if len(stripped.strip()) < 20:
            continue
        return re.sub(r"\s+", " ", stripped.strip())[:110]
    return ""


def lizheng_cards(rng: random.Random) -> list[dict]:
    cards = []
    for f in sorted((LZ / "context").glob("*.md")):
        title = ""
        for line in f.read_text().splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        cards.append(
            {
                "id": f"lz-ctx:{f.stem}",
                "corpus": "lizheng-context",
                "title": title or f.stem,
                "date": "",
                "snippet": first_paragraph(f),
                "path": f"upstream/lizheng-open-context/context/{f.name}",
            }
        )

    for name, corpus, n in [
        ("videos", "lizheng-video", 8),
        ("community-posts", "lizheng-post", 5),
        ("community-comments", "lizheng-comment", 2),
    ]:
        rows = [
            json.loads(line)
            for line in (LZ / "catalog" / f"{name}.jsonl").read_text().splitlines()
        ]
        rows = [r for r in rows if r.get("corpus_path")]
        rng.shuffle(rows)
        for r in rows[:n]:
            f = LZ / r["corpus_path"]
            date = (r.get("published_at") or "")[:10]
            cards.append(
                {
                    "id": f"lz:{Path(r['corpus_path']).stem}",
                    "corpus": corpus,
                    "title": r.get("title") or f.stem,
                    "date": date,
                    "snippet": first_paragraph(f) if f.exists() else "",
                    "path": f"upstream/lizheng-open-context/{r['corpus_path']}",
                }
            )
    return cards


def trap_cards() -> list[dict]:
    return [
        {
            "id": "trap:w3c-agent-id",
            "corpus": "deep-news",
            "title": "为 Agent 造身份证：W3C 新提案能终结凭证混乱吗",
            "date": "2026-07-22",
            "snippet": "W3C 上周放出了 Agent Identity 的 early draft，想给每个 agent 发一张可验证的身份证。问题是证书体系的每一次扩张，最后都变成了少数人收税的关口。",
            "path": None,
            "trap": True,
        },
        {
            "id": "trap:lizheng-solo-regret",
            "corpus": "lizheng-video",
            "title": "深夜谈：付费社群做到第三年，我后悔了哪三件事",
            "date": "2025-11-30",
            "snippet": "这期没提纲，就是想把三年做社群的三件事摊开说：定价、踢人、还有我自己舍不得放下的那部分表达欲。",
            "path": None,
            "trap": True,
        },
    ]


def main() -> None:
    rng = random.Random(SEED)
    cards = deep_news_cards(rng) + lizheng_cards(rng) + trap_cards()
    rng.shuffle(cards)
    for i, c in enumerate(cards):
        c["seq"] = i
    out = Path(__file__).parent / "cards.json"
    out.write_text(
        json.dumps({"seed": SEED, "count": len(cards), "cards": cards}, ensure_ascii=False, indent=1)
    )
    print(f"wrote {len(cards)} cards -> {out}")
    from collections import Counter

    print(Counter(c["corpus"] for c in cards))


if __name__ == "__main__":
    sys.exit(main())
