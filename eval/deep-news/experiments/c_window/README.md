# C — 显式日期窗口的召回前筛选

## 行为

`search` = B 的 `normalize` + `execute_plan`：

- `mode == window`：`select_paths(window, runtime.documents)` 按 frontmatter `published_at`（含两端）算出 allowed_paths → `retrieve(topical_query, route, 100, allowed_paths)`。
- 其他 mode / status≠ok：与 B 完全一致（原样或回退查询、全范围、一次调用）。
- 空 allowed 集合法：短路返回空、不耗预算、不回退全库、不拿窗外文章凑数。

## 范围编码（与 A 的 transport 分工）

C 只算路径集合；A 的 transport 把它编成补集排除 globs（`*.md` 全收 → 逐个 `!path` 排除补集 → `!eval/**`），依赖 zg 规则顺序覆盖语义。路径校验：必须属于冻结 metadata、不含 glob 元字符；transport 返回越界文档 → 整轮错误而非低分。

## 结果

见 [RESULTS.md](RESULTS.md)。
