# D — 软时间偏好加权 + 演进阶段覆盖

## 路由

| QueryPlan | 行为 |
|---|---|
| status≠ok | B 回退（原查询一次调用） |
| none | 与 B 完全一致 |
| window | 委托 C.execute_plan |
| prefer_recent | B 单次主题召回 → `recency.rerank_recency` 全候选重排（soft 关闭时退回 B） |
| stages | 每阶段 `C.select_paths` + 限额召回 → `stages.merge_stages` 轮转合并（stages 关闭时退回 B 单次） |

## D-soft（`recency.py`）

`S = R·(1 + w·F)`，`R = 1/(60+rank)`，`F = 2^(-age/30)`，默认 `weight=0.25`。对全部去重候选重排后取序；`weight=0` 与原序严格一致；未来日期/非法配置直接报错。软偏好不是硬截断，候选集合不增不减。

## D-stages（`stages.py`）

- `allocate_budget(100, m)`：均分余量前置（3→34/33/33，2→50/50），v1 支持 2–5 阶段，超出回退 B 单次。
- 空阶段零调用，预算不转移；不追加查询、不重分配。
- `merge_stages`：按阶段顺序轮转取各自下一篇未输出文档；重复路径保留首次位置并累加 provenance；候选全量保留。

## 配置

`config.json`：`{"soft":{"enabled":true,"rank_constant":60,"half_life_days":30,"weight":0.25},"stages":{"enabled":true}}`。`--strategy-config` 覆盖；未知字段报错；配置原文与 SHA256 归档进 run。

## 对照运行

- `runs/experiments/d/`：soft=true、stages=true（完整 30×3 真实检索）
- `runs/experiments/d_no_soft/`：soft=false、stages=true（完整 30×3）
- `runs/experiments/d_no_stages/`：soft=true、stages=false（完整 30×3）

三组均为全量真实运行而非回放子集。

## 结果

见 [RESULTS.md](RESULTS.md)。
