#!/usr/bin/env python3
"""校验剪辑单里的每一个字都是原话。

为什么这一步不能省：剪辑单的全部价值在于剪辑师能拿文字去搜字幕文件、
找到对应的那一帧。只要有一个字是改写的，那句话就搜不到，剪辑就卡住。

而改写的诱惑非常大。整段引用时人不太会动手，但一到摘"金句卡点"这种
短句，就会不自觉地把"他的创作主题，加上颗粒，再加上技能或者叫技巧"
压成"主题 + 颗粒 + 技能"——更好看，也更没用。这类错误肉眼几乎发现不了，
只有跑程序才抓得住。

用法
----
  python verify_verbatim.py <cutlist.md> <transcript>
  python verify_verbatim.py <cutlist.md> <transcript> --strict

校验对象
--------
  1. 引用块       以 '> ' 开头的行（会剥掉 '**[L12]**' 这类行号标记）
  2. 反引号短语   `……`，用于 IN/OUT 切点和字幕卡点句
     自动跳过：纯时间码、文件名、路径、纯英文标识符

退出码 0 = 全部通过；1 = 有不符项。--strict 下额外要求每个短语在
原稿中唯一出现（做切点用的串如果出现多次，剪辑师会定位到错的地方）。
"""

import argparse
import re
import sys
from pathlib import Path

TS_LINE = re.compile(
    r"^(?:[^()（）\n]{1,40}[(（](\d{1,2}:\d{2}(?::\d{2})?)[)）]\s*[:：]\s*"
    r"|\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*(?:[^:：\n]{1,40}\s*[:：]\s*)?"
    r"|(\d{1,2}:\d{2}:\d{2})\s+(?:[^:：\n]{1,40}\s*[:：]\s*)?)(?P<txt>.*)$"
)
SRT_TIME = re.compile(r"\d{1,2}:\d{2}:\d{2}[,.]\d{1,3}\s*-->")

# 反引号里这些东西不是原话，不该被校验
SKIP = [
    re.compile(r"^[\d:：.,\s\-–—]+$"),          # 纯时间码/数字
    re.compile(r"^[\w./\\-]+\.\w{1,5}$"),        # 文件名
    re.compile(r"^[/~][\w./\\-]*$"),             # 路径
    re.compile(r"^--?[\w-]+$"),                  # 命令行参数
    re.compile(r"^[A-Za-z_][\w.]*\(\)?$"),       # 函数名/标识符
    re.compile(r"[*\[\]>]"),                     # markdown 标记，是格式示例不是引文
]


def load_transcript(path):
    """返回 (拼接后的全文, {行号: 该行正文})。"""
    raw = Path(path).read_text(encoding="utf-8")
    per_line = {}
    if SRT_TIME.search(raw):
        for n, line in enumerate(raw.split("\n"), 1):
            t = line.strip()
            if t and not SRT_TIME.search(t) and not re.fullmatch(r"\d+", t):
                per_line[n] = t
    else:
        for n, line in enumerate(raw.split("\n"), 1):
            m = TS_LINE.match(line.rstrip())
            if m and m.group("txt").strip():
                per_line[n] = m.group("txt").strip()
    if not per_line:
        sys.exit(f"没能从 {path} 解析出内容，检查格式。")
    return "".join(per_line.values()), per_line


def extract(cutlist):
    """从剪辑单里抽出所有需要校验的字符串。"""
    items = []
    for n, line in enumerate(Path(cutlist).read_text(encoding="utf-8").split("\n"), 1):
        s = line.rstrip()
        if s.startswith(">"):
            body = s.lstrip("> ").strip()
            m = re.match(r"^\*\*\[L(\d+)\]\*\*\s*(.*)$", body)
            if m:
                items.append(("引用块", n, int(m.group(1)), m.group(2)))
            elif body and body not in ("", "**"):
                items.append(("引用块", n, None, body))
        for q in re.findall(r"`([^`\n]+)`", s):
            if any(p.match(q) for p in SKIP):
                continue
            items.append(("短语", n, None, q))
    return items


def diverge(quote, source):
    """找出引文从第几个字开始跟原文对不上，并给出上下文。"""
    best, best_k = None, -1
    head = quote[: min(len(quote), 12)]
    for start in [m.start() for m in re.finditer(re.escape(head), source)] or [None]:
        if start is None:
            return 0, ""
        k = 0
        while k < len(quote) and start + k < len(source) and quote[k] == source[start + k]:
            k += 1
        if k > best_k:
            best_k, best = k, start
    ctx = source[best : best + best_k + 30] if best is not None else ""
    return best_k, ctx


def main():
    ap = argparse.ArgumentParser(description="校验剪辑单是否逐字忠于原稿")
    ap.add_argument("cutlist")
    ap.add_argument("transcript")
    ap.add_argument("--strict", action="store_true", help="额外要求每个短语在原稿中唯一出现")
    args = ap.parse_args()

    full, per_line = load_transcript(args.transcript)
    items = extract(args.cutlist)
    if not items:
        sys.exit("剪辑单里没找到任何引用块或反引号短语，检查文件路径和格式。")

    bad, ambiguous = [], []
    by_kind = {}
    for kind, mdline, srcline, text in items:
        by_kind[kind] = by_kind.get(kind, 0) + 1
        # 带行号的引用块要求落在指定那一行里，定位更严
        scope = per_line.get(srcline) if srcline else full
        if srcline and srcline not in per_line:
            bad.append((kind, mdline, srcline, text, f"原稿里没有 L{srcline} 这一行"))
            continue
        if text in scope:
            if args.strict and kind == "短语" and full.count(text) > 1:
                ambiguous.append((mdline, text, full.count(text)))
            continue
        k, ctx = diverge(text, scope)
        loc = f"L{srcline}" if srcline else "原稿"
        if k == 0:
            why = (f"{loc}里完全没有这句话，开头几个字就对不上。"
                   "多半是整句改写的，或者把不相邻的两处拼在了一起。")
        else:
            why = (f"在{loc}中前 {k} 个字对得上，从第 {k + 1} 个字起开始分岔"
                   f"｜剪辑单写的：…{text[max(0, k - 12):k + 20]}…"
                   + (f"｜原稿实际是：…{ctx}…" if ctx else ""))
        bad.append((kind, mdline, srcline, text, why))

    print(f"校验 {args.cutlist}  ←→  {args.transcript}")
    print(f"检查对象：" + "，".join(f"{k} {v} 条" for k, v in by_kind.items()))
    print()

    if bad:
        print(f"✗ {len(bad)} 处不是原话：\n")
        for kind, mdline, srcline, text, why in bad:
            print(f"  [{kind}] 剪辑单第 {mdline} 行")
            print(f"    {text[:90]}")
            print(f"    → {why}\n")

    if ambiguous:
        print(f"⚠ {len(ambiguous)} 个短语在原稿中出现多次，做切点会定位到错的位置：\n")
        for mdline, text, c in ambiguous:
            print(f"  第 {mdline} 行：{text[:60]}  （出现 {c} 次，换一个更长的唯一子串）\n")

    if not bad and not ambiguous:
        print(f"✓ 全部 {len(items)} 条与原稿逐字一致，零处改动。")
        print("  可以把这份剪辑单交给剪辑 agent 了。")
        return 0

    print("修法：把不符的地方替换成原稿里的连续子串。宁可留着口误和重复词，")
    print("也不要为了顺口改字——观众听到的是原声，字幕必须跟原声对齐。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
