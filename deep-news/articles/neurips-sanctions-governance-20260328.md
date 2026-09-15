---
title: "NeurIPS\n制裁争议：它为什么改口，中国为什么有反制力"
date: 2026-03-28
source: https://yage.ai/share/neurips-sanctions-governance-20260328.html
slug: neurips-sanctions-governance-20260328
lang: zh
---
# NeurIPS 制裁争议：它为什么改口，中国为什么有反制力

发布于 2026 年 3 月 28 日 · [查看原网页](https://yage.ai/share/neurips-sanctions-governance-20260328.html)

> 2026-03-28 | 面向 AI 从业者的事件解析与治理分析

---

2026 年 3 月 23 日，NeurIPS（Conference on Neural Information
Processing Systems，AI 领域最重要的学术会议之一）在其 2026
年投稿手册中写入了一条制裁合规条款，声称美国法律要求其拒绝来自受制裁机构的投稿。四天之内，中国计算机学会（CCF）号召抵制，中国科协（CAST）宣布停止资助中国学者参会并将
NeurIPS 论文排除出评价体系，NeurIPS 自身发布道歉声明并修改了条款。

这件事的意义超出了会议投稿规则。它是一个具体的案例，展示了当美国国内法律管辖权、一个非营利基金会的治理决策、以及一个高度依赖中国人才和论文供给的全球学术市场三者碰撞时，会发生什么。如果你关心
AI
研究的基础设施：谁决定哪些研究被发表、被评审、被认可，这个案例值得仔细拆解。

---

## 一、事件经过

### 1.1 NeurIPS 最初做了什么

3 月 23 日发布的 Main Track Handbook
中包含了这样一段话（以下为原文，后已被修改）：

> The NeurIPS Foundation, like any entity operating within U.S. legal
> jurisdiction, is required by law to comply with U.S. sanctions and trade
> restrictions. Under these regulations, providing ‘services’ (which
> includes peer review, editing, and publishing) to individuals
> representing sanctioned institutions is prohibited. Consequently, we are
> unable to accept or publish submissions from these institutions.

条款末尾附了一个链接，指向美国财政部海外资产控制办公室（OFAC）的
Sanctions List Search 通用筛查工具。

NeurIPS 作为在加州注册的 501(c)(3)
非营利基金会，确实受美国法律管辖。条款的问题在于两处关键的过度扩张，后文会详细分析。

### 1.2 中国方面的反应

反应速度和力度都超出了通常学术争议的节奏。

3 月 25 日，CCF 连夜发表声明，呼吁中国研究者拒绝向 NeurIPS 2026
投稿、拒绝担任审稿人和 Area Chair。这个反应模式与 2019 年 IEEE
限制华为员工审稿时 CCF 的反应高度相似。

3 月 26 日，CAST 宣布两项措施：停止受理 NeurIPS 2026
的出席资助申请；NeurIPS 录用论文不再被认定为 CAST
体系内的代表性成果。第二项措施影响更深远。在中国的学术评价体系中，CAST
的成果认定直接影响职称评审、基金申请和机构排名。将 NeurIPS
排除出这个认定体系，等于降低了中国研究者向 NeurIPS 投稿的职业回报。

### 1.3 NeurIPS 改了什么，算不算让步

3 月 26 日，NeurIPS 在 X 上发布初步回应，措辞模糊，未明确道歉。3 月
27
日发布正式声明，承认手册链接了一个覆盖范围远超其法律义务的制裁筛查工具，称这是基金会与法务团队之间的沟通失误。

具体改了什么？原始条款指向的 OFAC Sanctions List Search
是一个通用筛查工具，覆盖了多个清单，其中包括 SDN List（Specially
Designated
Nationals，最严格的制裁名单，上榜意味着资产冻结、美国人不得与之有任何交易）和
Non-SDN CMIC
List（中国军工复合体清单，华为和中芯国际在这个清单上）。关键区别在于：Non-SDN
CMIC List
的法律效果仅限于禁止美国人买卖这些公司的公开交易证券，与学术服务完全无关。原始条款把这两类清单混在一起，等于把华为、中芯国际这样的机构也纳入了潜在限制范围。

修改后的条款将限制范围明确收窄为 SDN，并新增了一句关键表述：NeurIPS
will consider submissions from institutions and individuals categorized
as Non-SDN。链接也从通用筛查工具改为 SDN
名单入口。这是合规口径的实质收窄，将华为、中芯国际等 Non-SDN
实体明确排除在限制之外。

但 NeurIPS 没有放弃制裁合规本身。修改后的手册仍然保留了”NeurIPS
Foundation
在美国法律管辖下运营，必须遵守美国制裁和贸易限制”的声明，仍然拒绝接受
SDN 名单上实体的投稿。NeurIPS
的官方叙事框定为”纠正错误”，而非”撤回政策”。

更准确的描述是 partial retreat：NeurIPS
从一个过于宽泛、在法律上站不住脚的合规姿态退回到了一个更窄、更接近法定义务边界的姿态。它承认了执行方式有问题，但没有承认合规方向本身有问题。

这也是中国方面对道歉”不买账”的原因。从中方视角看，问题不仅在于执行口径的宽窄，更在于一个自称国际学术会议的机构将美国单边制裁法嵌入其全球治理规则这个事实。条款修改解决了技术层面的过度扩张，但没有回应治理合法性层面的质疑。

---

## 二、法律依据到底是什么

### 2.1 OFAC 制裁与两份清单的区别

法律依据是《国际紧急经济权力法》（IEEPA, 50 U.S.C. § 1701 et
seq.），执法机构是 OFAC。核心规则：美国人士（包括美国注册实体）不得与
SDN List 上的实体或个人进行任何交易，包括提供服务。

SDN List
是最严格的制裁名单，上榜意味着资产冻结和全面交易禁令。Non-SDN CMIC List
的法律后果仅限于证券交易禁令。NeurIPS
原始条款链接到的通用筛查工具把两类清单混在一起呈现，这是事件中最核心的技术性错误。

### 2.2 同行评审是否构成”服务”

即使仅针对
SDN，一个更深层的问题仍然存在：学术同行评审、编辑和出版是否构成 OFAC
意义下被禁止的”服务”？目前没有法院直接裁决过这个问题。

最接近的先例是 2024 年 GPE v. OFAC 案的和解。OFAC
在和解中认定，在特定条件下，让受制裁人士参与公开会议发言不构成被禁止的”服务”，但明确限定了多项前提（不涉及金融交易、不涉及技术协助等），且标注这是基于特定事实的窄幅判断。同行评审涉及编辑协调、审稿人分配、修改意见往返，是否超出”言论”范畴而构成”服务”，在法律上仍是灰色地带。

IEEPA
也包含信息材料豁免条款，保护信息和信息材料的进出口不被禁止，但这个豁免保护的是已完成材料的传播，而非创造过程中的服务提供。同行评审本质上是一个服务过程，是否落入豁免范围同样没有定论。

### 2.3 与 2019 年 IEEE 事件的法律框架区别

2019 年华为被列入 BIS 出口管制实体清单后 IEEE
限制华为员工审稿，涉及的是 BIS 出口管制（EAR），而非 OFAC 经济制裁。EAR
有一个明确的”基础研究例外”，2019 年美国商务部正是通过澄清同行评审不构成
EAR 下的受控”服务”来解除了限制。

2026 年 OFAC 并没有发布类似澄清。NeurIPS
的条款修改是基金会自身在法律灰色地带中重新定位合规口径的结果，而非法律约束本身的变化。这意味着
2026 年的修改比 2019 年更脆弱：它依赖于 NeurIPS
基金会对法律义务范围的自行判断，而这个判断未来可能因 OFAC
执法态度变化而再次调整。

### 2.4 小结

NeurIPS Foundation 作为美国注册实体，确实受 OFAC 管辖，确实不能向 SDN
提供服务，这是法律硬约束。但原始条款的两个核心问题都不是法律强制的：链接到覆盖
Non-SDN 清单的通用筛查工具，以及对”affiliated with sanctioned
institutions”的模糊界定。这两处过度扩张是基金会法务团队在灰色地带中做出的保守选择。

这也回答了很多人的核心疑问：如果这是美国法律要求的，NeurIPS
怎么能改？答案是，NeurIPS
修改的部分本来就不是法律要求的。法律的硬边界（不得向 SDN
提供服务）从未被撤回。

---

## 三、中国的反应为什么有效

CCF 的抵制号召和 CAST 的反制措施在四天内推动了 NeurIPS
发布正式道歉和条款修改。这个速度依赖于中国在 NeurIPS
生态中的几个具体杠杆。

**论文供给。**
中国大陆机构（清华、北大、上交、中科院等）合计大约占 NeurIPS 接收论文的
12% 到 15%。如果把口径扩大到
Chinese-background（曾在中国接受本科教育、后来在海外工作的研究者），The
Economist 在 2026 年 3 月的样本分析估计 NeurIPS 2025
大约有一半论文涉及具有中国学术背景的研究者。这两个口径不能混写：前者回答的是中国本土机构的份量，后者回答的是中国培养出来的人才在全球
AI 研究中的份量。两者叠加，才解释了为什么中国侧的反应会让 NeurIPS
感到实质压力。

**审稿劳动力。** NeurIPS 2025 有超过 20,000 名
reviewer、1,600 余名
AC。这套评审系统本质上是全球志愿劳动基础设施。NeurIPS
官方不公布审稿人国籍分布，但公开 proxy
显示中国机构或中国背景研究者在审稿池里有相当存在感。CCF
号召拒绝担任审稿人和
AC，直接威胁到会议的同行评审能力。审稿人短缺不像投稿下降那样可以通过提高录取率来缓解，它会直接降低评审质量。

**评价体系。** CAST 将 NeurIPS
论文排除出成果认定，改变的是中国研究者投稿 NeurIPS
的职业激励。在中国学术评价体系中，论文被哪些机构认定为”代表性成果”直接影响项目申请、职称评审和机构排名。当
NeurIPS 论文不再计入时，同样精力投入到被 CAST
认可的会议上职业回报更高。

需要说明的是，这些杠杆的有效性不等于”中国政府改变了 NeurIPS
的政策”。CCF 是学术社团，CAST
是学术组织，它们的反制措施在中国学术体系内有实际影响力，但不是行政命令。NeurIPS
修改条款的直接原因，按其自身声明，是内部沟通失误；中国方面的反应提供了外部压力和时间紧迫性，但推动修改的因素还包括非中国背景研究者的批评、法律学者的分析、以及基金会对声誉风险的评估。真正有说服力的叙事是：在一个中国贡献了大量论文和审稿劳动的学术市场中，任何被感知为歧视性的规则变动都会触发足够大的反弹。

---

## 四、治理权与贡献权的错配

NeurIPS
到底是美国会议还是国际会议？答案是两者并存，而这种并存本身就是争议的根源。

法律层面，NeurIPS Foundation 是加州注册的 501(c)(3) 非营利组织，OFAC
的制裁规则对它有管辖权，无论参会者来自哪里。学术层面，NeurIPS
的投稿人、审稿人和录用论文覆盖数十个国家，学术声誉建立在全球研究社区的集体参与之上。

这里存在一个关键的不对称：中国研究者对 NeurIPS
的贡献权（论文、审稿、参会）远大于他们在治理层面的代表权。2025 年
NeurIPS Foundation 的 Board of Trustees
主要来自美国及其盟国机构（Salk、Apple、Stanford、Google、Meta、Mila、KAIST
等），公开名单里没有中国大陆机构归属的董事会成员。NeurIPS
的现实是：法律壳和治理壳高度美国化，人才和论文市场高度全球化。这个错配平时不显眼，但一旦规则碰到地缘政治，就会立刻暴露。

这也不是 NeurIPS 独有的问题。几乎所有由美国非营利组织运营的大型 AI
会议（ICML、ICLR 等）都面临类似的法律管辖权约束。NeurIPS 2026
事件引发更强烈反应，部分因为条款措辞覆盖范围超出了同行会议的现有政策，部分因为它发生在中美科技脱钩加速的背景下。

---

## 五、对 AI 从业者的启示

**学术会议是有法律管辖权的基础设施。**
NeurIPS、ICML、ICLR 在功能上是全球 AI
研究的分发和认证系统。谁的论文被录用、谁被邀请做审稿人，这些决定塑造了研究者的职业轨迹和研究方向的合法性。但运营这些系统的组织受特定国家法律管辖。当地缘政治进入法律框架时，学术基础设施的国际性就面临考验。

**法律约束和治理选择是两件事。**
这次事件中，真正由法律强制要求的部分和基金会自行选择的过度合规部分被混在一起呈现。区分这两者对于评估类似事件至关重要。当一个组织说”法律要求我们这样做”时，值得追问：法律要求的边界在哪里，执行口径是否超出了这个边界？

**信任赤字已经形成。** CAST
的反制措施截至发稿仍未撤回。中国学界对 NeurIPS
是否会在未来再次扩大合规口径持怀疑态度。对于依赖国际学术会议作为研究传播渠道的从业者来说，中国主导的
AI
会议和期刊是否会在这一背景下获得更多关注和投稿，是一个值得观察的趋势。

---

## 附：关键信息来源

本文分析基于以下一手材料：

- NeurIPS 2026 Main Track Handbook（原始版与修改版措辞对比）
- NeurIPS 2026-03-27 官方声明（X 平台 @NeurIPSConf）
- OFAC Sanctions List Search 数据库（SDN 与 Non-SDN CMIC
  清单区分）
- OFAC FAQ #1190（宪法保护声明）
- IEEPA 信息材料豁免条款（50 U.S.C. § 1702(b)(3)）
- GPE v. OFAC 案和解文件及 Hogan Lovells、Morgan Lewis 律所分析
- Peter Henderson, “Can NeurIPS Be Required to Reject Papers from
  Sanctioned Entities?”（Trials & Errors, 2026-03-26）
- BIS EAR Part 734 基础研究例外条款
- IEEE 2019 华为审稿限制及撤回声明
- Reuters、SCMP、Global Times、The Transmitter 相关报道

文中区分了三类陈述：可验证的事实（来源于上述一手材料）、基于事实的分析判断（标注为分析层面）、以及尚未有定论的开放性问题（标注为灰色地带或未裁决）。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
