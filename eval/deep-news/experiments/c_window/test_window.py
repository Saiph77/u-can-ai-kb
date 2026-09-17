"""C: select_paths purity + window routing + no-fallback-on-empty."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.c_window import strategy as c  # noqa: E402
from experiments.common.loader import load_eval_core  # noqa: E402
from experiments.common.runtime import Runtime  # noqa: E402

core = load_eval_core()
PATHS = [f"deep-news/articles/d{i:02d}.md" for i in range(1, 6)]
DATES = dict(zip(PATHS, ["2026-06-30", "2026-07-01", "2026-07-15",
                         "2026-07-31", "2026-08-01"]))
CORPUS = {"files": {p: "x" for p in PATHS}, "dates": DATES,
          "canonical": {p: p for p in PATHS}}
DOCS = {p: {"published_at": DATES[p]} for p in PATHS}
WINDOW = {"start": "2026-07-01", "end": "2026-07-31"}


def fake(hits):
    def fn(query, route, limit, allowed_paths, all_paths):
        fn.calls.append((query, allowed_paths))
        return {"command": ["f"], "stdout": "", "stderr": "", "returncode": 0,
                "elapsed_ms": 0,
                "raw_hits": [{"rank": i + 1, "matched_by": "fts", "path": p}
                             for i, p in enumerate(hits)]}
    fn.calls = []
    return fn


def rt(t):
    return Runtime(core=core, documents=DOCS, corpus=CORPUS,
                   strategy_config={}, candidate_budget=100, transport=t)


def req(q="只找 2026 年七月发布的 X。"):
    return {"query": q, "as_of": "2026-09-15", "route": "fts",
            "candidate_budget": 100}


class SelectPaths(unittest.TestCase):
    def test_inclusive_bounds(self):
        got = c.select_paths(WINDOW, DOCS)
        self.assertEqual(got, PATHS[1:4])   # 07-01, 07-15, 07-31 included

    def test_inverted_rejected(self):
        with self.assertRaises(ValueError):
            c.select_paths({"start": "2026-08-01", "end": "2026-07-01"}, DOCS)


class Routing(unittest.TestCase):
    def test_window_prefilters(self):
        t = fake([PATHS[2]])
        res = c.search(req(), rt(t))
        self.assertEqual(t.calls[0][1], PATHS[1:4])
        self.assertEqual(res["diagnostics"]["eligible_count"], 3)
        self.assertEqual(res["diagnostics"]["excluded_count"], 2)
        self.assertEqual([d["path"] for d in res["ranked_documents"]], [PATHS[2]])

    def test_empty_scope_legal_empty(self):
        t = fake([PATHS[0]])
        r = rt(t)
        # craft a plan whose window matches nothing
        plan = {"status": "ok", "mode": "window", "topical_query": "X",
                "window": {"start": "2026-01-01", "end": "2026-01-31"},
                "stages": [], "warnings": []}
        res = c.execute_plan(req(), plan, r)
        self.assertEqual(res["ranked_documents"], [])
        self.assertEqual(len(t.calls), 0)          # no full-corpus fallback

    def test_non_window_identical_to_b(self):
        t = fake([PATHS[0], PATHS[1]])
        res = c.search(req("X 主题，不限发布时间。"), rt(t))
        self.assertIsNone(t.calls[0][1])           # no allowed_paths
        self.assertEqual(res["diagnostics"]["policy"], "normalize")

    def test_gold_independence(self):
        """allowed set derives only from query+metadata (this test: fixed docs)."""
        s1 = c.select_paths(WINDOW, DOCS)
        s2 = c.select_paths(WINDOW, dict(DOCS))
        self.assertEqual(s1, s2)


if __name__ == "__main__":
    unittest.main()
