"""B normalizer tests: grammar coverage + the frozen 30-query conformance."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.b_normalize.strategy import normalize  # noqa: E402

AS_OF = "2026-09-15"
SPEC = json.loads((Path(__file__).resolve().parents[2] / "queries.json").read_text())


def N(q, as_of=AS_OF):
    return normalize(q, as_of)


class FrozenConformance(unittest.TestCase):
    """Every frozen query parses to its declared mode/window/stage set."""

    @staticmethod
    def _frontmatter_month(path: str) -> str:
        import re
        root = Path(__file__).resolve().parents[4]
        text = (root / path).read_text()
        return re.search(r'^date:\s*"?(\d{4}-\d{2})', text, re.M).group(1)

    def test_all_30(self):
        for q in SPEC["queries"]:
            p = N(q["query"], q["as_of"])
            gold = q["time"]
            self.assertEqual(p["status"], "ok", q["id"])
            self.assertEqual(p["mode"], gold["mode"], q["id"])
            if gold["mode"] in ("window", "prefer_recent"):
                self.assertEqual(p["window"],
                                 {"start": gold["start"], "end": gold["end"]},
                                 q["id"])
            if gold["mode"] == "stages":
                self.assertEqual(len(p["stages"]), len(q["stages"]), q["id"])
                # stage boundaries: every gold doc's frontmatter month must
                # fall inside its stage window (scoring-side check only)
                for stage, gold_stage in zip(p["stages"], q["stages"]):
                    months = {self._frontmatter_month(x)
                              for x in gold_stage["paths"]}
                    for m in months:
                        self.assertTrue(
                            stage["window"]["start"][:7] <= m
                            <= stage["window"]["end"][:7],
                            f"{q['id']} {stage['id']} month {m} outside "
                            f"{stage['window']}")
                    self.assertTrue(stage["topical_query"].strip(), q["id"])

    def test_trace_spans_match_source(self):
        """Every trace entry's text must equal the original span it cites."""
        for q in SPEC["queries"]:
            p = N(q["query"], q["as_of"])
            for t in p["trace"]:
                self.assertEqual(q["query"][t["start"]:t["end"]], t["text"],
                                 f"{q['id']} trace {t['rule']}")


class Grammar(unittest.TestCase):
    def test_same_month_range(self):
        p = N("查找 2026 年 9 月 1 日至 15 日发布的 X 主题。")
        self.assertEqual(p["mode"], "window")
        self.assertEqual(p["window"], {"start": "2026-09-01", "end": "2026-09-15"})
        self.assertNotIn("2026", p["topical_query"])
        self.assertNotIn("发布的", p["topical_query"])

    def test_cross_month_range(self):
        p = N("只找 2026 年 8 月 15 日至 9 月 15 日的 X。")
        self.assertEqual(p["window"], {"start": "2026-08-15", "end": "2026-09-15"})

    def test_single_month(self):
        p = N("只找 2026 年四月发布的 X。")
        self.assertEqual(p["window"], {"start": "2026-04-01", "end": "2026-04-30"})

    def test_month_range(self):
        p = N("只找 2026 年六月至七月发布的 X。")
        self.assertEqual(p["window"], {"start": "2026-06-01", "end": "2026-07-31"})

    def test_february_nonleap(self):
        p = N("只找 2026 年二月发布的 X。")
        self.assertEqual(p["window"]["end"], "2026-02-28")

    def test_prefer_recent_two_months(self):
        p = N("截至 2026 年 9 月 15 日，X 怎么选？优先近两个月的分析。")
        self.assertEqual(p["mode"], "prefer_recent")
        self.assertEqual(p["window"], {"start": "2026-07-15", "end": "2026-09-15"})
        self.assertNotIn("优先", p["topical_query"])
        self.assertNotIn("截至", p["topical_query"])

    def test_prefer_month_end_clamp(self):
        p = N("优先近三个月的分析，X 主题", "2026-08-31")
        self.assertEqual(p["window"]["start"], "2026-05-31")

    def test_no_date_limit(self):
        # frozen control group: the query is kept VERBATIM (plans/B §2)
        q = "为什么 X 难？想找解释的文章，不限发布时间。"
        p = N(q)
        self.assertEqual(p["mode"], "none")
        self.assertEqual(p["topical_query"], q)

    def test_no_temporal_passthrough(self):
        q = "GPT-4 的上下文窗口机制是什么？"
        p = N(q)
        self.assertEqual(p["mode"], "none")
        self.assertEqual(p["topical_query"], q)

    def test_version_numbers_kept(self):
        p = N("比较 GPT-4o 与 Claude 4 在 2025 年基准上的表现。")
        self.assertEqual(p["topical_query"], "比较 GPT-4o 与 Claude 4 在 2025 年基准上的表现。")

    def test_vague_recent_ambiguous(self):
        p = N("最近 X 有什么进展？")
        self.assertEqual(p["status"], "ambiguous")
        self.assertEqual(p["topical_query"], "最近 X 有什么进展？")

    def test_asof_mismatch_unsupported(self):
        p = N("截至 2026 年 8 月 1 日，X 怎么选？优先近两个月的分析。")
        self.assertEqual(p["status"], "unsupported")

    def test_inverted_range_ambiguous(self):
        p = N("只找 2026 年 9 月 15 日至 1 日的 X。")
        self.assertEqual(p["status"], "ambiguous")

    def test_conflict_ambiguous(self):
        p = N("只找 2026 年六月的 X，不限发布时间。")
        self.assertEqual(p["status"], "ambiguous")

    def test_stages_two(self):
        p = N("梳理 X 的演进：八月的甲问题，再看九月的乙问题。两个阶段都要。")
        self.assertEqual(p["mode"], "stages")
        self.assertEqual(len(p["stages"]), 2)
        self.assertEqual(p["stages"][0]["window"]["start"], "2026-08-01")
        self.assertEqual(p["stages"][1]["window"]["end"], "2026-09-30")

    def test_stages_month_range_stage(self):
        p = N("找出 X 的材料：六月到七月的甲、九月的乙。")
        self.assertEqual(p["stages"][0]["window"],
                         {"start": "2026-06-01", "end": "2026-07-31"})
        self.assertEqual(len(p["stages"]), 2)

    def test_stage_desc_with_dunhao(self):
        p = N("把 X 两阶段找齐：八月的甲，九月对钱、数据和能力的判断。")
        self.assertEqual(len(p["stages"]), 2)
        self.assertIn("钱", p["stages"][1]["topical_query"])

    def test_unseen_topic_same_structure(self):
        p = N("只找 2026 年七月发布的数据库备份与照片整理分析。")
        self.assertEqual(p["mode"], "window")
        self.assertIn("数据库备份", p["topical_query"])

    def test_trace_coordinates(self):
        q = "只找 2026 年六月发布的 X。"
        p = N(q)
        for t in p["trace"]:
            self.assertEqual(q[t["start"]:t["end"]], t["text"])

    def test_multiple_year_months_ambiguous(self):
        # two distinct dated months must not be silently reduced to the first
        p = N("对比 2026 年六月和 2026 年七月的 X 讨论。")
        self.assertEqual(p["status"], "ambiguous")
        self.assertEqual(p["topical_query"],
                         "对比 2026 年六月和 2026 年七月的 X 讨论。")

    def test_invalid_month_unsupported_not_exception(self):
        for q in ("只找 2026 年十三月发布的 X。",
                  "只找 2026 年 13 月发布的 X。",
                  "只找 2026 年十三月至十四月发布的 X。"):
            p = N(q)  # must not raise
            self.assertEqual(p["status"], "unsupported", q)
            self.assertEqual(p["topical_query"], q)

    def test_invalid_stage_month_falls_back(self):
        # an unparseable stage month must not crash; query kept verbatim
        p = N("梳理 X：十三月的甲、九月的乙。")
        self.assertNotEqual(p["mode"], "stages")
        self.assertIn(p["status"], ("ok", "ambiguous", "unsupported"))
        self.assertEqual(p["topical_query"], "梳理 X：十三月的甲、九月的乙。")


if __name__ == "__main__":
    unittest.main()
