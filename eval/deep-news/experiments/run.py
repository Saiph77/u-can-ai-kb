#!/usr/bin/env python3
"""Unified experiment runner for variants a/b/c/d.

    python3 eval/deep-news/experiments/run.py --variant a
    python3 eval/deep-news/experiments/run.py --variant d \
        --strategy-config eval/deep-news/experiments/d_temporal/config.json \
        --label d
    python3 eval/deep-news/experiments/run.py --variant a --replay <history.json>

Writes an independent directory under
eval/deep-news/runs/experiments/<label-or-variant>/<run-id>/ — never a
shared latest file.  The strategy sees only the whitelisted request
fields; gold stays on the scoring side.
"""
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVAL_DIR = HERE.parent
REPO_ROOT = EVAL_DIR.parents[1]
sys.path.insert(0, str(EVAL_DIR))

from experiments.common import evaluation  # noqa: E402
from experiments.common.loader import (load_eval_core, load_eval_deepnews,  # noqa: E402
                                       load_strategy)
from experiments.common.runtime import (BudgetError, ReplayTransport,  # noqa: E402
                                        Runtime, TransportError, ZgTransport)

REQUEST_FIELDS = ("query", "as_of", "route", "candidate_budget")


def build_request(q: dict, route: str, budget: int) -> dict:
    return {"query": q["query"], "as_of": q["as_of"], "route": route,
            "candidate_budget": budget}


def route_diagnostics(items: list[dict], route: str) -> dict:
    calls = requested = 0
    elapsed, cand = [], []
    fallbacks = []
    for item in items:
        res = item["routes"][route]
        calls += len(res.get("calls", []))
        requested += res.get("budget_used", 0)
        elapsed.extend(c.get("elapsed_ms", 0) for c in res.get("calls", []))
        cand.append(res.get("unique_candidate_count", 0))
        if res.get("diagnostics", {}).get("fallback"):
            fallbacks.append(item["id"])
    return {"calls": calls, "requested_limit": requested,
            "candidates_median": statistics.median(cand) if cand else None,
            "elapsed_median_ms": round(statistics.median(elapsed), 1) if elapsed else 0,
            "elapsed_p95_ms": round(sorted(elapsed)[max(0, int(len(elapsed) * .95) - 1)], 1)
            if elapsed else 0,
            "fallback_queries": fallbacks}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--variant", required=True, choices=["a", "b", "c", "d"])
    p.add_argument("--routes", default="hybrid,fts,vector")
    p.add_argument("--ids", default="")
    p.add_argument("--strategy-config", default="")
    p.add_argument("--label", default="")
    p.add_argument("--replay", default="",
                   help="run JSON whose recorded calls feed a ReplayTransport")
    args = p.parse_args()

    core = load_eval_core()
    dn = load_eval_deepnews()

    routes = args.routes.split(",")
    if not routes or len(routes) != len(set(routes)) \
            or any(r not in core.ROUTES for r in routes):
        p.error("invalid or duplicate routes")
    label = args.label or args.variant

    # ---- frozen inputs ---------------------------------------------------
    source_paths = [EVAL_DIR / "queries.json", EVAL_DIR / "judgments.json",
                    EVAL_DIR / "run.py", REPO_ROOT / "eval/zg/run.py"]
    frozen = {str(pth): pth.read_bytes() for pth in source_paths}
    spec = json.loads(frozen[str(EVAL_DIR / "queries.json")])
    judgments = json.loads(frozen[str(EVAL_DIR / "judgments.json")])
    corpus = dn.corpus_snapshot()
    dn.validate(spec, judgments, corpus)

    wanted = set(filter(None, args.ids.split(",")))
    if wanted - {q["id"] for q in spec["queries"]}:
        p.error("unknown query ids")
    queries = [q for q in spec["queries"] if not wanted or q["id"] in wanted]

    # ---- strategy + config ------------------------------------------------
    strategy = load_strategy(args.variant)
    variant_dir = {"a": "a_baseline", "b": "b_normalize",
                   "c": "c_window", "d": "d_temporal"}[args.variant]
    strategy_files = sorted((HERE / variant_dir).glob("*.py"))
    common_files = sorted((HERE / "common").glob("*.py")) + [HERE / "run.py"]

    if args.strategy_config:
        cfg_path = Path(args.strategy_config)
        strategy_config = json.loads(cfg_path.read_text())
    elif args.variant == "d":
        cfg_path = HERE / "d_temporal/config.json"
        strategy_config = json.loads(cfg_path.read_text())
    else:
        cfg_path, strategy_config = None, {}
    cfg_raw = cfg_path.read_bytes() if cfg_path else b"{}"

    # ---- transport ---------------------------------------------------------
    replay = None
    if args.replay:
        replay_payload = json.loads(Path(args.replay).read_text())
        replay = ReplayTransport.from_run(replay_payload)
        transport = replay
    else:
        manifest_path = REPO_ROOT / ".zvec-grep/manifest.json"
        manifest_raw = manifest_path.read_bytes()
        manifest = json.loads(manifest_raw)
        if not manifest["rootPaths"] or any(
                "!eval/**" not in r.get("globs", []) for r in manifest["rootPaths"]):
            p.error("index roots must exclude eval/**")
        transport = ZgTransport(core, REPO_ROOT)

    documents = {path: {"published_at": d} for path, d in corpus["dates"].items()}
    run_dir = evaluation.new_run_dir(label)
    snapshots = {**{pth.name: pth.read_bytes() for pth in strategy_files},
                 **{f"common/{pth.name}": pth.read_bytes() for pth in common_files}}
    for name, data in snapshots.items():
        (run_dir / "src").mkdir(exist_ok=True)
        (run_dir / "src" / name.replace("/", "__")).write_bytes(data)
    (run_dir / "queries.json").write_bytes(frozen[str(EVAL_DIR / "queries.json")])
    (run_dir / "judgments.json").write_bytes(frozen[str(EVAL_DIR / "judgments.json")])
    (run_dir / "strategy-config.json").write_bytes(cfg_raw)

    payload = {"eval": spec["name"], "variant": args.variant, "label": label,
               "at": datetime.now(timezone.utc).isoformat(),
               "as_of": spec["as_of"],
               "candidate_budget": spec["candidate_budget"], "routes": routes,
               "corpus": corpus, "replay": args.replay or None,
               "strategy_config": strategy_config,
               "strategy_config_sha256": core.digest(cfg_raw),
               "source_sha256": {
                   **{pth.relative_to(REPO_ROOT).as_posix(): core.digest(frozen[str(pth)])
                      for pth in source_paths},
                   **{f"experiments/{n}": core.digest(d) for n, d in snapshots.items()}},
               "queries_sha256": core.digest(frozen[str(EVAL_DIR / "queries.json")]),
               "judgments_sha256": core.digest(frozen[str(EVAL_DIR / "judgments.json")]),
               "zg_version": (subprocess.check_output(["zg", "--version"], text=True).strip()
                              if not args.replay else "replay"),
               "items": []}

    for i, q in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] {q['id']}", flush=True)
        item = {**q, "routes": {}}
        for route in routes:
            res: dict = {}
            try:
                rt = Runtime(core=core, documents=documents, corpus=corpus,
                             strategy_config=strategy_config,
                             candidate_budget=spec["candidate_budget"],
                             transport=transport)
                result = strategy.search(build_request(q, route,
                                                       spec["candidate_budget"]), rt)
                docs = result["ranked_documents"]
                if any(d["path"] not in corpus["files"] for d in docs):
                    raise TransportError("strategy emitted out-of-corpus doc")
                if any("call_id" not in prov for d in docs
                       for prov in d.get("provenance", [])):
                    raise TransportError("doc without call provenance")
                res.update(plan=result["plan"], diagnostics=result["diagnostics"],
                           calls=[{k: c[k] for k in
                                   ("call_id", "query", "route", "limit_requested",
                                    "elapsed_ms", "returncode")}
                                  | {"allowed_count": (len(c["allowed_paths"])
                                     if c["allowed_paths"] is not None else None),
                                     "allowed_sha256": (core.digest(
                                         json.dumps(c["allowed_paths"]).encode())
                                         if c["allowed_paths"] else None)}
                                  for c in rt.calls],
                           calls_raw=[{"call_id": c["call_id"], "query": c["query"],
                                       "route": c["route"], "raw_hits": c["raw_hits"]}
                                      for c in rt.calls],
                           budget_used=rt.requested_limit,
                           ranked_documents=docs,
                           hits=docs[:10], unique_candidate_count=len(docs),
                           metrics=dn.metrics_for(docs, q, corpus))
            except (OSError, subprocess.SubprocessError, ValueError,
                    BudgetError, TransportError) as e:
                res["error"] = f"{type(e).__name__}: {e}"
            item["routes"][route] = res
            if "error" in res:
                print(f"  {route}: ERROR {res['error']}", flush=True)
            else:
                m = res["metrics"]
                print(f"  {route}: Primary@5={m['primary_at_5']:.0f} "
                      f"Task@5={m['task_success_at_5']:.0f} "
                      f"cand={res['unique_candidate_count']}", flush=True)
        payload["items"].append(item)
        (run_dir / "checkpoint.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

    payload["summary"] = {r: evaluation.aggregate(payload["items"], r, dn)
                          for r in routes}
    kinds = sorted({q["kind"] for q in queries})
    payload["by_kind"] = {k: {r: evaluation.aggregate(
        [q for q in payload["items"] if q["kind"] == k], r, dn)
        for r in routes} for k in kinds}
    payload["diagnostics"] = {r: route_diagnostics(payload["items"], r)
                              for r in routes}
    unchanged = (corpus["sha256"] == dn.corpus_snapshot()["sha256"]
                 and all(pth.read_bytes() == frozen[str(pth)] for pth in source_paths))
    if not args.replay:
        unchanged = unchanged and manifest_raw == manifest_path.read_bytes()
    payload["snapshot_unchanged"] = unchanged
    payload["valid"] = unchanged and all(
        not b["errors"] for b in payload["summary"].values())
    report = evaluation.render_report(payload, dn)
    evaluation.write_run(run_dir, payload, report)
    print(report)
    print(f"Artifacts: {run_dir}")
    if not payload["valid"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
