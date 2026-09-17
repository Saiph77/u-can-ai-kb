"""Shared runtime for the A/B/C/D retrieval experiments.

Contract: eval/deep-news/plans/README.md §5.
- runtime.documents: {path: {"published_at": "YYYY-MM-DD"}} frozen metadata
- runtime.strategy_config: read-only dict for the active strategy
- runtime.retrieve(query, route, budget, allowed_paths=None) -> call dict

All real retrieval goes through transport (zg subprocess or replay); the
strategy never touches subprocess itself.  Every call is budgeted against
request.candidate_budget; exceeding it is a configuration error, not a
quality result.
"""
from __future__ import annotations

import re
import subprocess
import time
from typing import Any, Callable

GLOB_META = re.compile(r"[*?\[\]{}]")
ALLOW_ALL_GLOB = "deep-news/articles/*.md"
EVAL_EXCLUDE = "!eval/**"
MAX_ARGV_BYTES = 200_000  # well below macOS/Linux ARG_MAX; fail loudly first


class BudgetError(RuntimeError):
    """requested_limit would exceed candidate_budget."""


class TransportError(RuntimeError):
    """zg failed, output unparsable, or results escaped allowed_paths."""


def globs_for_allowed(allowed_paths: list[str], all_paths) -> list[str]:
    """Complement-exclusion globs per plans/C-WINDOW §3.

    Include all articles, then exclude every corpus path NOT in
    allowed_paths in stable sorted order.  Correct only because zg applies
    -g rules in order (later rules override earlier ones); appending
    positive globs for the allowed set after the broad include would NOT
    intersect, it would re-include everything.
    """
    allowed = set(allowed_paths)
    globs = [ALLOW_ALL_GLOB]
    for path in sorted(all_paths):
        if path not in allowed:
            globs.append(f"!{path}")
    globs.append(EVAL_EXCLUDE)
    return globs


class ZgTransport:
    """Real retrieval via the zg CLI.  subprocess argv list, never shell."""

    def __init__(self, core, cwd, timeout: int = 120) -> None:
        self.core = core
        self.cwd = cwd
        self.timeout = timeout

    def __call__(self, query: str, route: str, limit: int,
                 allowed_paths: list[str] | None, all_paths) -> dict:
        cmd = ["zg", "query", *self.core.ROUTES[route], query,
               "--limit", str(limit), "--preview", "none", "--refresh", "off"]
        globs = ([ALLOW_ALL_GLOB, EVAL_EXCLUDE] if allowed_paths is None
                 else globs_for_allowed(allowed_paths, all_paths))
        for g in globs:
            cmd += ["-g", g]
        argv_bytes = sum(len(str(a).encode()) + 1 for a in cmd)
        if argv_bytes > MAX_ARGV_BYTES:
            raise TransportError(
                f"argv {argv_bytes}B exceeds limit {MAX_ARGV_BYTES}B")
        start = time.monotonic()
        proc = subprocess.run(cmd, cwd=self.cwd, capture_output=True,
                              text=True, timeout=self.timeout)
        elapsed_ms = (time.monotonic() - start) * 1000
        result = {"command": cmd, "stdout": proc.stdout, "stderr": proc.stderr,
                  "returncode": proc.returncode, "elapsed_ms": elapsed_ms}
        if proc.returncode:
            raise TransportError(
                f"zg exited {proc.returncode}: {proc.stderr[:500]}")
        try:
            result["raw_hits"] = self.core.parse_hits(proc.stdout)
        except ValueError as e:
            raise TransportError(f"unparsable zg output: {e}") from e
        return result


class ReplayTransport:
    """Deterministic transport feeding recorded raw_hits.

    calls_map: {(query, route): [raw_hits, ...]} consumed in call order.
    allowed_paths is applied as a pre-filter on the recorded hits,
    simulating recall-time restriction.
    """

    def __init__(self, calls_map: dict) -> None:
        self.calls_map = {k: list(v) for k, v in calls_map.items()}

    @classmethod
    def from_run(cls, payload: dict) -> "ReplayTransport":
        calls_map: dict[tuple[str, str], list] = {}
        for item in payload.get("items", []):
            for route, res in item.get("routes", {}).items():
                calls = res.get("calls_raw") or res.get("calls")
                if calls:
                    for c in calls:
                        key = (c.get("query") or item["query"], route)
                        calls_map.setdefault(key, []).append(
                            c.get("raw_hits", []))
                elif "raw_hits" in res:
                    calls_map.setdefault((item["query"], route), []).append(
                        res["raw_hits"])
        return cls(calls_map)

    def __call__(self, query: str, route: str, limit: int,
                 allowed_paths: list[str] | None, all_paths) -> dict:
        key = (query, route)
        if not self.calls_map.get(key):
            raise TransportError(
                f"replay has no recorded call for ({query[:40]!r}, {route})")
        raw = self.calls_map[key].pop(0)
        if allowed_paths is not None:
            allowed = set(allowed_paths)
            raw = [h for h in raw if h["path"] in allowed]
        return {"command": ["replay", route, f"--limit {limit}", query],
                "stdout": "", "stderr": "", "returncode": 0,
                "elapsed_ms": 0.0, "raw_hits": raw}


class Runtime:
    """Per-(query, route) runtime handed to the strategy."""

    def __init__(self, *, core, documents: dict, corpus: dict,
                 strategy_config: dict, candidate_budget: int,
                 transport: Callable) -> None:
        self.core = core
        self.documents = documents          # {path: {"published_at": str}}
        self.corpus = corpus                # deep-news corpus_snapshot()
        self.strategy_config = strategy_config or {}
        self.candidate_budget = candidate_budget
        self.requested_limit = 0
        self.calls: list[dict] = []
        self._transport = transport
        self._seq = 0

    # -- contract API ------------------------------------------------------

    def retrieve(self, query: str, route: str, budget: int,
                 allowed_paths: list[str] | None = None) -> dict:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("empty retrieval query")
        if route not in ("hybrid", "fts", "vector"):
            raise ValueError(f"unknown route: {route}")
        if not isinstance(budget, int) or budget <= 0:
            raise ValueError("budget must be a positive int")

        allowed: list[str] | None = None
        if allowed_paths is not None:
            allowed = list(dict.fromkeys(allowed_paths))
            for p in allowed:
                if p not in self.documents:
                    raise ValueError(f"allowed_paths outside corpus: {p}")
                if GLOB_META.search(p):
                    raise ValueError(f"glob metachar in path: {p}")
            if not allowed:
                # legal empty scope: no retrieval, no budget consumed
                self._seq += 1
                call = {"call_id": f"call-{self._seq}", "query": query,
                        "route": route, "limit_requested": 0,
                        "allowed_paths": [], "command": None, "stdout": "",
                        "stderr": "", "returncode": None, "elapsed_ms": 0.0,
                        "raw_hits": [], "documents": [],
                        "short_circuit": "empty_allowed_paths"}
                self.calls.append(call)
                return call

        self._charge(budget)
        raw = self._transport(query, route, budget, allowed,
                              list(self.documents.keys()))
        self._seq += 1
        call = self._finish_call(raw, query, route, budget, allowed)
        if allowed is not None:
            allowed_set = set(allowed)
            for d in call["documents"]:
                if d["path"] not in allowed_set:
                    raise TransportError(
                        f"transport returned out-of-scope path: {d['path']}")
        return call

    # -- internals ---------------------------------------------------------

    def _charge(self, budget: int) -> None:
        if self.requested_limit + budget > self.candidate_budget:
            raise BudgetError(
                f"requested_limit {self.requested_limit}+{budget} exceeds "
                f"candidate_budget {self.candidate_budget}")
        self.requested_limit += budget

    def _finish_call(self, raw: dict, query: str, route: str,
                     budget: int, allowed: list[str] | None) -> dict:
        docs = self.core.document_hits(raw["raw_hits"], self.corpus)
        for i, d in enumerate(docs, 1):
            d["call_rank"] = i
            d["published_at"] = self.corpus["dates"][d["path"]]
        call = {"call_id": f"call-{self._seq}", "query": query, "route": route,
                "limit_requested": budget, "allowed_paths": allowed,
                "command": raw["command"], "stdout": raw["stdout"],
                "stderr": raw["stderr"], "returncode": raw["returncode"],
                "elapsed_ms": raw["elapsed_ms"], "raw_hits": raw["raw_hits"],
                "documents": docs}
        self.calls.append(call)
        return call


def ranked_from_call(call: dict, reason: str) -> list[dict]:
    """call.documents -> SearchResult ranked_documents (full candidate list)."""
    out = []
    for i, d in enumerate(call["documents"], 1):
        out.append({"path": d["path"], "rank": i,
                    "published_at": d["published_at"], "score": None,
                    "provenance": [{"call_id": call["call_id"],
                                    "call_rank": d["call_rank"],
                                    "raw_rank": d["raw_rank"]}],
                    "reason": reason})
    return out
