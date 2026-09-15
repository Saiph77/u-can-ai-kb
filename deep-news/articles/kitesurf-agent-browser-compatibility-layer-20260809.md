---
title: "浏览器是 Agent 覆盖面最广的兼容层，但 Chrome\n不是：为什么我们需要 Kitesurf？"
date: 2026-08-09
source: https://yage.ai/share/kitesurf-agent-browser-compatibility-layer-20260809.html
slug: kitesurf-agent-browser-compatibility-layer-20260809
lang: zh
---
# 浏览器是 Agent 覆盖面最广的兼容层，但 Chrome 不是：为什么我们需要 Kitesurf？

发布于 2026 年 8 月 9 日 · [查看原网页](https://yage.ai/share/kitesurf-agent-browser-compatibility-layer-20260809.html)

*浏览器作为 Agent 兼容层*

浏览器作为 Agent 兼容层

聊起 AI Agent 的基础设施，大家常假设未来的软件都会暴露一套干净优雅的
AI 原生接口。可现实往往正好相反，市面上数以万计的网页应用、SaaS
系统和企业内网软件，在未来很长一段时间里都不可能专程为了模型去重写
API。面对这个现实断层，行业选了一条看似笨拙却格外管用的路径：直接让
Agent 操控浏览器去接管既有应用。Cloudflare 最近发布的 [Kitesurf](https://blog.cloudflare.com/kitesurf/)，正是专为这一场景打造的
Agent 无头浏览器基础设施：它允许 Agent 通过兼容现有工具的 Chrome
DevTools Protocol (CDP) endpoint
操控云端网页渲染与交互，同时把原本属于传统浏览器的庞大开销压到了较低水平。

## 兼容层困境：为什么在很长一段时间内，Agent 都无法摆脱浏览器？

图形界面是人类与软件交互了几十年的底层通用协议。现代网页和桌面 UI
构成了现实世界最完整的数据流动网络。绝大多数在线服务都提供一个能让普通人在屏幕上点击、阅读的网页，即使没有开放开发者
API 也有这个入口。

当 Agent 需要跨越多个软件去完成复杂任务时，指望所有服务商主动接入
REST API 或者 Model Context Protocol (MCP) 接口是不现实的。给外部开 API
远不只是写几道接口代码那么简单，背后涉及到繁重的代码重构、商业合规谈判、安全审计、防刷限流，还有各家对核心数据壁垒的死守。与其漫长等待生态自行改造，直接让
Agent 操控网页，在无法获得 API 时常是改造成本较低的路径。

浏览器也因此顺理成章地成了 Agent
操作既有软件覆盖面最广的兼容层。只要某个功能在网页上看得见、点得到，Agent
就有机会接管操作。这个兼容层不需要等待应用厂商配合，直接复用了现成的互联网基础设施。

这种兼容层还会长期陪伴我们。对于绝大多数 SaaS 和 Web
厂商来说，人类用户的订阅与广告点击是直接的收入来源，而专门为 AI 构建 API
Key
分发、计费与鉴权体系需要额外的投入。在缺乏直接商业激励的前提下，厂商更愿意维护现有的
Web
界面。只要网页依然是软件交付的主渠道，浏览器作为通用适配器的地位就很难动摇。面对这种现实，将浏览器改造为适应
Agent 调用的计算通道，便成了工程上水到渠成的路径。

然而，一旦把这套模式从实验室探索推向大规模的生产环境，底层架构上的负担与瓶颈就会快速爆发。

## 扩展性悖论：给人类视觉定制的 Chrome 为什么扛不住 Agent 的高并发？

这种架构上的负担，根源在于传统浏览器的设计前提：Chromium
这类引擎，全都是围绕人类的生理特征与行为模式构建的。当访问的主体从人类变成
Agent 时，需求层面爆发了两个根本性的错位。

第一个错位是扩展性与并发诉求的错位。人类使用者同一时间只有一个注意力焦点，手里只有一只鼠标，眼前只有一对眼睛。哪怕是重度用户，一次也只能在一个活动标签页里打字或浏览，剩下几十个后台标签页基本处于静止或挂起状态。但
Agent
作为可以弹性扩容的执行实体，优势偏偏在于并发吞吐。Agent不仅要同时打开几十甚至上百个网页，还要在这些页面上持续提取结构化数据、触发交互并监控状态变化。在网页面前，Agent
是时刻处于高频交互状态的多任务实体，不同于后台挂起的人类标签页。

第二个错位是功能需求与冗余优化配比的错位。现代 Chromium
相当一部分额外的资源开销，全都是浏览器几十年里专程为人类视觉体验与富媒体演进出的高级优化：为了人类眼中的
60fps 平滑滚动与 3D 动画，构建了占内存的 GPU 图层贴图合成与 WebGL/WebGPU
渲染管线；为了 JS 的执行速度，拉起了包含多级编译管线的 V8 JIT
优化编译器堆与 Inline Cache
缓存；为了防崩溃与跨站安全，设计了多进程沙箱骨架，通过 Site Isolation
按站点分配渲染进程；为了多媒体集成，内置了 WebRTC
与音视频解码协议栈。

这些优化对人类很有意义，但对许多 Agent
工作负载来说并非刚需，反而带来了额外的资源负担。Kitesurf
针对的是短生命周期、突发式的截图和 HTML 提取等任务，这类任务不需要 60
帧滚动、GPU 3D 贴图或音视频流。当然，Agent
的需求并不总是如此简单，有些需要长期认证、复杂渲染或对抗反爬，Cloudflare
明确建议这些场景回退到 Chromium。

当 Agent 高频并发的吞吐需求，撞上 Chromium
为人类视觉与富媒体定制的重型架构，资源开销就会快速叠加。Chromium
的多进程模型通常带来数百 MiB 级任务内存：Cloudflare 自己的对照测试测得
warm Chromium 池在截图和 HTML 提取任务中分别占用 271.0 MiB 和 273.7
MiB。在实际部署中，具体内存取决于页面复杂度、进程复用和站点隔离策略，但
RAM 往往先于 CPU
成为瓶颈。一旦业务请求量上涨，成百上千个操作系统进程会迅速挤爆 cgroups
的限制，内核因为内存耗尽触发 OOM
Killer，直接清理掉运行中的浏览器进程，反映到上层业务里就是莫名其妙的请求超时或任务中断。

个人开发者用单台服务器很难扛住高并发
Agent，云基础设施服务商也面临着沉重的算力负担。

## 场景破局与技术接应：如何在 V8 Isolate 里重新构建浏览器？

*Chromium 多进程 vs Kitesurf V8 Isolate 架构对比*

Chromium 多进程 vs Kitesurf V8 Isolate
架构对比

针对上面提到的扩展性瓶颈，Cloudflare 推出的 Kitesurf
给出了一套非常直观的解题路径：既然 Agent
不需要人类的眼睛，那就把所有给人类看的高级优化统统剥离；既然在本地单机上跑
Chrome 太占资源，就把渲染的重活直接搬到分布式边缘网络上。

在实现上，Kitesurf 没有选择移植动辄千万行代码的 Chromium
源码，而是把基于 Rust 开发的轻量级渲染引擎直接编译成 WebAssembly
(WASM)，让它运行在 [Cloudflare
Workers](https://developers.cloudflare.com/workers/reference/how-workers-works/) 的 V8 Isolate
环境里。这么一来，系统彻底扔掉了操作系统多进程模型的沉重骨架，把页面渲染与数据提取做成了轻量调用的组件。Cloudflare
2018 年称一般 Workers isolate 可在约 5
毫秒启动，不过这是平台级的启动指标，不是 Kitesurf
页面上下文完整生命周期的 benchmark。

更妙的是算力与内存压力的转移。以前用 Playwright 或
Puppeteer，我们需要在自己的电脑或服务器上开着笨重的 Headless Chrome。而
Kitesurf 把最吃资源的 DOM 解析、CSS 布局和栅格化计算，搬到了 Cloudflare
宣称覆盖 330+ 城市的全球网络上执行。请求会被路由到最近的 PoP，相关的
Workers 和 isolate 在那里协作完成渲染。本地只需要维持极轻量的信号编排与
CDP 协议握手，真正的内存和算力消耗都直接卸载到了云端。

这种架构上的重构，反映在工程数据上是非常清晰的折中。以下数字均来自
Cloudflare 自己的基准测试：14 个 URL、每项运行 5 次取中位数，对比的是
Cloudflare 自己的 warm Chromium
池，目前尚无第三方独立复现。在该测试中，提取 HTML 数据时单页内存占用只有
39.4 MiB，对照 warm Chromium 为 273.7 MiB，约低 7 倍，CPU 节省了 3.8
倍；渲染截图时内存为 57.8 MiB，降低了 4.7
倍。当然，天下没有免费的午餐。因为 Kitesurf
使用冷启动的软件渲染器，而对照的 Chromium 有 warm JIT 优势，Kitesurf
截取图片的端到端耗时是 1,148 毫秒，比 Chromium 的 637 毫秒慢了约 1.8
倍，差距主要来自栅格化与 JPEG/PNG 编码。

同时在功能边界上，Kitesurf 当前明确不支持视频播放、WebGL 3D
渲染以及要求真实 TLS 指纹的 bot challenge
握手，也不适合需要长期持久状态的认证会话。这些有些是当前未实现的能力，有些是短生命周期、尽量无状态设计带来的取舍，并非全部由
[Workers
安全模型](https://developers.cloudflare.com/workers/reference/security-model/)直接禁止。但对于高并发、短生命周期的数据提取任务来说，用较慢的响应延迟去换取显著更低的
CPU
和内存，在系统工程里常常是个划算的交易。实际并发密度和成本收益还需按具体
workload 验证。Kitesurf 实际上为 Agent 重新打造了一个剥离视觉开销的 Web
通道。

## 终局思考：从 Accessibility 对抗看 AI-Native 兼容层的两难本质

Kitesurf 的探索其实勾勒出了一个规律：把现有的旧软件改造成 Agent
适用的基础设施，最管用的办法往往是重新设计底层兼容层。顺着这个视角回看隔离技术的演进，有两条并行谱系。一条是端点侧的硬件隔离：Bromium
在 2010 年用 Intel VT-x 硬件虚拟化给每个浏览器标签页和下载起一个
microVM。另一条是远程浏览器隔离（RBI）：把整个浏览器搬到云端，先是用像素流把渲染结果传回，后来演进出
DOM 树重建和网络矢量渲染（NVR）。

到了今天，Kitesurf 在 V8 isolate
这个语言运行时级别的边界上引入了新的执行粒度。但它没有取代 OS
进程和系统沙箱——Workers 的安全模型仍然在 isolate 外叠加进程分组、Linux
namespace/seccomp 和出站代理，生产安全边界是分层组合。类似的思路在桌面
GUI 自动化领域也有体现。许多 Agent 会优先使用 DOM 或 Accessibility
树的结构化语义，在结构不可得或视觉信息关键时才使用截图和 VLM。毕竟
Accessibility 树自带控件层级与语义标记，Agent
读写软件状态的开销远低于去分析像素图片。

然而，这种通过重构兼容层来提升机器效率的方案，很快就会撞上一条现实中的深层次矛盾：适配效率与生态安全之间的长期博弈。

拿 Accessibility 接口和无头自动化通道来说，站在 Agent
开发者角度，它们无疑是交互成本较低的捷径。但在应用服务商眼中，这种绕过视觉
UI
的自动化接口，在技术特征上会共享许多反自动化系统关注的技术信号：无头、高速、重复、非人类交互模式。因此仅靠协议和无头特征往往难以判断意图。为了保护用户隐私、维护生态安全与数据资产，部分应用会限制或检测非人类手势的自动化通道。

这种矛盾在 Cloudflare 身上体现得尤为生硬。Cloudflare
自称其整体网络位于约 20% 的 web 前方，Bot Management
利用这部分网络可见性来检测和拦截自动化爬虫；另一方面，Cloudflare 又是
Kitesurf 这类 Agent 浏览器基础设施的推手。当 Agent 借由 Kitesurf
高频访问网页时，流量经 SandboxOutbound worker 发出，其外部可见的 TLS
指纹具体是什么尚需实测确认，但官方已明确 Kitesurf 当前不能处理要求真实
TLS 指纹的 bot challenge。这会产生一个尚未解决的问题：Kitesurf
流量如何被 Cloudflare
及其他反自动化系统分类，目前没有公开测试或政策答案。在协议握手阶段，安全系统很难判断发起的到底是个善意的
AI 助手，还是恶意的抓取脚本。

只要现存的软件生态还没有全面迈向 AI 原生形态，这种在提升 Agent
效率与服务商防范自动化之间的攻防对抗就会一直持续。Kitesurf
尝试用边缘中介与组件解耦来缓解冲突，但如何在机器交互效率与安全防护界限之间找到平衡，依然是
Agent 基础设施演进中绕不开的深水区课题。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
