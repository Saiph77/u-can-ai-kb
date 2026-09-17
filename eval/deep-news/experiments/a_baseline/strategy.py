"""Variant A — frozen baseline.

Original query, whole corpus, original ranking.  One retrieval call at
limit=100 with allowed_paths=None; dedupe fragments to documents by first
hit, keep order.  The plan is a passthrough marker: no time inference.
"""
from __future__ import annotations

from experiments.common.runtime import ranked_from_call


def search(request: dict, runtime) -> dict:
    call = runtime.retrieve(request["query"], request["route"], 100,
                            allowed_paths=None)
    return {
        "plan": {"schema_version": 1, "original_query": request["query"],
                 "topical_query": request["query"], "mode": "none",
                 "window": None, "stages": [], "status": "ok",
                 "warnings": [], "trace": []},
        "ranked_documents": ranked_from_call(call, "original_order"),
        "diagnostics": {"fallback": False, "policy": "baseline"},
    }
