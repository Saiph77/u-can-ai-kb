# zg 检索评测

方案：[EVAL-DESIGN.md](EVAL-DESIGN.md)；审查及本轮结果：[REVIEW.md](REVIEW.md)。

36 条固定查询，35 条计分，1 条仅作无答案诊断；这是开发回归集。比较 zg hybrid / fts / vector 在同一 Markdown 语料上的文章检索。它不评生成回答，也不证明优于 viewer。

## 运行

在仓库根目录先同步索引，排除包含答案的评测目录：

```bash
zg index . \
  --embedding local/potion-multilingual-128m \
  --device metal \
  -g '!upstream/**' \
  -g '!.idea/**' \
  -g '!deep-news/assets/**' \
  -g '!viewer/static/**' \
  -g '!eval/**' \
  --reset-paths

python3 -m unittest discover -s eval/zg -p 'test_*.py' -v
python3 eval/zg/run.py
# 子集仅用于排障，不能和全量平均比较
python3 eval/zg/run.py --ids col-jenny-ep1,sem-context-not-model,sem-token-fake
```

默认每路线获取 100 个片段，按首次出现去重成文章后取前 10 篇；相同路径片段合并，by-audience / by-format 的字节相同副本合并，形态不同的文档分别计分。`--k` 只接受 10；`--candidate-budget` 改变评测条件，比较时所有路线必须一致。

## 产物

- `runs/<UTC时间戳>/latest.json`：命令、原始 stdout/stderr、片段/文章排名、单题指标、分族汇总、语料和索引信息。
- 同目录保存 `queries.json`、`run.py` 和中途 checkpoint。
- `runs/latest.json` / `latest.md`：最近一次完成的运行，可能是子集；先检查题数和 `valid`。
- `runs/review-v1/`：此次修改前的设计、脚本、金标和历史结果备份。

有错误的路线不发布平均分，整轮退出非 0。任何语料或 manifest 变动也使该轮无效。完整报告通常优先看 Primary@5、semantic 分组和 collection 失败案例。

## 金标与解释

`queries.json` 用精确 `paths` 列表表示一个文档的等价副本；grade 2 为首选，grade 1 为有正文支持的强相关。同题路径不得重叠。启动校验会阻止不存在、内容不同、别名不全的金标。

Recall 是已标注文档覆盖率，不是全库真实召回率；多首选中找到一篇就可通过 Primary@5。无金标题只展示返回内容，不能据此推断拒答能力。

v2 改了排名单位、金标与查询过滤/候选预算，**不可用 v1→v2 的分数变化表示模型提升**。题集规模和标注独立性仍有限，本轮结果仅为描述性对照。
