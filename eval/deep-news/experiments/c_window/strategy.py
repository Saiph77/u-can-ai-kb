"""Variant C — hard date-window pre-filtering on top of B's topical query.

window mode only: compute allowed_paths from frozen frontmatter metadata
(start <= published_at <= end, inclusive), then retrieve the topical query
inside that scope.  Empty scope is a legal empty result — never widened.
All other modes behave exactly like B.
"""
from __future__ import annotations

import sys
from pathlib import Path

_EVAL_DIR = Path(__file__).resolve().parents[2]
if str(_EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(_EVAL_DIR))

from experiments.common.runtime import ranked_from_call  # noqa: E402


def _b():
    from experiments.common.loader import load_strategy
    return load_strategy("b")


def select_paths(window: dict, documents: dict) -> list[str]:
    """Pure function: paths whose published_at falls inside [start, end]."""
    start, end = window["start"], window["end"]
    if not (start <= end):
        raise ValueError(f"inverted window: {start}..{end}")
    return sorted(p for p, meta in documents.items()
                  if start <= meta["published_at"] <= end)


def execute_plan(request: dict, plan: dict, runtime) -> dict:
    if plan["status"] != "ok":
        return _b()._single_call(request, runtime, request["query"], plan, True)
    if plan["mode"] == "window":
        allowed = select_paths(plan["window"], runtime.documents)
        call = runtime.retrieve(plan["topical_query"], request["route"], 100,
                                allowed_paths=allowed)
        return {
            "plan": plan,
            "ranked_documents": ranked_from_call(call, "original_order"),
            "diagnostics": {"fallback": False, "policy": "window_prefilter",
                            "eligible_count": len(allowed),
                            "excluded_count": len(runtime.documents) - len(allowed)},
        }
    return _b()._single_call(request, runtime, plan["topical_query"], plan, False)


def search(request: dict, runtime, normalizer=None) -> dict:
    normalize = normalizer or _b().normalize
    plan = normalize(request["query"], request["as_of"])
    return execute_plan(request, plan, runtime)
