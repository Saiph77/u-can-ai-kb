---
title: "低光增强 vs\n高光过曝恢复：为什么一边繁荣、一边沉寂"
date: 2026-03-25
source: https://yage.ai/share/highlight-recovery-vs-low-light-survey-20260325.html
slug: highlight-recovery-vs-low-light-survey-20260325
lang: zh
---
# 低光增强 vs 高光过曝恢复：为什么一边繁荣、一边沉寂

发布于 2026 年 3 月 25 日 · [查看原网页](https://yage.ai/share/highlight-recovery-vs-low-light-survey-20260325.html)

> 调研日期：2026-03-25

## 核心判断

如果把问题说得非常直接：低光增强之所以能长成一个独立而成熟的方向，是因为暗部很多时候还有信息，只是弱、噪、难用；高光过曝恢复之所以一直没有形成同等规模的领域，是因为很多细节在拍摄时就已经撞到上限，被截断了。

所以，真正稀缺的不是所有与亮部有关的处理，而是这样一件事：拿到一张已经拍完的照片，再把那些变成纯白的区域恢复成真实细节。工业界当然也处理亮部问题，但主流做法不是事后救回来，而是在信息丢失之前就介入：用传感器
HDR、多帧融合、曝光包围和 RAW 工作流，尽量别让高光先死掉。

这也是这篇文章最想帮读者建立的直觉：低光增强更像把一段很小声、但确实录下来的声音放大并降噪；高光过曝恢复更像试图补回已经被削平的波形。前者是提取，后者更接近补全。

---

## 先理清概念：这些名字各自指什么

讨论这个问题之前，有必要把几个经常被混用的概念拆开。它们的区别不在于名字，而在于输入是什么状态、信息还剩多少、以及算法要做的事情本质上是估计还是猜测。

**低光增强（Low-Light Image Enhancement）**
处理的是拍暗了的照片。传感器确实接收到了光子，只是太少，导致图像灰暗且噪声很大。这里的核心操作是放大微弱信号的同时压制噪声——信息在那儿，只是需要挖出来。

**图像去噪（Image Denoising）**
更通用一些，不限于低光场景，但低光是噪声最严重的场景之一。高 ISO
拍摄时传感器的随机电子噪声会淹没有用信号，去噪算法的工作是从统计意义上分离信号和噪声。

**曝光校正（Exposure Correction）**
同时覆盖拍暗了和拍亮了两种情况。2021
年之后，学术界开始认真对待「一个模型同时处理欠曝和过曝」这个设定，这是一个值得注意的趋势，后面会展开。

**单张 HDR 重建 / 逆色调映射（Single-Image HDR Reconstruction /
Inverse Tone Mapping）**
要做的事是从一张普通动态范围的图片推断出更宽的亮度范围。这通常需要处理高光区域丢失的信息，但它的目标不是「修复过曝」，而是「生成一张
HDR 图」——高光恢复只是其中一个子问题。

**RAW 高光恢复（RAW Highlight Recovery）** 是 RAW
处理软件中常见的功能。相机传感器记录的原始数据通常有 12-14 bit
的色深，远超 JPEG 的 8 bit。当一张照片的某些区域在 JPEG
中看起来已经纯白时，RAW 数据中可能仍然有部分通道保留了未饱和的信息。RAW
高光恢复利用的正是这种残留数据。它能做到多少，取决于有多少通道还没有完全截断。

**多帧 HDR / 曝光包围（Multi-Frame HDR / Bracketing）**
需要多张不同曝光的照片作为输入。短曝光帧保留高光细节，长曝光帧保留暗部细节，算法将它们融合为一张宽动态范围的图像。这是手机计算摄影中最主流的高动态范围方案，但它从根本上不是单张图片的高光恢复——它要求拍摄时就获取了额外信息。

**生成式填补（Generative Fill / Inpainting）**
是最新的方向。当高光区域确实什么信息都没有了，生成模型可以根据周围内容「想象」出看起来合理的纹理，比如把纯白的天空补上云彩。这在视觉上可能令人满意，但它本质上是创造而非恢复——补出来的内容与拍摄时实际存在的场景没有对应关系。

把这些概念摆出来之后，可以看到一个关键分界线：低光增强、去噪、RAW
高光恢复处理的都是「信息还在但不好用」的情况；而单张图片的高光过曝恢复（尤其是所有颜色通道都已经饱和截断的情况）面对的是「信息已经不在了」。前者是估计问题，后者是推断和生成问题。

---

## 信息丢失的机制：为什么低光和过曝根本不对称

理解这个不对称需要回到相机传感器的工作方式。

传感器上的每个像素本质上是一个光子计数器。曝光时间内接收到的光子越多，积累的电荷越高，记录的数值越大。这个计数器有一个下限（暗电流噪声，即使没有光也会产生一些随机电荷）和一个上限（满阱容量，积累的电荷达到物理极限后就不再增加）。

在低光条件下，光子很少，有用信号和随机噪声的比例很差。但信号确实存在。如果拍多张同样的照片，噪声是随机的、信号是固定的，通过平均就能逐步抬升信噪比。这正是手机夜间模式和
burst
降噪的物理基础。即使只有一张照片，现代深度学习去噪算法也能通过学习自然图像的统计规律，从噪声中合理地估计出信号。这并不是无中生有——底层信号一直在那里。

高光过曝是完全不同的情况。当光子太多、电荷达到满阱容量后，计数器停在了最大值。无论实际亮度是最大值的
1.1 倍还是 100
倍，记录的数值都一样——所有超过上限的信息被不可逆地截断了。这不是信噪比差的问题，而是信息被物理抹去了。用一个直白的类比：低光像是一段用很小声音录下的音频，你可以放大音量、用降噪软件清理底噪，原始的声音还在；过曝像是一段录音的音量超过了麦克风的最大承受范围，波形顶部被削平了，那些被削掉的部分没有任何办法从同一段录音中复原。

这个物理事实决定了两个方向在算法、数据集、评测方式和产品化路径上的根本差异。

---

## 学术研究：一边是成熟产业，一边是零散散布

低光增强在学术界已经是一个高度成熟的研究方向。它有权威综述，如 Li et
al. 在 IEEE TPAMI 2022 发表的 [Low-Light Image and Video
Enhancement Using Deep Learning: A Survey](https://arxiv.org/abs/2104.10729)；有 SID、LOL
这样的标准测试集；有 [awesome-low-light-image-enhancement](https://github.com/zhihongz/awesome-low-light-image-enhancement)
这样的长期维护资源；也有 NTIRE 挑战赛持续给它提供公共
benchmark。换句话说，这个方向已经完成了一整套成熟领域该有的基础设施建设。

如果只抓几个路标来看，也很清楚。2018 年 Chen et al. 的 [Learning
to See in the Dark](https://openaccess.thecvf.com/content_cvpr_2018/papers/Chen_Learning_to_See_CVPR_2018_paper.pdf) 把 RAW 域低光恢复真正推到前台；2020 年 Guo et
al. 的 [Zero-DCE](https://openaccess.thecvf.com/content_CVPR_2020/papers/Guo_Zero-Reference_Deep_Curve_Estimation_for_Low-Light_Image_Enhancement_CVPR_2020_paper.pdf)
让零参考方法出圈；到 2023 年之后，Transformer
和扩散模型也自然接入了这个方向。它已经不是零散问题，而是一整片成熟地带。

相比之下，过曝校正和高光恢复并不是完全没人做，而是始终没有形成一个统一、稳定、所有人都用同一个名字讨论的领域。高光相关研究更多散落在几个邻近方向里。单张
HDR 重建是最典型的例子。Liu et al. 的 [SingleHDR](https://openaccess.thecvf.com/content_CVPR_2020/papers/Liu_Single-Image_HDR_Reconstruction_by_Learning_to_Reverse_the_Camera_Pipeline_CVPR_2020_paper.pdf)（CVPR
2020）里，处理高光缺失的核心步骤已经非常接近我们直觉中的高光恢复，但论文的主任务定义仍然是
HDR reconstruction，不是 highlight recovery。AIM 2025 的 [Inverse
Tone Mapping Challenge](https://openaccess.thecvf.com/content/ICCV2025W/AIM/papers/Wang_AIM_2025_challenge_on_Inverse_Tone_Mapping_Report_Methods_and_ICCVW_2025_paper.pdf) 也说明这条线一直在研究，只是它长期挂靠在 HDR
和 inverse tone mapping 这些更大的任务名下面。

真正的变化出现在 2021 年之后。Afifi et al. 的 [Learning
Multi-Scale Photo Exposure Correction](https://github.com/mahmoudnafifi/Exposure_Correction)（CVPR
2021）开始把过曝和欠曝放进同一个曝光校正框架里。到 2025 年 ICCV 的 [CLIER
benchmark](https://openaccess.thecvf.com/content/ICCV2025/papers/Wang_From_Abyssal_Darkness_to_Blinding_Glare_A_Benchmark_on_Extreme_ICCV_2025_paper.pdf)，极端过曝才第一次被正式拉进比较清晰的评测体系。它还谈不上已经形成大领域，但至少开始从边角问题走向更明确的研究对象。

但即便如此，低光增强在论文数量、benchmark
数量、社区资源和竞赛赛道上的优势仍然是压倒性的。过曝方向至今没有自己的
awesome list，没有持续维护的社区资源，也没有独立的 NTIRE 赛道。

---

## 工业实践：低光是品牌，高光是管线细节

工业界的不对称比学术界更明显，因为产品不会按论文分类来组织自己，产品只会把资源投到最能解决真实问题的链路上。

低光场景催生了一系列有名有姓的产品功能。Google 有 [Night
Sight](https://research.google/blog/night-sight-seeing-in-the-dark-on-pixel-phones/)，Samsung 有 [Nightography](https://news.samsung.com/global/interview-no-light-no-problem-nightography-delivers-epic-night-shots-says-samsung-researchers)，Apple
有 [Night Mode](https://support.apple.com/en-us/102519)，DxO
甚至把 [DeepPRIME](https://www.dxo.com/technology/deepprime/)
做成了独立品牌。无论背后是多帧融合、去噪、RAW
处理还是深度学习，这些能力最后都被包装成一个用户能立刻理解的承诺：暗处也能拍得更干净、更亮。

高光恢复从来没有获得过类似的产品地位。没有任何手机厂商把它做成一个像
Night Mode 那样的独立入口，因为工业界真正大规模做的是另外两件事：一是在
RAW 里尽量把还没死透的数据拉回来，二是在拍摄时就不要让它死掉。

第一类是 RAW 编辑器中的 Highlights 滑块。Adobe Lightroom / Camera
Raw、Capture One、RawTherapee、Darktable
都有类似能力。它们之所以有用，不是因为软件能从纯白里变出细节，而是因为
RAW 里有时还留着一些余量：某个通道已经饱和，别的通道还没饱和；JPEG
看着死白，RAW 里还没全死。Capture One 的 [Why shoot RAW?](https://www.captureone.com/blog/why-shoot-raw)
就把这个边界说得很清楚。RawTherapee 的 Reconstruct Colour
之类方法，本质上也是在利用这些还活着的局部信息。

但这里有一个关键限制：当三个颜色通道全部饱和时（即 RAW
数据中所有通道的值都达到了传感器的满阱容量），Highlights
滑块能做的就只是产生中性灰。正如 [Adobe
社区讨论](https://community.adobe.com/questions-675/does-highlight-recovery-add-neutral-density-993636) 中指出的：「When there is no detail to recover (i.e. all
three channels are completely blown), you get a neutral gray when you
drag the Highlights slider to the left.」

第二类是手机 HDR 拍摄管线。Google 的 [HDR+
with Bracketing](https://research.google/blog/hdr-with-bracketing-on-pixel-phones/)、Samsung 的 [Staggered
HDR](https://semiconductor.samsung.com/technologies/image-sensor/hdr-technology/)、Qualcomm 的 [Spectra
ISP](https://www.qualcomm.com/snapdragon/news/How-Snapdragon-technology-is-revolutionizing-smartphone-photography-with-the-Qualcomm-Spectra-ISP)
都属于这一类。它们的共同点很简单：高光问题尽量在拍摄时解决。短曝光保高光，长曝光保暗部，多帧融合把两边拼起来。工业界真正大规模部署的是高光保护，不是高光复活。

这两种形式的共同点是：它们都依赖于信息尚未完全丢失这个前提。RAW
高光恢复需要至少一个通道还有数据；HDR
管线需要有短曝光帧保留了高光细节。当一张 JPEG
照片中某个区域的三个通道全部是 255 时，这两种方案都帮不上忙。

对于这种彻底丢失信息的情况，目前最接近的产品方案是 Adobe Photoshop 的
Generative Fill。它可以选中过曝区域然后让生成模型填补内容。但 Generative
Fill
不是专门的高光恢复工具，它是通用的内容生成功能。而且，生成出来的内容是模型根据上下文推测的，与拍摄时实际存在的场景细节没有对应关系。Topaz
Photo AI 的社区中有用户 [明确请求
glare removal
功能](https://community.topazlabs.com/t/feature-request-removing-glare/86086)，但至今没有被实现——这本身就说明了这个需求在产品层面的空白。

---

## 为什么会出现这种不对称

回到这个不对称的成因，可以从几个层面来解释。

最根本的是物理层面的差异。低光场景中的信号可以通过多帧叠加（noise
averaging）或更好的去噪模型来恢复，因为底层信息是完整的，只是被噪声掩盖了。高光截断则意味着信息被永久移除，除非有来自别处的信息（另一帧、另一个通道、或者模型学到的先验知识），否则没有任何数学手段能从同一张图中推出被截断的原始值。这不是算法够不够好的问题，而是信息论层面的约束。

其次是数据和评测的问题。要训练一个低光增强模型，可以用长曝光/短曝光配对、合成噪声、或者甚至无需配对数据（如
Zero-DCE）。SID 数据集用「极端短曝光 +
正常长曝光」的配对方式提供了大规模训练数据。但要训练一个高光恢复模型，需要知道被截断区域的「真实答案」是什么——而这些信息在拍摄时就已经丢失了。HDR
数据集可以提供部分参考（因为 HDR 图像有更宽的动态范围），但从 HDR
到「真实场景亮度」的映射本身也存在假设。这个数据获取的难度从根源上限制了独立的高光恢复研究。

第三是用户需求和市场叙事的差异。暗光拍摄是每天都会遇到的场景：餐厅、酒吧、夜景、室内聚会。用户能直接看到「照片太暗了」这个问题，并且对「能在暗处拍出好照片」有强烈需求。手机厂商愿意为这个需求起名字、做营销，因为它直接影响购买决策。而高光过曝在手机上已经被
HDR
管线大幅缓解（正常使用手机拍照时很少遇到严重过曝），剩下的场景更多出现在专业摄影中（背光人像、直射太阳光），专业摄影师通常会用
RAW
工作流和合理的曝光控制来预防这个问题。需求侧的差异进一步导致了研究投入和产品投入的差异。

最后一个因素是评价标准的模糊性。低光增强的效果相对容易评价：图像更亮了、噪声更少了、细节更清晰了，这些都可以用
PSNR、SSIM
等指标量化。但高光恢复的效果怎么评价？如果原始信息已经丢失，那么任何「恢复」都是某种程度的猜测。一个模型在被截断的天空区域补上了蓝天白云，看起来很自然，但真实场景可能是灰蒙蒙的雾霾天。这种「看起来对但不一定真实」的困境让研究社区很难建立公认的评测标准。

---

## 几个常见误解

在整理这些材料的过程中，有几个容易混淆的点值得明确指出。

**RAW 高光恢复不等于恢复 JPEG 中的过曝区域。** RAW
编辑器的 Highlights 滑块之所以有效，是因为 RAW 数据中通常有 12-14 bit
的色深和未经压缩的通道数据。当一个通道被截断但其他通道还有信息时，可以做跨通道推算。但
JPEG 只有 8 bit 色深且经过了有损压缩，当 JPEG 中的像素值达到 255
时，那个区域的信息已经被编码过程抹去了。所以同一张照片，RAW
版本可能恢复出高光细节，JPEG 版本做不到。

**手机宣传的 HDR 和高光保护不是单张高光恢复。** Google
HDR+、Apple Smart HDR、Samsung Staggered HDR
的原理都是在拍摄阶段就获取了额外信息（通过多帧或片上分像素），然后融合出更宽的动态范围。这是预防措施，不是事后修复。当用户已经拿到一张过曝的照片时，这些技术帮不上忙。

**生成式补全不等于真实恢复。** Adobe Generative Fill
或类似工具可以在过曝区域生成看起来合理的内容，但生成的细节是模型推测的，与实际场景不存在对应关系。在需要真实性的场合（如新闻摄影、医学影像、遥感图像），这种方法不能被视为恢复。

**Specular highlight removal 是另一个不同的问题。**
学术界有一个叫「镜面高光去除」的方向（ICCV 2025
有多篇相关论文），它处理的是物体表面因为镜面反射产生的局部高亮——比如金属物体上的光斑。这与「过曝」是不同的问题：镜面高光通常只影响局部小区域，而且物理模型相对清晰（可以用二色反射模型分离漫反射和镜面反射分量）。它不能被归入「高光过曝恢复」这个范畴。

---

## 正在变化的趋势

虽然整体不对称仍然明显，但有几个信号表明情况正在缓慢变化。

曝光校正作为独立方向从 2021 年开始增长，到 2024-2025 年已经在 CVPR 和
ICCV 上有稳定的论文产出。2025 年 ICCV 的 [CLIER
benchmark](https://openaccess.thecvf.com/content/ICCV2025/papers/Wang_From_Abyssal_Darkness_to_Blinding_Glare_A_Benchmark_on_Extreme_ICCV_2025_paper.pdf) 的标题「From Abyssal Darkness to Blinding
Glare」明确将极端过曝纳入了评测范围，这在之前没有先例。同时，ECCV 2024
的 [IntrinsicHDR](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/01723.pdf)
尝试用内在分解（将图像分为 albedo 和 shading）的方式做 HDR
重建，提供了新的思路来处理过曝区域。

生成模型的能力提升也在改变这个方向的可行性。扩散模型已经在低光增强中得到了应用（如
Diff-Retinex、ExposureDiffusion），同样的生成能力理论上可以用于过曝区域的内容推断。区别在于：对低光图像来说，生成模型更多是辅助去噪和细节增强；对过曝区域来说，生成模型需要承担更大的「创造」角色。这涉及到真实性和可信度的边界问题——当模型补全的内容越来越逼真时，如何让用户理解哪些是恢复、哪些是生成？这是一个尚未解决的产品设计问题。

从传感器技术来看，Sony 2025 年发布的 IMX828 传感器宣称达到 [25
stops 的动态范围](https://ymcinema.com/2025/12/08/sony-mobile-sized-sensor-25-stops-dynamic-range/)（约 150
dB）。如果传感器能力持续增长，日常拍摄中因为传感器动态范围不足导致的高光截断会越来越少——问题在上游被消解了，下游的恢复需求也会相应减弱。

---

## 结论

回到最初的问题：你的观察是对的。低光增强算法确实远多于高光过曝恢复算法，而且这个差距不是偶然形成的。

低光增强之所以会长成一个完整领域，是因为它同时满足了几个条件：物理上可做，信号还在；数据上可构造，能建立训练集；评测上可比较，大家知道什么叫更好；产品上有高频需求，用户每天都在暗处拍照。高光过曝恢复则刚好相反：一旦信息被截断，任务就会从恢复滑向补全；ground
truth 更难定义；评测更难建立；而工业界又能通过 HDR、bracketing 和 RAW
工作流在更前面的链路解决大部分问题。

所以这件事最值得带走的判断不是暗光比高光更重要，而是：暗光问题更多发生在信息还活着的时候，高光问题更多暴露在信息已经死掉之后。前者自然更容易长成一个繁荣的算法和产品方向，后者则更适合被预防，而不是被事后恢复。

---

*本报告基于 2026 年 3 月 25
日的公开学术论文、产品文档、技术博客和社区讨论整理而成。引用来源包括
IEEE TPAMI、CVPR、ICCV、ECCV 等学术会议，以及 Google Research
Blog、Samsung Newsroom、Adobe Help Center、DxO 官网、Capture One Blog
等工业一手材料。*

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
