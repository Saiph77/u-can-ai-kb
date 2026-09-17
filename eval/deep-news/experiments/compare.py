#!/usr/bin/env python3
"""Compare experiment runs.  Usage:

    python3 eval/deep-news/experiments/compare.py runA.json runB.json [runC.json runD.json]

Inputs are explicit run files (never a guessed latest).  Runs are only
comparable when corpus / queries / judgments / scorer fingerprints, qid
sets, routes, budget and as_of all match and every run is valid.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVAL_DIR = HERE.parent
REPO_ROOT = EVAL_DIR.parents[1]
sys.path.insert(0, str(EVAL_DIR))

COMPARE_METRICS = ["hit_at_1", "primary_at_5", "recall_at_5", "ndcg_at_10",
                   "task_success_at_5", "window_primary_at_5",
                   "stage_coverage_at_5", "all_stages_at_5",
                   "candidate_task_success"]


def check_comparable(payloads: list[dict]) -> None:
    base = payloads[0]
    keys = ["as_of", "candidate_budget", "queries_sha256", "judgments_sha256"]
    for i, p in enumerate(payloads[1:], 1):
        for k in keys:
            if p.get(k) != base.get(k):
                raise SystemExit(f"not comparable: {k} differs "
                                 f"({base.get(k)} vs {p.get(k)})")
        if p["corpus"]["sha256"] != base["corpus"]["sha256"]:
            raise SystemExit("not comparable: corpus fingerprint differs")
        if {q["id"] for q in p["items"]} != {q["id"] for q in base["items"]}:
            raise SystemExit("not comparable: qid sets differ")
        if set(p["routes"]) != set(base["routes"]):
            raise SystemExit("not comparable: routes differ")
        scorer = {k: v for k, v in p["source_sha256"].items()
                  if not k.startswith("experiments/")}
        base_scorer = {k: v for k, v in base["source_sha256"].items()
                       if not k.startswith("experiments/")}
        if scorer != base_scorer:
            raise SystemExit("not comparable: scorer/queries fingerprints differ")
    for p in payloads:
        if not p.get("valid"):
            raise SystemExit(f"invalid run cannot be ranked: "
                             f"{p['variant']}/{p.get('label')}")


def fmt(v) -> str:
    return "—" if v is None else f"{v:.3f}"


def main() -> None:
    paths = sys.argv[1:]
    if len(paths) < 2:
        raise SystemExit("usage: compare.py run1.json run2.json [more.json]")
    payloads = [json.loads(Path(p).read_text()) for p in paths]
    check_comparable(payloads)
    routes = payloads[0]["routes"]
    names = [f"{p['variant']}:{p.get('label') or p['variant']}" for p in payloads]
    kinds = sorted({q["kind"] for q in payloads[0]["items"]})

    out = ["# 实验对比", "",
           "| run | " + " | ".join(names) + " |",
           "|---|" + "---:|" * len(names)]
    for scope, filt in [("全体", lambda q: True)] + \
                       [(k, (lambda kk: (lambda q: q["kind"] == kk))(k)) for k in kinds]:
        for m in COMPARE_METRICS:
            row = f"| {scope} {m} |"
            for p in payloads:
                items = [q for q in p["items"] if filt(q)]
                # mean over routes of the per-route metric
                vals = []
                for r in routes:
                    xs = [q["routes"][r].get("metrics", {}).get(m)
                          for q in items]
                    xs = [x for x in xs if x is not None]
                    vals.append(sum(xs) / len(xs) if xs else None)
                avg = sum(v for v in vals if v is not None) / len(vals) \
                    if any(v is not None for v in vals) else None
                row += f" {fmt(avg)} |"
            out.append(row)
    out.append("")

    # per-query win/tie/loss on task_success_at_5 (mean over routes)
    out += ["## 逐题 Task@5 对比（相对第一个 run）", "",
            "| qid | " + " | ".join(names[1:]) + " |", "|---|" + "---|" * (len(names) - 1)]
    base_by_id = {q["id"]: q for q in payloads[0]["items"]}
    wins = {n: 0 for n in names[1:]}
    ties = {n: 0 for n in names[1:]}
    losses = {n: 0 for n in names[1:]}
    for qid, bq in base_by_id.items():
        b = sum(bq["routes"][r].get("metrics", {}).get("task_success_at_5") or 0
                for r in routes) / len(routes)
        row = f"| {qid} |"
        for p, n in zip(payloads[1:], names[1:]):
            pq = next(q for q in p["items"] if q["id"] == qid)
            v = sum(pq["routes"][r].get("metrics", {}).get("task_success_at_5") or 0
                    for r in routes) / len(routes)
            mark = "win" if v > b else ("loss" if v < b else "=")
            wins[n] += v > b
            losses[n] += v < b
            ties[n] += v == b
            row += f" {mark} ({b:.0f}→{v:.0f}) |"
        out.append(row)
    out.append("")
    for n in names[1:]:
        out.append(f"- {n}: win {wins[n]} / tie {ties[n]} / loss {losses[n]}")
    out.append("")

    out += ["## 诊断", ""]
    for p, n in zip(payloads, names):
        for r in routes:
            d = p["diagnostics"][r]
            out.append(f"- {n} {r}: calls={d['calls']} "
                       f"requested={d['requested_limit']} "
                       f"median_ms={d['elapsed_median_ms']} "
                       f"p95_ms={d['elapsed_p95_ms']} "
                       f"fallback={len(d['fallback_queries'])}")
    print("\n".join(out))


if __name__ == "__main__":
    main()
