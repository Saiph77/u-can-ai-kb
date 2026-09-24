#!/usr/bin/env python3
"""解析带时间戳的逐字稿，建段落索引，算片段时间码。

为什么需要这个脚本：逐字稿只在每段开头给一个时间戳。当你的剪辑片段
正好从某段开头切入、到某段结尾切出时，边界时间是转写工具给的真实值，
可以直接信任。但只要从段落中间切，就必须靠段内字符位置线性插值估算，
误差通常在正负 2 秒。这两种精度不能混为一谈——脚本会替你标出来。

用法
----
  index    <transcript> [--json out.json] [--offset HH:MM:SS]
           打印全部段落的时间码索引（起、止、时长、字数、语速）

  stats    <transcript> [--speaker NAME]
           语速统计。写口播稿换算时长时用这个数，不要用通用经验值。

  find     <transcript> "一句原话" [--offset HH:MM:SS]
           这句话在第几段、大约第几秒。定位切点时用。

  cut      <transcript> --spec spec.json [--md]
           批量计算片段时间码，输出 markdown 表格。spec 格式见下。

spec.json
---------
  {
    "offset": "00:29:37",          // 视频文件第 0 秒对应逐字稿的哪个时刻
    "segments": [
      {"id": "A", "name": "段落主题",
       "from": {"line": 13, "after": "因为我对于内容的理解是什么"},
       "to":   {"line": 17}},
      {"id": "B", "name": "另一段",
       "from": {"line": 25, "after": "ai 时代内容已经不值钱了"},
       "to":   {"line": 33, "until": "我先拿做演示，比较方便"}}
    ]
  }

  from.after  省略 = 从该段开头进（真实时码）
  to.until    省略 = 到该段结尾出（真实时码）
  两者都是原话子串，脚本会校验它们确实存在，不存在直接报错退出。

支持的逐字稿格式
----------------
  说话人(HH:MM:SS): 文本
  说话人（HH:MM:SS）：文本
  [HH:MM:SS] 说话人: 文本   /   [MM:SS] 文本
  HH:MM:SS 说话人: 文本
  SRT / VTT
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- 时间工具


def to_sec(s):
    """'01:09:02' / '9:02' / '00:01:23,456' -> 秒（float）"""
    s = s.strip().replace(",", ".")
    parts = s.split(":")
    if len(parts) == 3:
        h, m, sec = parts
    elif len(parts) == 2:
        h, m, sec = 0, parts[0], parts[1]
    else:
        raise ValueError(f"无法解析时间: {s}")
    return int(h) * 3600 + int(m) * 60 + float(sec)


def fmt(t):
    """秒 -> 'HH:MM:SS'。负数会被夹到 0，并在返回值前加 '-' 提示 offset 设错了。"""
    neg = t < 0
    t = int(round(abs(t)))
    out = f"{t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}"
    return ("-" + out) if neg else out


def count_units(text):
    """数"音节"：一个汉字算 1，一串连续的拉丁字母/数字算 1。

    中文语速用字/分钟衡量，但逐字稿里混着 ai、skill、100 这类词。
    把它们各算 1 个单位，比按字母数算更接近实际发声时长。
    """
    cjk = len(re.findall(r"[一-鿿]", text))
    latin = len(re.findall(r"[A-Za-z0-9]+", text))
    return cjk + latin


# ---------------------------------------------------------------- 解析

PATTERNS = [
    # 说话人(00:29:37): 文本   /   说话人（00:29:37）：文本
    re.compile(
        r"^(?P<sp>[^()（）\n]{1,40})[(（](?P<t>\d{1,2}:\d{2}(?::\d{2})?)[)）]\s*[:：]\s*(?P<txt>.*)$"
    ),
    # [00:29:37] 说话人: 文本   /   [29:37] 文本
    re.compile(
        r"^\[(?P<t>\d{1,2}:\d{2}(?::\d{2})?)\]\s*(?:(?P<sp>[^:：\n]{1,40})\s*[:：]\s*)?(?P<txt>.*)$"
    ),
    # 00:29:37 说话人: 文本
    re.compile(
        r"^(?P<t>\d{1,2}:\d{2}:\d{2})\s+(?:(?P<sp>[^:：\n]{1,40})\s*[:：]\s*)?(?P<txt>.*)$"
    ),
]

SRT_TIME = re.compile(
    r"(\d{1,2}:\d{2}:\d{2}[,.]\d{1,3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[,.]\d{1,3})"
)


def parse_srt_vtt(raw):
    """SRT/VTT 自带结束时间，比逐字稿精确，直接用。"""
    segs = []
    lines = raw.split("\n")
    i = 0
    while i < len(lines):
        m = SRT_TIME.search(lines[i])
        if not m:
            i += 1
            continue
        start, end = to_sec(m.group(1)), to_sec(m.group(2))
        body = []
        i += 1
        while i < len(lines) and lines[i].strip() and not SRT_TIME.search(lines[i]):
            if not re.fullmatch(r"\d+", lines[i].strip()):
                body.append(lines[i].strip())
            i += 1
        txt = " ".join(body).strip()
        if txt:
            segs.append(
                {"line": i, "speaker": "", "start": start, "end": end, "text": txt,
                 "end_is_real": True}
            )
    return segs


def parse(path):
    raw = Path(path).read_text(encoding="utf-8")
    if SRT_TIME.search(raw):
        segs = parse_srt_vtt(raw)
    else:
        segs = []
        for n, line in enumerate(raw.split("\n"), 1):
            line = line.rstrip()
            if not line.strip():
                continue
            for p in PATTERNS:
                m = p.match(line)
                if m:
                    txt = m.group("txt").strip()
                    if not txt:
                        break
                    segs.append(
                        {
                            "line": n,
                            "speaker": (m.groupdict().get("sp") or "").strip(),
                            "start": to_sec(m.group("t")),
                            "text": txt,
                            "end_is_real": True,
                        }
                    )
                    break

    if not segs:
        sys.exit(
            f"没能从 {path} 里解析出任何带时间戳的段落。\n"
            "检查一下格式是不是脚本支持的那几种（见文件顶部 docstring）。"
        )

    segs.sort(key=lambda s: s["start"])

    # 每段的结束时间 = 下一段的开始时间。最后一段没有下一段，按全局语速估。
    for i, s in enumerate(segs):
        s["chars"] = count_units(s["text"])
    known = [s for i, s in enumerate(segs[:-1])]
    for i, s in enumerate(segs[:-1]):
        s.setdefault("end", segs[i + 1]["start"])
        if "end" not in s or s["end"] is None:
            s["end"] = segs[i + 1]["start"]
    for i, s in enumerate(segs[:-1]):
        s["end"] = s.get("end") or segs[i + 1]["start"]
        if s["end"] <= s["start"]:
            s["end"] = s["start"] + 0.5

    if len(segs) > 1:
        total_c = sum(s["chars"] for s in segs[:-1])
        total_d = sum(s["end"] - s["start"] for s in segs[:-1])
        rate = (total_c / total_d) if total_d else 5.0
    else:
        rate = 5.0
    last = segs[-1]
    if "end" not in last or last["end"] is None:
        last["end"] = last["start"] + max(1.0, last["chars"] / max(rate, 0.1))
        last["end_is_real"] = False

    for s in segs:
        s["dur"] = s["end"] - s["start"]
        s["rate"] = (s["chars"] / s["dur"]) if s["dur"] > 0 else 0.0
    return segs


def by_line(segs):
    return {s["line"]: s for s in segs}


# ---------------------------------------------------------------- 时间码计算


def point(seg, sub=None, at_end=False):
    """算一个切点的时间。

    返回 (秒, 是否真实时码)。sub 为空表示切在段落边界上——那是转写工具
    给的原始时间，可信；否则按字符位置线性插值，标记为估算。
    """
    if sub is None:
        return (seg["end"] if at_end else seg["start"]), True
    i = seg["text"].find(sub)
    if i < 0:
        sys.exit(
            f"L{seg['line']} 里找不到这句话：{sub!r}\n"
            f"该段原文：{seg['text'][:120]}…\n"
            "切点必须是原话的精确子串。检查是不是多打了标点或改了字。"
        )
    if at_end:
        i += len(sub)
    frac = i / max(len(seg["text"]), 1)
    return seg["start"] + frac * seg["dur"], False


def slice_text(seg, after=None, until=None):
    t = seg["text"]
    if after:
        j = t.find(after)
        if j < 0:
            sys.exit(f"L{seg['line']} 里找不到 from.after：{after!r}")
        t = t[j:]
    if until:
        k = t.find(until)
        if k < 0:
            sys.exit(f"L{seg['line']} 里找不到 to.until：{until!r}")
        t = t[: k + len(until)]
    return t


# ---------------------------------------------------------------- 子命令


def cmd_index(args):
    segs = parse(args.transcript)
    off = to_sec(args.offset) if args.offset else 0.0
    if args.json:
        Path(args.json).write_text(
            json.dumps(segs, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"已写入 {args.json}（{len(segs)} 段）")
    print(f"{'行号':>6} {'起':>9} {'止':>9} {'时长':>6} {'字数':>5} {'字/分':>6}  说话人 | 开头")
    for s in segs:
        if args.speaker and s["speaker"] != args.speaker:
            continue
        print(
            f"L{s['line']:<5d} {fmt(s['start'] - off):>9} {fmt(s['end'] - off):>9} "
            f"{s['dur']:>5.0f}s {s['chars']:>5d} {s['rate'] * 60:>6.0f}  "
            f"{s['speaker'][:8]:<8} | {s['text'][:36]}"
        )


def cmd_stats(args):
    segs = parse(args.transcript)
    if args.speaker:
        segs = [s for s in segs if s["speaker"] == args.speaker]
    if not segs:
        sys.exit("筛选后没有段落。检查 --speaker 拼写。")
    # 极短段落的语速噪声很大（一个"对。"占 5 秒），过滤掉再统计
    solid = [s for s in segs if s["chars"] >= 30 and s["dur"] >= 5]
    pool = solid or segs
    c = sum(s["chars"] for s in pool)
    d = sum(s["dur"] for s in pool)
    rates = sorted(s["rate"] * 60 for s in pool)
    mid = rates[len(rates) // 2]
    print(f"段落数 {len(segs)}（用于统计的实心段 {len(pool)}）")
    print(f"总字数 {c}，总时长 {d:.0f}s")
    print(f"平均语速 {c / d * 60:.0f} 字/分钟   中位数 {mid:.0f} 字/分钟")
    print(f"区间 {rates[len(rates) // 10]:.0f} – {rates[-len(rates) // 10 - 1]:.0f} 字/分钟")
    print()
    print("写口播稿换算时长时用上面这个数，不要用 250 字/分钟这类通用经验值——")
    print("每个人语速差异很大，用错基准会让成片时长偏出一两分钟。")


def cmd_find(args):
    segs = parse(args.transcript)
    off = to_sec(args.offset) if args.offset else 0.0
    hits = 0
    for s in segs:
        i = s["text"].find(args.query)
        while i >= 0:
            hits += 1
            frac = i / max(len(s["text"]), 1)
            t = s["start"] + frac * s["dur"]
            edge = "真实时码" if i == 0 else "插值 ±2s"
            print(f"L{s['line']}  {fmt(t - off)}  [{edge}]  …{s['text'][max(0, i - 20):i + 40]}…")
            i = s["text"].find(args.query, i + 1)
    if not hits:
        print(f"原稿里找不到：{args.query!r}")
        sys.exit(1)
    if hits > 1:
        print(f"\n注意：出现了 {hits} 次，做切点的话要挑一个更长、唯一的子串。")


def cmd_cut(args):
    segs = parse(args.transcript)
    idx = by_line(segs)
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    off = to_sec(spec.get("offset", "0:00:00"))

    total = 0.0
    rows_all = []
    print(f"# 剪辑时间码（offset = {spec.get('offset', '0:00:00')}）\n")
    for seg_spec in spec["segments"]:
        f, t = seg_spec["from"], seg_spec["to"]
        if f["line"] not in idx:
            sys.exit(f"spec 里的 line {f['line']} 在逐字稿中不存在")
        if t["line"] not in idx:
            sys.exit(f"spec 里的 line {t['line']} 在逐字稿中不存在")
        a, a_real = point(idx[f["line"]], f.get("after"), at_end=False)
        b, b_real = point(idx[t["line"]], t.get("until"), at_end=True)
        if b <= a:
            sys.exit(f"片段 {seg_spec.get('id')} 的结束时间不晚于开始时间，检查 from/to 顺序")
        dur = b - a
        total += dur

        lines = [s for s in segs if f["line"] <= s["line"] <= t["line"]]
        chars = 0
        rows = []
        for s in lines:
            txt = slice_text(
                s,
                f.get("after") if s["line"] == f["line"] else None,
                t.get("until") if s["line"] == t["line"] else None,
            )
            chars += count_units(txt)
            partial = (s["line"] == f["line"] and f.get("after")) or (
                s["line"] == t["line"] and t.get("until")
            )
            sa = point(s, f.get("after") if s["line"] == f["line"] else None)[0]
            sb = point(s, t.get("until") if s["line"] == t["line"] else None, at_end=True)[0]
            rows.append(
                {
                    "line": s["line"],
                    "speaker": s["speaker"],
                    "start": sa,
                    "end": sb,
                    "partial": bool(partial),
                    "text": txt,
                }
            )
        rows_all.append((seg_spec, a, b, rows))

        print(f"## {seg_spec.get('id', '?')} ｜ {seg_spec.get('name', '')}")
        print(
            f"原稿 {fmt(a)} → {fmt(b)} ｜ 视频内 {fmt(a - off)} → {fmt(b - off)} "
            f"｜ {dur:.0f}s ｜ {chars}字 "
            f"｜ 边界精度 起={'真实' if a_real else '插值±2s'} 止={'真实' if b_real else '插值±2s'}"
        )
        print()
        print("| 原稿行 | 原稿起 | 原稿止 | 视频内起 | 视频内止 | 时长 | 用法 | 时码精度 |")
        print("|---|---|---|---|---|---|---|---|")
        for r in rows:
            print(
                f"| L{r['line']} | {fmt(r['start'])} | {fmt(r['end'])} "
                f"| {fmt(r['start'] - off)} | {fmt(r['end'] - off)} "
                f"| {r['end'] - r['start']:.0f}s "
                f"| {'段内截取' if r['partial'] else '整段'} "
                f"| {'插值 ±2s' if r['partial'] else '原稿时码'} |"
            )
        print()
        if args.quotes:
            for r in rows:
                print(f"> **[L{r['line']}]** {r['text']}")
                print(">")
            print()

    n_real = sum(1 for _, _, _, rows in rows_all for r in rows if not r["partial"])
    n_all = sum(len(rows) for _, _, _, rows in rows_all)
    print("---\n")
    print(f"片段数 {len(rows_all)}，跳切 {max(0, len(rows_all) - 1)} 次")
    print(f"成片总时长 {int(total // 60)} 分 {int(total % 60)} 秒（原速）")
    print(f"段落边界精度：{n_real}/{n_all} 为原稿真实时码，其余 {n_all - n_real} 处为插值估算")


def main():
    ap = argparse.ArgumentParser(
        description="逐字稿解析与剪辑时间码计算",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("index", help="打印段落时间码索引")
    p.add_argument("transcript")
    p.add_argument("--json")
    p.add_argument("--offset")
    p.add_argument("--speaker")
    p.set_defaults(fn=cmd_index)

    p = sub.add_parser("stats", help="语速统计")
    p.add_argument("transcript")
    p.add_argument("--speaker")
    p.set_defaults(fn=cmd_stats)

    p = sub.add_parser("find", help="定位一句原话")
    p.add_argument("transcript")
    p.add_argument("query")
    p.add_argument("--offset")
    p.set_defaults(fn=cmd_find)

    p = sub.add_parser("cut", help="按 spec 批量算片段时间码")
    p.add_argument("transcript")
    p.add_argument("--spec", required=True)
    p.add_argument("--quotes", action="store_true", help="同时输出逐字引用块")
    p.set_defaults(fn=cmd_cut)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
