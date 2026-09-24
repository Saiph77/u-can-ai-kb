"""Variant B — separate temporal intent from the query text (deterministic).

normalize(query, as_of) -> QueryPlan (schema_version 1, see plans/README §4).
search() still retrieves the WHOLE corpus once with only the topical query;
no date filtering, no rerank, no extra recall.

Supported v1 grammar (per plans/B-NORMALIZE §3):
  2026 年 9 月 1 日至 15 日 / 2026 年 8 月 15 日至 9 月 15 日
  2026 年四月 / 2026 年六月至七月 / 2026 年八月
  截至 2026 年 9 月 15 日      (must equal as_of else unsupported)
  优先近两个月                 (prefer_recent, calendar months, clamped)
  不限发布时间                 (none, query kept)
  八月的X、九月的Y             (stages, 2-5; year inferred <= as_of)
  六月到七月的X                (a stage may itself span a month range)

Anything else temporal (bare 最近/近期, conflicting constraints,
unsupported dates) -> status ambiguous/unsupported with the ORIGINAL
query kept verbatim; never guesses a window, never reads gold.
"""
from __future__ import annotations

import calendar
import re
import sys
from datetime import date
from pathlib import Path

_EVAL_DIR = Path(__file__).resolve().parents[2]
if str(_EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(_EVAL_DIR))

from experiments.common.runtime import ranked_from_call  # noqa: E402

CN_DIGIT = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
            "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def cn_num(s: str) -> int:
    """一至三十一 or ASCII digits -> int."""
    s = s.strip()
    if s.isdigit():
        return int(s)
    if s in CN_DIGIT:
        return CN_DIGIT[s]
    total = 0
    if "十" in s:
        left, _, right = s.partition("十")
        total = (CN_DIGIT.get(left, 1) * 10) + CN_DIGIT.get(right, 0)
    elif s:
        total = CN_DIGIT.get(s, 0)
    if not total:
        raise ValueError(f"unsupported numeral: {s}")
    return total


MONTH = r"([一二两三四五六七八九十]{1,2}|十一|十二|\d{1,2})"
DAY = r"([一二三四五六七八九]{0,2}十[一二三四五六七八九]?|\d{1,2})"

RE_NO_DATE = re.compile(r"不限发布时间")
RE_ASOF = re.compile(rf"截至\s*(\d{{4}})\s*年\s*{MONTH}\s*月\s*{DAY}\s*日")
RE_PREFER = re.compile(rf"优先近\s*{MONTH}\s*个?月")
RE_RANGE_FULL = re.compile(
    rf"(\d{{4}})\s*年\s*{MONTH}\s*月\s*{DAY}\s*日\s*[至到]\s*"
    rf"(?:(\d{{4}})\s*年\s*)?(?:{MONTH}\s*月\s*)?{DAY}\s*日")
RE_RANGE_MONTHS = re.compile(
    rf"(\d{{4}})\s*年\s*{MONTH}\s*月\s*[至到]\s*{MONTH}\s*月(?!\s*{DAY}\s*日)")
RE_MONTH_SINGLE = re.compile(rf"(\d{{4}})\s*年\s*{MONTH}\s*月(?!\s*\d|{DAY}\s*日)")
RE_VAGUE = re.compile(r"最近|近期")
RE_COLON = re.compile(r"[：:]")
RE_STAGE_HEAD = re.compile(
    rf"(先看|再看|首先|其次|然后看|以及)?\s*{MONTH}\s*月"
    rf"(?:\s*[至到]\s*{MONTH}\s*月)?\s*的?")
RE_STAGE_TRAILER = re.compile(
    r"[，,、。]?\s*(各要一个阶段的材料|[一二两三四五六七八九十\d]+\s*个?阶段都要)\s*。?\s*$")
RE_YEAR_MONTH = re.compile(rf"\d{{4}}\s*年\s*{MONTH}\s*月")
LEADING_VERBS = re.compile(r"^(只找|查找|找出|找齐|寻找|想找|梳理|把|找)\s*")
GENERIC_ONLY = re.compile(r"^[的文章分析进展报道材料了呢吧啊，。、\s]*$")


def _month_range(year: int, month: int) -> tuple[str, str]:
    last = calendar.monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-01", f"{year:04d}-{month:02d}-{last}"


def _shift_months(d: date, months: int) -> date:
    """Calendar-month subtraction, clamped to the target month's last day."""
    m = d.year * 12 + (d.month - 1) - months
    y, mo = divmod(m, 12)
    mo += 1
    day = min(d.day, calendar.monthrange(y, mo)[1])
    return date(y, mo, day)


def _infer_year(end_month: int, as_of: date) -> int:
    """Undated month: latest occurrence not later than as_of."""
    return as_of.year if end_month <= as_of.month else as_of.year - 1


def _clean_topic(text: str) -> str:
    text = LEADING_VERBS.sub("", text.strip())
    text = re.sub(r"^[，,、。\s]+|[，,、。\s]+$", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def _clean_shared_topic(head: str) -> str:
    t = LEADING_VERBS.sub("", head.strip())
    t = re.sub(r"的[一二两三四五六七八九十\d]+\s*个?阶段.*$", "", t)
    t = re.sub(r"的(讨论演进|演进材料|演进分析|讨论脉络|演进|脉络)$", "", t)
    t = re.sub(r"(找齐|都要|材料)$", "", t)
    return _clean_topic(t)


def _build(query: str, topical: str, mode: str, window, stages,
           status: str, warnings: list, trace: list) -> dict:
    return {"schema_version": 1, "original_query": query,
            "topical_query": topical, "mode": mode, "window": window,
            "stages": stages, "status": status,
            "warnings": warnings, "trace": trace}


def _fallback(query: str, status: str, warnings: list, trace: list) -> dict:
    return _build(query, query, "none", None, [], status, warnings, trace)


def normalize(query: str, as_of: str) -> dict:
    ref = date.fromisoformat(as_of)
    warnings: list[str] = []
    trace: list[dict] = []
    removals: list[tuple[int, int]] = []   # spans in ORIGINAL coordinates

    def span(rule: str, m: re.Match, absorb_prefix: str = "",
             absorb_suffix: str = "") -> None:
        s, e = m.span()
        text = m.group(0)
        if absorb_prefix and text.startswith(absorb_prefix):
            s += len(absorb_prefix)
        while e < len(query) and query[e] in absorb_suffix:
            e += 1
        trace.append({"rule": rule, "text": query[s:e], "start": s, "end": e})
        removals.append((s, e))

    # ---- pass 1: explicit "no date limit" -------------------------------
    no_date = None
    for m in RE_NO_DATE.finditer(query):
        s, e = m.span()
        while s > 0 and query[s - 1] in "，,、 ":
            s -= 1
        while e < len(query) and query[e] in "，,、。":
            e += 1
        no_date = (s, e)
        trace.append({"rule": "no_date_limit", "text": query[s:e],
                      "start": s, "end": e})

    # ---- pass 2: stages ---------------------------------------------------
    stages: list[dict] = []
    stage_descs: list[str] = []
    colon = RE_COLON.search(query)
    if colon:
        head, body = query[:colon.start()], query[colon.end():]
        body_clean = RE_STAGE_TRAILER.sub("", body)
        trailer = RE_STAGE_TRAILER.search(body)
        if trailer:
            s0, e0 = trailer.span()
            trace.append({"rule": "stage_trailer",
                          "text": query[colon.end() + s0:colon.end() + e0],
                          "start": colon.end() + s0, "end": colon.end() + e0})
        heads = list(RE_STAGE_HEAD.finditer(body_clean))
        parsed: list[tuple[int, int, str, int, int]] = []
        ok = bool(heads)
        if ok:
            for i, h in enumerate(heads):
                try:
                    m1 = cn_num(h.group(2))
                    m2 = cn_num(h.group(3)) if h.group(3) else m1
                    if not (1 <= m1 <= 12 and 1 <= m2 <= 12):
                        raise ValueError("month out of range")
                except ValueError:
                    ok = False
                    warnings.append(f"invalid stage month in {h.group(0)!r}")
                    break
                seg_end = heads[i + 1].start() if i + 1 < len(heads) else len(body_clean)
                desc = body_clean[h.end():seg_end]
                desc = desc.strip(" ，,、。；;")
                if not desc or m1 > m2:
                    ok = False
                    break
                s = colon.end() + h.start()
                e = colon.end() + h.end() + len(body_clean[h.end():seg_end])
                parsed.append((m1, m2, desc, s, e))
        else:
            ok = False
        if ok and len(parsed) >= 2:
            if no_date or RE_PREFER.search(query):
                return _fallback(query, "ambiguous",
                                 ["stage form combined with other temporal "
                                  "constraints"], trace)
            shared = _clean_shared_topic(head)
            if not shared:
                warnings.append("stage head yielded empty shared topic")
            for i, (m1, m2, desc, s, e) in enumerate(parsed, 1):
                year = _infer_year(m2, ref)
                start, end = _month_range(year, m1)
                _, end = _month_range(year, m2)
                if end > as_of:
                    warnings.append(f"stage-{i} window end after as_of")
                stages.append({"id": f"stage-{i}",
                               "topical_query": _clean_topic(f"{shared} {desc}") if shared
                               else _clean_topic(desc),
                               "window": {"start": start, "end": end},
                               "source_span": {"start": s, "end": e}})
                stage_descs.append(desc)
                trace.append({"rule": "stage", "text": query[s:e],
                              "start": s, "end": e})
            topical = _clean_topic(
                f"{shared}，{'、'.join(stage_descs)}" if shared
                else "、".join(stage_descs))
            return _build(query, topical, "stages", None, stages,
                          "ok", warnings, trace)
        if ok and len(parsed) == 1:
            warnings.append("colon form but only one stage clause; "
                            "treating as non-stage query")

    # ---- pass 3: explicit windows ----------------------------------------
    window = None
    matched_spans: list[tuple[int, int]] = []
    for m in RE_RANGE_FULL.finditer(query):
        y = int(m.group(1)); mo = cn_num(m.group(2)); d1 = cn_num(m.group(3))
        mo2 = cn_num(m.group(5)) if m.group(5) else mo
        y2 = int(m.group(4)) if m.group(4) else y
        d2 = cn_num(m.group(6))
        try:
            start = date(y, mo, d1).isoformat()
            end = date(y2, mo2, d2).isoformat()
        except ValueError:
            return _fallback(query, "unsupported",
                             [f"invalid explicit date in {m.group(0)!r}"], trace)
        if start > end:
            return _fallback(query, "ambiguous",
                             ["date range inverted"], trace)
        window = {"start": start, "end": end}
        s, e = m.span()
        while e < len(query) and query[e:e + 3] == "发布的":
            e += 3
        trace.append({"rule": "explicit_range", "text": query[s:e],
                      "start": s, "end": e})
        removals.append((s, e))
        matched_spans.append((s, e))
        break
    if window is None:
        for m in RE_RANGE_MONTHS.finditer(query):
            try:
                y = int(m.group(1))
                m1, m2 = cn_num(m.group(2)), cn_num(m.group(3))
                start, _ = _month_range(y, m1)
                _, end = _month_range(y, m2)
            except ValueError:
                return _fallback(query, "unsupported",
                                 [f"invalid month range in {m.group(0)!r}"],
                                 trace)
            if m1 > m2:
                return _fallback(query, "ambiguous",
                                 ["month range inverted"], trace)
            window = {"start": start, "end": end}
            s, e = m.span()
            if query[e:e + 3] == "发布的":
                e += 3
            trace.append({"rule": "month_range", "text": query[s:e],
                          "start": s, "end": e})
            removals.append((s, e))
            matched_spans.append((s, e))
            break
    if window is None:
        for m in RE_MONTH_SINGLE.finditer(query):
            s, e = m.span()
            if any(s < me and e > ms for ms, me in matched_spans):
                continue
            try:
                y = int(m.group(1)); mo = cn_num(m.group(2))
                start, end = _month_range(y, mo)
            except ValueError:
                return _fallback(query, "unsupported",
                                 [f"invalid month in {m.group(0)!r}"], trace)
            window = {"start": start, "end": end}
            if query[e:e + 3] == "发布的":
                e += 3
            trace.append({"rule": "single_month", "text": query[s:e],
                          "start": s, "end": e})
            removals.append((s, e))
            break

    # ---- pass 4: as-of anchor ---------------------------------------------
    asof_ok = True
    m = RE_ASOF.search(query)
    if m:
        d = date(int(m.group(1)), cn_num(m.group(2)), cn_num(m.group(3)))
        s, e = m.span()
        while e < len(query) and query[e] in "，, ":
            e += 1
        trace.append({"rule": "as_of_anchor", "text": query[s:e],
                      "start": s, "end": e})
        removals.append((s, e))
        if d.isoformat() != as_of:
            asof_ok = False
            warnings.append(
                f"as-of anchor {d.isoformat()} != request.as_of {as_of}; "
                "unsupported to avoid fake historical backtest")

    # ---- pass 5: soft preference -------------------------------------------
    prefer = None
    m = RE_PREFER.search(query)
    if m:
        n = cn_num(m.group(1))
        start_d = _shift_months(ref, n)
        prefer = {"start": start_d.isoformat(), "end": as_of, "months": n}
        s, e = m.span()
        while s > 0 and query[s - 1] in "，,、 ":
            s -= 1
        while e < len(query) and query[e] in "的分析，,、。 ":
            e += 1
        trace.append({"rule": "prefer_recent", "text": query[s:e],
                      "start": s, "end": e})
        removals.append((s, e))
    elif RE_VAGUE.search(query) and window is None:
        vague = RE_VAGUE.search(query)
        trace.append({"rule": "vague_recent", "text": vague.group(0),
                      "start": vague.start(), "end": vague.end()})
        return _fallback(query, "ambiguous",
                         ["bare 最近/近期 without determinable window"], trace)

    # ---- conflict / combine --------------------------------------------------
    if no_date and (window or prefer):
        return _fallback(query, "ambiguous",
                         ["conflicting temporal constraints"], trace)
    if window and prefer:
        return _fallback(query, "ambiguous",
                         ["explicit window and soft preference conflict"], trace)
    if not asof_ok:
        return _fallback(query, "unsupported", warnings, trace)

    # "不限发布时间" is a frozen control group: keep the query VERBATIM
    # (plans/B-NORMALIZE §2: v1 完全保留原查询, mode=none).
    if no_date:
        return _build(query, query, "none", None, [], "ok", warnings, trace)

    # more than one unconsumed YYYY年M月 mention -> ambiguous, never guess
    for ym in RE_YEAR_MONTH.finditer(query):
        if not any(s <= ym.start() and ym.end() <= e for s, e in removals):
            return _fallback(query, "ambiguous",
                             ["multiple distinct year-month mentions"], trace)

    if window:
        if window["end"] > as_of:
            warnings.append("window end after as_of")
        mode = "window"
    elif prefer:
        mode = "prefer_recent"
        window = {"start": prefer["start"], "end": prefer["end"]}
    else:
        mode = "none"

    # ---- build topical query --------------------------------------------------
    if mode == "none" and not removals:
        topical = query.strip()
    else:
        removals.sort()
        parts, pos = [], 0
        for s, e in removals:
            parts.append(query[pos:s])
            pos = e
        parts.append(query[pos:])
        topical = _clean_topic("".join(parts))
    if not topical or GENERIC_ONLY.match(topical):
        return _fallback(query, "unsupported",
                         warnings + ["topical query empty/generic after "
                                     "temporal removal"], trace)
    return _build(query, topical, mode, window, stages, "ok", warnings, trace)


def _single_call(request: dict, runtime, query_text: str, plan: dict,
                 fallback: bool) -> dict:
    call = runtime.retrieve(query_text, request["route"], 100,
                            allowed_paths=None)
    return {"plan": plan,
            "ranked_documents": ranked_from_call(call, "original_order"),
            "diagnostics": {"fallback": fallback, "policy": "normalize"}}


def search(request: dict, runtime) -> dict:
    plan = normalize(request["query"], request["as_of"])
    if plan["status"] != "ok":
        return _single_call(request, runtime, request["query"], plan, True)
    return _single_call(request, runtime, plan["topical_query"], plan, False)
