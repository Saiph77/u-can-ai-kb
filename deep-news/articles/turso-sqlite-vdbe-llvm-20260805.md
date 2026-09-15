---
title: "SQLite 里藏着一台虚拟机，Turso 把它变成了数据库的\nLLVM"
date: 2026-08-07
source: https://yage.ai/share/turso-sqlite-vdbe-llvm-20260805.html
slug: turso-sqlite-vdbe-llvm-20260805
lang: zh
---
# SQLite 里藏着一台虚拟机，Turso 把它变成了数据库的 LLVM

发布于 2026 年 8 月 7 日 · [查看原网页](https://yage.ai/share/turso-sqlite-vdbe-llvm-20260805.html)

## SQLite 里藏着一台虚拟机

你在终端打开 SQLite，随便敲一条最简单的条件查询，前面加个
EXPLAIN：

```
sqlite> EXPLAIN SELECT name FROM users WHERE id <= 10;
```

控制台刷出来的不是我们熟悉的树状语法分析，而是一串带着地址和寄存器的汇编指令：

```
addr  opcode         p1    p2    p3    p4             p5  comment
----  -------------  ----  ----  ----  -------------  --  -------------
0     Init           0     9     0                    0   Start at 9
1     OpenRead       0     2     0     2              0   root=2 iDb=0; users
2     Rewind         0     8     0                    0
3       Column         0     0     1                    0   r[1]= cursor 0 column 0
4       Gt             2     7     1     BINARY-8       84  if r[1]>r[2] goto 7
5       Column         0     1     3                    0   r[3]= cursor 0 column 1
6       ResultRow      3     1     0                    0   output=r[3]
7     Next           0     3     0                    1
8     Halt           0     0     0                    0
9     Transaction    0     0     1     0              1   usesStmtJournal=0
10    Integer        10    2     0                    0   r[2]=10
11    Goto           0     1     0                    0
```

*VDBE 字节码执行模型：左侧平坦线性字节码循环（addr + opcode + 寄存器 + while(1) switch），右侧对比经典 Volcano 模型的树状算子递归。*

VDBE
字节码执行模型：左侧平坦线性字节码循环（addr + opcode + 寄存器 +
while(1) switch），右侧对比经典 Volcano
模型的树状算子递归。

这几行代码一出来，SQLite 怎么干活的就一目了然了。第 1 行 OpenRead
打开根节点为 2 的 B-Tree 表，第 2 行 Rewind 把游标归位，第 3 行 Column
拿 `id` 放入寄存器 `r[1]`，第 4 行 Gt
比较大小，只要 `id` 超过 10 就跳到第 7 行 Next
跳过该行，没超过就取 `name` 字段放入寄存器 `r[3]`
用 ResultRow 吐出结果，再调 Next 继续循环。

做过数据库开发的人都知道，多数 SQL
引擎的物理执行器习惯写成树状算子结构。比如同样的查询，经典引擎解析出 AST
语法树后，会构建出一棵物理执行计划树：`Project(name) -> Filter(id <= 10) -> SeqScan(users)`。运行时就像著名的
Volcano 模型那样，自顶向下递归调用
`next()`，数据再从底层的扫描节点一层层向上流转。

但 SQLite
走的完全是另一条路。它不在运行时递归遍历任何算子树，而是像现代编译器一样，直接把
SQL
语句翻译成了一段线性的字节码流。这段代码里有程序计数器（`addr`）、操作码（`OpenRead`、`Le`、`Goto`）、寄存器（`r[1]`）以及条件跳转。运行时，SQLite
内核实际上就是跑在一个平坦的循环里：`while(1) { switch(opcode) { ... } }`。

我们平时用的 `EXPLAIN QUERY PLAN`
查到的只是高层策略（比如用了什么索引），而直接用
`EXPLAIN`，露出来的才是底层的字节码指令。

这套隐藏的引擎叫 VDBE。从 2000 年 Richard Hipp 动手写 SQLite
开始，它就在内核里默默运转了。但在过去 25 年里，Hipp
和社区一直把它当成不公开的内部实现细节，没给它写公共标准，也没开放
ABI。大家习惯了隔着 SQL
文本接口去用它，反而渐渐忘了，它的肚子深处本来就是一台完整的虚拟机。

## 为什么我们需要把 Postgres 编译到 SQLite 的虚拟机上

既然 SQLite
底层原本就是一台图灵完备的虚拟机，那它在今天能帮我们解决什么现实问题？这恰恰对应了最近写
AI Agent 和 Local-first 应用时，几乎每个团队都会碰到的选型两难。

在开发体验和生态这一端，大家很自然想用 Postgres。它有最丰富的 SQL
语法、强大的类型系统，几乎所有
ORM、迁移工具和框架开箱即用。但在实际部署和运维这一端，大家又看重 SQLite
的物理特性：毫秒级启动、单个文件就能做单租户隔离、内存开销小到可以忽视，甚至能直接打成
WebAssembly 包塞进浏览器里跑，轻轻松松扩展出成千上万个独立数据库。

过去想把这两者结合起来，行业里最普遍的做法是在最外层的 SQL
文本上做方言翻译，比如收到 Postgres 的 SQL
字符串，在中间层用正则或语法树改写成 SQLite 的 SQL
再发过去。但只要稍微写过复杂的系统就知道，这条路走起来有多痛苦。标量函数名字对不上、内置类型行为不一致、隐式类型转换有微妙差异，字符串翻译不仅笨重脆弱，为了照顾边缘语法还要平添几层解析开销，很快就会撞上一面语义阻抗失配的硬墙。

可是，如果我们越过外层的 SQL 文本直接往数据库内核看，会发现 Postgres
和 SQLite 在磁盘和内存里的底层操作其实大同小异：归根结底都是在调度
B-Tree 节点、数据页和索引游标。张力和矛盾全在表面的 SQL
语法上，底层的数据结构和存储调度本质上是一套语言。

既然如此，为什么还要在最外层费力做字符串翻译？直接在编译器这一层，把
Postgres 解析出来的抽象语法树编译成 VDBE
的字节码指令，事情就顺了。在指令和 B-Tree
调度层共享同一个后端底座，上层拿到了完整的 Postgres
方言与开发生态，下层又保留了 SQLite
嵌入式、极轻量、单文件物理隔离的部署优势。

## 从实现细节到公共抽象

从“把 Postgres 编译成 VDBE 指令”这个构想往前再走一步，就碰到了 Turso
架构设计里最核心的操作：把 SQLite 藏了 25
年的这套内核实现细节翻出来，正式化成了一个公开的中间层。

在 [2026
年 7 月的官方 Newsletter](https://turso.tech/blog/a-new-modern-version-of-postgres-in-rust) 里，Turso
第一次把这个愿景喊得非常明确：我们正在成为数据库界的
LLVM，拥有一个现代、可靠的核心，上面可以编译运行各种数据库前端。SQLite
是我们的第一个前端，而重写 Postgres 的初始代码也已经成功合并。

学过编译器的朋友对这个逻辑不会陌生。LLVM 当年做的事情，就是把
C++、Rust、Swift 各种语言的前端解析器，和 x86、ARM
这些底层硬件解耦开来。Turso
在数据库里干了相同的事：把数据库拆成两层，上层是可插拔的语法前端，专门负责解析不同的
SQL
方言并吐出抽象语法树；下层则是统一的存储与虚拟机核心，专门接收编译出来的
VDBE 字节码并调度存储引擎。

*数据库的 LLVM：左侧 LLVM 编译器（C++/Rust/Swift 前端 → LLVM IR → x86/ARM 后端），右侧 Turso 数据库（SQLite frontend / Postgres frontend pgmicro → VDBE 字节码 → 统一存储引擎），两层中间层 IR 通过公共中间层对齐。*

数据库的 LLVM：左侧 LLVM
编译器（C++/Rust/Swift 前端 → LLVM IR → x86/ARM 后端），右侧 Turso
数据库（SQLite frontend / Postgres frontend pgmicro → VDBE 字节码 →
统一存储引擎），两层中间层 IR 通过公共中间层对齐。

在他们的代码库里，一个叫 [pgmicro](https://github.com/glommer/pgmicro)
的子项目验证了这个思路。用 Rust 写的 pgmicro 能够直接解析 Postgres SQL
表达式，并生成对应的 VDBE 字节码序列，让 Postgres 语法直接跑在 SQLite
的虚拟机内核上。在官方博客 [A
new, modern version of Postgres in Rust](https://turso.tech/blog/a-new-modern-version-of-postgres-in-rust) 中，团队详细拆解了用 Rust
重写 Postgres 语法解析并对接底层 VM 的过程；而 [Concurrent
writes on Turso Cloud](https://turso.tech/blog/concurrent-writes-on-turso-cloud)
则补充了他们在云端实现并发写入的方案，给这套统一内核补齐了扩展能力。

## 在数据库虚拟机里玩游戏：通用编译路径的真实信号

如果说将 Postgres 编译到 VDBE
上还只是数据库方言之间的跨界，那么一个自然的疑问就是：这台隐姓埋名的虚拟机，计算表达能力到底有多通用？之前
Turso
在社区里演示了一个很火的项目，给出了一个带有冲击力的答案：直接在数据库引擎内核里跑
Doom 游戏，代码开源在 GitHub 仓库 [turso-vdbe-doom-example](https://github.com/tursodatabase/turso-vdbe-doom-example)。

乍一看，在数据库里玩游戏像是个炫技的花哨动作。但把底层的编译工具链扒开看，会发现它暴露了一条硬核的通用计算路径：

```
C 游戏源码 (doomgeneric)
  └── clang -O2 -emit-llvm
        └── LLVM IR (.ll)
              └── vdbecc
                    └── VDBE 字节码
```

关键在于，专门写的编译器 `vdbecc` 吃进去的并不是特制的
Doom 语法，而是标准的 LLVM IR
文件。这意味着，只要任何语言（C、C++、Rust、Swift）能编译成 LLVM
IR，就能顺理成章通过这套管线翻译成 VDBE
字节码。在数据库内核里玩游戏，本质上是在用复杂的交互逻辑，去测试这台 VM
承载通用 C 语言代码的能力。

翻看 `vdbecc`
的实现细节很有意思：程序运行需要的内存地址空间，被直接映射成了数据库单行表
`_vdbecc_mem` 里的一块 `ram` blob
字段。所有的指针偏移与内存读写，都被翻译成了 VDBE 的
`BlobRead` 和 `BlobWrite` 指令。画面刷新时，底层的
C 函数触发 `vdbe_present` 扔出一行 ResultRow
图像数据并挂起状态机，外面再通过循环调 `step()`
推动下一帧。

这干净利落地证明了一件事：VDBE
是一台图灵完备的虚拟机。它不仅仅是一个处理 SELECT/INSERT 的 SQL
解释器，而是可以真正承载任意通用计算逻辑的底座。

## 真正难啃的骨头是扩展生态

用运行游戏验证了 VDBE
的通用计算底子之后，再回到数据库本业，我们会发现把 Postgres
语法编译过去固然漂亮，但真要走到生产环境，很快就会撞上一块难啃的骨头：Postgres
庞大的扩展生态（比如 PostGIS、pgvector）。

Postgres 的优势从来不只是它的 SQL 语法，而是它几十年来攒下的各种 C
语言扩展。这里要分清两个概念：网络协议 Wire Protocol
只管客户端和数据库之间怎么打报文，而真正决定插件能不能跑的是 Internal
ABI。Postgres 的原生扩展都是直接读取 C
内核的结构体指针和内存布局的。

为了啃下这块骨头，Turso 提出过一个思路：把 Postgres 的扩展编译成
WebAssembly 容器，再塞进虚拟机里跑。但这个方案目前还停留在 PoC 阶段。跨
WASM
沙箱边界调用底层数据结构必然有不可忽视的性能损耗，而且客观来说，也不是随便拿来一个现成的
C 语言扩展都能无缝转成 WASM 运行。

Turso 官方在产品说明 [What
is Turso](https://turso.tech/what-is-turso) 以及 [Hacker News
讨论](https://news.ycombinator.com/item?id=48935487)
里说的其实很实在：现在的架构是基础设施的基石，远不是大包大揽的成熟终局，他们并不打算盲目去追求
100% 兼容 Postgres
的每一个边缘细节与历史包袱。能不能搞定一套高效率的扩展 ABI
机制，才是这个愿景未来真正需要迈过的关卡。

## 把隐性细节变成通用基础设施

虽然扩展 ABI 还有关卡要过，但从 SQLite 隐藏 VM 到 Turso
将其推向台前，这条技术演进线已经展现出了清晰的轮廓。回顾这 25 年，从
2000 年 Richard Hipp 为了极简把 VDBE 藏在内核深处，到今天 Turso
把它推到台前做数据库的
LLVM，最打动我的其实是一个朴素的软件工程规律：当一个内部实现细节被证明拥有足够强的表达力时，把它规范化、提升为公开的公共抽象，往往能释放出远超原本设计的能量。

把隐姓埋名的 VDBE 升格为公共中间层，上层的 SQL
语法方言和底层的物理存储就被解耦开了。在指令字节码这一层共享 B-Tree
调度，既解开了了 Postgres 开发者体验与 SQLite
物理部署特性之间的死结，也让我们看到了未来的数据库引擎前端可插拔、后端通用计算的系统新拓扑。对于这种单文件轻量数据库如何在多智能体架构中做状态隔离，我们在[本系列第二篇](https://yage.ai/share/turso-database-per-agent-20260805.html)里继续展开；单文件容器如何承载
RAG 向量检索，则在[本系列第三篇](https://yage.ai/share/turso-rag-file-isolation-20260805.html)中给出实战测试。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
