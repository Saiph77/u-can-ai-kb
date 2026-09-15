---
title: "RAG 的每一项核心技术，搜索引擎都做过"
date: 2026-03-26
source: https://yage.ai/share/rag-reinvented-search-engine-20260326.html
slug: rag-reinvented-search-engine-20260326
lang: zh
---
# RAG 的每一项核心技术，搜索引擎都做过

发布于 2026 年 3 月 26 日 · [查看原网页](https://yage.ai/share/rag-reinvented-search-engine-20260326.html)

> 2026-03-26

我们在 LangChain 里写
`RecursiveCharacterTextSplitter`，把文档切成 512 token 的
chunk。我们用 OpenAI 的 embedding API 把 chunk 变成向量。我们把向量存进
Pinecone，用余弦相似度检索最相关的 5 条结果。我们加了一个 cross-encoder
reranker 做二次排序。我们觉得这套管线是 2023 年 AI 社区的集体发明。

每一步都不是。

文档切块是 1994 年 Callan 在 SIGIR 上发表的 passage
retrieval。把文本变成向量是 2013 年微软的 DSSM
双塔模型。近似最近邻搜索是 2016 年的 HNSW 算法。两阶段排序是 2005
年微软研究院的 Learning to Rank。混合检索用的 Reciprocal Rank Fusion 是
2009 年的 Cormack 论文。

这不是在说 RAG 没有价值。RAG
的贡献是真实的，但它发生在工程层和产品层：它把原本需要信息检索（Information
Retrieval, IR）博士才能搭建的搜索管线，压缩成任何 Python 开发者用
LangChain 就能跑起来的几十行代码。这是成本压缩，是
democratization。但在算法层面，RAG 管线的每个组件都有 IR
前身，时间差距从 2 年到 50 年不等。

理解这个事实有直接的实用价值：IR
领域在这些问题上积累了几十年的工程经验和失败教训，知道哪些路走不通、哪些
trade-off 值得做。如果我们只在 RAG 的框架内思考，会反复掉进 IR
已经解决的坑里。

---

## 一张对照表

先给出全貌。以下是 RAG 管线中 7 个核心组件与它们在 IR 中的前身：

| RAG 组件 | IR 前身 | IR 年份 | RAG 采用年份 | 时间差 |
| --- | --- | --- | --- | --- |
| Document Chunking | Passage Retrieval (Callan) | 1994 | 2020 (DPR) | 26 年 |
| Dense Embedding | Dual Encoder (DSSM) | 2013 | 2020 (DPR) | 7 年 |
| Vector Search (HNSW) | HNSW 算法 | 2016 | 2021+ | 5 年 |
| Cross-encoder Reranking | Learning to Rank / BERT Reranking | 2005/2019 | 2022+ | 3-17 年 |
| Hybrid Search (RRF) | Reciprocal Rank Fusion | 2009 | 2023+ | 14 年 |
| Query Rewriting | Rocchio Relevance Feedback | 1971 | 2023+ | 52 年 |
| Query Expansion | RM3 Pseudo-Relevance Feedback | 2001 | 2023+ | 22 年 |

这些数字背后是一整个学科五十多年的积累。从 1960 年代 Salton
在康奈尔建立 SMART 系统和向量空间模型，到 1972 年 Spärck Jones 提出 IDF
的统计解释，到 1990 年代 BM25 和 TREC 评测框架的成熟，再到 2010 年代
neural IR 的兴起，IR
是一个有完整理论体系、标准评测和工业部署经验的学科。RAG 社区在 2020-2023
年间重新走过了这条路，但跳过了沿途积累的大量工程经验。

下面逐项展开。每项聚焦三件事：这个技术要解决什么问题（直觉），IR
原始论文做了什么关键 technical decision（trade-off），以及这些 trade-off
如何指导我们优化 RAG 系统（调优）。

---

## Chunking：passage size 是一个被忽视的变量

RAG
管线的第一步是把长文档切成短片段。核心直觉很简单：整篇文档太长，粒度太粗，一篇包含多个主题的文档如果整篇参与检索，会稀释跟查询真正相关的段落的信号。切成小段才能精确匹配。

Callan 在 1994 年 SIGIR 上研究这个问题时，做了一个关键 technical
decision：系统地测试不同 passage size 对检索效果的影响。他的实验发现
100-150 词是最优区间，但最优值随查询类型变化。事实性查询（factoid
question）适合短
passage，因为答案通常集中在一两句话里；主题性查询（topical
question）适合长 passage，因为需要更多上下文才能判断相关性。TREC Passage
Track（2003-2004）在标准化评测中进一步验证了这个结论。DPR（2020）论文用的
100-word passage 设置跟 TREC 标准几乎一模一样，但 RAG
社区在二次传播中把这个变量固化成了 512 token，不再区分查询类型。

这意味着一个直接的调优机会：chunk size 应该是 RAG
系统的一个可调参数，而非固定常数。具体来说，按语义边界切割（标题、段落、列表边界）通常优于按固定
token 数切割，而 hierarchical
retrieval（先检索文档级、再检索段落级）在长文档场景下效果更好。如果只能选一个默认值，TREC
的经验指向 200-300 token 而非 512。

---

## Dense Embedding：cosine vs dot product 不是随便选的

把文本变成向量、用向量相似度做检索，这是 RAG
最核心的技术选择。直觉也很清晰：关键词匹配只能找到字面重合的内容，理解不了同义词和语义关联。我们需要把文本变成数字向量，在一个连续的语义空间里比较含义的远近。

2013 年微软研究院发表的 DSSM 是第一个 production-ready 的 dense
retrieval 模型。它的架构跟 2020 年的 DPR
完全一致：两个独立的编码器分别处理查询和文档，输出低维向量，用相似度排序。DSSM
做了一个关键 technical decision：用 cosine similarity 而非 dot product
做匹配。原因是 cosine 会归一化向量长度，消除文档长度对分数的影响。一篇
5000 词的文档和一篇 200 词的文档，只要语义相关度相同，cosine similarity
给出的分数就相同。很多 RAG 实现默认用 dot
product（部分向量数据库的默认设置），在文档长度差异大的语料上会产生系统性偏差：长文档的
embedding 范数更大，dot product 天然偏向长文档。

调优建议很具体：如果我们的语料包含长度差异显著的文档（比如混合了短
FAQ 和长技术手册），应该确认向量数据库使用的是 cosine similarity 而非
dot product，或者在 embedding 之后做 L2 归一化。另一个来自 IR
的经验是，纯 dense retrieval
在精确匹配上有明显弱点。专有名词、产品编号、错误代码这类
token，embedding 模型倾向于把它们泛化成语义类别，丢失字面精确性。这是
hybrid search 存在的根本原因。

---

## Vector Search：检索阶段省的毫秒，在 LLM 调用上不值一提

向量数据库的核心算法 HNSW（Hierarchical Navigable Small World）2016
年发表后，最先大规模使用它的是推荐系统和广告技术。Facebook 2019 年开源的
FAISS 主要用途是推荐场景的 embedding
检索。向量数据库创业潮（Pinecone、Weaviate、Qdrant、Milvus）是在 HNSW
之上加了 CRUD
接口和持久化。直觉层面没有太多需要解释的：暴力搜索在百万级向量上太慢，我们需要近似算法在速度和精度之间做平衡。

HNSW 的关键 technical decision
是把构建精度和查询精度分成两个独立参数：`ef_construction`
控制索引构建时的精度（影响图结构质量），`ef_search`
控制查询时探索的邻居数量（影响召回率和延迟）。这两个参数可以独立调节，因为构建是离线的一次性成本，查询是在线的持续成本。RAG
教程通常用默认值，但 IR
和推荐系统的经验表明，对于检索质量敏感的场景，应该把
`ef_search` 调到默认值的 2-3 倍。原因是成本结构：一次 HNSW
查询耗时几毫秒到几十毫秒，而后续的 reranking 和 LLM generation
耗时几百毫秒到几秒。检索阶段多花 10ms 换回 5% 的召回率提升，在 LLM
调用的成本面前完全可以忽略。

---

## Reranking：上限取决于召回，而非排序模型

RAG 管线的 reranker 通常是一个
cross-encoder：把查询和文档拼接在一起输入 BERT
类模型，输出相关性分数。直觉是分两步做检索：第一步用快但粗的方法（dual
encoder）从百万文档中捞出 top-100
候选，第二步用慢但准的方法（cross-encoder）在这 100
个候选中精排。这样既保证了大规模检索的速度，又保证了最终排序的精度。

IR 把这个架构叫 cascade ranking，从 2005 年微软的 RankNet
开始就是标准做法。这里有一个容易被忽视的 technical decision：cascade
的效果上限由第一阶段的召回质量决定，而非第二阶段的排序模型。如果第一阶段没把相关文档捞上来，reranker
面对的全是不相关的候选，排序再精确也没用。RAG
社区的一个常见误区是把大量精力放在选择和微调 reranker
上，却忽略了召回阶段的多样性和覆盖率。IR
的做法是确保第一阶段有多个检索通道（BM25 + dense + 可能的其他信号），用
reranker 融合排序。

调优的优先级因此很清晰：先确保召回阶段的覆盖率（多通道、合理的
top-k），再投入精力调 reranker。另外，RAG 社区常用的 ms-marco 系列
reranker 是在 Bing 搜索日志上训练的，偏向通用网页查询。如果 RAG
系统服务于特定领域（法律、医疗、代码），至少应该做一次 domain-specific
评测，确认通用 reranker 在目标领域的效果。

---

## Hybrid Search 和 RRF：用 rank 做 fusion，不要用 score

纯 dense retrieval 的精确匹配弱点让 RAG 社区逐渐接受了 hybrid
search：同时用
BM25（一种经典的关键词检索算法，基于词频和文档长度计算相关性）做稀疏检索，用
embedding 做稠密检索，再把两路结果合并。合并的标准方法是 Reciprocal Rank
Fusion（RRF）。

RRF 是 Cormack 在 2009 年 SIGIR 上发表的，原论文只有 2
页，公式极其简单：对每条结果计算
`1 / (k + rank)`，把所有通道的分数加总。这个方法来源于
meta-search 领域（多个搜索引擎的结果如何融合成统一排序），它的关键
technical decision 是用 rank（排名位置）而非
score（原始分数）做融合。原因是不同检索通道的 score 量纲完全不可比：BM25
的分数范围可能是 0-30，cosine similarity 的范围是 -1 到
1。直接加权平均这两种分数没有统计意义，但 rank 是通用的：第 1 名就是第 1
名，无论分数是多少。这个 insight 在 RAG 社区经常被忽视，一些实现试图对
BM25 分数和 cosine similarity 做归一化后加权，效果反而不如简单的
RRF。

BM25 本身也有一个值得理解的 design：它的词频项包含一个 saturation
function，词频增长到一定程度后收益递减。这防止了长文档因为词频高而垄断排名。Dense
retrieval 没有这个机制，长文档的 embedding 信号会淹没短文档。这是 hybrid
search 的另一个价值：BM25 通道天然地对文档长度做了补偿，平衡 dense
通道的长度偏差。调优建议：如果目前只用 dense retrieval，加一个 BM25
通道做 hybrid search 是投入产出比最高的改进，RRF 的 k 值取
60（原论文默认值，40-100 都可以）。

---

## Query Rewriting：LLM 是 Rocchio 的升级版

RAG 系统中越来越流行的优化是让 LLM
改写用户查询：把模糊的问题变精确，或生成多个变体查询提升召回。直觉很直接：用户输入的查询往往信息量不足，跟语料中的表述方式有
vocabulary gap，需要扩展或改写才能匹配到相关内容。

这个思路在 IR 中的历史可以追溯到 1971 年 Rocchio 的 relevance
feedback：用户给出初始查询，系统返回结果，用户标记相关/不相关，系统据此修改查询向量再次检索。后来
Lavrenko 和 Croft（2001）用 RM3 实现了 pseudo-relevance
feedback：假设第一轮检索的 top-k
结果是相关的，直接从中提取关键词扩展查询，跳过人工标记。LLM 做 query
rewriting
本质上是这个思路的升级版，用生成模型替代了统计方法，灵活性大幅提高。这是
RAG 相对于 IR 有实质改进的少数环节之一。

但 IR 的经验指向一个风险：query
drift。如果第一轮检索结果本身不相关，基于这些结果做扩展会引入噪声，越改越偏。LLM
query rewriting 也有同样的风险，尤其当 LLM
在改写时引入了原始查询中没有的概念。对策是同时用原始查询和改写后的查询做检索，取并集，而不是完全替换原始查询。

---

## RAG 的真正贡献在哪里

前面逐项对照的目的不是贬低 RAG。RAG
的贡献是真实的，只是它发生的层面跟很多人以为的不一样。

RAG 的核心贡献是成本压缩。在 RAG 出现之前，搭建一个包含
chunking、embedding、向量检索、reranking 的管线，需要 IR
背景的工程师，需要理解 BM25 的数学原理、HNSW 的图结构、Learning to Rank
的目标函数。RAG
框架（LangChain、LlamaIndex、Haystack）把这些封装成了高层 API，任何会写
Python 的开发者都可以在一天内搭出一个可以工作的检索增强生成系统。

这种 democratization
的价值不应该被低估。技术史上，很多重大进步都是通过降低门槛而非发明新算法实现的。Linux
没有发明操作系统内核，但让服务器操作系统从大型机走向了普通 PC。AWS
没有发明虚拟化，但让计算资源从采购硬件变成了 API 调用。RAG
在检索增强生成这个领域做了类似的事情。

RAG 的第二个贡献是产品形态的创新。把检索结果直接喂给 LLM
生成连贯的回答，而不是展示一列链接。搜索引擎返回的是链接列表，用户需要自己点击、阅读、综合。RAG
把这个综合步骤交给了
LLM，用户直接得到一个基于检索结果的回答。这是交互范式的改变。

但在算法层面，RAG 管线中的每个组件都是 IR
的成熟技术。认识到这一点的实用意义在于：IR
领域的大量工程经验、评测方法、失败教训都可以直接复用。我们不需要从零摸索
chunk size 的最优值，TREC 的实验已经给出了指导。我们不需要纠结要不要加
BM25，IR 社区二十年的实践已经证明 sparse + dense
的组合优于任何单一通道。我们不需要自己发明 score fusion 方法，RRF
已经是一个被验证过的、简单有效的方案。

---

## 搜索引擎也在变：双向融合

到目前为止，故事的一面是 RAG 从 IR
继承技术。另一面是搜索引擎在积极吸收 LLM。这个融合正在三个层面发生。

表面层：AI 摘要叠加在搜索结果上。Google AI Overviews
是最典型的例子。用户搜索一个问题，Google
在传统的蓝色链接列表上方展示一段 LLM
生成的摘要。底层的检索管线没有根本改变，改变的是结果的呈现方式。

检索层：Neural retrieval 增强传统搜索。Elasticsearch 在 2023 年推出了
ELSER（Elastic Learned Sparse EncodeR），用 BERT 模型学习每个 token
的权重，替代传统的 BM25
词频统计，但输出仍然是稀疏向量，兼容倒排索引。用户无需切换到向量数据库，在原有的
Elasticsearch 集群上就能获得语义检索能力。

推理层：LLM 作为搜索决策者。Perplexity 让 LLM
决定搜索什么、搜索几次、如何组合不同来源的信息。用户提出一个问题，LLM
把它拆解成多个子查询，分别搜索，评估结果的可信度，再综合生成回答。

搜索引擎从检索端出发加入生成能力，RAG
从生成端出发引入检索技术。两者的架构正在趋同。

---

## 碰撞产生的新东西

真正值得关注的是两个世界碰撞之后产生的新技术，IR 传统和 LLM
时代的交叉产物，两边单独都做不出来。

SPLADE（SParse Lexical AnD Expansion model）让 BERT
学会写倒排索引。它用 BERT 的 Masked Language Model head
对输入文本预测词汇表中所有词的概率，取高概率词作为扩展词，用
log-saturation
函数把概率转换成权重。输出是一个稀疏向量，维度等于词汇表大小，大部分维度为零。它同时做了隐式的
query expansion 和学习型的词权重，而且输出兼容倒排索引，可以直接存进
Elasticsearch。这是 neural IR 和传统 IR 的桥梁。

ColBERT（Contextualized Late Interaction over
BERT）在效率和效果之间找到了一个新的平衡点。传统 dual encoder
把整个文档压缩成一个向量，丢失了 token 级别的细粒度信息。Cross-encoder
保留了 token 交互，但计算成本太高。ColBERT 保留每个 token
的向量（而非压缩成一个），在匹配时对每个查询 token 找到最相似的文档
token，取 MaxSim 加总。文档 token 向量可以预计算和索引，比 cross-encoder
快几个数量级，比 dual encoder 更精确。

Agentic Search 是最新的方向：LLM
主动规划检索策略。一个需要多步推理的问题（比如比较两年间某个领域的研究方向变化），传统搜索和传统
RAG 都处理不好。Agentic search 让 LLM
充当检索规划器，决定搜什么、搜几次、每步用什么方法。Perplexity 的 Deep
Research 和 OpenAI 的 deep research 模式都在探索这个方向。

---

## 学术界已经在正式讨论这件事

SIGIR 2024 举办了第一届 IR-RAG Workshop，明确指出 current efforts
have undervalued the role of information retrieval within the RAG
pipeline。SIGIR 2025 延续了这个 Workshop，征稿主题包括如何把 IR
的评测方法引入 RAG。

TREC（IR 领域运行了 30 多年的标准评测）在 2025 年正式设立了 RAG
Track。首轮评测收到了 12 个研究组的 46 个提交，评估 RAG
系统在开放域问答上的端到端表现。IR 社区开始用自己的评测框架来系统地衡量
RAG 系统的质量。

RAGFlow（一个开源 RAG 框架）的开发者在 2025
年中发表了一篇反思文章，直言 genuine innovation in concepts and systems
was notably scarce。他们的观察是：RAG
领域发了大量论文，但大部分是在已有组件上做微调，缺乏基础性的创新。

这些声音汇聚成一个共识：RAG 需要从 IR 领域吸收更多，而 IR
也需要认真面对 LLM 带来的新范式。两个社区的隔阂正在缩小。

---

## 实操建议：五件我们今天就能做的事

基于以上分析，如果我们正在维护一个 RAG
系统，以下五个改进是投入产出比最高的：

第一，加入 BM25 通道做 hybrid search。用 RRF 融合两路结果，k 值取
60。用 rank 做 fusion 而非 score 加权。Elasticsearch、Vespa、Weaviate 和
Milvus 都原生支持。

第二，重新审视 chunking 策略。把 chunk size
当作可调参数而非固定常数。按语义边界切割通常优于按固定 token
数切割。长文档场景考虑 hierarchical retrieval。

第三，确保召回阶段的多样性。Reranker
的上限受制于候选集质量。先把召回做好（多通道、合理的
top-k），再投入精力调 reranker。

第四，检查向量相似度的选择。如果语料包含长度差异大的文档，确认使用
cosine similarity 而非 dot product，或在 embedding 之后做 L2
归一化。

第五，关注 learned sparse retrieval。SPLADE 和 ELSER 桥接了 sparse 和
dense 两个世界，是 BM25 的自然升级路径。如果已经在用
Elasticsearch，ELSER 可以在不改变架构的情况下引入语义检索。

---

## 一个收敛的方向

搜索引擎和 RAG 正在从两个方向走向同一个架构模式：多通道检索（sparse +
dense + 其他信号）、neural reranking、LLM
生成或推理。搜索引擎从检索端出发，逐步加入 neural retrieval
和生成能力。RAG 从生成端出发，逐步引入 BM25、hybrid search 和更成熟的
retrieval 评测。

理解 IR 基础不会让我们变得保守。相反，它让我们在设计 RAG
系统时有更丰富的工具箱：我们知道 BM25 能解决什么问题，HNSW
的参数怎么调，RRF 为什么可以无缝融合不同量纲的分数，cascade ranking
为什么是两阶段而不是一阶段。这些知识直接转化为更好的系统设计。

IR 领域积累了 50 年的检索技术，LLM
带来了生成能力和语义理解。两者的交叉正在产生 SPLADE、ColBERT、agentic
search
这些新方向。如果我们同时理解两边的语言，就站在了这个交叉点上。

---

## 参考来源

技术史与经典论文： - Callan (1994), Passage-level evidence in
document retrieval, SIGIR: https://dl.acm.org/doi/10.1145/188490.188560
- TREC Passage Retrieval Track (2003):
https://trec.nist.gov/pubs/trec12/papers/PASSAGE.OV.pdf - DSSM (2013),
Learning Deep Structured Semantic Models, CIKM:
https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/cikm2013\_DSSM\_fullversion.pdf
- Cormack et al. (2009), Reciprocal Rank Fusion, SIGIR:
https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf - Karpukhin et
al. (2020), Dense Passage Retrieval, EMNLP:
https://arxiv.org/abs/2004.04906

双向融合： - Google AI Overviews:
https://developers.google.com/search/docs/appearance/ai-features -
Perplexity API:
https://docs.perplexity.ai/docs/getting-started/overview.md -
Elasticsearch ELSER:
https://www.elastic.co/search-labs/blog/elastic-learned-sparse-encoder-elser-retrieval-performance

学术前沿： - SPLADE, TOIS:
https://hal.sorbonne-universite.fr/hal-04787990/file/splade\_tois\_REVISION\_-1.pdf
- ColBERT, SIGIR 2020:
https://people.eecs.berkeley.edu/~matei/papers/2020/sigir\_colbert.pdf -
SIGIR 2025 IR-RAG Workshop CFP: https://easychair.org/cfp/irrag2025 -
TREC RAG Track 2025: https://arxiv.org/html/2603.09891v1

行业观点： - Coveo, Search Engine vs Vector Database:
https://www.coveo.com/blog/search-engine-vs-vector-database/ - RAGFlow
2025 Mid-year Reflections:
https://ragflow.io/blog/rag-at-the-crossroads-mid-2025-reflections-on-ai-evolution

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
