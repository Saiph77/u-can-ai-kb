"""Scoring and run archiving shared by all experiment variants.

Reuses eval/deep-news/run.py's metrics_for/aggregate untouched: the
strategy's full ranked_documents list is scored directly (the scorer cuts
its own top-5/top-10 and computes CandidateTask over the whole list).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .loader import REPO_ROOT

RUNS = REPO_ROOT / "eval/deep-news/runs/experiments"


def score_result(docs: list[dict], gold_query: dict, corpus: dict,
                 dn_eval) -> dict:
    """Score a SearchResult's ranked_documents with the original metrics."""
    return dn_eval.metrics_for(docs, gold_query, corpus)


def aggregate(items: list[dict], route: str, dn_eval) -> dict:
    return dn_eval.aggregate(items, route)


def new_run_dir(variant_label: str) -> Path:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    directory = RUNS / variant_label / run_id
    directory.mkdir(parents=True)
    return directory


def write_run(directory: Path, payload: dict, report: str) -> None:
    (directory / "run.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    (directory / "run.md").write_text(report, encoding="utf-8")


def render_report(payload: dict, dn_eval) -> str:
    core = dn_eval.core
    lines = [f"# Deep News 实验 — variant={payload['variant']}"
             + (f"（label={payload['label']}）" if payload.get("label") else ""),
             "",
             f"- UTC: {payload['at']}; as_of: {payload['as_of']}; "
             f"valid: {payload['valid']}",
             f"- replay: {payload.get('replay') or '否（真实检索）'}; "
             f"articles: {len(payload['corpus']['files'])}; "
             f"queries: {len(payload['items'])}",
             f"- 每题每路线预算: {payload['candidate_budget']}; "
             f"策略配置指纹: {payload.get('strategy_config_sha256')}", ""]
    keys = ["hit_at_1", "primary_at_5", "ndcg_at_10", "task_success_at_5",
            "window_primary_at_5", "stage_coverage_at_5", "all_stages_at_5",
            "candidate_task_success"]

    def table(label, blocks):
        lines.extend([f"## {label}", "",
                      "| route | n | errors | Hit@1 | Primary@5 | nDCG@10 | Task@5 | WindowPrimary@5 | StageCov@5 | AllStages@5 | CandidateTask |",
                      "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"])
        for route, b in blocks.items():
            m = b["metrics"] or dict.fromkeys(keys)
            lines.append(f"| {route} | {b['n']} | {b['errors']} | "
                         + " | ".join(core.fmt(m[k]) for k in keys) + " |")
        lines.append("")

    table("全体", payload["summary"])
    for kind, blocks in payload["by_kind"].items():
        table(kind, blocks)

    lines += ["## 调用与预算", "",
              "| route | 总调用数 | 总 requested_limit | 候选文档中位数 | 耗时中位 ms | 耗时 p95 ms |",
              "|---|---:|---:|---:|---:|---:|"]
    for route, diag in payload["diagnostics"].items():
        lines.append(f"| {route} | {diag['calls']} | {diag['requested_limit']} "
                     f"| {diag['candidates_median']} | {diag['elapsed_median_ms']} "
                     f"| {diag['elapsed_p95_ms']} |")
    lines += ["", "## 解析回退", ""]
    for route, diag in payload["diagnostics"].items():
        lines.append(f"- {route}: fallback={diag['fallback_queries'] or '无'}")
    lines += ["", "## 前五未满足任务的查询", ""]
    for route in payload["routes"]:
        failures = [q["id"] for q in payload["items"]
                    if q["routes"][route].get("metrics", {}).get(
                        "task_success_at_5") == 0]
        lines.append(f"- {route}: {', '.join(failures) or '无'}")
    lines += ["", "## 说明", "",
              "- ranked_documents 完整候选列表评分（CandidateTask 不受截断影响）；Top10 由评分端切取。",
              "- 窗口判定使用 frontmatter date；策略端不可见 gold。",
              "- 本子集/回放运行不覆盖任何 latest 文件；跨版本比较请用 experiments/compare.py。",
              ""]
    return "\n".join(lines)
