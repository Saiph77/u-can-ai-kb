---
title: "美国开始把中国开源 AI 当作一条独立的竞争路径"
date: 2026-03-23
source: https://yage.ai/share/us-sees-china-open-source-ai-path-20260323.html
slug: us-sees-china-open-source-ai-path-20260323
lang: zh
---
# 美国开始把中国开源 AI 当作一条独立的竞争路径

发布于 2026 年 3 月 23 日 · [查看原网页](https://yage.ai/share/us-sees-china-open-source-ai-path-20260323.html)

---

2026 年 3 月 23
日，美中经济与安全审查委员会（USCC）发布了一份研究报告，标题是 [*Two
Loops: How China’s Open AI Strategy Reinforces Its Industrial
Dominance*](https://www.uscc.gov/sites/default/files/2026-03/Two_Loops--How_Chinas_Open_AI_Strategy_Reinforces_Its_Industrial_Dominance.pdf)。[Reuters
当天的报道](https://www.reuters.com/business/autos-transportation/chinas-open-source-dominance-threatens-us-ai-lead-us-advisory-body-warns-2026-03-23/)用了一个醒目的措辞：中国开源 AI 正在制造 “self-reinforcing
competitive advantage”。

如果只看标题，很容易误读成又一轮”中国 AI
要超过美国了”的叙事。但报告的关注点在别处。报告承认，美国闭源模型在大多数评测维度上仍然”slightly
ahead”。真正让美国政策圈紧张的是另一个问题：中国正在用一条完全不同的路径去争夺全球
AI
的影响力，而美国现有的政策工具——主要是芯片出口管制——几乎管不到这条路径。

对中国 AI
从业者来说，这个判断值得认真对待。它意味着美国正式把开源模型的分发能力、API
定价、框架兼容性、工业场景部署这些事情，当作一条独立的竞争维度来评估了。这条维度已经超出
benchmark 竞赛本身，指向一场关于谁能成为全球开发者默认选项的较量。

## 发生了什么

先交代清楚这份报告的性质。USCC
是美国国会设立的常设咨询机构，长期跟踪中美经济与安全议题。但 *Two
Loops* 的性质是 Research Working Group
Paper，代表研究团队的分析，不是委员会的正式年度报告或政策建议书。这个区分很重要：它有分析价值，但不能等同于美国政府的官方立场。

报告提出了一个”双回路”框架来解释中国开源 AI 的扩张机制。

第一条是数字回路：开源模型发布后，全球开发者下载、微调、在它的基础上构建衍生模型，使用反馈又推动模型迭代，然后更多开发者加入。这是一个典型的网络效应故事。第二条是物理回路：AI
模型部署到制造业、物流、机器人等工业场景，产生真实世界的交互数据，这些数据反哺模型改进，改进后的模型又能进入更多场景。

USCC
认为这两条回路正在相互强化。而且它明确指出了一个政策上的尴尬：

> U.S. export controls primarily target the digital loop—restricting
> access to advanced chips used for frontier model training—but are not
> well suited to addressing the physical loop of deployment-driven data
> creation and accumulation across China’s manufacturing base.

换句话说，芯片管制卡的是训练环节，但中国模型的全球扩散和工业数据积累发生在部署环节——部署用的通常是蒸馏或量化过的小模型，对前沿芯片的依赖远低于预训练。出口管制对这条路径几乎没有着力点。

## Qwen：证据最充分的案例

在所有被 USCC 报告点名的中国模型里，阿里巴巴的 Qwen
系列是证据最充分的案例。

Qwen 从 6
亿参数的轻量模型到数百亿参数的大模型全部开放权重，形成了一条完整的产品线。全球开发者可以基于
Qwen 进行微调、蒸馏和二次开发，而不仅仅是调用
API——这是它与闭源模型在竞争逻辑上的核心差异。

在 HuggingFace 上，Qwen 的扩散数据相当引人注目。据[新华社援引
HuggingFace 数据](https://english.news.cn/20260113/af90462629d146c2acad0e99525faba3/c.html)，截至 2026 年 1 月，Qwen 家族累计下载量超过 7
亿次，2025 年 12 月单月下载量超过了排名第二到第九的模型之和，已经超过
Meta Llama 成为 HuggingFace
上下载量最大的开源模型系列。衍生模型方面，USCC 报告引用的是 2025
年底超过 10 万个的数据，后续第三方来源更新为 18 万个以上。ATOM
项目创始人 Nathan Lambert 的统计显示，Qwen 的衍生模型已占 HuggingFace
上新增语言模型衍生的 40% 以上，而 Meta Llama 下降到约 15%（[MIT
Technology Review, 2026-02-12](https://www.technologyreview.com/2026/02/12/1132811/whats-next-for-chinese-open-source-ai/)）。

同样重要的是，Qwen 已经被 vLLM、HuggingFace
Transformers、TensorRT-LLM、LlamaFactory
等主流推理和微调框架原生支持。这意味着开发者使用 Qwen
时几乎不存在额外的技术集成成本，它已经是开发者工具链中的一等公民。

当然，下载量和衍生模型数分别代表不同的含义。前者反映开发者的兴趣和试用行为（包括重复下载和自动化脚本），后者反映技术生态的建设深度。两者都不直接等于企业级生产部署的市场份额。USCC
报告也指出，“measuring use of AI models in applications is difficult
compared to tracking model downloads and derivative uploads.”
这一点在解读所有后续数据时都需要记住。

## 价格和分发：Kimi、MiniMax 提供的补充信号

Qwen 之外，Moonshot AI 的 Kimi K2.5 和 MiniMax M2.5
在全球扩张证据方面不如 Qwen
充分，但它们在两个维度上提供了有意义的信号：价格竞争力和第三方平台可接入性。

价格层面，Kimi K2.5 的 input token 定价约 $0.60/M，Anthropic Claude
Opus 4.6 是 $5/M，相差约 8 倍（[nxcode.io](https://www.nxcode.io/resources/news/kimi-k2-5-pricing-plans-api-costs-2026)）。MiniMax
M2.5 更低，input $0.30/M，output
$1.20/M，在独立基准测试中每次运行成本约为 Claude Sonnet 的三分之一（[LLM
Benchmark 2026](https://ianlpaterson.com/blog/llm-benchmark-2026-38-actual-tasks-15-models-for-2-29/)）。需要注意，API 定价比较高度依赖具体用例和 token
长度分布，上述数字来自公开定价和第三方测试，实际场景中差异可能更大或更小。

分发层面，Together AI、Fireworks AI 等第三方推理平台已经把 Qwen、Kimi
K2.5 和 MiniMax M2.5 纳入标准模型库。在 OpenRouter 平台上，中国模型的
API 调用量在 2026 年 2 月首次超过美国模型（[CGTN,
2026-02-28](https://news.cgtn.com/news/2026-02-28/Chinese-AI-models-overtake-U-S-rivals-in-global-token-usage-1L8h5rMl26c/p.html)）；2 月第三周，OpenRouter Top 5
调用量中有四个来自中国厂商，合计贡献 85.7%（[36Kr](https://eu.36kr.com/en/p/3700980530851712)）。

但 OpenRouter 的数据需要谨慎解读。它是一个面向开发者的 API
聚合平台，用户群偏向价格敏感型个人开发者和小型团队，不代表企业级部署全貌，也不代表
AWS、GCP、Azure 这类大型云平台上的使用分布。

## 美国为什么开始紧张

理解了上面这些证据之后，USCC
报告引发美国政策圈关注的原因就比较清晰了。

过去几年，美中 AI
竞争的主叙事围绕两个轴线：谁的模型在最难的任务上得分最高（frontier
benchmark），以及谁能调动最多算力来训练最大的模型（training
compute）。美国在这两个维度上仍然领先。出口管制的设计逻辑也建立在这个框架之上：限制中国获取最先进芯片，就能限制其训练能力。

USCC 报告的冲击在于，它用 “two loops”
的分析指出，竞争可能同时发生在另外两个层面：谁的模型被全球开发者最广泛采用，以及谁能通过工业部署积累最多真实世界数据。在这两个层面上，芯片管制的杠杆效果很弱。用报告的概括：

> Open model proliferation creates alternative pathways to AI
> leadership.

这句话的含义是：即使美国在前沿能力上保持领先，中国模型如果通过开源分发占据了全球开发者生态的默认地位，美国的技术领先就难以自动转化为产业主导和地缘影响力。

而且这种关注并非孤立事件。USCC 早在 3 月 4 日的 [China
Bulletin](https://www.uscc.gov/trade-bulletins/china-bulletin-march-4-2026) 中就专门分析了 Qwen3.5
的推理成本优势。美国国家情报总监办公室（ODNI）在 3 月 19
日的全球威胁评估中也提到，中国正在”以规模化方式在国内和国际推动 AI
采用”（[Defense
One, 2026-03-19](https://www.defenseone.com/threats/2026/03/AI-intelligence-new-global-threat/412232/)）。对中国 AI
扩张的警惕已经从经济安全领域扩展到了情报和国防评估的范畴。

## 这更像业界共识，还是 USCC 的独立判断

如果只看 3 月 23
日这份报告，读者很容易以为这是美国政策圈刚刚提出的一种新说法。顺着过去几个月产业界的公开表达往回看，图景并不是这样。更接近事实的判断是：工业界已经持续用
deployment、inference、ecosystem 和 industrial integration 这些维度理解
AI 竞争，USCC 这次是把这套语言翻译成了政策和安全分析。

Jensen Huang 是最值得看的一个参照。过去一年，NVIDIA 反复把 AI
竞争的重点从模型本身，转向推理、系统部署和 physical AI。GTC 2026
之后，eWeek 对黄仁勋整场演讲的概括是，AI is moving from model spectacle
to systems economics，也就是竞争开始从模型奇观转向系统经济学。这个判断和
USCC 的 two loops 很接近：前者说 AI 价值开始落在持续推理、agent 软件层和
physical AI
负载上，后者说中国可能通过开源分发和工业部署形成两条自我强化的回路。两边说法不同，底层观察是一致的，大家都在把竞争重心从
谁训练出最强模型 转向 谁控制部署和使用。

微软的 Satya Nadella 也在用类似语言描述这个变化。2026 年初，他把企业
AI 的阶段判断概括为从 discovery 进入
diffusion。这个词很关键。它关心的已经不是模型首次展示了什么能力，而是这些能力能不能进入真实组织、真实流程和真实工作负载。亚马逊
CTO Werner Vogels 的表达更直接：AI capability is sufficient; the
constraint is human-centered
scaling。意思是，模型能力本身已经不是唯一瓶颈，真正决定竞争的是谁能把 AI
融入人的工作流、企业的系统和可以规模化运行的环境。

如果把这个视角再往下推一步，AWS、OpenAI、Google
这些公司的动作也都在证明同一件事。Andy Jassy 近几次公开表态反复强调
inference 成本才是未来的大头。Sam Altman 把 enterprise sales 作为 2026
年的第一优先级，OpenAI
也开始越来越多地讲企业工作流、结构化使用和平台化入口。Google 这边则是把
Gemini 尽可能深地嵌入 Search、Workspace、Chrome 和
Android。它们的商业路径并不一样，但都没有把竞争理解成单一的 benchmark
竞赛。真正争夺的是默认入口、使用深度和部署位置。

研究机构的判断也在往同一个方向收敛。Gartner 讲 task-specific agents
和 domain-specific models，McKinsey 讲从 pilot 到 scale 的鸿沟，Deloitte
讲 deployment 阶段的治理能力。这些报告的语言更偏企业管理，但底层意思与
USCC 很接近：模型能力的展示阶段已经过去，下一阶段是谁能把 AI
变成可复制、可分发、可运营的系统。

放在这个背景里再看
USCC，就比较容易定位它的意义了。它并不是突然发明了一个全新的竞争框架。更准确的说法是，USCC
把一个工业界已经持续讨论的变化，翻译成了政策语言和国家竞争语言。工业界谈的是
inference economics、enterprise diffusion、ecosystem control 和 physical
AI。USCC 谈的是 digital loop、physical loop
和出口管制的覆盖盲区。语言不同，观察对象是同一件事。

这也是为什么这份报告值得中国 AI
从业者注意。它说明美国政策圈正在追认一个原本主要存在于产业界的判断：未来几年，AI
竞争不会只看谁的模型更强，还会看谁的模型更便宜、更容易接入、更容易被全球开发者采用，以及谁能把模型部署进更大规模的真实场景。USCC
关注中国开源
AI，不只是因为它看到了几组平台数据，而是因为这套竞争方式已经被工业界证明具有现实意义。

当然，这并不意味着工业界和政策圈已经形成了完全一致的结论。工业界更关心
ROI、部署效率和生态位置，政策圈更关心这种变化会不会削弱既有的技术和地缘优势。但如果只回答一个问题：这是一家之言，还是已经形成的主流视角？答案更接近后者。

## 竞争逻辑的变化

回到最开始的问题：这件事对中国 AI 从业者意味着什么？

USCC
这份报告揭示的核心变化在于，美国政策圈开始用一套新的分析框架来评估中美
AI
竞争。在这套框架里，竞争的评判维度从”谁训练出最强模型”扩展到了”谁的模型被全球开发者和工业场景最广泛地采用”。

这对中国 AI 从业者有两个直接含义。

其一，中国开源模型在全球开发者生态中的存在感正在被认真对待，但同时也被当作政策议题来审视。Qwen
在 HuggingFace
的生态地位、中国模型在推理云平台的渗透率、远低于美国闭源模型的 API
定价——这些本来是市场竞争的正常结果，现在正在被纳入地缘安全的分析视野。后续可能出现针对开源模型分发环节的政策讨论，值得持续关注。

其二，这份报告也提醒了一个事实：adoption 和 frontier capability
是两回事。中国模型在分发速度、价格和开发者接入门槛上确实有优势，但在企业级信任、合规审查、超级云分发和前沿任务能力方面仍然存在明显差距。把
adoption 层面的进展等同于全面领先，和把 benchmark
上的领先等同于产业主导，犯的是同一个错误——都是把竞争简化成了单一维度。

真实的图景是：竞争的维度在变多，而中美各自的优势集中在不同维度上。美国政策圈刚刚开始认真面对这个现实，而这本身就是值得记录的变化。

---

## 参考来源

**一手来源**

1. USCC, *Two Loops: How China’s Open AI Strategy Reinforces Its
   Industrial Dominance*, 2026-03-23. [PDF](https://www.uscc.gov/sites/default/files/2026-03/Two_Loops--How_Chinas_Open_AI_Strategy_Reinforces_Its_Industrial_Dominance.pdf)
   | [报告页](https://www.uscc.gov/research/two-loops-how-chinas-open-ai-strategy-reinforces-its-industrial-dominance)
2. USCC, *China Bulletin: March 4, 2026*. [链接](https://www.uscc.gov/trade-bulletins/china-bulletin-march-4-2026)

**媒体报道**

3. Reuters, “China’s open-source dominance threatens US AI lead, US
   advisory body warns,” 2026-03-23. [链接](https://www.reuters.com/business/autos-transportation/chinas-open-source-dominance-threatens-us-ai-lead-us-advisory-body-warns-2026-03-23/)
4. Defense One, “US intelligence elevates AI as a top global threat in
   new report,” 2026-03-19. [链接](https://www.defenseone.com/threats/2026/03/AI-intelligence-new-global-threat/412232/)

**Adoption 与技术分析**

5. MIT Technology Review, “What’s next for Chinese open-source AI,”
   2026-02-12. [链接](https://www.technologyreview.com/2026/02/12/1132811/whats-next-for-chinese-open-source-ai/)
6. 新华社, “Alibaba’s Qwen leads global open-source AI community with
   700M downloads,” 2026-01-13. [链接](https://english.news.cn/20260113/af90462629d146c2acad0e99525faba3/c.html)
7. AICerts, “Alibaba Qwen Model Downloads: Metrics and Enterprise
   Impact.” [链接](https://www.aicerts.ai/news/alibaba-qwen-model-downloads-metrics-and-enterprise-impact/)
8. CGTN, “Chinese AI models overtake U.S. rivals in global token
   usage,” 2026-02-28. [链接](https://news.cgtn.com/news/2026-02-28/Chinese-AI-models-overtake-U-S-rivals-in-global-token-usage-1L8h5rMl26c/p.html)
9. 36Kr, “February Sees Surge in AI Usage: China’s AI Call Volume
   Overtakes US,” 2026-02. [链接](https://eu.36kr.com/en/p/3700980530851712)

**价格与基准测试**

10. nxcode.io, “Kimi K2.5 Pricing 2026.” [链接](https://www.nxcode.io/resources/news/kimi-k2-5-pricing-plans-api-costs-2026)
11. LLM Benchmark 2026, “38 Actual Tasks, 15 Models.” [链接](https://ianlpaterson.com/blog/llm-benchmark-2026-38-actual-tasks-15-models-for-2-29/)
12. morphllm.com, “Best AI for Coding (2026).” [链接](https://morphllm.com/best-ai-model-for-coding)

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
