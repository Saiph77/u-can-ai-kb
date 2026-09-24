# B — 查询归一化（时间表达与主题分离）

## 行为

`normalize(query, as_of)` 用确定性规则产出 QueryPlan（schema_version=1），`search` 仍对**全语料**单次检索 `topical_query`，limit=100，原顺序。不按窗口过滤、不加权、不拆阶段。

## 解析器

`strategy.py` 内 `normalize`：

- 显式区间 `2026 年 9 月 1 日至 15 日` / `8 月 15 日至 9 月 15 日`，单月 `2026 年四月`，月区间 `2026 年六月至七月`（calendar 月末）。
- `截至 YYYY-MM-DD` 与 request.as_of 校验，不等 → `unsupported`（不假装支持历史回测）。
- `优先近 N 个月` → `prefer_recent`，日历月回退并夹到月末（9/15 −2 → 7/15；8/31 −3 → 5/31）。
- **`不限发布时间` → `none`，原查询逐字保留**（冻结控制组，plans/B §2），不做任何 span 删除。
- 阶段：`：<month>的<desc>` ≥2 个（支持 `六月到七月` 区间阶段、`先看/再看/以及` 前缀、描述内含顿号）；共享主题取自冒号前并剥离 `梳理/把/找齐/的两阶段…/的讨论演进` 等模板；无年份月按「不晚于 as_of 的最近一次」推年。
- 错误分支：裸 `最近/近期` → `ambiguous`；窗口与软偏好/不限发布冲突 → `ambiguous`；**未被消费的第二个 `YYYY年M月` → `ambiguous`**（不静默取第一个）；非法月份（十三月/13 月）→ `unsupported` 而非异常；阶段月份越界 → 回退非阶段；主题剥空 → `unsupported`。非 ok 一律原查询回退并记 fallback。
- trace 记录每条规则的原文 span 坐标，测试断言 `text == query[start:end]` 对全部 30 题成立。

## 边界（v1 明确不做）

不调用 LLM、不读正文与 gold；未覆盖的中文口语时间一律 fallback；阶段头部不带年份。

## 结果

见 [RESULTS.md](RESULTS.md)。
