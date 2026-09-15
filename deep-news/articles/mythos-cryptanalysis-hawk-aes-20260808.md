---
title: "从 HAWK 撤回到 AES 7 轮：Anthropic Mythos\n密码学突破的技术真相"
date: 2026-08-08
source: https://yage.ai/share/mythos-cryptanalysis-hawk-aes-20260808.html
slug: mythos-cryptanalysis-hawk-aes-20260808
lang: zh
---
# 从 HAWK 撤回到 AES 7 轮：Anthropic Mythos 密码学突破的技术真相

发布于 2026 年 8 月 8 日 · [查看原网页](https://yage.ai/share/mythos-cryptanalysis-hawk-aes-20260808.html)

2026 年 7 月，[NIST
PQC Round 3 官方状态页](https://csrc.nist.gov/Projects/pqc-dig-sig/round-3-additional-signatures)
记录了一项重要变动：入围第三轮评估的后量子数字签名算法
HAWK，由其设计团队宣布主动撤回。促成撤回的直接原因，源于 Anthropic 在 [Anthropic
官方研究公告](https://www.anthropic.com/research/discovering-cryptographic-weaknesses) 中披露的 Claude Mythos Preview
模型研究成果。模型不仅推导出针对 HAWK 算法的密钥恢复路径，Anthropic 还随
[HAWK
Key Recovery 论文](https://www.anthropic.com/document/hawk_key_recovery.pdf) 公开了验证代码。HAWK 团队复核后，于 [HAWK
团队在 NIST 论坛的撤回声明](https://groups.google.com/a/list.nist.gov/g/pqc-forum/c/2r2u6SbHun4/m/0_I2KOZ_CQAJ) 中确认攻击会让恢复等价私钥所需的格规约
block size
约减半。由于强行提升参数以维持安全会损害其轻量快速的性能优势，设计团队选择退出选拔。

在同步发布的 [AES
Möbius Bridge 论文](https://www.anthropic.com/document/aes_mobius_bridge.pdf) 中，Anthropic 还展示了模型对经典对称加密算法
AES-128 的分析进展。模型提出的 Möbius Bridge 方法将 7 轮简化版 AES-128
的破解效率提升了常数倍。密码学家在 [Matthew
Green 密码学博客点评](https://blog.cryptographyengineering.com/2026/07/29/some-notes-about-anthropics-new-results/)
中指出，该成果属于纯学术性质的算法优化，完全不影响生产环境 10 轮 AES-128
的安全防线。选拔赛上一个候选算法的突然撤回与对称加密的学术优化，共同勾勒出前沿
AI 模型在密码攻防边界上的真实探索。

## 规则解析与量子威胁：量子计算机如何破解经典加密？

选拔赛上算法的生死决定，建立在密码工程对安全裕度的严苛评估之上。安全裕度是密码系统抵御未知数学突破的缓冲区。如果一项新攻击显著削弱了算法的数学硬度，设计团队就必须扩充密钥长度或增加计算轮数。对于主打轻量化的候选算法而言，参数膨胀会直接损害其在工程部署中的竞争力。

全世界之所以急于寻找新一代后量子算法，是因为量子算力对经典非对称加密带来了根本性冲击。像
RSA
这类经典公钥算法，安全性建立在大整数因子分解难题上。正向计算两个大素数的乘积
p×q=Np \times q = N
开销很低，但经典计算机尚无已知的多项式时间逆向算法；目前最好的通用整数分解算法是亚指数级的数域筛，而不是简单穷举。

量子计算机打破这一平衡的核心武器是 Shor
算法。它把整数分解转化为模幂函数的周期寻找问题，再用量子傅里叶变换对周期信息进行采样。一旦恢复周期，经典计算就能以多项式时间求出因子
pp
与
qq。

格密码把安全性建立在高维格中的困难问题上，例如寻找足够短的向量。研究界目前不知道如何把这类问题转化成
Shor
算法擅长的周期寻找，也没有发现能在密码所用参数上高效求解它们的经典或量子算法。正因如此，格密码成为后量子密码的主流路线之一。

## 剖析 HAWK 攻击：高维网格里的降维打击

既然研究界尚未发现能高效攻破格密码的通用量子算法，构建在格密码之上的
HAWK 为什么会在 Mythos 面前失守？答案要从 HAWK
自身的代数构造中寻找。HAWK
的私钥是高维网格内部一组几何尺寸极短且近乎正交的私钥向量基，使用者掌握这组短向量即可完成签名；公钥则隐藏了短向量本身，仅公开了短向量之间的几何投影关系，即
Gram 矩阵
Q=B\*BQ = B^\* B。

在 [2025 年 HAWK
秘密基理论研究](https://eprint.iacr.org/2025/928) 中，学者已经证明：如果攻击者能获得 HAWK
底层整数格的一个非平凡自同构，密钥恢复至少可以获得二次加速。但该研究没有给出如何仅凭
HAWK 公钥获得这种自同构，论文当时也明确表示结果尚不影响 HAWK。

Mythos 模型的突破恰好补全了这项未完成的代数推导。模型识别出 Galois
involution
τ:ζ↦−ζ\tau: \zeta \mapsto -\zeta
这一具体自同构，再利用公钥 Gram
矩阵，将私钥在该变换下的变化关系构造为只依赖公钥的
τ\tau-cocycle
子格
Λτ(Q)\Lambda\_\tau(Q)。在
[HAWK
Key Recovery 论文](https://www.anthropic.com/document/hawk_key_recovery.pdf) 中，Mythos
证明该子格具备代数同构性质，其最短向量正好对应隐藏的对称变换，且这些目标向量集中在子空间
ℤn/2+1⊕2ℤn/2−1\mathbb{Z}^{n/2+1} \oplus \sqrt{2}\mathbb{Z}^{n/2-1}
中。

这一构造在算法层面压缩了最困难的搜索。以 HAWK-512
为例，攻击先从公钥构造一个秩为 512 的
τ\tau-cocycle
子格，再利用它的特殊结构，把精确最短向量求解器的调用维度降到 257
维，也就是
n/2+1n/2+1。格规约成本对维度和
block size 高度敏感，这次归约因此大幅降低了估算成本。Anthropic
随后公开自动化求解脚本，调用 BKZ 与 Sieve 算法，在 96 核参考机器上用时 3
小时 42 分钟求解出 HAWK-256
试验参数的等价私钥；截至本文核查时，尚未见第三方完整重跑这条端到端管线。

*HAWK 攻击从公开 Gram 矩阵构造 cocycle 子格，将 HAWK-512 的最难搜索维度从 512 压到 257，并在 HAWK-256 演示中恢复等价私钥*

HAWK 攻击从公开 Gram 矩阵构造 cocycle
子格，将 HAWK-512 的最难搜索维度从 512 压到 257，并在 HAWK-256
演示中恢复等价私钥

HAWK 团队在 [HAWK
团队在 NIST 论坛的撤回声明](https://groups.google.com/a/list.nist.gov/g/pqc-forum/c/2r2u6SbHun4/m/0_I2KOZ_CQAJ) 中确认，该攻击将恢复等价私钥所需的格规约
block size 约缩减了一半。虽然标准参数 HAWK-512 与 HAWK-1024
在现有物理算力下仍无法在现实时间内破解，但其安全裕度已受损。若通过扩大参数来恢复原有的安全裕度，HAWK
将失去轻量快速的性能优势，设计团队因而主动选择撤回。

## 还原 AES Möbius Bridge：为什么它不影响生产环境的 AES？

相比于后量子选拔赛中的 HAWK 退赛，公众更关心的往往是现役生产加密算法
AES 是否受到了波及。厘清这一疑虑，需要区分学术试验场与实际生产环境。AES
算法通过字节替换、行移位、列混合和密钥加法等步骤迭代加密，生产环境中部署的
AES-128 严格执行 10
轮迭代计算。在学术密码分析中，研究人员通常使用削减轮数的简化版本作为试验场，以评估新型数学工具的分析能力。Mythos
提出的 Möbius Bridge 攻击，作用对象正是只运行 7 轮的简化版 AES-128。

Möbius Bridge 的数学直觉建立在 AES 核心非线性部件 S-box
的有限域代数结构上。S-box
在数学上由有限域求逆与固定仿射变换组合而成。传统的猜解攻击需要针对每一个候选密钥字节逐一尝试
256 种可能。Mythos 在 [AES
Möbius Bridge 论文](https://www.anthropic.com/document/aes_mobius_bridge.pdf)
中利用有限域求逆在特定变换下的不变量，设计了一种特殊的代数指纹。该指纹在未知密钥字节变化时保持不变，从而能一次性过滤掉大量无效猜测，将每个字节的尝试次数从
256 次降至 1 次。

即便实现了这种代数压缩，攻击仍需要获取
21052^{105}
个选择明文。在综合平衡数据、时间与内存消耗后，攻击在整体计算复杂度上带来了
2.1–2.7 bits 的改善，总复杂度仍约为
296.32^{96.3}，这里使用的是论文定义的
table-lookup 计价单位。

*Möbius Bridge 只改进 7 轮 AES-128 研究攻击，没有给出针对生产环境 10 轮 AES-128 的攻击*

Möbius Bridge 只改进 7 轮 AES-128
研究攻击，没有给出针对生产环境 10 轮 AES-128 的攻击

密码学家在 [Matthew
Green 密码学博客点评](https://blog.cryptographyengineering.com/2026/07/29/some-notes-about-anthropics-new-results/)
中总结，这是一项学术范围内的温和常数倍优化。当前方法只覆盖 7 轮
AES-128，没有给出延伸至生产环境 10 轮 AES-128
的攻击。生产系统不需要因这项结果迁移或修补。

## 认知转移：当寻找漏洞变便宜，验证与处置成了新瓶颈

将 HAWK 的高维降维与 AES 的 7 轮优化放在一起观察，能够勾勒出
Anthropic Mythos 在密码学领域的真实能力画像。生产环境中运行的
AES-128，以及 NIST 已完成标准化的后量子算法（如
ML-KEM、ML-DSA），均不受这两项结果影响。这次事件的真实意义，在于前沿 AI
模型在人类搭建的研究框架内，完成了前沿论文阅读、数学构造和自动化代码验证；成果随后通过
HAWK 团队确认，并促成标准候选算法撤回。

从技术能力演进的角度看，Mythos
展现了通用语言模型参与研究级代数推理的能力。模型并未局限于已知漏洞的模式匹配，而是补全了前置研究尚未给出的数学构造，并编写出可执行的验证代码。HAWK
团队确认了攻击对格规约 block size 的影响，NIST 随后更新了候选状态。

如果这种能力能稳定泛化，安全工程的资源瓶颈将随之改变。过去发现前沿代数缺陷依赖稀缺的专家直觉；模型若能高并发地产生可执行攻击假设，研究社区将面对更密集的候选结果。在此背景下，快速验证漏洞真实性、准确评估安全裕度影响，以及完成披露和处置，会比单纯生成更多候选更稀缺。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
