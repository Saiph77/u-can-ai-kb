"""D: recency math, stage budgets, merge semantics, config validation."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.common.loader import load_eval_core  # noqa: E402
from experiments.common.runtime import Runtime  # noqa: E402
from experiments.d_temporal import recency, stages, strategy as d  # noqa: E402

core = load_eval_core()
PATHS = [f"deep-news/articles/m{i:02d}.md" for i in range(1, 7)]
DATES = dict(zip(PATHS, ["2026-04-10", "2026-06-29", "2026-07-16",
                         "2026-08-28", "2026-09-05", "2026-09-12"]))
CORPUS = {"files": {p: "x" for p in PATHS}, "dates": DATES,
          "canonical": {p: p for p in PATHS}}
DOCS = {p: {"published_at": DATES[p]} for p in PATHS}
CFG = {"soft": {"enabled": True, "rank_constant": 60,
                "half_life_days": 30, "weight": 0.25},
       "stages": {"enabled": True}}


def docs(*paths):
    return [{"path": p, "rank": i + 1, "published_at": DATES[p],
             "score": None, "provenance": [], "reason": "original_order"}
            for i, p in enumerate(paths)]


class Recency(unittest.TestCase):
    def test_weight_zero_identity(self):
        d0 = docs(PATHS[0], PATHS[5])
        out = recency.rerank_recency(d0, "2026-09-15",
                                     {**CFG["soft"], "weight": 0})
        self.assertEqual([x["path"] for x in out], [PATHS[0], PATHS[5]])

    def test_half_life(self):
        d0 = docs(PATHS[0])  # 2026-08-16-ish age vs 09-15
        d0[0]["published_at"] = "2026-08-16"
        out = recency.rerank_recency(d0, "2026-09-15", CFG["soft"])
        self.assertAlmostEqual(out[0]["F"], 0.5, places=6)

    def test_recency_can_reorder(self):
        d0 = docs(PATHS[0], PATHS[5])
        out = recency.rerank_recency(d0, "2026-09-15", CFG["soft"])
        self.assertEqual(out[0]["path"], PATHS[5])
        self.assertEqual(out[0]["original_rank"], 2)
        self.assertEqual(out[1]["rank"], 2)

    def test_future_date_error(self):
        d0 = docs(PATHS[0]); d0[0]["published_at"] = "2026-10-01"
        with self.assertRaises(ValueError):
            recency.rerank_recency(d0, "2026-09-15", CFG["soft"])

    def test_bad_config(self):
        for bad in ({"enabled": True, "rank_constant": 60, "half_life_days": 0, "weight": .2},
                    {"enabled": True, "rank_constant": 60, "half_life_days": 30, "weight": -1},
                    {"enabled": True, "rank_constant": 60, "half_life_days": 30, "weight": .2, "x": 1}):
            with self.assertRaises(ValueError):
                recency.rerank_recency(docs(PATHS[0]), "2026-09-15", bad)


class StageBudget(unittest.TestCase):
    def test_allocations(self):
        self.assertEqual(stages.allocate_budget(100, 3), [34, 33, 33])
        self.assertEqual(stages.allocate_budget(100, 2), [50, 50])
        with self.assertRaises(ValueError):
            stages.allocate_budget(100, 6)

    def test_round_robin_dedup(self):
        s1 = docs(PATHS[1], PATHS[2], PATHS[0])
        s2 = docs(PATHS[3], PATHS[2])
        merged = stages.merge_stages([s1, s2])
        self.assertEqual([x["path"] for x in merged],
                         [PATHS[1], PATHS[3], PATHS[2], PATHS[0]])
        dup = [x for x in merged if x["path"] == PATHS[2]][0]
        self.assertEqual(len(dup["provenance"]), 0)  # input had none; see below

    def test_provenance_accumulates(self):
        def pd(p, call):
            x = docs(p)[0]
            x["provenance"] = [{"call_id": call, "call_rank": 1, "raw_rank": 1}]
            return x
        merged = stages.merge_stages([[pd(PATHS[0], "c1")], [pd(PATHS[0], "c2")]])
        self.assertEqual(len(merged), 1)
        self.assertEqual(len(merged[0]["provenance"]), 2)


def fake(hits_map):
    def fn(query, route, limit, allowed_paths, all_paths):
        fn.calls.append((query, limit, allowed_paths))
        return {"command": ["f"], "stdout": "", "stderr": "", "returncode": 0,
                "elapsed_ms": 0,
                "raw_hits": [{"rank": i + 1, "matched_by": "fts", "path": p}
                             for i, p in enumerate(hits_map(query))]}
    fn.calls = []
    return fn


def rt(t, cfg=CFG):
    return Runtime(core=core, documents=DOCS, corpus=CORPUS,
                   strategy_config=cfg, candidate_budget=100, transport=t)


class StrategyRouting(unittest.TestCase):
    Q = "梳理 X 的两阶段讨论：四月的甲、九月的乙。"

    def test_window_delegates_to_c(self):
        t = fake(lambda q: [PATHS[3]])
        res = d.search({"query": "只找 2026 年八月发布的 X。", "as_of": "2026-09-15",
                        "route": "fts", "candidate_budget": 100}, rt(t))
        self.assertEqual(t.calls[0][2], [PATHS[3]])

    def test_prefer_recent_soft(self):
        t = fake(lambda q: [PATHS[0], PATHS[5]])
        res = d.search({"query": "截至 2026 年 9 月 15 日，X？优先近两个月的分析。",
                        "as_of": "2026-09-15", "route": "fts",
                        "candidate_budget": 100}, rt(t))
        self.assertEqual(res["ranked_documents"][0]["path"], PATHS[5])
        self.assertEqual(res["diagnostics"]["policy"], "recency_soft")

    def test_soft_disabled_is_b(self):
        t = fake(lambda q: [PATHS[0], PATHS[5]])
        cfg = {"soft": {**CFG["soft"], "enabled": False}, "stages": CFG["stages"]}
        res = d.search({"query": "截至 2026 年 9 月 15 日，X？优先近两个月的分析。",
                        "as_of": "2026-09-15", "route": "fts",
                        "candidate_budget": 100}, rt(t, cfg))
        self.assertEqual(res["ranked_documents"][0]["path"], PATHS[0])

    def test_staged_calls_and_budget(self):
        t = fake(lambda q: [PATHS[0]] if "甲" in q else [PATHS[4]])
        r = rt(t)
        res = d.search({"query": self.Q, "as_of": "2026-09-15", "route": "fts",
                        "candidate_budget": 100}, r)
        limits = [c[1] for c in t.calls]
        self.assertEqual(limits, [50, 50])
        self.assertEqual(r.requested_limit, 100)
        paths = [x["path"] for x in res["ranked_documents"]]
        self.assertEqual(paths, [PATHS[0], PATHS[4]])

    def test_empty_stage_no_fallback(self):
        # stage "四月" has PATHS[0]; stage "九月" has PATHS[4],PATHS[5]
        t = fake(lambda q: [])
        r = rt(t)
        res = d.search({"query": "梳理 X：三月的甲、九月的乙。",
                        "as_of": "2026-09-15", "route": "fts",
                        "candidate_budget": 100}, r)
        march = res["diagnostics"]["stages"][0]
        self.assertEqual(march["eligible_count"], 0)
        self.assertIsNone(march["call"])
        self.assertEqual(len(t.calls), 1)  # only september called

    def test_stages_disabled_single_call(self):
        t = fake(lambda q: [PATHS[0]])
        cfg = {"soft": CFG["soft"], "stages": {"enabled": False}}
        r = rt(t, cfg)
        d.search({"query": self.Q, "as_of": "2026-09-15", "route": "fts",
                  "candidate_budget": 100}, r)
        self.assertEqual(len(t.calls), 1)
        self.assertIsNone(t.calls[0][2])

    def test_unknown_config_field(self):
        with self.assertRaises(ValueError):
            d.validate_config({"soft": {"enabled": True, "bogus": 1}})


if __name__ == "__main__":
    unittest.main()
