---
title: "高扇入场景下的 Agent 控本：在 Agent 看到输入之前"
date: 2026-08-06
source: https://yage.ai/share/pre-agent-fan-in-filter-cost-20260806.html
slug: pre-agent-fan-in-filter-cost-20260806
lang: zh
---
# 高扇入场景下的 Agent 控本：在 Agent 看到输入之前

发布于 2026 年 8 月 6 日 · [查看原网页](https://yage.ai/share/pre-agent-fan-in-filter-cost-20260806.html)

越来越多团队在尝试把 AI 引入 SRE 和系统运维，搭建 AI
运维值班助手。它的工程目标很明确：当生产环境出现异常时，代替疲惫的人类值班工程师，自动拉取日志、对比代码改动、查询调用链并快速定位故障根因。但在高告警量、且每条告警都会触发多步调查的系统里，一个常见风险是
API
账单随单次故障迅速上升。问题并非出在模型不够聪明，而在于直觉式的架构设计。大家往往把监控系统的告警直接通过
Webhook 直连 Agent，尝试实现一条告警触发一个 Agent
任务。然而在真实的生产环境里，故障并不是孤立发生的。

## 场景与困境：当你尝试搭一个 AI 运维值班助手

为了理解这个困境，我们可以还原一个常见的故障现场。假设你维护着一个微服务系统。某天底层数据库因为连接池配置不当发生了短暂的超时，在接下来的
90 秒内，这个底层故障会引发连锁反应，包括上游 API 网关开始抛出 502
错误，异步消息队列产生严重积压，K8s 容器存活性检查陆续失败，APM
性能监控同时发出响应延迟告警。如果你的系统设定是每监听到一条告警就启动一个
Agent 任务去跑排查，那么在几分钟内，监控面板弹出的 50
条关联告警就会派生出 50 个独立的 Agent 任务。

这会带来两个严重的后果。首先是工具调用与轨迹爆炸：Agent
的主要开销并不是单次 Prompt
长度，而是为了排查问题进行的多次工具调用，例如执行终端命令、查询日志库、提取
Git 提交。50 个独立运行的 Agent 意味着 50
条长轨迹在同时消耗算力，几分钟内就能跑出上千次 API
调用。其次是诊断极为割裂：这 50 个 Agent
彼此不知道对方的存在，它们分别针对网关 502、队列积压和 Pod 重启给出 50
份治标不治本的割裂报告，却没有人看到底层数据库连接池才是真正的罪魁祸首。

在传统运维中，PagerDuty 官网的 [Chicago Trading Company
客户案例](https://www.pagerduty.com/customers)称，该客户使用 Event Intelligence 自动分组告警后，一次涌入的
50 到 200 条告警降至 5 到 10 条；这是客户案例，不是通用压缩比例。而在
2026 年 7 月 28 日，Datadog 在其发布的 [AI
Security Detection Pipeline](https://www.datadoghq.com/blog/ai/ai-security-detection-pipeline/)
中展现了同一经济结构的极端版本。据该官方博客披露，Mambark 是一个约 96.9M
参数的 Mamba 模型，每天从约 100 亿条安全事件中选出约 10,000
条候选，再交给大模型 Agent
调查；按候选数计算相差六个数量级，但这些生产规模和成本数字目前仍是厂商自报，未经独立复核。

如果只看这句话，很多人可能还无法体会到这个设计精妙的地方，甚至会误以为这只是一套常见的级联架构，或是用一个便宜的小模型去做通用文本分类。但实际情况更具体。Mambark
不是对单条日志做通用文本问答，而是先用自监督的 next-event prediction
学习事件序列，并用负对数似然产生 surprise score；Datadog
同时说明，它还会针对每个下游来源做短暂微调，分类哪些事件值得进入
Agent。如果真用通用的文本小模型去处理日志流，首先遇到的并不是算力开销，而是任务形态上的错位：在没有任何人提问的日志流里，单条日志本身并没有好坏之分，小模型在没有查询的情况下不知道自己要找什么。这套设计的真实直觉，在于它并没有把日志当作文本去提问，而是把日志流视作系统的状态序列，利用序列模型完成无监督的下一个事件预测。当实际出现的事件偏离了系统常态的演进概率时，系统就自动将其标为高异常度事件。这种不依赖提问与人工
Prompt，而是利用序列困惑度捕捉状态异常的做法，才是它能够在低开销下完成百亿级筛选的核心原因。

*高扇入输入的两阶段漏斗：廉价过滤层把 N 收窄到 K，再交给昂贵 Agent 调查*

高扇入输入的两阶段漏斗：廉价过滤层把 N
收窄到 K，再交给昂贵 Agent 调查

这个设计把昂贵大模型 Agent 的调查对象从全量事件收窄到候选
shortlist，也支撑了一个核心判断：在应对高扇入流式事件时，决定什么值得让
Agent 启动调查，比把 Agent 单次思考调便宜更重要，也更具结构性优势。在 [《AI
补贴退潮后，agent 开始按每美元智能计价》](https://yage.ai/share/ai-cost-subsidy-retreat-agent-design-20260628.html) 和 [《你的
Agent 管线里，最贵的模型可能在最错的位置》](https://yage.ai/share/agentopt-model-selection-pipeline-20260409.html) 中，我们讨论过 Agent
内部的模型分工与成本控制，而 Pre-Agent 过滤则构成了站在 Agent
外部的控本大门。

## 算困惑度而非向量比对：从 DeepLog 到 Mamba 的九年演进

当工程师听到前文提及的信息检索与两阶段筛选时，最直观的工程联想往往是
[DPR](https://aclanthology.org/2020.emnlp-main.550/) 这类
query-driven dense
retriever：它从一个问题出发，在向量索引中寻找相关文本。但并非所有向量方法都要求人类显式提问；这里真正的区别是
DPR 优化 query-to-corpus retrieval，而事件流异常检测优化 item-to-history
scoring。在海量日志和安全事件流中，并没有人在实时提问，系统无法预知下一秒会发生什么异常，因此无法凭空构造一个查询向量。

解决这一难题的本质，是将第一层变为语言模型的困惑度或概率计算。这一思路至少可以追溯到犹他大学团队发表于
[ACM CCS
2017 的 DeepLog](https://users.cs.utah.edu/~lifeifei/papers/deeplog.pdf)。DeepLog 将系统日志看作自然语言，用 LSTM
预测下一个日志事件的概率分布；当实际出现的 log key 不在模型给出的 top-g
候选中时，将其判为序列异常。

在从 2017 到 2026 年的演进历程中，这一范式经历了三次关键迭代：

- **2017 年（LSTM 时代）**：DeepLog 使用 LSTM
  预测下一个日志事件。虽然验证了范式可行，但 LSTM
  模型容量较小、表征能力有限，难以捕获复杂微服务之间的跨系统依赖。
- **2020 至 2023 年（Transformer 时代）**：2022 年的
  TransLog 等工作把 self-attention 引入日志异常检测；完整 self-attention
  的计算量随序列长度呈平方增长，但 TransLog
  本身不是自回归生成系统，不能把它的限制归因于 KV
  Cache。对需要持续维护超长事件历史的流式 scorer，Transformer
  的上下文计算和随长度增长的状态存储才是主要压力。
- **2023 至 2026 年（Mamba 状态空间模型时代）**：基于 [Mamba SSM](https://arxiv.org/abs/2312.00752)
  架构的引入打开了新路径。2023 年底发布的 Mamba 用固定大小的 SSM
  与卷积状态替代随上下文增长的 attention KV
  cache，使流式推理的状态内存不再随序列长度线性膨胀。

小语言模型在此处找到了清晰的工程定位：它不需要用来回答问题或调用工具，而是通过计算下一个事件的出现概率，充当高性能的流式异常过滤器。

*两类 cascade 的区别：范式 A 优化单输入想多深，范式 B 优化海量输入中哪些值得想*

两类 cascade 的区别：范式 A
优化单输入想多深，范式 B 优化海量输入中哪些值得想

## 从高层直觉到工程落地：具体是怎么做的？

理解了无监督序列预测的高层直觉后，要在实际工程中搭建这套 Pre-Agent
过滤层，具体可以拆解为三个关键实现环节。

首先是模版化分词与日志预处理。对于海量系统日志，切忌直接使用常规的
BPE 子词分词器。因为在通用大语言模型的分词规则中，时间戳、IP
地址和变量哈希会被拆解为大量无意义的字符碎片，极大浪费计算开销。推荐的做法是先使用
[Drain](https://github.com/logpai/logparser)
等模版解析工具，将形如 User login failed from IP
的非结构化文本抽取为固定的日志模版与事件编号。这种模版化分词将非结构化的日志流转化为离散的事件序列，从源头降解了序列预测的复杂度。

其次是基座模型选择与自监督微调。在开源生态中，模型选择并不需要庞大的参数规模，实验原型可以从
Hugging Face 上的 [`state-spaces/mamba-130m-hf`](https://huggingface.co/state-spaces/mamba-130m-hf)
或类似的小型 Mamba 模型开始；Hugging Face 也提供了 LoRA 示例。若输入采用
Drain event ID，还需自行定义事件词表并适配 embedding/output
head，训练时长则应按数据量、序列长度和硬件实测。

最后是根据事件量级选择门槛。可以把每日
10210^2-10310^3、10310^3-10410^4
和
105+10^5+
条当作粗略容量规划起点，而不是固定门槛；是否增加过滤层及选用规则、浅层分类器还是小型序列模型，应由每条调查成本、目标稀有度、漏检代价和调查容量实测决定。当事件量较低、且强模型只做一次批量摘要时，直接调用通用大模型往往更简单；当每条候选都会触发多步
Agent 调查、且 shortlist 能压到 10%-20% 时，廉价 triage
或规则预筛选开始有财务空间；当 cheap API pass
本身成为主要成本、且流量持续更高时，才值得考虑专用小模型过滤层。

许多 Builder 可能会好奇，为什么 [Anthropic
的 Agent 架构指南](https://www.anthropic.com/engineering/building-effective-agents)、[OpenAI 的
Agent 开发者指南](https://developers.openai.com/tracks/building-agents) 以及 [Cursor
的 Harness 演进](https://cursor.com/blog/continually-improving-agent-harness)
等主流材料中很少提供这种过滤组件。在这里引用的三份指南中，讨论单位主要是已经进入系统的
task 或
session，至少这些材料没有把高扇入流式入口过滤抽象为通用组件。一个可能原因是，过滤掉的
false negative 不会进入常规 Agent
trace，现有评估较难观察它；这是一种解释，而不是这些厂商公开确认的设计原因。security、AIOps、fraud
和 content moderation
等垂直领域其实早已有同构架构，只是它们长期封在各自领域名下，尚未上升为横向
agent 工程的一等 primitive。

## 总结：应对海量输入的工程护城河

在大模型技术快速迭代的当下，不少人存在一种错觉，认为随着未来 Token
单价的持续降低，入口处的过滤与收窄会变得不再重要。但从系统工程的角度来看，在会触发多轮工具调用的
Agent 工作负载中，总成本往往同时受模型单价、token
量、轨迹长度和外部工具费用影响；高扇入尤其会放大重复轨迹的成本。在海量流式输入面前，如果不做入口筛选，未经过滤的轨迹调用依然会导致过高的账单与混乱的诊断。在
[《KV
cache 命中率：Agent 推理的第一成本杠杆》](https://yage.ai/share/prefix-cache-agent-cost-lever-20260625.html) 中我们探讨过 Agent 内部的
Prefill 重读优化，而 Pre-Agent 过滤则是站在 Agent 外部收窄入口门槛。在
Agent
看到输入之前决定什么值得思考，才是应对高扇入海量事件时最坚固的工程护城河。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
