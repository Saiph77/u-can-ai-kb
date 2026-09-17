"""Contract tests for common.runtime (budget, scope, transport rules)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.common import runtime as rt_mod  # noqa: E402
from experiments.common.loader import load_eval_core  # noqa: E402
from experiments.common.runtime import (BudgetError, Runtime,  # noqa: E402
                                        TransportError, globs_for_allowed)

core = load_eval_core()

PATHS = [f"deep-news/articles/a{i}.md" for i in range(5)]
DATES = {p: f"2026-08-0{i+1}" for i, p in enumerate(PATHS)}
CORPUS = {"files": {p: "x" for p in PATHS},
          "dates": DATES, "canonical": {p: p for p in PATHS}}
DOCS = {p: {"published_at": DATES[p]} for p in PATHS}


def fake_transport(hits):
    def fn(query, route, limit, allowed_paths, all_paths):
        fn.calls.append((query, route, limit, allowed_paths))
        return {"command": ["fake"], "stdout": "", "stderr": "",
                "returncode": 0, "elapsed_ms": 1.0, "raw_hits": hits}
    fn.calls = []
    return fn


def hits(*paths):
    return [{"rank": i + 1, "matched_by": "fts", "path": p}
            for i, p in enumerate(paths)]


def make(transport, budget=100):
    return Runtime(core=core, documents=DOCS, corpus=CORPUS,
                   strategy_config={}, candidate_budget=budget,
                   transport=transport)


class BudgetTest(unittest.TestCase):
    def test_34_33_33_ok(self):
        rt = make(fake_transport(hits(PATHS[0])))
        for b in (34, 33, 33):
            rt.retrieve("q", "fts", b)
        self.assertEqual(rt.requested_limit, 100)

    def test_34_34_33_rejected(self):
        rt = make(fake_transport(hits(PATHS[0])))
        rt.retrieve("q", "fts", 34)
        rt.retrieve("q", "fts", 34)
        with self.assertRaises(BudgetError):
            rt.retrieve("q", "fts", 33)

    def test_empty_scope_no_charge_no_call(self):
        t = fake_transport(hits(PATHS[0]))
        rt = make(t)
        rt.retrieve("q", "fts", 100)
        res = rt.retrieve("q", "fts", 100, allowed_paths=[])
        self.assertEqual(res["documents"], [])
        self.assertEqual(res["limit_requested"], 0)
        self.assertEqual(len(t.calls), 1)
        self.assertEqual(rt.requested_limit, 100)


class ScopeTest(unittest.TestCase):
    def test_unknown_path_rejected(self):
        rt = make(fake_transport(hits(PATHS[0])))
        with self.assertRaises(ValueError):
            rt.retrieve("q", "fts", 10, allowed_paths=["nope/x.md"])

    def test_glob_metachar_rejected(self):
        rt = make(fake_transport(hits(PATHS[0])))
        with self.assertRaises(ValueError):
            rt.retrieve("q", "fts", 10, allowed_paths=["deep-news/articles/*.md"])

    def test_out_of_scope_result_is_error(self):
        rt = make(fake_transport(hits(PATHS[1])))
        with self.assertRaises(TransportError):
            rt.retrieve("q", "fts", 10, allowed_paths=[PATHS[0]])

    def test_dedup_and_published_at(self):
        rt = make(fake_transport(hits(PATHS[0], PATHS[0], PATHS[1])))
        res = rt.retrieve("q", "fts", 100)
        self.assertEqual([d["path"] for d in res["documents"]],
                         [PATHS[0], PATHS[1]])
        self.assertEqual(res["documents"][0]["published_at"], "2026-08-01")
        self.assertEqual(res["documents"][1]["call_rank"], 2)


class GlobsTest(unittest.TestCase):
    def test_complement_exclusion(self):
        globs = globs_for_allowed([PATHS[1]], PATHS)
        self.assertEqual(globs[0], "deep-news/articles/*.md")
        self.assertEqual(globs[-1], "!eval/**")
        excluded = set(PATHS) - {PATHS[1]}
        self.assertEqual(sorted(globs[1:-1]), sorted(f"!{p}" for p in excluded))
        self.assertNotIn(f"!{PATHS[1]}", globs)


if __name__ == "__main__":
    unittest.main()
