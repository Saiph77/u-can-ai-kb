---
title: "Gemini Robotics 2\n的架构逻辑：机器人的感知与规划正在走向合并"
date: 2026-08-09
source: https://yage.ai/share/gemini-robotics-2-architecture-merge-20260809.html
slug: gemini-robotics-2-architecture-merge-20260809
lang: zh
---
# Gemini Robotics 2 的架构逻辑：机器人的感知与规划正在走向合并

发布于 2026 年 8 月 9 日 · [查看原网页](https://yage.ai/share/gemini-robotics-2-architecture-merge-20260809.html)

Google 在 2026 年 8 月发布了 [Gemini
Robotics 2
家族](https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots)，一下子推出了三款面向不同任务层级的模型：负责高层具身推理的云端模型
Gemini Robotics ER 2、处理动作控制的 VLA 模型 Gemini Robotics
2，以及直接跑在硬件设备上的 Gemini Robotics On-Device 2（详见 [Model
Card 评估说明](https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-Robotics-On-Device-2-Model-Card.pdf)）。如果你在 Google AI Studio 或 Gemini API
里上手试用过公开的 [ER
2
模型](https://deepmind.google/models/model-cards/gemini-robotics-er-2)，会发现一个非常有意思的现象：这个模型虽然能同时看懂图像、视频、音频和文字，但它输出的内容只有文字和
Tool Calls
函数调用，并不直接给出力矩大小、关节角度或者机械臂的末端运动轨迹。如果你想让机器人去收拾桌面，ER
2
更像是一个大牌调度指挥官。它看着现场摄像头传回来的画面，心里盘算任务进展到了哪一步，再生成下一步的文字计划去调用你在代码里写好的函数接口。至于怎样把夹爪精准移动到某个坐标点这些底层的物理动作，它全交给了下层的
VLA 模型或者机器人自带的控制器去完成。

## 为什么具身大模型没有做成单体，反而分成了高低层

初看这种设计，很多人心里会冒出一个疑问：在大模型时代，我们讲具身智能的架构演进，直觉上难道不应该是一个超大模型从视觉像素直接管到电机控制吗？为什么像
ER 2 这样的大大脑反而把动作控制交了出去，看起来好像把系统给拆开了？

答案在于物理世界有两个无法规避的硬约束。

第一个约束是运行频率与算力的物理张力。负责思考高层逻辑的大大脑要看懂复杂场景、理解人类意图、考虑几分钟后的任务，它必须足够庞大，而公开的
streaming ER 2 视觉输入上限为每秒 1 帧；Google
没有披露模型推理频率或端到端延迟。而在底层，以 Figure 为例，Helix
的动作策略以 200 Hz 运行，Helix 02 的平衡层以 1 kHz
处理接触与协调。Google 没有披露 Gemini Robotics 2
的对应频率。在现有的硬件算力下，超大模型跑不了 200 Hz 的高频，而能跑 200
Hz 的轻量小模型又塞不下全网的通用常识。

第二个约束是软件解耦与硬件隔离。高层语义推理不需要关心具体的机械臂臂长或者灵巧手关节数，完全可以做成通用的云端
API
供全球开发者共享；而底层的动作控制必须深度绑定具体的硬件动作空间与物理安全。这种高低频分离的结构，就像人类的大脑皮层负责慢速思考决策，而小脑和脊髓反射弧负责快速肌肉控制一样。

## 解构两次合并：感知、规划与控制的重组

*传统 Sense-Plan-Act 三模块架构与基础模型时代 VLM + VLA 两层架构的对比*

传统 Sense-Plan-Act
三模块架构与基础模型时代 VLM + VLA 两层架构的对比

明白了为什么要保留高低层分工，就能更清晰地看懂大模型带来的两次真实合并。早在
1969 年斯坦福研究院（SRI）打造移动智能机器人 [Shakey](https://ethw.org/Milestones:SHAKEY:_The_World%E2%80%99s_First_Mobile_Intelligent_Robot,_1972)
时，工程团队建立了经典的 Sense-Plan-Act
架构，把机器人拆成了三块：视觉模块构建世界模型、STRIPS
符号规划器选择下一步，再由控制器执行。正如我们在先前的 [VLA
模型与物理控制分析](https://yage.ai/share/vla-vs-physics-robotics-20260413.html)
中所探讨的，现代基础模型的引入，实际上是在这两个局部完成了合并。

第一次合并发生在高层。过去看懂画面和推导步骤是两套独立的程序，但在 ER
2 这类 VLM
里，视觉理解与逻辑推演整合到了同一个神经网络内部。模型在接收图像输入的当下，就在同一个
VLM
中把场景理解和步骤安排一并做好了，不再需要独立的视觉检测管线与符号推理引擎。

第二次合并发生在底层。过去在规划指令和电机旋转之间，工程师需要写大量的轨迹优化代码和显式运动规划算法。到了
Gemini Robotics 2 和 On-Device 2 这类 VLA
模型里，神经网络参数直接学会了怎样生成轨迹，把视觉图像和高层指令直接映射成电机控制信号，把一部分原本显式的运动规划压进神经网络权重；不过碰撞规划、平衡、力控和功能安全仍需要底层控制器负责。从
2022 年 Google 在 [SayCan 项目](https://say-can.github.io)
中用 PaLM 做高层规划器，到 [RT-2 论文](https://arxiv.org/abs/2307.15818) 尝试将动作离散
token 化，再到 2024 年的 Figure Helix 采用 7-9 Hz 的 S2 VLM 与 200 Hz 的
S1 动作策略、2026 年的 Helix 02 又加入 1 kHz 的 S0 平衡层，以及 Physical
Intelligence 的 [π 系列模型](https://physicalintelligence.company/blog/pi0)
演进，这些代表性系统正在收敛到相似的架构思路：高层整合感知与推理做思考，下层整合感知与运动规划做控制。

*从 1969 年 Shakey 到 2026 年 Gemini Robotics 2 的机器人架构演化时间线*

从 1969 年 Shakey 到 2026 年 Gemini
Robotics 2 的机器人架构演化时间线

## Gemini Robotics 2 的三项工程落地

在这样的架构逻辑下观察 Gemini Robotics
2，它的成果主要体现在三个落地维度：首先是高层具身推理模型的标准化 API
交付。Gemini Robotics ER 2 基于 Gemini 3.5 Flash 底座，给到了 128k
的上下文窗口，不仅能接收文本、图像、视频和音频，标准版处理图像和视频输入，另一个
streaming preview 还能通过 Live API 接收最高每秒 1 帧的 JPEG
视觉输入，直接输出 Tool Calls 和你在 [官方代码示例](https://github.com/google-gemini/robotics-samples)
里写的后端代码拼在一起。

其次是同一个模型权重能跨硬件跑。Google 在测试中展示，云端 VLA
模型用同一个权重 Checkpoint，就能同时跑在装了 SharpaWave 多指灵巧手的
Apptronik Apollo 2、装了 Inspire 手的 Apollo 2，以及装了 Robotiq 夹爪的
Franka Duo 上。

再次是端侧 VLA
模型对示范数据量的需求明显变小了。主要评估于站立双臂操作的 On-Device 2
模型展示了几小时级示范数据下的适配曲线：在 SO101 本体上只用了 0.25 到
1.7 小时/任务的示范数据，任务成功率就从 6.7% 冲到了 53.3%；在 Dexmate
本体上用了 0.3 到 2 小时/任务的数据，成功率也从 24.4% 提升到了
75.6%。

不过从具体的物理操控测试来看，官方公布的数据也如实展示了不同任务的难度差异。装了
22 自由度 SharpaWave 灵巧手的机器人在拧下灯泡测试里拿到了 92%
的成功率，在货架和桌面抓取测试里也有 76.3% 和
68.4%。但是在系垃圾袋（44%）、封保鲜袋（40%）、拧入灯泡（36%）以及扫入簸箕（32%）这些涉及柔性捏拉和精密力控的复杂动作上，依然有不小的提升空间。

## 衡量通用大脑的维度：本体接入税

当高层推理做成标准 API
之后，我们看通用机器人大脑的角度也跟着变了。光展示适配了多少种机械手臂还不够，真正落到工程应用里，大家最关心的其实是把新机器人接进来要花多少综合成本。这里可以把这笔开销称为”本体接入税”。要把通用大脑装进一台全新的机械臂或者人形机器人本体里，往往需要付出数据、算力、控制协调和安全适配等多方面的代价。

这笔接入开销主要来自四个方面： 1.
示范数据采集成本：人工去录制成功轨迹需要投入的人工工时与场地搭建成本；
2.
模型微调与算力消耗：端侧或者云端权重恢复泛化能力需要消耗的训练时间和算力；
3. 控制频率与延迟适配：高层 API
的推理速度能不能跟上底层控制器的运行步伐； 4.
安全保障与边界测试：高层模型的语义安全拒绝机制（比如在 [ASIMOV-Agentic
安全报告](https://storage.googleapis.com/deepmind-media/gemini-robotics/Gemini-Robotics-2-Safety.pdf)
中评估的危险指令拦截）替代不了底层的硬件功能安全认证，现场依然需要独立的物理安全控制器和硬件冗余保护。

Gemini Robotics On-Device 2 展示的每任务约 0.25 到 2
小时示范数据适配实验（这里指示范数据采集量，不是训练耗时），给降低接入成本提供了一个很好的工程范例。不过要从实验室走进工厂流水线和千家万户，具身智能系统依然需要在生产级可靠性与综合接入开销之间找到一个可验证的平衡点。

从 Shakey 时代由人工设计的感知、符号规划与控制模块，到如今 Gemini
Robotics 2
展现出的高低层大模型协作，具身智能的演进跨越了单一算法的奇迹，呈现为一场由算力、数据与物理世界硬约束共同驱动的渐进式工程再造。当大脑的思考泛化能力随云端标准化
API 逐步解构，下层的肌肉动作控制也在神经权重的内化下变得更加轻盈。

对于绝大多数开发者和 AI Builder
来说，眼下更切实的落脚点不在于演示视频里又展示了某种新的机械臂，而在于怎样在现有的高层
API
接口与真实的物理环境之间，搭好属于自己的工作流与安全防线。毕竟，当机器大脑的思考门槛大幅降低之后，谁能在具体场景里把物理接入的账单算明白、把边缘异常处理干净，谁才能真正把通用智能装进现实世界的机器身体里。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
