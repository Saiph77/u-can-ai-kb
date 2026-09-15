---
title: "MLX：Apple Silicon 上本地推理的下一个底层引擎"
date: 2026-03-31
source: https://yage.ai/share/mlx-apple-silicon-20260331.html
slug: mlx-apple-silicon-20260331
lang: zh
---
# MLX：Apple Silicon 上本地推理的下一个底层引擎

发布于 2026 年 3 月 31 日 · [查看原网页](https://yage.ai/share/mlx-apple-silicon-20260331.html)

2026 年 3 月 30 日，Ollama 宣布在 Apple Silicon 上切换到 MLX
作为推理引擎（preview
阶段）。这个消息在社区引发了广泛讨论，但讨论的焦点大多集中在 Ollama
本身。更值得关注的是 Ollama 选择切换的对象：Apple 的 MLX 框架。MLX
是什么，它在 Apple Silicon
上做对了什么，它的生态发展到了什么程度，当前的局限在哪里——这些问题比
Ollama 的版本更新本身更有长期价值。

## 1. MLX 是什么

MLX 是 Apple 为自家芯片设计的机器学习框架。它的核心设计围绕 Apple
Silicon 的统一内存架构展开：CPU 和 GPU 共享同一块物理内存，tensor
操作可以在两者之间零拷贝传递，省去了传统框架中 CPU→GPU
内存搬运的开销。对于 LLM
推理这种以内存带宽为主要瓶颈的任务，这个架构优势直接转化为性能收益。

框架本身在 GitHub 上有 24.9k stars，配套的推理工具 mlx-lm 有 4.3k
stars。HuggingFace 上的 mlx-community 组织已经积累了 4,316
个预转换模型，几乎所有主流开源模型在发布后数天内就有社区 MLX
量化版本。

## 2. 为什么 Apple Silicon 用户应该关注 MLX

### M5 Neural Accelerators：硬件为 MLX 定制

2026 年 1 月，Apple 发表了一篇研究论文（[Apple
ML Research](https://machinelearning.apple.com/research/exploring-llms-mlx-m5)），展示了 M5 芯片每个 GPU 核心集成的专用 Neural
Accelerators 在 MLX 上的表现：Qwen3-14B-4bit 的 time-to-first-token 比
M4 快 4.06 倍，token 生成快 1.19 倍。这个提升来自专门为 MLX
计算模式设计的硬件电路，而非更高的 GPU 频率或更大的带宽。

这释放了一个明确的信号：Apple 在芯片设计阶段就为 MLX
优化了硬件。Neural Accelerator 专门针对 MLX 的计算图，意味着 MLX 在
Apple Silicon 上的性能优势会随芯片迭代持续扩大。而 llama.cpp 的 Metal
backend 本质上是把 CUDA 计算模式翻译成 Metal
shader，存在一层抽象损失，无法自动受益于这些专用硬件。

### WWDC 2025 的官方定位

WWDC 2025 上，Apple 用三场专题讲座将 MLX 确立为 Apple Silicon 上 LLM
推理的首选框架，并发布了 Foundation Models
framework——一个面向应用开发者的 Swift API，直接调用端侧的 ~3B
参数模型。MLX 面向研究人员和高级开发者，Foundation Models
面向应用开发者，两层并行。Ollama 在 2026 年 3 月宣布切换到
MLX，是这条路线的又一个验证。

## 3. 性能表现

### Decode 阶段：MLX 的强项

在 steady-state token 生成阶段，MLX 在 Apple Silicon
上的优势有多个独立 benchmark 支撑。

Mac mini M4 Pro (64GB) 上跑 Qwen3-Coder-30B-A3B（MoE 架构），MLX 约
130 tok/s，Ollama（llama.cpp 后端）约 43 tok/s，差距 3 倍（[Reddit
r/LocalLLM](https://www.reddit.com/r/LocalLLM/comments/1s18yrt/)）。M4 Max (128GB) 上跑 Qwen3.5-35B-A3B，MLX 130 tok/s vs
Ollama 43.5 tok/s（[antekapetanovic.com](https://antekapetanovic.com/blog/qwen3.5-apple-silicon-benchmark/)）。MoE
模型上 MLX 优势最大，可达 3 倍；Dense 模型上约 1.4-1.6 倍。

一个经常被忽略的细节：同样的 M4 Max 上，裸 llama.cpp（Metal
backend）的性能是 89.4 tok/s，而 Ollama 只有 43.5 tok/s（[GitHub
#14861](https://github.com/ollama/ollama/issues/14861)）。Ollama 的 Go wrapper 层吃掉了约 50%
的性能。也就是说，社区常说的 MLX 比 Ollama 快 3 倍，有相当一部分归因于
Ollama 自身的架构开销，而非 MLX 对 llama.cpp 的全面碾压。MLX 对裸
llama.cpp 的实际优势在 1.4-1.8 倍左右。

### Prefill 阶段：MLX 的弱项

MLX 在 time-to-first-token（首 token 延迟）上反而落后于
llama.cpp。一位开发者在 M1 Max 上的实测数据（[Reddit
r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/comments/1rs059a/)）：prompt 约 650 tokens 时，MLX 的 effective
tok/s（综合 prefill 和 decode）只有 13 tok/s，GGUF 达到 20 tok/s。原因是
MLX 94% 的时间花在了 prefill 上。

这直接影响实际使用体验。如果你用模型做 coding
agent（长输出、单次请求生成大量 token），prefill 开销会被分摊到数千个
decode tokens 中，MLX 的优势能充分发挥。但如果是聊天场景（短 prompt +
短回复），每次请求的大部分时间花在 prefill 上，MLX 的综合速度反而不如
GGUF。

### 内存效率

内存效率是 MLX 更扎实的优势。Qwen3-Coder-30B-A3B 在 MLX 上占用 34.7
GB，在 GGUF 上占用 40 GB，节省 13%（[Reddit
r/LocalLLM](https://www.reddit.com/r/LocalLLM/comments/1s18yrt/)）。Qwen3-235B-A22B 在 MLX 上 124 GB vs GGUF 133 GB，节省
7%（[MacStories](https://www.macstories.net/notes/)）。根因是
MLX 利用统一内存做零拷贝 tensor 操作，不需要在 CPU 和 GPU
之间搬运数据。这个差异在大模型上更明显，因为模型权重本身就是内存带宽的主要消费者。

### 长上下文

arXiv 论文（[2511.05502](https://arxiv.org/abs/2511.05502)）在 M2 Ultra
上的测试显示 MLX 的 decode 阶段延迟最稳定。但社区在 M3 Ultra
上的实测（[GitHub mlx-lm
#763](https://github.com/ml-explore/mlx-lm/issues/763)）显示，30K+ context 下 MLX 的 token generation 比
llama.cpp（开启 Flash Attention）慢约 50%。不同模型对长 context
的友好度差异很大。

## 4. 生态：八个 inference server 争夺同一个平台

MLX 推理生态在 2026 年初快速增长，围绕它已经形成了一批 inference
server，各自解决不同场景的问题。

Apple 官方的 **mlx-lm**（[GitHub](https://github.com/ml-explore/mlx-lm)）是最成熟的 MLX
推理工具，支持推理和 LoRA/QLoRA fine-tuning，内置 OpenAI-compatible
server mode。**Rapid-MLX**（[GitHub](https://github.com/raullenchai/rapid-mlx)，2026-03-23
发布）定位为 Ollama 的 drop-in replacement，在 M3 Ultra 上实测比
Ollama（llama.cpp 后端）快 2-4.2 倍。**vLLM-MLX**（[GitHub](https://github.com/waybarrios/vllm-mlx)）带来
continuous batching，5 并发请求时吞吐量提升 3.4
倍。**oMLX**（[GitHub](https://github.com/jundot/omlx)）专门为 coding agent
场景优化，用 SSD 做 KV cache 持久化，把重复 prefix 的 TTFT 从 30-90
秒压缩到 1-3 秒。**LM Studio** 的 mlx-engine（[GitHub](https://github.com/lmstudio-ai/mlx-engine)，MIT
开源，本体闭源）在 0.4.2 版本添加了 MLX 的 continuous batching，支持 MLX
和 GGUF 双后端自动切换。

Ollama 在这个生态中的定位是通用 LLM 工具。v0.19.0 起，Ollama
通过模型格式自动分流：GGUF 格式走 llama.cpp（Metal
backend），safetensors 格式走 MLX（[源码](https://github.com/ollama/ollama/blob/main/server/sched.go)）。它的优势是易用性和广泛的模型库，代价是
Go wrapper 层带来的性能损失。截至 v0.19.0，MLX runner 支持 6
个模型架构（Gemma 3、GLM-4 MoE Lite、Llama 全系列、Qwen 3、Qwen
3.5、Qwen 3.5 MoE），与 llama.cpp 支持的上百种架构相比仍在早期。

整个 MLX 生态当前缺少的关键能力：multi-LoRA serving（[MOLA](https://github.com/ml-explore/mlx/discussions/3323)
是唯一探索，alpha 阶段）、确定性推理（MLX 的 floating-point
nondeterminism 是框架级问题，[adityakarnam.com](https://adityakarnam.com/mlx-non-determinism-apple-silicon/)）、以及跨平台一致性。

## 5. 当前的局限

MLX 当前面临的问题，一部分是框架自身的，一部分是生态早期阶段的。

在框架层面，prefill 性能是最大的短板。MLX 采用 full prefill
策略（不像 llama.cpp 有 sliding-window cache），短 prompt
场景下开销明显。MLX 的浮点运算存在 nondeterminism 问题（batch size
变化可产生显著数值差异），对需要确定性输出的场景构成风险。

在兼容性层面，Metal 4（随 macOS 15 和 M4+
芯片引入）收紧了类型检查。以 Ollama 为例，M5 芯片用户遇到
`bfloat`/`half` 类型不匹配导致模型无法运行（[#14432](https://github.com/ollama/ollama/issues/14432)），M4
Pro + macOS 26.2 下 GPU 路径间歇性崩溃（[#14611](https://github.com/ollama/ollama/issues/14611)）。这些问题部分源于
MLX-C 的 API 在快速演进（0.5.0 → 0.6.0 有 breaking
changes），下游工具在追一个移动的靶子。

在生态层面，8 个以上独立 inference server
的碎片化是早期阶段的典型特征。每个 server 解决不同的瓶颈（continuous
batching、KV cache 持久化、LoRA
热切换），最终会收敛到少数几个主流方案，但现在做框架锁定的风险较高。

MLX 仍以 Apple Silicon 为主平台。虽然已经添加了 Linux CUDA
后端（`pip install mlx[cuda]`），但这更多是为了让研究者在非
Mac 环境中开发 MLX 模型，而非与 CUDA 原生生态竞争。在 NVIDIA GPU
上，vLLM 在 A100 上可以达到 MLX 在 M5 上数倍的吞吐量。

## 6. 对 Apple Silicon 用户意味着什么

MLX 成为 Apple Silicon 上的标准推理框架是大概率事件。Apple
在芯片设计阶段就为 MLX 优化了硬件（M5 Neural Accelerators），WWDC 2025
用三场讲座做了官方背书，Ollama 的战略转向是又一个验证。llama.cpp 的
Metal backend 把 CUDA 计算模式翻译成 Metal shader，而 MLX 从 Apple
Silicon 的硬件特性出发设计。这个差异会随着芯片迭代持续扩大。

但从当前状态到可以放心依赖，还有距离。框架 API 仍在快速变化，Metal 4
兼容性问题影响最新硬件的用户，prefill 性能在短对话场景下落后于
llama.cpp。

对于在 Mac
上跑本地模型的用户，一个务实的判断框架：如果你的主要场景是长输出（coding
agent、长文生成），MLX 的 decode 优势能充分发挥，可以开始尝试 mlx-lm 或
Rapid-MLX
作为推理后端。如果你的场景是短对话或需要广泛的模型兼容性，llama.cpp（通过
Ollama 或裸跑）仍然是更稳定的选择。如果你在构建产品，中期应该开始评估
MLX 的迁移路径，但短期内 llama.cpp 仍然是更安全的基座。

不论选择哪条路径，保持对 mlx-lm 的关注——它是 Apple
官方维护的推理工具，是整个 MLX 生态最稳定的基准。

## 相关阅读

- [LLM
  推理是怎么跑的：跟着 SGLang Omni 团队的设计思路走一遍](https://yage.ai/share/sglang-omni-llm-inference-20260530.html) — MLX
  解决的问题在数据中心端有对应的架构设计：理解推理系统的整体格局
- [开源模型推理采购指南：GLM-5.1、DeepSeek
  V4 Pro、Kimi K2.6 的 API、订阅和 Ollama Cloud 对比](https://yage.ai/share/ollama-cloud-vs-api-vs-subscriptions-20260428.html) — Ollama 切换 MLX
  对实际推理采购决策的影响：本地推理在三种选项中的成本位置
- [如何在
  Mac 上本地运行 DeepSeek V4 Flash：DS4 引擎深度解读](https://yage.ai/share/ds4-deepseek-v4-flash-mac-20260522.html) — Mac
  上本地推理的另一路径：DS4 与 MLX 代表了不同模型的本地运行策略

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
