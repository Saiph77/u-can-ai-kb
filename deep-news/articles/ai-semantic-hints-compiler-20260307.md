---
title: "LLM Semantic Hints for Compiler Optimization"
date: 2026-03-07
source: https://yage.ai/share/ai-semantic-hints-compiler-20260307.html
slug: ai-semantic-hints-compiler-20260307
lang: zh
---
# LLM Semantic Hints for Compiler Optimization

发布于 2026 年 3 月 7 日 · [查看原网页](https://yage.ai/share/ai-semantic-hints-compiler-20260307.html)

> 程序里有大量编译器证不了、但人一眼能看出的语义信息。 LLM
> 最适合把这些信息转成 noalias 等编译器可消费的提示。 真正的机会不是让 AI
> 重写代码，而是补上语义理解与形式化证明之间的 gap。

## 核心观察

程序有很多性质，从语义层面一眼就能看出来，但编译器要形式化地证明需要复杂的分析、甚至根本无法证明。

比如一个函数接收五个指针参数，循环内交替读写这些指针指向的内存。一个读过代码的人立刻知道这些指针指向五块独立分配的数组，不可能互相
alias。但编译器要证明这一点需要做 interprocedural alias
analysis：追溯每个指针的来源，穿越函数调用边界，分析所有可能的执行路径。这在实践中经常失败，尤其是跨编译单元调用、通过
opaque wrapper
分配内存、或使用多维数组的场景。编译器的应对是保守处理：要么插入运行时别名检查（增加代码大小），要么直接放弃优化（丧失性能）。

LLM 天然站在语义理解一侧。编译器天然站在形式化证明一侧。这个 gap
的存在意味着：如果 LLM
能把它的语义理解转化为编译器可消费的形式（attribute、metadata），就能直接解锁编译器已经知道怎么做、但不敢做的优化。

这不仅仅是 restrict 一个关键字的事。LLVM IR 有一系列
attribute（noalias、nonnull、align、nsw/nuw、readonly、dereferenceable、branch
weights
等），每一个都对应一类编译器想知道但证不了的性质。系统性地找出哪些
attribute 的语义-证明 gap 最大、LLM
能做到什么程度、做不到的原因是什么——这本身就是一个有意义的研究贡献。

## 为什么编译器做不到

编译器的优化能力远超它的证明能力。它知道几百种优化手段，但在大量真实代码中卡在「证不了安全」这一步。根本原因是
C/C++ 的类型系统太弱，没有足够的手段编码语义信息。

以 Polybench 中的 gesummv 为例：函数接收矩阵 A、B 和向量 tmp、x、y
共五个数组参数，内层循环中同时读写多个数组。编译器看到的是五个 double
(\*)[N] 类型的指针，C
类型系统没有任何机制表达「这五个指针指向不相交的内存」。即使每个数组都是独立
malloc 出来的，只要分配发生在另一个编译单元（比如 Polybench 的
polybench\_alloc\_data
函数），编译器在当前编译单元看不到分配点，就无法推断。

对照组：Rust 的 borrow checker 天然给 LLVM 提供了 C
无法表达的别名信息（&mut reference 自动携带 noalias 语义）。同一个
LLVM 后端，Rust 前端生成的 IR 通常能获得更好的优化。这不是 Rust
编译器更聪明，而是它看到了更多信息。

本文的方向本质上是：让 AI 扮演一个「虚拟类型系统」，给 C/C++
代码提供类似 Rust 级别的语义信息，但不需要程序员改变编程习惯。

实验验证：Gap 的大小取决于代码复杂度 我们用 restrict（对应 LLVM IR 的
noalias）作为第一个测试 attribute，在两组不同复杂度的 benchmark 上验证了
gap 的存在和大小分布。

### 简单模式：编译器已经处理得很好

第一组实验使用 10 个手写
kernel，覆盖向量更新、归约、矩阵乘法、stencil、稀疏矩阵、卷积、前缀和、直方图等计算模式，一维数组指针参数。所有
kernel 标记 noinline 阻止编译器通过内联看到分配点。Clang 19, -O2, Apple
Silicon。

结果：只有 1/10 的 kernel（Stream
Triad）展现了可测量的运行时提升（+5.4%）。3/10 的 kernel 有 8-18%
的代码大小减少。其余 7/10 完全不受影响。

Opportunity Sizing

不受影响的原因分三类：归约模式（Dot Product, GEMV, Conv
2D）的内层循环将结果累加到局部标量变量，循环体内不写数组，编译器不需要别名信息就能向量化。无法向量化的模式（Prefix
Sum, Histogram, SpMV）性能瓶颈不在别名分析上。对于受影响的
kernel，编译器在 plain 版本中生成了运行时别名检查代码（比较指针地址差 →
决定走向量化还是标量回退路径），restrict 消除了这些检查。但检查本身是
O(1) 的，循环体是 O(N)，对于大数组而言检查开销被摊薄到可忽略。

初看之下，restrict
的价值有限。但这个结论只对简单的一维数组模式成立。

复杂模式：编译器的 gap 显著放大 第二组实验使用 Polybench/C
4.2.1（编译器优化领域的标准 benchmark suite）中的 10 个 kernel，覆盖
BLAS、线性代数内核、stencil、数据挖掘四个子类。Polybench 的 kernel
使用二维 VLA 参数（double A[restrict
N][N]），涉及更复杂的多维数组访问模式和更多的指针参数。Polybench 自带
restrict 支持（-DPOLYBENCH\_USE\_RESTRICT），同样注入 noinline。

结果完全不同：6/10 的 kernel 展现了 >5% 的运行时提升，最高达到
+34.9%（BiCG）和 +25.7%（SYR2K）。正确性验证确认 10 个 kernel 的 plain
和 restrict 版本在 -DPOLYBENCH\_DUMP\_ARRAYS 下输出完全一致，restrict
只影响性能，不改变计算结果。

Polybench Results

Kernel 运行时加速 代码大小变化 机制

BiCG +34.9% +88% 向量化使能

SYR2K +25.7% +80% 向量化使能

FDTD 2D +13.2% -5% 别名检查消除

Jacobi 2D +9.8% -28% 别名检查消除

Heat 3D +9.5% -35% 别名检查消除

SYMM +6.9% -4% 别名检查消除

2MM +2.7% -2% —

Correlation +1.3% -17% —

MVT +1.1% -31% —

GEMM +0.4% -16% —

通过比较 -Rpass 向量化报告，restrict
的收益来自两种截然不同的机制。

机制一：向量化使能。 BiCG 和 SYR2K 中，编译器在 plain
版本中完全放弃了内层循环的向量化（报告 “loop not vectorized” 或
“vectorization not beneficial”）。加上 restrict 后，同样的循环变成了
“vectorized (width: 2, interleaved:
4)”。编译器不是不会向量化，而是不敢——因为无法证明多个数组参数不
alias。这正是语义-证明 gap 最大的场景：LLM
一眼就能看出五个数组参数来自独立分配，编译器需要穿越整个调用链才能（尝试）证明。这种
gap 产生了 25-35%
的运行时收益。代码反而变大了（+80-88%），因为向量化循环本身就比标量循环占用更多指令空间。

机制二：别名检查消除。 三个 stencil kernel（Jacobi 2D, FDTD 2D, Heat
3D）的向量化决策在两个版本中完全相同。restrict
消除的是运行时别名检查分支和标量回退路径，产生了 9-13% 的运行时收益和
5-35% 的代码大小减少。

两组实验的对比揭示了一个关键规律：gap 的大小取决于编译器 alias
analysis 的难度。一维数组、两个指针 → 编译器自己能处理（gap 小）。二维
VLA、五个指针交叉读写 → 编译器束手无策（gap 大）。而需要 AI
辅助编写的恰恰是后者——复杂的数据结构和算法实现。

超越 Restrict：哪些 Attribute 有最大的语义-证明 Gap Restrict/noalias
只是 LLVM attribute 体系中的一个。系统性地 map 每种 attribute
的「语义理解难度」和「形式化证明难度」，才能找到 AI
辅助编译优化的完整机会空间。

以下是 LLVM 中主要 attribute 的初步分析：

Attribute 编译器证明难度 LLM 识别难度 解锁的优化 分析

noalias 高（interprocedural alias analysis） 低（看分配点即可）
向量化、LICM 已验证。Polybench 上最高 +35%

nonnull 中高（interprocedural null flow） 低（看分配和错误处理） null
check 消除 malloc 返回值、经过 null check 的指针。LLM
能直接看到控制流

align(N) 中高（需跟踪对齐穿越分配链） 低（知道分配 API 的对齐保证）
aligned SIMD load/store 已验证。Polybench 的 posix\_memalign(4096)
返回值注入 assume\_aligned(64) 后，30 kernel 中仅 5 个有 >2% 加速，14
个反而变慢。Apple Silicon 上是弱杠杆

nsw/nuw 高（value range analysis） 中（需理解值域）
循环优化、算术简化 循环变量从 0 到 N 递增不会 overflow，LLM
能从循环结构推断。但嵌套计算的 overflow 推理更难

readonly/writeonly 高（需 whole-program 分析） 低中（读函数体）
CSE、dead store elimination、LICM 单函数分析 LLM 很准确。跨模块依赖时
LLM 也可能看不全

dereferenceable(N) 高（escape analysis + lifetime） 低（看 buffer
大小和生命周期） speculative load、LICM LLM 知道 malloc(100) 返回的指针
dereferenceable(100)

branch weights 不可能（无 PGO 数据无法知道） 中（理解错误处理 vs
正常路径） 代码布局、分支预测 最极端的 gap：编译器在没有 PGO
数据时完全盲目，LLM 能理解 “这是 error handling，很少走到”

!range 高（value range propagation） 中（理解输入域约束） bounds
check 消除、narrowing enum 值、数组下标、已 validated 的输入。LLM 能理解
“这个值是从 0-255 的 pixel”

几个观察。

Gap 最大的 attribute：noalias（已验证）和 branch weights。前者因为
interprocedural alias analysis
是编译器最难的分析之一。后者因为编译器在没有 PGO profile
的情况下对分支概率完全没有信息，而 LLM 能从代码语义理解哪些是 error
path、哪些是 hot path。

LLM 最擅长的维度：指针相关的
attribute（noalias、nonnull、dereferenceable、align），因为这些性质通常在分配点就确定了，LLM
能直接看到分配 API 的语义。

LLM 可能挣扎的维度：值域相关的
attribute（nsw/nuw、!range），需要对算术运算链做推理，LLM
的数值推理能力是已知弱点。不过循环变量的简单 case（0 到 N
递增）应该没问题。

最有实践价值的方向：同时满足「编译器证明难度高」+「LLM
识别难度低」+「解锁的优化收益大」三个条件的 attribute。目前看来
noalias、branch weights、nonnull + dereferenceable 是最优先的目标。

## 相关工作

### AI × 编译器优化

截至 2025 年，这个方向有五类主要工作，没有一类和本文的想法重合。

替换编译器启发式。 Google MLGO（2021+）用 RL 替换 LLVM 的
inlining/register allocation 决策，已部署在 Chrome、Fuchsia、Android
中。Magellan/AlphaEvolve（2025）用 Gemini 演化 LLVM heuristic 函数的 C++
代码，在 inlining-for-size 上比上游 heuristic 好
4.27%。这类工作不改变编译器看到的信息量，只在固定信息条件下做更优的决策。

预测优化 pass 序列。 Meta LLM Compiler（2024，7B/13B，546B token
LLVM-IR 训练）预测最优 pass 序列，达到 autotuning 搜索 77%
的效果。IR-OptSet（NeurIPS 2025）提供 170K 样本 LLVM IR
优化数据集，fine-tune 后的 LLM 在部分 case 上超过
-O3。同样是在已有信息下做选择。

重写源码。 LLNL 的 CompilerGPT（2025）让 LLM 读编译器 optimization
remark 后重写代码，在 prefix sum 上拿到 6.5x
提升。这改变了程序实现本身，需要证明语义等价。

领域特定 pragma 插入。 TimelyHLS / LIFT（2024-2025）让 LLM 向 C
代码插入 FPGA HLS pragma（#pragma HLS pipeline、#pragma HLS
unroll），3.5x 加速。这在 HLS 垂直领域验证了「AI 插 pragma →
编译器消费」的 pipeline 可行性，但 HLS pragma
的正确性约束比通用编译器的语义标注宽松得多（HLS pragma
错了通常只是性能不好，不会 wrong result）。

LLM 增强静态分析。 Cheng et al.（北大/华科/NTU/蚂蚁/UNSW，2025）的
CAFD 系统用 LLM（Qwen3-14B、LLaMA-3.2-3B、Phi-4、DeepSeek-R1）检测 C
代码中的自定义内存分配函数。核心观察：真实 C 项目中大量堆分配通过
xmalloc、g\_new 等项目特定的 wrapper 完成，标准指针分析工具（如
SVF）无法识别，导致别名集膨胀。CAFD 在 17 个大型 C 项目中找到 700+
个自定义分配函数，别名集缩小 41.5%。这项工作验证了「LLM 语义理解 →
更精确的别名信息」这条路径，但方向是分析已有代码来恢复丢失的语义信息。本文提出在生成阶段直接嵌入。两者互补：CAFD
处理存量代码，本文方案处理增量代码。

### AI 生成代码的质量研究

多项研究（Licorish et al. 2025，Molison et al. MSR 2025，Abbassi et
al. ICSME 2025）比较了 LLM
生成代码和人写代码的质量。关键事实是：这些研究全部聚焦于
correctness、maintainability、security 等维度，没有任何研究讨论过 AI
生成代码的「编译器可优化性」。

### 语义信息丢失问题

LLVM 社区对这个问题有切身体会。ISSTA 2025 的 “Type-Alias Analysis:
Enabling LLVM IR with Accurate Types”（Zhou et al.）指出 LLVM 转向
opaque pointer 后丢失了类型信息，导致 alias analysis 退化。nikic 的 2024
LLVM 年度回顾也提到，GEP 上新增的 nuw flag 是因为「frontend
过去没有手段向 LLVM 传达 offset 非负」。这些都是语义 gap
的直接证据。

### 形式化验证工具

Alive2（Lopes et al., PLDI 2021）是 LLVM 的 translation validation
工具，能形式化验证 IR 变换的正确性。可以用来验证 AI 生成的 attribute
是否引入了未定义行为。2024 年有工作将 fine-tuned LLM 和 Alive2 结合，当
SMT solver 超时时用 LLM 预测变换正确性再用 fuzzing 确认。这种「形式化 +
AI + fuzzing」的分层验证策略可以直接复用。

## 核心挑战

挑战一：Metadata 在修改中的失效 AI 在 t=0 时刻生成的 metadata
是正确的，但代码在 t=1, t=2, … 不断被修改。修改可能打破 metadata
依赖的假设。比如最初 a 和 b 指向独立的 malloc，后来有人改成了 b = a +
offset，这时 restrict 就不再成立了。

这是核心挑战，也是最有研究价值的问题。

### 挑战二：LLM 本身的可靠性

即使在生成时刻，LLM 也可能生成不一致的代码和
metadata。比如代码里实际做了 b = a + 1，但 metadata 声明了 restrict(a,
b)。metadata 的正确性是在代码正确性之上的第二层要求。

### 挑战三：训练数据缺失

现有训练数据中很少有带优化标注的代码。人类程序员几乎不写
restrict、\_\_builtin\_expect、alignment attribute。LLM
需要被明确引导才会生成这些标注。

### 挑战四：跨模块失效

一个函数的 metadata
可能依赖于调用方或被调用方的行为。跨模块的变化检测比模块内的更难。

## 可能的解决方法

JIT 编译器的先例：Speculative Optimization + Deoptimization JIT
编译器（V8、HotSpot/Graal、PyPy）长期使用一种成熟的模式处理「基于假设的优化」：收集
profile → 基于假设生成优化代码并插入 guard → guard 失败时
deoptimize。POPL 2021 的 “Formally Verified Speculation and
Deoptimization in a JIT Compiler” 用 Coq 形式化验证了这种模式。

AI 生成的 metadata 等价于 JIT 中的「假设」，guard 等价于 runtime
assertion，deoptimization 等价于回退到无 metadata 的保守编译。区别在于
JIT 在运行时动态做，AOT 场景需要在编译时 + 测试时完成。

Design by Contract（Eiffel/Meyer） AI 生成的 metadata 本质上就是一种
contract。restrict(a, b) 是一个 invariant：「在此函数执行期间，a 和 b
不指向重叠内存」。DbC 在主流语言中推广不开的原因是维护成本太高。但如果
contract 由 AI 自动生成和维护，这个成本障碍就消失了。

### 分层验证策略

第一层（编译时）：静态分析检查 metadata
是否和代码存在明显矛盾。第二层（测试时）：每个 metadata 伴随 runtime
assertion，在 debug 构建和 CI
中启用。第三层（形式化验证）：对性能关键路径用 Alive2
验证。任何一层检测到问题，metadata 自动移除（优雅降级）。

## 验证计划

实验一：General Opportunity Sizing（已完成） 目标：确定
restrict/noalias 在不同代码复杂度下的收益分布。

已完成内容：(1) 10 个手写 kernel（一维数组，简单模式），(2) 10 个
Polybench kernel（二维
VLA，复杂模式）。已完成测量运行时性能和汇编代码大小差异。

核心发现：gap
大小取决于代码复杂度。简单一维模式下编译器自己能处理（1/10 有 >5%
加速）；复杂多维模式下编译器 alias analysis 失效（6/10 有 >5%
加速，最高 +35%）。restrict 通过两种机制产生收益：向量化使能（gap
最大时）和别名检查消除（gap 中等时）。

实验二：推上限 + 归因分析（全 Polybench，30 kernels） 目标：在
Polybench 全部 30 个 kernel 上推出更多优化的性能上限，同时归因分析 LLM
的能力边界。

方法论：holistic profile → 跨 kernel 聚合 → 批量优化

不逐 kernel 分析，而是先收集所有 kernel 的 -Rpass-missed 报告，跨
kernel 聚合统计 missed optimization 的类型分布。这样即使某个
optimization 在每个 kernel 中都不是最大的瓶颈，只要它出现在多数 kernel
中，它的总杠杆就值得优先处理。确定优先级后，对所有 kernel
批量应用同一类优化，一次性测量全局效果。

Missed optimization 全景：对 30 个 kernel 的 plain 和 restrict
版本收集了完整的 -Rpass-missed remarks。Restrict 解决了 126 条 GVN（冗余
load）、96 条 SLP vectorizer、71 条 LICM（load 提升）和 23 条
loop-vectorize 的 missed optimization。残留问题按 kernel
覆盖度排序：LICM 仍失败（19/30 kernels）、cost model
拒绝向量化（14/30）、GVN 未消除（11/30）。LICM 残留的典型 pattern
是累加器 q[i] += A[i][j] \* p[j] 中 q[i] 无法提到循环外，推测 LLVM 的
alias analysis 无法将参数级 noalias 完全传播到 VLA derived pointer 的
load/store 上。

强制向量化验证：用 -mllvm -force-vector-width=N 覆盖 cost model
决策后，30 个 kernel 中有 13 个获得 >10% 的额外加速，最高达到
+84%（gesummv）。同时有 2 个 kernel 变慢（symm -22%, correlation
-10%），说明 cost model 在部分 case 上的保守判断是正确的。

两种优化的叠加效果显著。 Restrict alone：10/30 kernels 有 >5%
加速，均值 +7.3%。加上 fvw 后：19/30 有 >5% 加速（63%），13/30 有
>20% 加速（43%），均值 +30.6%。最高累积加速 +88.4%（bicg）和
+88.2%（trisolv）。正确性验证：30/30 kernel 的 restrict 版本输出与 plain
版本完全一致。

四类 kernel 的归因分析。按「什么优化手段有效」将 30 个 kernel
分为四类：(A) restrict + fvw 双重收益（4 个，如
bicg/trisolv），有复杂多指针模式 AND cost model 不准确。(B) 主要受益于
restrict（3 个，如 syrk +32%），alias analysis 是唯一瓶颈。(C)
主要受益于 fvw（9 个，如 gesummv +85%/durbin +78%），alias 不是问题但
cost model 误判。(D) 无显著收益（7 个，如
floyd-warshall），计算模式不适合或编译器已足够好。

这揭示了两类不同的语义-证明 gap。第一类是正确性证明 gap：编译器缺乏
alias 信息，无法证明优化的安全性。LLM
通过理解内存布局来弥补（风险高，标错是 UB）。第二类是策略判断
gap：编译器有能力执行优化但 cost model 判断错误。LLM
通过理解计算模式来弥补（风险低，选错只是变慢）。两者互补叠加，单一手段只能覆盖
23-43% 的 kernel，两者结合覆盖 63%。

对齐标注的实验否定了第三种 gap 的显著性。 Polybench
的内存分配函数内部使用 posix\_memalign(&ret, 4096, …)，所有数组至少
4096 字节对齐。但编译器看到的是 void\*
返回值，不知道对齐保证。通过在函数声明上添加
**attribute**((assume\_aligned(64)))
将这一信息传递给编译器后，30 个 kernel 中仅 5 个有 >2% 加速（gesummv
+30%, durbin +29%, gemver +29%），14 个反而变慢（平均 -12%），整体均值
-2.2%。原因是 Apple Silicon NEON 的 unaligned load 与 aligned load
性能几乎没有差别，对齐信息对 cost model
的影响在这个架构上很小。额外的属性还可能扰动 LLVM 的 pass
序列，导致次优的指令调度。这个 negative result 确认了优先级排序：noalias
>> 向量化建议 >> 对齐标注。不过在 x86 平台（尤其早期 SSE
需要对齐到 16 字节）上结论可能不同，值得未来验证。

从 learnings 到 agentic optimizer：一个有效的 agentic optimizer
需要两个模块。Alias annotator 分析函数签名和调用上下文，提供 noalias
信息（保守策略）。Vectorization advisor 分析循环结构和 -Rpass-missed
输出，提供向量化建议（speculate-then-verify
策略）。两个模块独立运行、结果叠加。两个模块已实现为 opencode
skill，设计理念来自「结果确定性」：不规定过程、只定义验证标准，让 agent
在 feedback loop 中自行迭代。每个 kernel 的决策结果（含失败样本）追加到
optimizer\_learnings.md，形成知识飞轮。

实验三：TSVC-2 泛化验证（Gap 2 跨 benchmark） Polybench
的代码模式比较同质（线性代数和 stencil），两类 gap 的发现是否只是特定
benchmark 的巧合？TSVC-2（Test Suite for Vectorizing Compilers,
v2）提供了不同的验证场景：151 个 kernel、涵盖归约、循环重构、induction
variable 识别、控制流、间接寻址等多种计算模式。

TSVC-2 的结构特点消除了 Gap 1。TSVC-2 使用全局 static
数组（**attribute**((aligned(64)))），编译器天然知道这些数组之间互不
alias。因此 restrict 实验在 TSVC-2
上没有意义。这反过来提供了一个干净的隔离：TSVC-2 上的实验结果纯粹反映
Gap 2（cost model 判断失误），不混入 Gap 1 的贡献。

146 个有效 kernel 的 fvw 实验显示 Gap 2 是普遍现象。 33/146 kernel
(23%) 通过 fvw override 获得 >5% 加速，19 个 >20%，mean +9.2%。与
Polybench 相比（fvw 贡献 63% 覆盖率），TSVC-2 的 23%
看起来更低，但差异主要来源于 Polybench 同时存在 Gap 1。单看 Gap 2
的贡献（Polybench 中 C 类 kernel 9/30 = 30%），两个 benchmark
的表现一致。

最重要的发现：14 个纯 cost model gap 案例。 这些 kernel
中编译器完全没有自动向量化（autovec gain ~0%），但强制向量化后加速
25-94%。按模式分：前 6 个全是 reduction（sum: s311 +93%, product: s312
+94%, coupled: s319 +89%），其余涉及间接寻址和 induction variable
识别。编译器在 -O3（不含 -ffast-math）下拒绝向量化 FP reduction，原因是
reduction tree 改变了运算顺序。但实际上这些 kernel
的数值敏感度很低，向量化带来的 FP 差异（最大 relative diff
6.87e-4）完全可接受。这是典型的策略判断
gap：编译器有能力做这个优化，安全性也没问题（只是 FP 顺序变化，不是
UB），但 cost model 判断「不值得」。

FVW4 优于 FVW2 的硬件启示。 在 float32 + 128-bit NEON（4 lanes
自然宽度）下，fvw4 mean +8.9% 而 fvw2 mean -3.6%。强制比自然宽度窄的
SIMD 反而退化。这为 vectorization advisor 提供了可靠的
heuristic：default to hardware natural vector width。

编译器 cost model 在多数场景下判断正确。 107/146 kernel (73%) 在 ±5%
范围内不受 fvw 影响，说明 cost model 的保守在大多数 case 中是正确的。FVW
的价值集中在少数 cost model
失灵的场景，这些场景的特征是可学习的（reduction、indirect
addressing、induction variable patterns）。

## 下一步

继续推上限。对齐标注已测试（弱杠杆，见上）。下一步测试 IR 级 !noalias
scope metadata 的增量收益，可能解决 19/30 kernel 中残留的 LICM
问题（restrict 在源码级提供了参数间的 noalias，但 LLVM 的 alias analysis
未能将其完全传播到 VLA derived pointer 的 load/store 上）。

构建 agentic optimizer prototype。两个模块已实现为 opencode
skill（skill\_compiler\_alias\_annotator.md 和
skill\_compiler\_vectorization\_advisor.md）。每个 skill
定义验证标准而非逐步过程，遵循「结果确定性」设计哲学：alias annotator
要求 diff 通过 + 编译干净 + 性能量化；vectorization advisor 要求数值容差
1e-2 内 + 性能量化。两个 skill 都包含 knowledge accumulation
机制，每完成一个 kernel 的决策都 append 到 optimizer\_learnings.md，形成
compounding effect。下一步在 Polybench 的 23 个非 D 类 kernel 上测试
skill 的准确度。

写作：Polybench 全集 + TSVC-2 的数据足以支撑一篇论文。核心贡献：(1)
两类语义-证明 gap 的发现和量化（正确性证明 + 策略判断），(2) Polybench
30 个 kernel 上 63% 覆盖率和 +30.6% 均值加速的叠加效果，(3) TSVC-2 146
个 kernel 验证 Gap 2 的普遍性（23% 覆盖率），(4) 四类 kernel
的归因分析和 agentic optimizer 的设计框架。

## 总结

核心 thesis 不是「AI 能让代码跑得更快」——这太泛了。核心 thesis
是：程序性质存在一个「语义理解容易、形式化证明困难」的 gap，LLM
天然适合弥补这个 gap，而这个 gap 直接映射到编译器的优化能力边界。

两个 benchmark 的实验验证了这个 thesis。Polybench/C 30 个 kernel
验证了两类 gap 的存在和叠加效果：正确性证明 gap（restrict/noalias）覆盖
10/30 kernel，策略判断 gap（fvw）覆盖额外 9/30 kernel，叠加后 19/30
kernel（63%）获得 >5% 加速，均值 +30.6%，最高 +88.4%。TSVC-2 的 146
个 kernel 验证了 Gap 2 的普遍性：33/146 (23%) 获得 >5% 加速，其中 14
个是纯 cost model gap 案例（编译器完全没有自动向量化，但实际可获 25-94%
加速）。对齐标注的 negative result
表明并非所有语义信息都有同等价值，属性的选择本身需要架构感知的判断。

两类 gap 对应两种 agentic optimizer 模块。Alias annotator 处理 Gap
1（保守策略，判错是 UB），vectorization advisor 处理 Gap
2（speculate-then-verify，判错只是变慢）。两个模块已实现为 opencode
skill，设计上遵循「结果确定性」原则，以可验证的交付标准取代过程规定。下一步在
Polybench 23 个非 D 类 kernel 上测试 skill 的准确度和自动化程度。

初稿：2026-03-07，更新：2026-03-08。Polybench 30 kernel + TSVC-2 146
kernel 实验完成。含 restrict、强制向量化、对齐标注、TSVC-2
泛化验证四轮实验。Polybench 30/30 正确性通过，19/30 有 >5%
加速。TSVC-2 33/146 有 >5% 加速（纯 Gap 2）。两个 agentic optimizer
skill 已完成设计。

🔊

(function() { ‘use strict’; if (!(‘speechSynthesis’ in window)) {
document.getElementById(‘tts-controls’).style.display = ‘none’; return;
}

var synth = window.speechSynthesis; var btn =
document.getElementById(‘tts-btn’); var status =
document.getElementById(‘tts-status’); var CHUNK\_SIZE = 200;

var chunks = []; var currentChunk = 0; var isPlaying = false; var
isPaused = false;

function getArticleText() { var body = document.body.cloneNode(true);
body.querySelectorAll(‘#tts-controls, pre, code, script, style,
table’).forEach(function(el) { el.remove(); }); return
body.innerText.trim(); }

function splitText(text) { var result = []; var sentences =
text.split(/(? CHUNK\_SIZE && buf.length > 0) {
result.push(buf.trim()); buf = sentences[i]; } else { buf +=
sentences[i]; } } if (buf.trim()) result.push(buf.trim()); return
result.filter(function(c) { return c.length > 0; }); }

function speakChunk(index) { if (index >= chunks.length) { stop();
status.textContent = ‘播放完毕’; setTimeout(function() {
status.textContent = ’‘; }, 2000); return; } currentChunk = index; var
utt = new SpeechSynthesisUtterance(chunks[index]); utt.lang = ’zh-CN’;
utt.rate = 1.05; utt.onend = function() { speakChunk(index + 1); };
utt.onerror = function(e) { if (e.error !== ‘canceled’) speakChunk(index
+ 1); }; status.textContent = (index + 1) + ‘/’ + chunks.length;
synth.speak(utt); }

function play() { if (isPaused) { synth.resume(); isPaused = false;
isPlaying = true; btn.textContent = ‘⏸’; btn.title = ‘暂停’; return; }
chunks = splitText(getArticleText()); currentChunk = 0; isPlaying =
true; isPaused = false; btn.textContent = ‘⏸’; btn.title = ‘暂停’;
speakChunk(0); }

function pause() { synth.pause(); isPaused = true; isPlaying = false;
btn.textContent = ‘▶’; btn.title = ‘继续播放’; }

function stop() { synth.cancel(); isPlaying = false; isPaused =
false; chunks = []; currentChunk = 0; btn.textContent = ‘🔊’; btn.title
= ‘朗读全文’; status.textContent = ’’; }

btn.addEventListener(‘click’, function() { if (isPlaying) pause();
else play(); });

var holdTimer; btn.addEventListener(‘mousedown’, function() {
holdTimer = setTimeout(function() { stop(); status.textContent =
‘已停止’; setTimeout(function() { status.textContent = ’‘; }, 1500); },
800); }); btn.addEventListener(’mouseup’, function() {
clearTimeout(holdTimer); }); btn.addEventListener(‘mouseleave’,
function() { clearTimeout(holdTimer); });

setInterval(function() { if (synth.speaking && !synth.paused)
{ synth.pause(); synth.resume(); } }, 10000); })();

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
