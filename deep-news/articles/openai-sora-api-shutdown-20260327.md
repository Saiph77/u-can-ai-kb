---
title: "OpenAI 关掉 Sora 可以理解，但为什么连 API\n都关了？"
date: 2026-03-27
source: https://yage.ai/share/openai-sora-api-shutdown-20260327.html
slug: openai-sora-api-shutdown-20260327
lang: zh
---
# OpenAI 关掉 Sora 可以理解，但为什么连 API 都关了？

发布于 2026 年 3 月 27 日 · [查看原网页](https://yage.ai/share/openai-sora-api-shutdown-20260327.html)

2026 年 3 月，OpenAI 正式关闭了 Sora，包括 consumer app 和开发者
API。作为一个 social video app，Sora 的失败并不意外。Day-30
用户留存率低于 5%，App Store 下载量从 2025 年 11 月的 330 万暴跌到 2026
年 2 月的 110 万，排名从 #1 滑到 #172。Disney 那笔看起来很大的 $10
亿合作协议也同步取消，BBC 报道双方之间实际上没有任何资金往来（[BBC](https://www.bbc.com/news/articles/c3w3e467ewqo)）。这是一个
consumer product 失败的标准剧本。

但真正值得关注的信号藏在另一个决策里：OpenAI 把 API 也关了。

一个 API，即使背后的 consumer app
失败了，仍然可以通过开发者生态产生价值。OpenAI 自己在 text 和 code
领域就是这么运作的——ChatGPT 是流量入口，API
是收入引擎，两件事的生命周期可以完全独立。视频 API
走了不同的路，这里面的原因比 app 失败本身更值得拆解。它指向的是 compute
economics、市场 commoditization 和 GPU
资源分配之间的一组深层矛盾。对于正在使用或计划使用 AI video API
的开发者，以及正在评估这个赛道投资价值的人来说，这个案例的信息密度远高于一条产品下架新闻。

## 视频生成的经济账

先看单位经济。Cantor Fitzgerald 分析师 Deepak Mathivanan 估算，Sora
生成一个 10 秒视频的 compute 成本约 $1.30，每个视频需要约 40 分钟 GPU
time（或 4 块 GPU 并行 8-10 分钟）。SemiAnalysis 的 AJ Kourabi
确认了这个估算（[Forbes](https://www.forbes.com/sites/phoebeliu/2025/11/10/openai-spending-ai-generated-sora-videos/)）。

为什么视频 inference 这么贵？文本生成的核心操作是 token-by-token
的自回归采样，每一步的计算量相对较小。视频生成则需要在高维像素空间中进行多步
diffusion 采样，每一步都涉及完整的 U-Net 或 DiT
前向传播，分辨率和帧数直接乘上去。一个 10 秒 720p 视频的 inference
计算量，大约是一次 GPT-4 级别文本请求的 10 倍以上。

Sora 2 API 的标准定价是 $1/10s 视频，Pro tier $3/10s。标准 tier
每生成一个视频净亏 $0.30 以上，还没算存储、带宽和 safety 审核的
overhead。消费端更夸张：Sora 峰值时日生成约 1130 万条视频，按
$1.30/条计算，日烧钱率达 $1500 万，年化 $54 亿（[Remio](https://www.remio.ai/post/the-real-sora-cost-openai-s-5-billion-ai-video-problem)）。而
Sora 作为独立 app 的累计收入仅 $210 万。成本收入比约 2500:1。

这些数字本身已经很致命，但单独的 unit economics 解释不了 API
的关闭。整个行业的单位经济都好不到哪去：Runway 2024 年收入 $4400
万，EBITDA 亏损 $1.55 亿，亏损率 3.5 倍于收入（[TechCrunch](https://techcrunch.com/2026/02/10/ai-video-startup-runway-raises-315m-at-5-3b-valuation-eyes-more-capable-world-models/)）。全球
VC 在 2025 年向 AI 视频创业公司投入了 $47
亿，而整个行业的实际软件收入还不到 $10 亿（[Crunchbase](https://news.crunchbase.com/venture/gen-ai-video-startup-unicorn-runway-seriese-raise/)）。所有人都在亏钱，问题变成：为什么
OpenAI 选择退出，而其他人选择留下？

## 四个同时作用的力量

**GPU 的机会成本是最根本的约束。** GPU 是 OpenAI
最稀缺的资源。同一批 GPU 跑 Codex，年化收入超 $10 亿；跑 Sora
API，累计收入 $210 万。这里的核心计算是：每一个 GPU-hour
分配给视频生成，都在对 OpenAI 的 text/code
核心业务造成直接的资源挤压。在 OpenAI 2025 年实际收入 $131 亿、2026
年预计亏损 $140 亿的背景下（[CNBC](https://www.cnbc.com/2026/01/19/openai-to-focus-on-practical-adoption-in-2026-says-finance-chief-sarah-friar.html)），把
GPU 从年收入数百亿的产品线上挪走，去维持一个收入可忽略的
API，每一天都在产生实际的机会成本。

**IPO 纪律提供了执行窗口。** OpenAI 正在推进 IPO，CFO
Sarah Friar 把 2026 年定义为 practical adoption 年，重点是
health、science、enterprise。apps head Fidji Simo
在全员会上的说法更直接：We cannot miss this moment because we are
distracted by side quests（[WIRED](https://www.wired.com/story/openai-shuts-down-sora-ipo-ai-superapp/)）。一个亏损的、留存崩塌的、还面临版权诉讼风险的
consumer video 产品，关 app 是止血，关 API 是向投资人传递 focus
信号。

**World model 技术的内部价值远高于外部 API 收入。** Sora
团队没有被解散，领导者 Bill Peebles 留任，方向转为 world simulation
research（[VentureBeat](https://venturebeat.com/technology/openai-is-shutting-down-sora-its-powerful-ai-video-app)）。Sam
Altman 公开确认了 robotics pivot。2026 年 1 月的 arXiv 论文详细描述了
video generation models 向 robotics world models 演进的技术路径（[arXiv](https://arxiv.org/html/2601.07823v1)）。一个粗略的换算：1
分钟 HD 视频的 compute 消耗，大约等于 1000 小时的 robotics
simulation。如果这项技术的终局是为物理世界建模，以 $1
一条的价格和竞品打价格战就成了一种资源错配。

**竞争格局的判断封死了坚守的理由。** Sora 关闭时，它在
Artificial Analysis 的质量排名上已被 Kling 3.0 超过，Runway Gen-4.5 比
Sora 高出 41 Elo。质量差距在收窄甚至逆转，而成本劣势在扩大——Kling 的 API
定价比 Sora 便宜 40-70%。继续投入 API
意味着在一个自己没有成本优势的赛道上，和有政府补贴
compute（Kling）或自研芯片成本优势（Google）的对手打价格战。

这四个力量的权重并不均等。Sora 的市场表现是触发条件，GPU
的机会成本是决定性约束，IPO 提供了执行窗口，world model
内部化确保了技术资产的回收路径。一个更精简的解释也许就够了：Sora
作为产品失败了，API 需求没起来，OpenAI
选择止损。但如果纯粹是产品失败，OpenAI 可以保留 API（成本远低于 consumer
app），减少投入，等市场成熟。选择彻底关闭 API，更合理的解读是 OpenAI
判断视频生成作为独立 API 品类的长期价值有限，尤其当 world model
技术有更高价值的内部用途时。一个佐证：OpenAI 内部已经在开发代号为 Spud
的下一代视频模型，是从零开始的架构重建（[MindStudio](https://www.mindstudio.ai/blog/openai-shutting-down-sora-what-happened-3/)）。关闭
API 避免了在一个即将被内部淘汰的架构上继续承担技术债务和客户承诺。

## 同一个市场，相反的选择

OpenAI 退出的同时，Google、快手和 Runway
留下了。这些相反的决策背后是完全不同的成本函数。

Google 的 Veo 依托 TPU，inference 成本比 Nvidia GPU 低约 80%（[CNBC](https://www.cnbc.com/2025/11/07/googles-decade-long-bet-on-tpus-companys-secret-weapon-in-ai-race.html)）。Midjourney
从 GPU 迁移到 TPU 后 inference 成本降低了 65%，这意味着 Google
的视频生成单位成本可能只有 OpenAI 的 1/3 到 1/5。Veo 的 Fast
模式定价低至 $0.15/秒，在这个价格水平上 Google
仍然可以维持正向单位经济。加上 YouTube 200 亿视频的训练数据、Google
Cloud $151.5 亿的季度收入（同比增长 34%），以及 $3500
亿以上的年总收入基座，Veo 对 Google 是 platform
feature，盈亏都不影响战略逻辑。Veo 在 Google 平台上占据了 96.4% 的 model
share，这是 Sora 从未接近过的垄断地位。

快手的 Kling 走了另一条路。Kling 在 2025 年 12 月的 ARR 达到 $2.4
亿，拥有超过 6000 万创作者（[Yahoo
Finance](https://finance.yahoo.com/news/2-charts-explain-why-openai-just-pulled-the-plug-on-sora-133016441.html)），和 Sora 的 $210
万累计收入之间是两个数量级的差距。成本端，快手有政府补贴 compute 和华为
Ascend 芯片（约 $6900/卡 vs H100 的 $25000-30000）。字节跳动的 Seedance
更极端，API 低至 $0.0247/秒，背后是字节与华为的 40
亿元芯片合同。对这些公司来说，短视频生成是产品线的自然延伸，和 text/code
AI 平台之间几乎没有资源竞争关系。

Runway 的情况最脆弱也最好理解：它是 all-in 视频生成的 pure
play，退出等于公司消失。Runway 2025 年化收入约 $3 亿，2026 年 2 月以 $53
亿估值融了 $3.15 亿。它的赌注是硬件成本下降和模型效率提升会在 2-3 年内让
unit economics 变得可持续。Gen-4.5 在质量排名上领先 Sora 41
Elo，说明纯粹专注一个方向的公司在产品质量上确实可以跑赢分心的巨头。

三种生存逻辑的对比很清晰：Google 靠成本优势（自研芯片），Kling
靠业务协同（视频是核心），Runway 靠 VC 输血和专注度。OpenAI
三者都不具备——租用 Nvidia GPU 成本最高，视频是边缘业务，且 GPU 资源在和
text/code 核心产品竞争。

## 前瞻：这个决策对不对

答案取决于两个变量。

第一个是 video generation
市场最终的规模和利润率。目前的狭义市场预估是 2033 年约 $34 亿（[Fortune
Business Insights](https://www.fortunebusinessinsights.com/ai-video-generator-market-110060)）。即使翻倍到 $70 亿，对一个 2025 年收入已达 $131
亿的 OpenAI
来说，规模不足以成为核心业务。如果考虑影视制作、广告、游戏的渗透率，市场规模突破
$500 亿，那早期退出可能是一个代价很高的判断失误。

第二个是 world model 技术在 robotics 领域的兑现速度。如果 OpenAI 的
robotics 业务在 2028-2030 年间产生显著收入，那么将视频生成的 compute
和研究资源重定向到 robotics 就是正确的选择。反之，如果 robotics
的商业化周期比预期更长（这在 robotics 历史上是常态），OpenAI
就是在一个已经有收入的品类和一个尚无收入的品类之间选择了后者。

我倾向于认为这是一个正确的决策。视频生成正在快速
commoditize，多个模型（Kling、Veo、Runway
Gen-4.5、Seedance）已经在质量上追平或超过 Sora，且成本更低。在一个
commoditize
的市场里，赢家是成本最低的玩家（Google）或和核心业务协同最强的玩家（快手、字节），OpenAI
两者都不是。Spud 的存在说明 OpenAI
保留了重新进入的选项：如果市场证明足够大，可以在更好的架构和更有利的时间点（GPU
成本下降、更高效的模型）重新进入。IPO 窗口的时间价值也很实际——在 2026
年完成 IPO，比带着一个仍然亏损的视频业务在 2028
年上市，对估值的影响可能超过 video generation 市场本身的全部利润。

值得标记的风险是：如果某个竞争对手（最可能是
Google）在视频生成领域建立了类似 ChatGPT 在文本领域的品牌垄断，Spud
再进入时将面临已经固化的用户习惯和开发者生态。Veo 在其平台上 96.4% 的
model share 还不完全等同于跨平台的品牌垄断，但如果 Google 将 Veo
深度整合进 YouTube、Google Workspace
等产品线，形成的分发壁垒会让后来者很难突破。

## 对 AI 从业者意味着什么

如果你的产品依赖了 Sora API，迁移是必须的，目标选项是
Veo（成本最低、平台最大）、Kling（性价比、中国市场覆盖）或
Runway（质量导向、独立平台）。迁移时要注意各家 API
在分辨率、时长、风格控制参数上的差异，这些差异会直接影响产品体验。

如果你在做 AI video 产品，市场格局正在重新划分。OpenAI
的退出消除了一个巨头竞争者，但也意味着这个品类在最大的 AI
平台上失去了入口。开发者生态的重心会向 Google
和中国厂商倾斜。对于独立开发者和小团队来说，选择 API 供应商时 compute
cost
的权重应该高于模型质量，因为质量差距在快速收窄，而成本差距反映的是芯片和基础设施层面的优势，短期内很难逆转。

如果你在评估 AI 投资，这个案例提供了一个关于 unit economics 和
compute allocation 的清晰样本。视频 inference 的成本约是文本的 10
倍，收入却只是零头。对于任何以租用 GPU
为基础的公司来说，视频生成业务在当前的成本曲线下几乎无法独立盈利。值得关注的变量是：芯片成本的下降速度（尤其是
Google TPU 和华为 Ascend 对 Nvidia
的价格压力）、模型效率的改善速度（更少的 diffusion
steps、更好的蒸馏），以及市场规模是否能突破当前预估的上限。

OpenAI 关闭 Sora API 的核心逻辑是 GPU
的机会成本太高：在一个自己没有成本优势的 commoditizing 市场里维持
API，每消耗一个 GPU-hour 都在侵蚀核心业务的收入潜力。IPO
纪律提供了执行窗口，world model 到 robotics
的技术转化路径确保了沉没成本的部分回收。唯一的真正风险在于时间：如果
robotics 的商业化比 video generation 市场的成熟来得更晚，OpenAI
会发现自己把资源从一个可以赚钱的领域移到了一个暂时赚不了钱的领域。从当前证据来看，这个赌注的期望值为正。

---

## 信源索引

- Forbes (Sora unit economics):
  https://www.forbes.com/sites/phoebeliu/2025/11/10/openai-spending-ai-generated-sora-videos/
- Remio (cost analysis):
  https://www.remio.ai/post/the-real-sora-cost-openai-s-5-billion-ai-video-problem
- WIRED (IPO / superapp):
  https://www.wired.com/story/openai-shuts-down-sora-ipo-ai-superapp/
- CNBC (Sarah Friar):
  https://www.cnbc.com/2026/01/19/openai-to-focus-on-practical-adoption-in-2026-says-finance-chief-sarah-friar.html
- Business Insider (compute crunch):
  https://www.businessinsider.com/openai-kills-sora-app-ai-compute-crunch-forces-hard-choices-2026-3
- TechCrunch (Runway):
  https://techcrunch.com/2026/02/10/ai-video-startup-runway-raises-315m-at-5-3b-valuation-eyes-more-capable-world-models/
- VentureBeat (world model pivot):
  https://venturebeat.com/technology/openai-is-shutting-down-sora-its-powerful-ai-video-app
- arXiv (video → robotics): https://arxiv.org/html/2601.07823v1
- BBC (Disney deal):
  https://www.bbc.com/news/articles/c3w3e467ewqo
- Variety (Disney partnership):
  https://variety.com/2026/digital/news/openai-shutting-down-sora-video-disney-1236698277/
- Ars Technica (Disney cancellation):
  https://arstechnica.com/ai/2026/03/the-end-of-sora-also-means-the-end-of-disneys-1-billion-openai-investment/
- MindStudio (Spud codename):
  https://www.mindstudio.ai/blog/openai-shutting-down-sora-what-happened-3/
- CNBC (TPU advantage):
  https://www.cnbc.com/2025/11/07/googles-decade-long-bet-on-tpus-companys-secret-weapon-in-ai-race.html
- Yahoo Finance (market data):
  https://finance.yahoo.com/news/2-charts-explain-why-openai-just-pulled-the-plug-on-sora-133016441.html
- Fortune Business Insights (market size):
  https://www.fortunebusinessinsights.com/ai-video-generator-market-110060
- Crunchbase (VC funding):
  https://news.crunchbase.com/venture/gen-ai-video-startup-unicorn-runway-seriese-raise/
- Forbes (discontinuation):
  https://www.forbes.com/sites/ronschmelzer/2026/03/24/openai-discontinues-ai-video-gen-app-sora/

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
