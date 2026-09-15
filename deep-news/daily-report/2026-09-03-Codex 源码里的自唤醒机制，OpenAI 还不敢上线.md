# [鸭哥 AI 手记] 2026-09-03: Codex 源码里的自唤醒机制，OpenAI 还不敢上线

- **发件人**: "鸭哥" <ya@news.yage.ai>
- **收件时间**: 2026-09-04 13:19:38
- **期号日期**: 2026-09-03
- **Message-ID**: `<lmu3evd75obmhndxw28s6h8d562w0ugh4z2op@kit-mail3.com>`
- **GID**: `qq_mail:INBOX:2565`

---

[鸭哥 AI 手记] 2026-09-03: Codex 源码里的自唤醒机制，OpenAI 还不敢上线

***************************************************
[鸭哥 AI 手记] 2026-09-03: Codex 源码里的自唤醒机制，OpenAI 还不敢上线
***************************************************

懒人包：媒体把 Codex 的后台模式讲成 24/7 永动机，源码模板里写的是每 1 到 3 分钟醒一次的采样循环，而网络请求里这个档位的值还写着 disabled。主动帮忙的时机判断准确率最高只有 64.4%，闹钟和任务单都交给模型还为时过早；另一边 prompt caching 正在搅浑三本 AI 账，智能体 token 名义用量过线人类 5.2 倍、实际账单只差约 2 倍。鸭哥昨天发了 2 篇文章：《改完代码自己定闹钟盯 CI：OpenAI 源码里的自唤醒机制》 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/m2h7h5h34vkme3fluq/aHR0cHM6Ly95YWdlLmFpL3NoYXJlL2NvZGV4LXBlcnNpc3RlbnQtbW9kZS0yMDI2MDkwMy5odG1s ) 用两个问题给所有后台 agent 分了类，给出三条今天就能搬走的后台纪律；《智能体 token 用量过线人类、OpenAI 自研芯片跑分出炉、GitHub 发布文档压缩原型》 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/dpheh0hepvz858tlu4/aHR0cHM6Ly95YWdlLmFpL3NoYXJlL2NhY2hpbmctZGlzY291bnQtdGhyZWUtbGVkZ2Vycy0yMDI2MDkwMy5odG1s ) 拆开名义口径和折扣后口径，给出核对用量、省钱故事与芯片跑分的三句口诀。

-------------
媒体标题与源码注释各说各话
-------------

WIRED 8 月 27 日爆料 OpenAI 正在给 Codex 开发后台模式（WIRED 报道 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/e0hph7h7r69q44c7u2/aHR0cHM6Ly93d3cud2lyZWQuY29tL3N0b3J5L29wZW5haS1pcy1kZXZlbG9waW5nLWEtcGVyc2lzdGVudC1haS1hZ2VudA== )），一圈媒体跟着发文，标题里写满 24/7 和永不停歇。鸭哥没跟着标题走，翻开 openai/codex 开源仓库里 8 月底合入的系统提示模板（开源模板 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/7qh7h8h9nqvwz3s9u6/aHR0cHM6Ly9naXRodWIuY29tL29wZW5haS9jb2RleC9ibG9iL21haW4vY29kZXgtcnMvY29yZS9hc3NldHMvcGVyc2lzdGVudF9tb2RlLm1k )）。模板写的是一个唤醒-检查-休眠的采样循环，核心词是 sampled again：agent 干完活给自己留张便签，记下目标、最近状态、收工条件和下次检查时间，每 1 到 3 分钟醒一次，看一眼没情况就接着睡。更有意思的是，模板虽然合入了开源代码，网络请求里这个档位的值依然写着 disabled，官方目前没有近期上线计划。

后台 agent 其实用两个日常问题就能看明白：闹钟在谁手里，任务单在谁手里。一个管什么时候醒，一个管醒了干什么。平时跑的外部定时脚本按固定逻辑执行，闹钟和任务单都在人手里。人定好闹钟让模型临场发挥，闹钟在人手里、任务单在模型手里。要是模型自己跑完定个延时闹钟、按人写的死规则回头检查，闹钟在模型手里、任务单还在人手里。Codex 的 Persistent mode 独占了第四格：闹钟和任务单第一次都放进模型手里，模型自己决定什么时候醒来复查、醒来后自己决定干什么。

代码写好了却不上线，卡在模型判断力不够。ProAgentBench 论文（ProAgentBench 论文 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/owhkhqhwqp3goxsqur/aHR0cHM6Ly9hcnhpdi5vcmcvaHRtbC8yNjAyLjA0NDgydjE= )）用 28,000 多条真实事件做评测，模型主动帮忙的时机判断准确率最高只有 64.4%，等于三个决定里要错一个。Anthropic 的工程数据（Anthropic 工程博客 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/z2hghnheln9pwnbzu0/aHR0cHM6Ly93d3cuYW50aHJvcGljLmNvbS9lbmdpbmVlcmluZy9jbGF1ZGUtY29kZS1hdXRvLW1vZGU= )）也提到同样的问题：93% 的用户对权限弹窗直接点同意，而自动审查对真实过度行为的漏检率达到 17%。哪怕模板里写着 Persistence does not broaden that scope 这样的权限铁律，一旦放开自唤醒，乱弹窗和过度介入也会直接打扰用户。

这种顾虑前面已经踩过坑。去年 9 月上线的 ChatGPT Pulse 活了九个月，今年 6 月 17 日宣布退役（Pulse 退役 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/p8heh9h4qmkgx6cru3/aHR0cHM6Ly95ZWxsb3cuY29tL25ld3MvY2hhdGdwdC1wdWxzZS1zY2hlZHVsZWQtdGFza3MtaHVi )），退役原因正是抓着旧话题凑数和不合时宜的弹窗。而在 WIRED 报道前一天，OpenAI 刚公布 Hugging Face 入侵事件技术报告（OpenAI 技术报告 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/x0hph6heqo8930ugul/aHR0cHM6Ly9vcGVuYWkuY29tL2luZGV4L2h1Z2dpbmctZmFjZS1pbmNpZGVudC1hbmQtdGhlLXJvYWQtYWhlYWQ= )），那起安全事故的放大器正是一个具备高度 persistent 特性的内部研究模型。自唤醒的时机一旦选错，不仅打扰人，还可能扩大权限漏洞带来的破坏。

鸭哥在 《改完代码自己定闹钟盯 CI：OpenAI 源码里的自唤醒机制》 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/m2h7h5h34vkme3fluq/aHR0cHM6Ly95YWdlLmFpL3NoYXJlL2NvZGV4LXBlcnNpc3RlbnQtbW9kZS0yMDI2MDkwMy5odG1s ) 里用两个问题给所有后台 agent 分了类，提炼出三条今天就能搬走的后台纪律：睡前写 checkpoint 四要素（目标、最近状态、收工条件与检查时间）、无实质变化保持静默、优先复用 cron 和 Webhook 等确定性机制。调度权交不出去是判断力问题，账本看不清是口径问题。另一边关于智能体到底消耗了多少算力，三份热闹数据背后藏着同一个容易忽略的变量。

----------
缓存折扣搅浑了三本账
----------

第一本账是智能体的用量增长。OpenRouter 的统计显示，2026 年 2 月 6 日是人类消耗 token 数量最后一次超过智能体（The Decoder 报道 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/kkhmh6hnxrg6m0sku7/aHR0cHM6Ly90aGUtZGVjb2Rlci5jb20vYWktaXMtYmVjb21pbmctYWlzLWJpZ2dlc3QtY3VzdG9tZXItYXMtYWdlbnRpYy10b2tlbi11c2FnZS1qdW1wcy0xNHgtb24tb3BlbnJvdXRlcg== )）。截至 8 月 10 日的七天均值，智能体每周消耗 7.3 万亿 token，人类只有 1.4 万亿，名义用量达到 5.2 倍。很多解读据此高呼智能体全面接管，却漏算了缓存折扣。智能体消耗的 token 里有七成到八成五是缓存读取，主流厂商对缓存读取只收约一折，实际产生的账单差距只有约 2 倍。此外 OpenRouter 自称只占全球推理量约 1%，单一应用 Hermes Agent 一周就吃掉 1.5 万亿 token，占了平台智能体用量的两成，直接拿来外推全行业难免失真。

第二本账是文档压缩原型到底能省多少钱。GitHub Next 推出原型 Knowledge Compressor（GitHub Next 原型 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/58hvh7hg6qpk7ra7u4/aHR0cHM6Ly9naXRodWJuZXh0LmNvbS9wb3N0cy9rbm93bGVkZ2UtY29tcHJlc3Nvcg== )），把一份合成文档从 996 个 token 压到 480 个，单次压缩成本约 2 美元，号称在未缓存读取下复用约 2,000 次就能回本。然而现实中的长文档极少次次走全价读取。

主流模型厂商的缓存读取普遍趋同一折：OpenAI GPT-5 Mini 输入每百万 token 标价 $0.25、缓存读取只需 $0.025；Anthropic 缓存读取按 0.1x 计价；Gemini 读取同样趋同一折但按小时另收存储费；DeepSeek 命中与未命中的比价约 3%。只要把真实的缓存命中率算进来，回本门槛就会拉长到 3,640 到 20,000 次，中位预期在 5,000 次以上。面对 10K token 的日常文档，跑一次压缩的起步成本就要约 45 美元。

第三本账是芯片跑分与真实负载的落差。OpenAI 公布了自研芯片 Jalapeño 的测试成绩（OpenAI 跑分 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/25h2hoh3m6r4dmc8u4/aHR0cHM6Ly9vcGVuYWkuY29tL2luZGV4L2phbGFwZW5vLWZpcnN0LXJlc3VsdHM= )），每瓦吞吐达到 Nvidia GB200 和 GB300 的 1.5 到 1.9 倍，端到端延迟快 1.7 到 3.6 倍。成绩看起来亮眼，但全部出自 8k/1k 固定长度的单轮测试，没有跑 SemiAnalysis 的 AgentX 真实 agent 负载（SemiAnalysis 分析 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/qvh8h7hdkzgonlaguk/aHR0cHM6Ly9uZXdzbGV0dGVyLnNlbWlhbmFseXNpcy5jb20vcC9hZ2VudHgtaW5mZXJlbmNleHYzLWRvZXMtY3VkYS1tb2F0 )）。真实的多轮交互全是长上下文和高前缀复用，8k/1k 的成绩再高，也回答不了多轮长会话下的表现。

鸭哥 6 月写过 《前缀缓存：智能体成本杠杆》 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/g3hnh5hmqr76p2f3u9/aHR0cHM6Ly95YWdlLmFpL3NoYXJlL3ByZWZpeC1jYWNoZS1hZ2VudC1jb3N0LWxldmVyLTIwMjYwNjI1Lmh0bWw= ) 一文。昨天这篇文章 《智能体 token 用量过线人类、OpenAI 自研芯片跑分出炉、GitHub 发布文档压缩原型》 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/dpheh0hepvz858tlu4/aHR0cHM6Ly95YWdlLmFpL3NoYXJlL2NhY2hpbmctZGlzY291bnQtdGhyZWUtbGVkZ2Vycy0yMDI2MDkwMy5odG1s ) 把这三本账从头算了一遍，总结了三句实用口诀：引用 token 用量先问缓存占比，听省钱故事先问按全价还是折扣价算，看芯片跑分先问负载口径。

-----
也值得知道
-----

Broadcom 财报给 Jalapeño 补了成本侧数字：9 月 2 日盘后财报显示，Broadcom 季度 AI 半导体收入达到 167 亿美元，同比翻了三倍。CEO Hock Tan 透露 OpenAI 自研芯片 Jalapeño 本季开始出货，推理表现超过 Grace Blackwell、单瓦性能达到约 1.9 倍，OpenAI 还计划在 2027 年部署 1.3 GW 算力规模（CRN 报道 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/9qhzhnhd50kz97hzu3/aHR0cHM6Ly93d3cuY3JuLmNvbS9uZXdzL2FpLzIwMjYvYnJvYWRjb20tcTMtY2VvLXRhbi1mb3JlY2FzdHMtc3VyZ2luZy1haS1pbmZyYXN0cnVjdHVyZS1idWlsZG91dA== )）。

OpenAI 发布 GPT-6 Astra：OpenAI 9 月 3 日分阶段推出新模型 GPT-6 Astra，自称最智能且最对齐。这是首个触发内部 Critical 网络安全阈值的模型，先进网络能力目前先开放给 Daybreak 网络防御项目参与企业（CNBC 报道 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/3ohphkh3p064v6hpun/aHR0cHM6Ly93d3cuY25iYy5jb20vMjAyNi8wOS8wMy9vcGVuLWFpLWFzdHJhLWdwdC02LWN5YmVyLmh0bWw= )）。

阿布扎比 IFM 发布 K2 Horizon 全开源模型家族：阿布扎比 IFM 9 月 3 日放出 6 个模型，参数量从 0.9B 到 375B。团队把模型权重、训练数据、代码与训练方法全部开源，允许社区完整复现训练过程（路透社报道 ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/n2hohvhv7mw6e8b0ug/aHR0cHM6Ly93d3cucmV1dGVycy5jb20vd29ybGQvbWlkZGxlLWVhc3QvYWJ1LWRoYWJpLWFpLWluc3RpdHV0ZS1yZWxlYXNlcy1mdWxseS1vcGVuLXNvdXJjZS1tb2RlbHMtd2l0aC10cmFpbmluZy1kYXRhLWNvZGUtMjAyNi0wOS0wMw== )）。

本期由 AI 基于鸭哥已发布文章和公开资料整理生成，请注意甄别幻觉。

订阅本 newsletter：daily.yage.ai ( https://0128b587.click.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op/48hvhehmxvz6kpaqu7/aHR0cHM6Ly9kYWlseS55YWdlLmFpLw== )

Unsubscribe ( https://0128b587.unsubscribe.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op ) | Update your profile ( https://preferences.kit-mail3.com/lmu3evd75obmhndxw28s6h8d562w0ugh4z2op )
