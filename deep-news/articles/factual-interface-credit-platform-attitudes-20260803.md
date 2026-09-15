---
title: "界面承诺决定平台态度：从 Google Earth 事件看 AI\n内容治理"
date: 2026-08-03
source: https://yage.ai/share/factual-interface-credit-platform-attitudes-20260803.html
slug: factual-interface-credit-platform-attitudes-20260803
lang: zh
---
# 界面承诺决定平台态度：从 Google Earth 事件看 AI 内容治理

发布于 2026 年 8 月 3 日 · [查看原网页](https://yage.ai/share/factual-interface-credit-platform-attitudes-20260803.html)

## 记录界面里出现了一个生成按钮

2026 年 7 月 30 日，Google 在网页版 `Google Earth`
里放进了一个新的生成按钮，背后用的是自家的图像生成模型
`Nano Banana 2`。Google 当时的想法其实挺直白：他们想把 Google
Earth
从一个单纯查卫星图的数据库，变成一个能帮你做假设推演的互动工具。比如做城市规划、模拟气候灾害，或者地理教学，你只要把地图拉到任何一个地方（这是真实的卫星画面输入），再敲进一句提示词（比如模拟暴雨淹没后的街区），就能在真实的卫星底图上直接合成出一张逼真的假想图（这是输出）。

不过这个功能上线才刚刚一天，Google 就紧急把它撤了下来。Google 在[官方声明](https://blog.google/products-and-platforms/products/earth/nano-banana-google-earth-image-generation)里直接说明了原因：「我们深知大家对
Google Earth
抱有独特的信任，把它当作观察真实世界的可靠窗口……但我们也看到，有人在社交平台上分享了一些生成的截图，看起来违反了我们的政策。在准备好更严格的防御措施之前，我们决定先撤回这个功能……这些生成的图片此前并没有直接呈现在其他人的主界面里，而且图片上也带上了
AI 生成的水印。」

读到这里，你可能会产生一个很自然的疑问：既然 Google
在声明里强调图片上有 AI
水印，而且这些生成结果并没有直接替换掉其他人屏幕上的真实地图，那大家为什么还会把它们当成现实中发生的事情？

关键就在于图片离开界面后的传播场景。用户在 Google Earth
网页里生成假想图后，随手就会截个图，发到 X（Twitter）、Reddit
或者微信群里。一旦图像脱离了 Google Earth
原生界面的约束，那些边角上的轻量 AI
标注或隐形水印在社交平台上就基本失效了：普通网友刷社交媒体时，压根不会拿专门的技术工具去扫水印，大家眼里看到的，就是一张带着
Google Earth 标志性视角和真实地形的卫星截图。

上线当晚，开源情报分析师 Henk van Ess
跑去试了一下，发现安全拦截很容易被绕过去。他一口气生成了洛杉矶不存在的弹坑、被水淹没的国会大厦、着火的
Googleplex、倒塌的埃菲尔铁塔、伊朗核电站，还有加沙医院被炸毁的画面（据
[Ars
Technica
报道](https://arstechnica.com/ai/2026/07/google-earth-releases-swiftly-retracts-ai-feature-to-make-fake-satellite-images)）。当这些截图被传到社交平台后，受众顺着过去的习惯，第一反应依然是这是从
Google Earth 上截下来的真实卫星图。van Ess 在接受 [BBC
采访](https://www.bbc.com/news/articles/c9349yx2ydvo)时讲的那句话，正好点破了这个玄机：「伪造图本身不需要看起来天衣无缝，它直接继承了诞生它的那张地图的信誉。」

这句话道出了界面设计里一个很容易被忽略的细节。过去二十年来，记者、情报分析人员和救援团队都习惯拿
`Google Earth`
当作核对现实的底牌。大家在这个界面里看图时，压根不会去怀疑图片的真假，就像你在
Google
导航上看到一条路，不会怀疑那条路根本不存在一样。当生成按钮直接嵌进这个界面时，地图给人的感觉还是客观记录，但输出的内容却已经变成了算法模拟。大家顺着过去的习惯去看图，就把合成画面当成了现实证据，期待和界面的实际属性就这么错开了。

[TechPolicy.Press
的评论](https://www.techpolicy.press/google-earth-ai-fiasco-underscores-why-tech-firms-must-listen-to-outside-experts)对这件事的总结也很传神：「Google Earth
不再只是对现实的记录，它变成了一个能够制造逼真现实的生成器，把大家最信任的现实基础设施与生成式
AI 之间的边界给抹平了。」

*信用比来源证明传播得更远：事实界面的信用随导出物传播，provenance 信号在离开界面后衰减*

信用比来源证明传播得更远：事实界面的信用随导出物传播，provenance
信号在离开界面后衰减

## 信用比来源证明传播得更远

Google Earth
事件暴露了一个很现实的问题：当生成图通过截图流向社交网络，光凭这是从权威界面截出来的这一视觉印象，就足够让不少人把假图当成真新闻了。那么，后续靠技术手段去查验这些图片的真伪，到底可不可行？

图片一旦离开了原生界面被到处转发，查清来源往往就很费劲了。2026 年 3
月 8 日，伊朗媒体 `Tehran Times` 在 X
上发了一组前后对比的卫星图，声称巴林的美军基地雷达被炸毁了。新闻核查团队
BBC Verify
随后拿这张图做了调查。如果只靠肉眼看，图片其实有很低级的漏洞，比如基地外面停着的几辆小车，在号称隔了一整年的两张卫星图里，停的位置居然分毫不差。

不过肉眼看到的破绽只是疑点，真正拿出过硬技术物证的，是 BBC Verify
调用的 `Google SynthID watermark detector`（SynthID
检测器）。SynthID 是 Google 搞的一种像素级隐形水印，只要是用 Gemini 或者
Google 的 AI
工具做出来的图，像素底层都会静默打上这种标记，一般的剪裁、打码或微调都不容易把它洗掉。检测器直接从像素底层证实了这张所谓的战时卫星图，确实是用
Google 的 AI 工具伪造或者修改出来的（详见 [BBC Verify
报道](https://www.bbc.com/news/articles/ckg8wvz427vo)）。

这是第一个被 SynthID
在技术层面实锤的战时虚假信息案例，说明靠水印追溯在技术上确实行得通。但问题在于，这种追溯非常依赖有人主动拿着工具去查，而且前提是图片在各个平台转发的过程中，水印信号还没被折腾掉。

现实中的传播链条可没这么理想。比如行业里推行的 `C2PA`
标准，这是由 Adobe、微软等公司联合发起的开源内容凭证协议（Content
Credentials）。它的做法是在图片或视频文件里插入加密数字签名，记录下这张图是用什么
AI
工具做的、经过了哪些修改。但这种方案有个致命弱点：签名是藏在文件的元数据里的。只要用户一截图，或者把原图传到
Facebook、Instagram、X 或 WhatsApp
上，社交平台为了省带宽做压缩转码，就会顺手把文件里的元数据全抹掉。这倒不是平台故意要帮伪造者遮掩，纯粹是网络分发转码时的附带伤害（详见
[SoftwareSeni
技术分析](https://www.softwareseni.com/durable-content-credentials-how-provenance-survives-metadata-stripping)）。直接埋在像素里的 `SynthID`
确实不怕普通截屏，但它既看不见，又绑定了 Google 自己的私有算法，Google
的检测器认不出 OpenAI 的水印，反过来也一样（据 [Ars
Technica 实测](https://arstechnica.com/ai/2026/07/tested-google-synthid-works-great-but-labeling-ai-content-may-be-a-losing-game)）。甚至网上早就有了免费的抹除工具（比如 [removesynthid.io](https://removesynthid.io)）和各种[破解教程](https://github.com/wiltodelta/remove-ai-watermarks/blob/main/docs/synthid.md)。开发者
Sean Goedecke 就直言，如果大家不都把签名用起来，C2PA
就更容易变成表面功夫。比如 FotoForensics
网站每周收到几万张图，里面带有效签名的往往只有十几张（见 [Sean
Goedecke 的分析](https://www.seangoedecke.com/c2pa-only-works-if-everything-is-signed)）。

这就造成了一种很无奈的落差，就像大家常说的“造谣一张嘴，辟谣跑断腿”：大平台和权威界面带给人的信任感可以跟着截图到处传，但证明这张图是
AI 做的标记，却在转发过程中一路流失。`Google Earth`
用二十年攒下的权威信用，被一张导出的截图轻易带走了，而要证明它是假的，却得靠专业的检测工具和繁琐的核验流程才能看出来。

BBC Verify 的测试也证实了这一点：`SynthID` 在 Google
自家的 Gemini 和 Lens
里识别率确实不错，但依然有办法绕过去；如果遇到稍微调过色或处理过的图片，第三方的检测工具经常直接失灵（详见
[BBC
测试结果](https://www.bbc.com/news/articles/c9349yx2ydvo)）。这种困境光靠把水印算法做得更厉害是很难解决的，因为信任在人际网络里的传播速度，本来就比技术验证流失的速度快得多。

*三种态度由界面承诺与商业激励共同决定：禁止、标注/降权、拥抱*

三种态度由界面承诺与商业激励共同决定：禁止、标注/降权、拥抱

## 界面承诺是首要因子

既然水印和技术标记在跨平台传播时必然会流失，平台显然就不能把希望全都寄托在事后验证上。在
2024 到 2026 年这几年间，全球主要的互联网平台在面对 AI
生成内容时，逐步演化出了三种截然不同的治理态度：直接封杀、打上标签，以及全面拥抱。有趣的是，平台选哪条路，可不是随机拍脑门定的。

把 `Wikipedia` 和 `Snapchat`
放在一起对比，这种差别就特别明显。2026 年 3 月 20
日，`Wikipedia` 的编辑社区以 44 对 2
的压倒性票数，决定严禁用大语言模型来生成或改写百科条目，只留了翻译和微调错别字这两个小开口（详见
[Quartz
报道](https://qz.com/wikipedia-editors-ban-ai-generated-articles) 与 [AI
Automation 政策解读](https://aiautomationglobal.com/blog/wikipedia-bans-ai-generated-content-policy-2026)）。社区最担心的就是 AI
弄乱了每句话都要有明确作者和可靠来源的铁律，还可能让互联网充斥 AI
自己抄自己的垃圾。但同一时间的 `Snapchat`
完全是另一个画风，他们在 2025 年底把 Imagine Lens 滤镜免费放给了 3.5
亿日活用户，AI 滤镜播放量刷到了 380 亿次，2026 年更是顺势推出了全套 AI
广告生成工具（见 [Snapchat
官方公告](https://forbusiness.snapchat.com/blog/human-first-ai-enabled-snaps-latest-ads-innovations)）。

两个平台之所以选了截然相反的方向，根子在于它们平时给用户做出的承诺不一样。维基百科给人的承诺是可核查的严肃事实档案，每句话都要有人负责；而
Snapchat 给人的预期就是朋友间找乐子的 AR 滤镜。在维基百科里塞进 AI
生成，等于直接砸了自己的招牌；但在 Snapchat
里，搞怪和好玩本来就是产品的一部分，大家看到恶搞滤镜根本不会当真。

`Google Earth`
之前那次踩坑，也是撞在了这根线上。作为大家查地理和地图的基准工具，它背负着极高的事实记录属性。直接在地图主界面里安一个生成按钮，等于在承诺没变的情况下，悄悄把给用户看的东西从事实变成了算法模拟。如果当时把它做成一个独立的虚拟沙盒模式，加上醒目的状态提示和原图对比，大家的反应绝不会这么大。

连同一家大厂内部，不同产品的策略也是大相径庭的：Google 在
`Google Earth` 上发现不对立刻撤回，但在 Gemini
对话界面里大力推广生成；Meta 在 Facebook
社区里严查政治敏感生成图，但在自己的设计软件 Meta Imagine
里却鼓励大家随便画；`LinkedIn` 之前还兴冲冲地推出了 AI
帮你写文章的功能，到了 2026 年 7 月 31
日又赶紧把这个功能关了，反而上线了一个怀疑是 AI
垃圾内容的举报按钮。决定平台政策的不是大厂口头上的价值观，而是具体产品和用户之间那份看不见的信任约定。

## 三种态度的深层困境与治理外包

如果我们顺着界面承诺的视角深入看下去，就会发现封杀、打标、拥抱这三条路径背后，各自对应着非常具体的现实困境与治理逻辑。

对于那些一旦出错后果极严重的领域，大家最普遍的防线就是直接一刀切。`BBC`
在内部测试里发现 AI 助手做新闻有 45%
的概率会捏造或弄错事实，于是干脆严禁在新闻采编出版里直接用生成工具（见
[Media Copilot
分析](https://mediacopilot.ai/newsroom-ai-strategies)）。像
`Elsevier`、`Springer Nature`、`Wiley`、`Science`
和 `Cell` 这些顶级学术期刊，也全都拒绝把 AI
当成论文作者，而且绝大多数都不允许提交 AI 做出来的实验图片（见 [学术出版政策汇总](https://www.thesify.ai/blog/ai-policies-academic-publishing-2026)）。音乐平台
`Bandcamp` 和 `Qobuz` 也一样，坚决不收纯 AI
生成的歌曲。这些地方的共同点就是：一旦假内容混进去了，事后澄清和收回的成本太高了。

至于靠打上 AI
生成标签让大家自己去辨别，实际效果其实挺尴尬的。多伦多都市大学 The Dais
找了 2472
个人做实验，发现平时大家见到的那些小标签，对大家信不信或者转不转发几乎没影响，只有那种挡住整张屏幕的强弹窗警告才管用（见
[The Dais
实验分析](https://kompozy.io/guides/tiktok-ai-labeling-at-scale)）。MIT 做了 7500 多人的实验也发现，光贴一个中性的 AI
生成标签，远不如直接标上虚假内容来得管用，有时候漏标了反而会让没贴标的内容看起来更像真的（见
[MIT
实验报告](https://mit-genai.pubpub.org/pub/hu71se89)）。平台自己心里也有数，知道光打标只是应付合规，所以大家现在基本都是打标加控钱与算法组合拳：`Tidal`
给 AI 歌曲贴标签的同时，直接把它们的版税收益给清零了（据 [Variety
报道](https://variety.com/2026/music/news/tidal-label-ai-generated-music-ban-royalties-from-ai-songs-1236798543)）；`TikTok` 水印、元数据和用户自报三管齐下，标了 30
多亿条视频（见 [TikTok
治理数据](https://kompozy.io/guides/tiktok-ai-labeling-at-scale)）；`LinkedIn`
则是一边放开举报入口，一边用算法自动降权，一天就能拦截几十万次机器人灌水（据
[Fortune
报道](https://fortune.com/2026/07/31/linkedin-seems-like-ai-slop-button-billions-automated-comments-attempts)）。

那些选择全面拥抱 AI
的平台，说白了是把鉴别的责任交给了用户或者市场自己。像
`Adobe Firefly` 推出创意助手（见 [Adobe
发布说明](https://news.adobe.com/news/2026/04/adobe-new-creative-agent)），`Canva` 靠 Magic Studio 卖到了 40
亿美元年收入，`Notion` 把 AI
当成主打卖点，因为大家用这些工具本来就是为了干活和搞创意，没人觉得里面的输出是严肃的现实依据。`Epic Games Store`
坚持不强制要求标注 AI 游戏资产，CEO Tim Sweeney 还吐槽 Steam
强迫开发商披露做法太苛刻（据 [VGC
报道](https://www.videogameschronicle.com/news/epic-games-ceo-says-its-really-irresponsible-of-steam-to-make-studios-disclose-ai-use)）。但 Steam 的公开数据显示，带有 AI 标签的游戏平均评论数少了
53%，说明玩家心里其实非常介意，不打标只是把风险留给了买游戏的玩家。

大家之所以这么头疼，根本原因在于 AI
生产太快，而人工审查根本跟不上。Starling Lab 算过一笔账：人类用了 149
年才拍出了 15 亿张照片，而生成式 AI 只要 18 个月就画出了同样多的图（见
[Starling
Lab 数据分析](https://arstechnica.com/ai/2026/07/tested-google-synthid-works-great-but-labeling-ai-content-may-be-a-losing-game)）。`LinkedIn` 每天拦截的自动化灌水，比
Facebook 过去一个月封的账号还要多（据 [MediaPost
报道](https://www.mediapost.com/publications/article/416924/linkedin-reverses-approach-to-ai-generated-content.html)）。虽然有半数 Z 世代用户说看到 AI
垃圾内容就想取关，但社交平台上依然有成千上万的推文在靠自动化农场维持热度（见
[Value
Add VC 报告](https://valueaddvc.com/blog/ai-generated-content-and-social-media-how-platforms-are-handling-the-flood)）。过去 Web2
靠封几个账号就能搞定审核的旧办法，在脱离真实身份的批量生产面前已经不管用了。

况且政策也在一步步逼近。2026 年 8 月 2 日，[EU
AI Act 第 50 条](https://artificialintelligenceact.eu/transparency-rules-article-50) 和 [加州 SB 942 细则](https://ai-law-center.orrick.com/california)
同一天生效了。欧洲要求合成内容必须带上机读标记，不然最高罚 1500
万欧元或者全球营收的
3%；加州则规定月活过百万的平台得免费给用户提供验证工具和隐性水印。Google
Earth 当时紧急关掉功能，刚好就在这个法规生效日的前两天。

## 结语：从「是否 AI」到界面契约

如果我们回头看看自己的产品，想评估怎么做 AI
治理，有三个衡量指标特别管用：产品的界面是不是偏向客观严肃记录、一旦大家看错图造成的代价有多大，以及生成的标记在传播里会不会轻易掉光。如果当时拿这套思路去给
`Google Earth`
做设计，最稳妥的办法显然不是在主参考界面里直接塞个按钮，而是把它单独拉出来做一个虚拟沙盒模式，加上醒目的状态标识，再提供和真实卫星图的同屏对比。只要界面的原本承诺没有被打破，大家自然就不会产生错误的期待。

当然，也有不少同行觉得平台这些操作全都是商业利益算计，界面承诺无非是事后找的漂亮借口。比如
Snapchat 开放功能是为了拉长停留时间，Tidal
切断版税是为了保住音乐人的钱袋子，LinkedIn
清理垃圾内容是为了防止自己的职业网络变得不值钱。商业利益确实能解释平台为什么在这个时间点出手，但它单凭自己很难解释为什么同一家巨头旗下的不同产品，会采取完全相反的态度。这两个视角其实不矛盾，刚好互为补充。

说到底，光死磕这张图或者这段话是不是 AI
做的，往往很难找到满意的答案。真正决定产品安全和治理路线的，是生成技术到底改变了内容的什么属性、界面给用户传递了什么样的信任，以及大家在发现真相之前会凭这些内容去干什么。当做产品的人不再指望某一个万能的水印或标签，而是重新审视自己界面和用户之间的那份信任契约时，AI
内容治理的难题才算找到了真正落地的解法。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
