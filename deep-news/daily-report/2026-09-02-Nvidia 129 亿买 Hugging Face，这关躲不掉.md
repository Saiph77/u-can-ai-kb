# [鸭哥 AI 手记] 2026-09-02: Nvidia 129 亿买 Hugging Face，这关躲不掉

- **发件人**: "鸭哥" <ya@news.yage.ai>
- **收件时间**: 2026-09-03 13:22:47
- **期号日期**: 2026-09-02
- **Message-ID**: `<wvu620qxp7bghklegxpi7hnegkqgrs8h29wog@kit-mail3.com>`
- **GID**: `qq_mail:INBOX:2560`

---

[鸭哥 AI 手记] 2026-09-02: Nvidia 129 亿买 Hugging Face，这关躲不掉

*******************************************************
[鸭哥 AI 手记] 2026-09-02: Nvidia 129 亿买 Hugging Face，这关躲不掉
*******************************************************

懒人包：Nvidia 用 129 亿美元、86 倍 ARR 的价格买下开发者默认入口 Hugging Face，绕了两年的申报这次绕不过去（9 月 2 日已官宣）。一行每天在全球终端执行数百万次的 from_pretrained() 撑起 86 倍 ARR 的定价，买的是入口惯性；另一边 fal 把视频生成压进播放时长，每小时 144 到 288 美元的运营硬账让能跑通的业务极窄。鸭哥昨天发了 2 篇文章：《绕过270亿美元后，Nvidia为什么必须在Hugging Face身上硬闯反垄断》 ( https://0128b587.click.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog/p8heh9h4qr5ddruru3/aHR0cHM6Ly95YWdlLmFpL3NoYXJlL252aWRpYS1oZi1hbnRpdHJ1c3QtMjAyNjA5MDIuaHRtbA== ) 拆了 86 倍 ARR 背后的入口价值、规避失效与 builder 防御三步；《观众开始给画面写剧本：实时生成内容的新成本账》 ( https://0128b587.click.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog/x0hph6heqkdzzohgul/aHR0cHM6Ly95YWdlLmFpL3NoYXJlL3JlYWx0aW1lLXZpZGVvLWNvc3QtbGVkZ2VyLTIwMjYwOTAyLmh0bWw= ) 算清了按小时计费的视频流账本与平台准入门槛。

------------
129 亿买的是入口惯性
------------

8 月 26 日深夜，The Information 挂出独家报道（The Information 独家 ( https://0128b587.click.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog/6qheh8hl9x6wwrh9uk/aHR0cHM6Ly93d3cudGhlaW5mb3JtYXRpb24uY29tL2FydGljbGVzL252aWRpYS1hZ3JlZXMtYnV5LW9wZW4tc291cmNlLW1vZGVsLXJlcG9zaXRvcnktaHVnZ2luZy1mYWNlLTEyLTktYmlsbGlvbg== )；CNBC 第二信源 ( https://0128b587.click.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog/e0hph7h7rmweeob7u2/aHR0cHM6Ly93d3cuY25iYy5jb20vMjAyNi8wOC8yNy9udmlkaWEtaHVnZ2luZy1mYWNlLWFjcXVpc2l0aW9uLmh0bWw= )）：Nvidia 拟以 129 亿美元收购 Hugging Face。9 月 2 日 Nvidia 正式提交 SEC 8-K 文件（SEC 8-K ( https://0128b587.click.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog/7qh7h8h9ndp887c9u6/aHR0cHM6Ly93d3cuc2VjLmdvdi9BcmNoaXZlcy9lZGdhci9kYXRhLzEwNDU4MTAvMDAwMTA0NTgxMDI2MDAwMDc4L252ZGEtMjAyNjA5MDIuaHRt )；Nvidia 官方博客 ( https://0128b587.click.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog/owhkhqhwqxlnnmsqur/aHR0cHM6Ly9ibG9ncy5udmlkaWEuY29tL2Jsb2cvbnZpZGlhLXRvLWFjcXVpcmUtaHVnZ2luZy1mYWNlLw== )），官宣达成收购协议。交易结构为 119 亿美元股东对价加最高 10 亿美元员工 retention，合计 129.3 亿美元，预计 2027 上半年交割，仍需监管批准。Nvidia 在公告里承诺平台保持开放，不要求使用 Nvidia 算力。

Hugging Face 年收入约 1.5 亿美元，只占 Nvidia 数据中心收入的 0.04%，约等于 Nvidia 3.5 小时的营业收入，估值给到了 86 倍 ARR。平台上两百多万个开源模型权重谁都能免费拉走，这笔钱买的是那行每天在全球终端执行数百万次的 from_pretrained()，以及它背后 1300 万开发者的肌肉记忆和行为遥测。

过去两年，巨头靠非典型交易绕开申报已经成了惯用套路。微软出资 6.2 亿美元买授权加招走 70 人；Nvidia 约 200 亿美元拿下 Groq 技术授权；另一笔交易用 60 亿美元授权加 10 亿美元入股带走 109 人。三笔交易合计约 270 亿美元，全因 1976 年制定的申报清单只盯股权和资产转移。把收购写成 license，申报义务就消失了。黄仁勋曾在内部邮件直言："We are not buying Groq, we are just licensing"。

但这套规避手法在 Hugging Face 身上失效了。平台的价值绑在实体、企业合同与搜索流量上，无法抽离，只能正面触发反垄断申报。这直接对标 2021 年 FTC 起诉阻止 Nvidia 400 亿美元收购 Arm 的先例（FTC 起诉 Arm 先例 ( https://0128b587.click.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog/z2hghnhel5r77qczu0/aHR0cHM6Ly93d3cuZnRjLmdvdi9uZXdzLWV2ZW50cy9uZXdzL3ByZXNzLXJlbGVhc2VzLzIwMjEvMTIvZnRjLXN1ZXMtYmxvY2stNDAtYmlsbGlvbi1zZW1pY29uZHVjdG9yLWNoaXAtbWVyZ2Vy )）。买下入口的那一刻，中立性信任就开始倒计时，三种监管走向决定这笔钱最终去向。HN 上 1970 分的讨论帖里批评声居多，也有人号召迁移，但智谱 GLM-5.3 依然在 Hugging Face 首发，也没有企业客户解约，言行反差印证了入口惯性的强度。

鸭哥昨天在 《绕过270亿美元后，Nvidia为什么必须在Hugging Face身上硬闯反垄断》 ( https://0128b587.click.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog/p8heh9h4qr5ddruru3/aHR0cHM6Ly95YWdlLmFpL3NoYXJlL252aWRpYS1oZi1hbnRpdHJ1c3QtMjAyNjA5MDIuaHRtbA== ) 里拆了 builder 防御的三步实操：用 HF_ENDPOINT 环境变量把模型下载源从业务代码里解耦；给关键管线建权重冷备；把 Optimum-AMD 和 Optimum-Intel 的维护节奏当中立性风向标，一旦停滞就是最早的退化信号。Nvidia 这笔是 129 亿一次付清买入口的战略账，而另一边，视频生成开始按小时算运营账了。

---------------
画面跟着观众变，成本按小时硬算
---------------

8 月 31 日上线的内容平台 fal.live（fal.live ( https://0128b587.click.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog/p8heh9h4qr5ddqbru3/aHR0cHM6Ly9mYWwubGl2ZQ== )）上，观众在聊天框敲一句 prompt，几秒后画面真的换了剧情。fal 拿 MiniMax 开源的 H3 做后训练，搞出提速版 H3 Max（fal 模型页 ( https://0128b587.click.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog/6qheh8hl9x6ww4a9uk/aHR0cHM6Ly9mYWwuYWkvbW9kZWxzL21pbmltYXgtaDMtbWF4L2ltYWdlLXRvLXZpZGVv )），把单段视频的生成时间压到了播放时长以下。

但账本逻辑在这里反转了。传统视频做完后，分发边际成本接近零；实时视频流多播一小时，后台就多硬算一小时。按 768p 分辨率折算，每小时生成成本落在 144 到 288 美元区间。对比数字人每小时约 12 美元的水平（Runway API 文档 ( https://0128b587.click.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog/kkhmh6hnxz2ee7bku7/aHR0cHM6Ly9kb2NzLmRldi5ydW53YXltbC5jb20vZ3VpZGVzL3ByaWNpbmc= )），实时视频流的开销是前者的 12 到 24 倍。

速度数字先要打个折。快于实时目前只在短片段里勉强成立，15 秒片段的生成时间已经压平了裕量，端到端延迟没有任何公开口径，跨片段的人物与场景一致性也还没有解决。fal 目前处理违规内容的方式是直接把画面切成全黑，在直播里等于直接断流。

按毛利厚度，业务形态分成三档：一条流大家看（秀场直播打平线约需 1,400 到 2,900 并发观众）、分支流分群（互动短剧），以及高意向节点触发（单次 15 秒成本约 0.6 到 1.2 美元，用于广告、电商或客服）。

鸭哥昨天在 《观众开始给画面写剧本：实时生成内容的新成本账》 ( https://0128b587.click.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog/x0hph6heqkdzzohgul/aHR0cHM6Ly95YWdlLmFpL3NoYXJlL3JlYWx0aW1lLXZpZGVvLWNvc3QtbGVkZ2VyLTIwMjYwOTAyLmh0bWw= ) 里算了这套账：审核延迟和成本都能塞进当前的生成窗口，真正的落地门槛不在审核技术，在法律责任归属与平台准入，推进节奏也会按美国、欧盟、中国的顺序依次展开。

-----
也值得知道
-----

观众驱动 AI 直播遭平台封禁：工程师 Rehan Sheikh 用 H3 Max 搭了观众敲 prompt 控剧情的直播，在 X 累计近 530 万次浏览，随后相继遭遇 Twitch 封禁与 Kick 下架，最终转往 Rumble。这正好印证了文章二的判断：阻碍落地的门槛不在审核技术，在平台准入（biggo 报道 ( https://0128b587.click.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog/58hvh7hg63o0opc7u4/aHR0cHM6Ly9maW5hbmNlLmJpZ2dvLmNvbS9uZXdzLzg2NDQzZmQwLTc2ZjEtNGY5Zi1hNWQ0LTM1MmQ2OTNiMWY4Ng== )）。

Anthropic 与 Lambda 签下 350 亿美元云协议：据 WSJ 报道，Anthropic 与 Lambda 签署为期六年、总额 350 亿美元的算力协议，算力部署在德州 Hut 8 园区。Nvidia 在这笔交易中身兼算力供应商、Lambda 股东和容量协议方三重角色，和上一篇里 Nvidia 的生态扩张是同一个方向（Investing.com 转述 ( https://0128b587.click.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog/25h2hoh3ml0g0va8u4/aHR0cHM6Ly93d3cuaW52ZXN0aW5nLmNvbS9uZXdzL3N0b2NrLW1hcmtldC1uZXdzL2FudGhyb3BpYy1zaWducy0zNS1iaWxsaW9uLWNsb3VkLWRlYWwtd2l0aC1udmlkaWFiYWNrZWQtbGFtYmRhLXdzai1yZXBvcnRzLTkzQ0gtNDg4MzM4MQ== )）。

Anthropic 发布 Claude Fable 与 Mythos 5.1：Anthropic 推出面向 agentic 场景的新模型，调用成本最高降幅达 45%，同时收窄 safeguard 规则回应企业客户批评（The Verge 报道 ( https://0128b587.click.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog/qvh8h7hdke2v24uguk/aHR0cHM6Ly93d3cudGhldmVyZ2UuY29tL2FpLWFydGlmaWNpYWwtaW50ZWxsaWdlbmNlLzk4NzgzMC9hbnRocm9waWMtY2xhdWRlLWZhYmxlLW15dGhvcy01LTE= )）。

本期由 AI 基于鸭哥已发布文章和公开资料整理生成，请注意甄别幻觉。

订阅本 newsletter：daily.yage.ai ( https://0128b587.click.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog/g3hnh5hmqgononf3u9/aHR0cHM6Ly9kYWlseS55YWdlLmFpLw== )

Unsubscribe ( https://0128b587.unsubscribe.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog ) | Update your profile ( https://preferences.kit-mail3.com/wvu620qxp7bghklegxpi7hnegkqgrs8h29wog )

---

## 相关深度长文（本地归档）

- [绕过270亿美元后，Nvidia为什么必须在Hugging Face身上硬闯反垄断](../articles/nvidia-hf-antitrust-20260902.md)（[yage.ai 原文](https://yage.ai/share/nvidia-hf-antitrust-20260902.html)）
- [观众开始给画面写剧本：实时生成内容的新成本账](../articles/realtime-video-cost-ledger-20260902.md)（[yage.ai 原文](https://yage.ai/share/realtime-video-cost-ledger-20260902.html)）
