#!/usr/bin/env python3
"""Local preview server for the curated u-can-ai-kb reading tree."""

from __future__ import annotations

import json
import mimetypes
import re
import threading
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
KB = ROOT.parent
STATIC = ROOT / "static"

FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
HEADING = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)

# Curated reading areas only — no upstream/ tooling
COLLECTIONS: dict[str, dict[str, Any]] = {
    "by-audience": {
        "label": "按读者入口",
        "path": "by-audience",
        "categories": True,
        "desc": "第一层索引：从这里开始、世界观、处境、协作…",
    },
    "by-format": {
        "label": "按内容形态",
        "path": "by-format",
        "categories": True,
        "desc": "第二层索引：长文、视频逐字稿、Skill、决策框架…",
    },
    "openmic": {
        "label": "开放麦档案",
        "path": "open-mic-archive",
        "categories": True,
        "desc": "第 1–7 期原文：知识页、逐字稿、AI 总结（Jenny 成文在独立栏目）",
    },
    "jenny": {
        "label": "Jenny 成文",
        "path": "Jenny",
        "categories": False,
        "desc": "开放麦 1–7 期 Jenny 文章",
    },
    "frank": {
        "label": "Frank",
        "path": "Frank",
        "categories": True,
        "desc": "访谈逐字稿与 Agent 指令",
    },
    "guides": {
        "label": "索引与说明",
        "path": None,
        "categories": False,
        "files": [
            "readme.md",
            "AGENTS.md",
            "index-by-audience.md",
            "index-by-format.md",
            "index-of-open-mic.md",
        ],
        "desc": "总览与 Markdown 索引页",
    },
}

SKIP_DIR_NAMES = {
    "viewer",
    "upstream",
    "data",
    "sources",
    "__pycache__",
    ".git",
}


def parse_front_matter(raw: str) -> tuple[dict[str, Any], str]:
    match = FRONT_MATTER.match(raw)
    if not match:
        return {}, raw
    meta: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        try:
            meta[key] = json.loads(value)
        except json.JSONDecodeError:
            meta[key] = value.strip('"')
    return meta, raw[match.end() :]


def title_from_markdown(path: Path, body: str, meta: dict[str, Any]) -> str:
    if meta.get("title"):
        return str(meta["title"])
    m = HEADING.search(body)
    if m:
        return m.group(1).strip()
    return path.stem.replace("-", " ")


def category_label(folder: str) -> str:
    labels = {
        "00-从这里开始": "从这里开始",
        "01-世界观与判断": "世界观与判断",
        "02-我的处境": "我的处境",
        "03-跟AI协作": "跟 AI 协作",
        "04-把判断做成东西": "把判断做成东西",
        "05-视频精选": "视频精选",
        "06-深度对话": "深度对话",
        "07-内部参考-协作者专用": "内部参考",
        "08-社区案例": "社区案例",
        "09-待归类": "待归类",
        "01-核心锚点": "核心锚点",
        "02-精选长文": "精选长文",
        "02-决策框架-axiom": "决策框架",
        "03-视频逐字稿": "视频逐字稿",
        "04-访谈与活动回放": "访谈与回放",
        "05-执行方法-skill": "执行方法 Skill",
        "06-内部规则-rules": "内部规则",
        "07-社区案例与工具分享": "社区案例",
        "interview-transcripts": "访谈逐字稿",
        "instructions": "Agent 指令",
        "mems": "记忆",
        "skills": "Skills",
    }
    return labels.get(folder, folder)


class KBCatalog:
    def __init__(self, kb_root: Path) -> None:
        self.kb_root = kb_root.resolve()
        self.items: list[dict[str, Any]] = []
        self.by_id: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()
        self.reload()

    def reload(self) -> None:
        with self._lock:
            items: list[dict[str, Any]] = []
            for key, spec in COLLECTIONS.items():
                if key == "guides":
                    for name in spec["files"]:
                        path = self.kb_root / name
                        if path.is_file():
                            items.append(self._item_from_path(key, path, category="guides"))
                    continue

                base = self.kb_root / spec["path"]
                if not base.exists():
                    continue
                if spec.get("categories"):
                    patterns = ("*.md", "*.txt") if key == "openmic" else ("*.md",)
                    for pattern in patterns:
                        for doc in sorted(base.glob(pattern)):
                            if doc.name == "README.md":
                                continue
                            items.append(self._item_from_path(key, doc, category=""))
                    for sub in sorted(p for p in base.iterdir() if p.is_dir()):
                        if key == "openmic" and sub.name == "知识库":
                            continue
                        for pattern in patterns:
                            for doc in sorted(sub.rglob(pattern)):
                                if doc.name == "README.md":
                                    continue
                                rel_cat = doc.parent.relative_to(base).as_posix()
                                items.append(self._item_from_path(key, doc, category=rel_cat))
                else:
                    for md in sorted(base.rglob("*.md")):
                        items.append(
                            self._item_from_path(
                                key,
                                md,
                                category="" if md.name == "README.md" else "",
                            )
                        )

            items.sort(key=lambda x: (x["collection"], x.get("category") or "", x["title"]))
            self.items = items
            self.by_id = {item["id"]: item for item in items}

    def _item_from_path(self, collection: str, path: Path, category: str) -> dict[str, Any]:
        rel = path.relative_to(self.kb_root).as_posix()
        raw = path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(raw)
        title = title_from_markdown(path, body, meta)
        return {
            "id": rel,
            "collection": collection,
            "collection_label": COLLECTIONS[collection]["label"],
            "category": category,
            "category_label": category_label(category.split("/")[0]) if category else "",
            "title": title,
            "path": rel,
            "size": path.stat().st_size,
            "meta": meta,
        }

    def meta(self) -> dict[str, Any]:
        categories: dict[str, list[dict[str, str]]] = {}
        for key, spec in COLLECTIONS.items():
            cats = sorted(
                {
                    item["category"]
                    for item in self.items
                    if item["collection"] == key and item.get("category")
                }
            )
            categories[key] = [
                {"id": c, "label": category_label(c.split("/")[0])} for c in cats
            ]

        by_collection: dict[str, int] = {}
        for item in self.items:
            by_collection[item["collection"]] = by_collection.get(item["collection"], 0) + 1

        return {
            "collections": [
                {
                    "id": key,
                    "label": spec["label"],
                    "desc": spec.get("desc", ""),
                    "count": by_collection.get(key, 0),
                    "categories": categories.get(key, []),
                }
                for key, spec in COLLECTIONS.items()
            ],
            "total": len(self.items),
            "kb_root": str(self.kb_root),
        }

    def list_items(
        self,
        collection: str | None = None,
        category: str | None = None,
        q: str = "",
        limit: int = 12,
        offset: int = 0,
    ) -> dict[str, Any]:
        rows = self.items
        if collection:
            rows = [i for i in rows if i["collection"] == collection]
        if category:
            rows = [i for i in rows if i.get("category") == category]
        if q:
            needle = q.lower()
            rows = [
                i
                for i in rows
                if needle in i["title"].lower() or needle in i["path"].lower()
            ]
        total = len(rows)
        page = rows[offset : offset + limit]
        return {"total": total, "offset": offset, "limit": limit, "items": page}

    def get_content(self, item_id: str) -> dict[str, Any]:
        item = self.by_id.get(item_id)
        if not item:
            raise KeyError(item_id)
        path = self.kb_root / item["path"]
        if not path.is_file() or not _is_safe_path(self.kb_root, path):
            raise FileNotFoundError(item_id)
        raw = path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(raw)
        return {**item, "raw": raw, "body": body, "meta": meta or item.get("meta", {})}


def _is_safe_path(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def json_response(handler: BaseHTTPRequestHandler, payload: Any, status: int = 200) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


def make_handler(catalog: KBCatalog):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:
            print(f"[{self.log_date_time_string()}] {self.address_string()} {fmt % args}")

        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)

            if parsed.path == "/api/health":
                json_response(self, {"ok": True, "total": len(catalog.items)})
                return

            if parsed.path == "/api/meta":
                json_response(self, catalog.meta())
                return

            if parsed.path == "/api/items":
                json_response(
                    self,
                    catalog.list_items(
                        collection=(params.get("collection") or [None])[0],
                        category=(params.get("category") or [None])[0],
                        q=(params.get("q") or [""])[0],
                        limit=int((params.get("limit") or ["12"])[0]),
                        offset=int((params.get("offset") or ["0"])[0]),
                    ),
                )
                return

            if parsed.path == "/api/content":
                item_id = (params.get("id") or [None])[0]
                if not item_id:
                    json_response(self, {"error": "missing id"}, status=400)
                    return
                try:
                    json_response(self, catalog.get_content(item_id))
                except (KeyError, FileNotFoundError):
                    json_response(self, {"error": "not found"}, status=404)
                return

            if parsed.path == "/api/reload":
                catalog.reload()
                json_response(self, {"ok": True, "total": len(catalog.items)})
                return

            file_path = STATIC / parsed.path.lstrip("/")
            if parsed.path == "/":
                file_path = STATIC / "index.html"
            if file_path.is_file() and _is_safe_path(STATIC, file_path):
                content = file_path.read_bytes()
                mime, _ = mimetypes.guess_type(str(file_path))
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", mime or "application/octet-stream")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()

    return Handler


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="U can AI KB preview server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--kb-root", default=str(KB))
    args = parser.parse_args()

    catalog = KBCatalog(Path(args.kb_root))
    handler = make_handler(catalog)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"KB preview: http://{args.host}:{args.port}/  ({len(catalog.items)} articles)")
    print(f"Root: {catalog.kb_root}")
    server.serve_forever()


if __name__ == "__main__":
    main()
