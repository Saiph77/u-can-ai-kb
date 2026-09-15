# Deep News 专属评测

评测 431 篇新闻文章中的**内容相关性、发布日期符合度和演进阶段覆盖**。30 道查询，固定参考日 2026-09-15。

- [设计与指标定义](EVAL-DESIGN.md)
- [题集](queries.json) · [原文证据](judgments.json)
- [首轮结果与结论](RESULTS.md)

## 运行

在知识库根目录运行：

```bash
python3 eval/deep-news/run.py --validate-only
python3 -m unittest discover -s eval/deep-news -p 'test_*.py' -v
python3 eval/deep-news/run.py
# 子集仅用于排障，不与全量分数混比
python3 eval/deep-news/run.py --ids latest-router,historical-router
```

运行前若语料有变动，按 [zg 索引同步命令](../zg/README.md) 刷新索引，必须保留 `!eval/**` 排除。若加入参考日之后的文章，需明确建立新题集版本，runner 不会自动移动参考日。

每条查询仅在 `deep-news/articles/*.md` 内检索，三路线统一取 100 个片段，按文章去重后评前十。**首轮没有日期过滤或时间加权**，用于建立改排序前的基线。

## 产物

`runs/<UTC时间戳>/latest.json` / `latest.md` 保存独立完整结果；`runs/latest.*` 指向最近一次完成的运行，可能是子集，先检查题数和 `valid`。同目录还有题集、证据与脚本快照。运行失败退出非 0。

## 先看什么

1. latest / historical 的 WindowPrimary@5：相关且在指定时期。
2. foundation 的 Primary@5：旧的机制解释有没有被找到。
3. evolution 的 AllStages@5：要求的阶段是否找齐。
4. CandidateTask：需要的文档是否已在原始候选中。

current 的近两个月仅为软偏好，不因文章旧就判其失效。6 个主题簇、17 篇种子金标尚未穷尽全库相关文档，结果是开发诊断，不能当作泛化结论或新闻事实核验。
