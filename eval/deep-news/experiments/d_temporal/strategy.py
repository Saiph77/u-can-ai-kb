"""Variant D — soft recency preference + staged coverage retrieval.

Routing (per plans/D-TEMPORAL §2):
  status != ok   -> B fallback
  none           -> identical to B
  window         -> delegated to C.execute_plan (hard window stays C's job)
  prefer_recent  -> B's single topical call, then recency rerank (soft)
  stages         -> per-stage windowed recall sharing the total budget,
                    then round-robin coverage merge (stages)

Both mechanisms can be disabled independently via strategy_config:
  {"soft": {"enabled": false, ...}}  -> prefer_recent behaves like B
  {"stages": {"enabled": false}}     -> stages behave like B (single call)
"""
from __future__ import annotations

import sys
from pathlib import Path

_EVAL_DIR = Path(__file__).resolve().parents[2]
if str(_EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(_EVAL_DIR))

from experiments.common.loader import load_strategy_module  # noqa: E402
from experiments.common.runtime import ranked_from_call  # noqa: E402

MAX_STAGES = 5
CONFIG_SCHEMA = {"soft": {"enabled": bool, "rank_constant": (int, float),
                          "half_life_days": (int, float), "weight": (int, float)},
                 "stages": {"enabled": bool}}


def _b():
    from experiments.common.loader import load_strategy
    return load_strategy("b")


def _c():
    from experiments.common.loader import load_strategy
    return load_strategy("c")


def validate_config(cfg: dict) -> dict:
    unknown = set(cfg) - set(CONFIG_SCHEMA)
    if unknown:
        raise ValueError(f"unknown config sections: {sorted(unknown)}")
    soft = cfg.get("soft", {})
    stages = cfg.get("stages", {})
    unknown = set(soft) - set(CONFIG_SCHEMA["soft"])
    if unknown:
        raise ValueError(f"unknown soft fields: {sorted(unknown)}")
    unknown = set(stages) - set(CONFIG_SCHEMA["stages"])
    if unknown:
        raise ValueError(f"unknown stages fields: {sorted(unknown)}")
    return {"soft": {"enabled": True, "rank_constant": 60,
                     "half_life_days": 30, "weight": 0.25, **soft},
            "stages": {"enabled": True, **stages}}


def _prefer_recent(request, plan, runtime, cfg, recency):
    call = runtime.retrieve(plan["topical_query"], request["route"], 100,
                            allowed_paths=None)
    docs = ranked_from_call(call, "original_order")
    if not cfg["soft"]["enabled"]:
        return {"plan": plan, "ranked_documents": docs,
                "diagnostics": {"fallback": False, "policy": "b_like",
                                "soft": "disabled"}}
    docs = recency.rerank_recency(docs, request["as_of"], cfg["soft"])
    return {"plan": plan, "ranked_documents": docs,
            "diagnostics": {"fallback": False, "policy": "recency_soft",
                            "soft": cfg["soft"]}}


def _stages(request, plan, runtime, cfg, c_mod, stages_mod):
    if not cfg["stages"]["enabled"]:
        return _b()._single_call(request, runtime, plan["topical_query"],
                                 plan, False)
    if not (2 <= len(plan["stages"]) <= MAX_STAGES):
        return _b()._single_call(request, runtime, plan["topical_query"],
                                 {**plan, "warnings": plan["warnings"] + [
                                     f"{len(plan['stages'])} stages outside "
                                     f"2-{MAX_STAGES}; single-call fallback"]})
    budgets = stages_mod.allocate_budget(request["candidate_budget"],
                                         len(plan["stages"]))
    stage_doc_lists, stage_info = [], []
    for stage, budget in zip(plan["stages"], budgets):
        allowed = c_mod.select_paths(stage["window"], runtime.documents)
        info = {"stage": stage["id"], "window": stage["window"],
                "budget": budget, "eligible_count": len(allowed)}
        if not allowed:
            info["call"] = None          # zero-call stage; budget NOT reused
            stage_doc_lists.append([])
        else:
            call = runtime.retrieve(stage["topical_query"], request["route"],
                                    budget, allowed_paths=allowed)
            info["call"] = call["call_id"]
            stage_doc_lists.append(ranked_from_call(call, "original_order"))
        stage_info.append(info)
    merged = stages_mod.merge_stages(stage_doc_lists)
    return {"plan": plan, "ranked_documents": merged,
            "diagnostics": {"fallback": False, "policy": "staged_coverage",
                            "stages": stage_info}}


def search(request: dict, runtime) -> dict:
    cfg = validate_config(runtime.strategy_config)
    recency = load_strategy_module("d", "recency")
    stages_mod = load_strategy_module("d", "stages")
    plan = _b().normalize(request["query"], request["as_of"])
    if plan["status"] != "ok":
        return _b()._single_call(request, runtime, request["query"], plan, True)
    mode = plan["mode"]
    if mode == "window":
        return _c().execute_plan(request, plan, runtime)
    if mode == "prefer_recent":
        return _prefer_recent(request, plan, runtime, cfg, recency)
    if mode == "stages":
        return _stages(request, plan, runtime, cfg, _c(), stages_mod)
    return _b()._single_call(request, runtime, plan["topical_query"], plan, False)
