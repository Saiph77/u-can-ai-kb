# A — 冻结基线与公共实验框架

## 行为

原查询、全语料、原始排名：单次 `retrieve(query, route, 100, allowed_paths=None)`，片段按首次命中去重为文档，保持顺序，plan 标记 passthrough。不推断时间。

## 同时交付的公共部分

- `common/runtime.py`：Runtime 契约 + `ZgTransport`（argv 数组、无 shell、补集排除 glob、argv 长度上限）+ `ReplayTransport`。
- `common/evaluation.py`：计分（复用 `eval/deep-news/run.py` 的 `metrics_for`/`aggregate`）与独立 run 目录归档。
- `run.py`：variant 延迟加载、request 白名单、快照前后校验、诊断汇总。
- `compare.py`：指纹/题集/预算/路线可比性校验后输出逐题差值。

## 结果

见 [RESULTS.md](RESULTS.md)。离线回放与真实运行分开报告。
