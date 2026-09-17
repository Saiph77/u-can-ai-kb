"""A: passthrough semantics — original query, whole corpus, original order."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.a_baseline import strategy  # noqa: E402
from experiments.common.loader import load_eval_core  # noqa: E402
from experiments.common.runtime import Runtime  # noqa: E402

core = load_eval_core()
PATHS = [f"deep-news/articles/a{i}.md" for i in range(3)]
CORPUS = {"files": {p: "x" for p in PATHS},
          "dates": {p: "2026-08-01" for p in PATHS},
          "canonical": {p: p for p in PATHS}}
DOCS = {p: {"published_at": "2026-08-01"} for p in PATHS}


def fake(query, route, limit, allowed_paths, all_paths):
    fake.seen = (query, route, limit, allowed_paths)
    return {"command": ["f"], "stdout": "", "stderr": "", "returncode": 0,
            "elapsed_ms": 0, "raw_hits": [
                {"rank": 1, "matched_by": "fts", "path": PATHS[1]},
                {"rank": 2, "matched_by": "fts", "path": PATHS[0]},
                {"rank": 3, "matched_by": "fts", "path": PATHS[1]}]}


class BaselineTest(unittest.TestCase):
    def test_single_call_full_corpus_first_hit_order(self):
        rt = Runtime(core=core, documents=DOCS, corpus=CORPUS,
                     strategy_config={}, candidate_budget=100,
                     transport=fake)
        req = {"query": "原始查询", "as_of": "2026-09-15",
               "route": "hybrid", "candidate_budget": 100}
        res = strategy.search(req, rt)
        self.assertEqual(fake.seen, ("原始查询", "hybrid", 100, None))
        docs = res["ranked_documents"]
        self.assertEqual([d["path"] for d in docs], [PATHS[1], PATHS[0]])
        self.assertEqual([d["rank"] for d in docs], [1, 2])
        self.assertEqual(docs[0]["provenance"][0]["call_id"], "call-1")
        self.assertFalse(res["diagnostics"]["fallback"])
        self.assertEqual(res["plan"]["mode"], "none")


if __name__ == "__main__":
    unittest.main()
