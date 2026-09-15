---
title: "Claude Code 的防线：它怎么防止你假装是它"
date: 2026-04-01
source: https://yage.ai/share/claude-code-defense-in-depth-20260401.html
slug: claude-code-defense-in-depth-20260401
lang: zh
---
# Claude Code 的防线：它怎么防止你假装是它

发布于 2026 年 4 月 1 日 · [查看原网页](https://yage.ai/share/claude-code-defense-in-depth-20260401.html)

泄露的 Claude Code TypeScript 源码揭示了一套至少覆盖 8
个层次的纵深防御体系。这套体系的目标很明确：确认每一个 API
请求确实来自正版客户端，在无法确认时降级处理，在最坏情况下（代码被完整逆向）仍保留服务端最后的验证能力。

这篇文章选取其中 6
层最具工程洞察的防御展开分析，按从编译期到运行时的顺序排列。每一层我会说清楚它防的是什么、怎么做的、以及工程师在设计时做了什么取舍。

## 第一层：编译期死代码消除

所有防御的基础是一个看似普通的编译选项。Claude Code 使用 Bun
作为运行时和打包工具，利用了 Bun 的编译期常量折叠能力。

核心机制是 `process.env.USER_TYPE`
这个变量。它在构建时通过 `--define` 注入，Bun
在打包阶段将它作为编译期常量处理。所有形如
`process.env.USER_TYPE === 'ant'` 的分支在外部构建时被求值为
`false`，整个分支连同引用的代码一起被 tree-shaking 移除。

```
// utils/model/antModels.ts
export function getAntModels(): AntModel[] {
  if (process.env.USER_TYPE !== 'ant') {
    return []
  }
  return getAntModelOverrideConfig()?.antModels ?? []
}
```

这段代码在外部二进制中会被优化为直接返回空数组。内部模型注册表（包含
capybara、tengu 等代号的完整配置）从二进制中物理消失。

分布范围值得注意：源码中 `USER_TYPE === 'ant'` 出现了 357
次，横跨 165
个文件。这意味着内部版和外部版在功能上的差异远超想象。内部版有完整的调试工具、undercover
模式、bash 分类器、connector text 摘要，外部版什么都看不到。

Bun 还提供了另一个编译期原语：`feature()` from
`bun:bundle`。`feature('ANTI_DISTILLATION_CC')`、`feature('NATIVE_CLIENT_ATTESTATION')`、`feature('CONNECTOR_TEXT')`
等标志在打包时被替换为布尔常量，控制更细粒度的功能开关。

```
// constants/system.ts
const cch = feature('NATIVE_CLIENT_ATTESTATION') ? ' cch=00000;' : ''
```

CI 管线还有最后一道检查：`scripts/excluded-strings.txt`
列出了所有内部模型代号和敏感字符串。构建后会扫描外部二进制，任何残留都会导致构建失败。源码注释反复提醒开发者：

```
// @[MODEL LAUNCH]: Add the codename to scripts/excluded-strings.txt
// to prevent it from leaking to external builds.
```

这层防御的设计哲学很清晰：编译期消除比运行时检查可靠得多。运行时检查可以被
patch，编译期消除意味着信息在二进制层面就已经从未存在过。

这里可能会有一个直觉上的疑问：代码被消除了，那些原本依赖这些代码的功能怎么办？答案是：编译期消除的全部是
Anthropic 内部专用的开发工具和调试设施，包括内部模型注册表、undercover
模式、内部调试入口等等。这些东西只对 Anthropic
的工程师有用，外部用户本来就看不见也用不到。对外部用户有价值的所有功能，API
调用、工具执行、文件操作、对话管理，完全保留在外部构建中。至于反蒸馏，它的实际执行发生在服务端，服务端通过
DRM attestation 和 GrowthBook
远程开关独立完成判断，客户端代码只是提供辅助信号。

## 第二层：Zig 层 DRM Attestation

这是整套体系中最精巧的一层，也是对抗仿冒客户端的核心手段。理解这一层需要一些背景。

Bun 是一个 JavaScript/TypeScript 运行时，和 Node.js
是同一赛道的竞品，但它额外集成了打包器和包管理器。对 Claude Code
来说，Bun 最关键的能力是 `bun build --compile`：它可以把整个
JS/TS 项目编译成一个独立的原生二进制文件（macOS 上是 Mach-O 格式，Linux
上是 ELF 格式），运行时完全脱离 Node.js。Claude Code
分发给用户的就是这样一个二进制。

Zig 是一门系统级编程语言，定位类似 C 和 Rust。Bun 本身就是用 Zig
编写的，这意味着 Bun 的核心基础设施，包括 HTTP 网络栈，都是 Zig
原生代码，运行在 JavaScript
引擎的内存空间之外。这个事实是这一层防御成立的前提：当一个 HTTP 请求在
JS 层完成序列化、准备发往网络时，Zig
代码可以在发送前对请求体的字节流做搜索和替换，而 JS
层的任何拦截手段（覆写 `fetch`、安装拦截器、monkey-patch
`http.request`）对此完全无感知。需要注意的是，Zig
语言本身是开源的，但 Anthropic 的 attestation
实现（`Attestation.zig`）存在于 Anthropic 私有的 Bun
fork（`bun-anthropic`）中，开源版 Bun 里找不到这段代码。

理解了这些背景，再来看具体机制。Claude Code 的 HTTP 请求中嵌入了一个
attestation token，这个 token 的生成完全在 JavaScript
层之下完成。具体流程是：JS 层在构建请求体时插入一个固定长度的占位符
`cch=00000`，然后 Bun 的原生 HTTP
栈在实际发送前，在序列化后的请求体字节流中定位这个占位符，用 Zig 计算的
attestation hash 覆写它。

```
// constants/system.ts (lines 64-91)
/**
 * When NATIVE_CLIENT_ATTESTATION is enabled, includes a `cch=00000` placeholder.
 * Before the request is sent, Bun's native HTTP stack finds this placeholder
 * in the request body and overwrites the zeros with a computed hash. The
 * server verifies this token to confirm the request came from a real Claude
 * Code client. See bun-anthropic/src/http/Attestation.zig for implementation.
 *
 * We use a placeholder (instead of injecting from Zig) because same-length
 * replacement avoids Content-Length changes and buffer reallocation.
 */
const cch = feature('NATIVE_CLIENT_ATTESTATION') ? ' cch=00000;' : ''
```

几个工程细节值得展开。

**同长度替换**。占位符 `00000` 和最终的 hash
长度相同，覆写后 Content-Length 不变，避免了重新计算 header 和重新分配
buffer。这是一个典型的性能优先设计：如果从 Zig
层注入新字段，需要重新序列化整个 JSON body。

**嵌入位置**。token 嵌在 system prompt 的 JSON body
里，而非作为 HTTP header。这意味着标准的 HTTP 代理、中间件、API gateway
无法在传输层观察或篡改它。attribution header 的完整格式是：

```
x-anthropic-billing-header: cc_version=1.2.3.abc; cc_entrypoint=cli; cch=fa318;
```

**执行层级**。如前文所述，Zig 代码运行在 JS
引擎的内存空间之外，JS
层的拦截手段对它无效。攻击者要绕过这一层，需要直接修改 Bun
的编译产物。

这层防御的工程代价也很明确：Claude Code 因此被绑定到 Bun 运行时。其他
JS 运行时（Node.js、Deno）无法提供等效的原生 HTTP 栈注入能力。这是一个
vendor lock-in 换安全性的决策。

## 第三层：消息指纹

attestation
证明了客户端的身份，但消息指纹解决的是另一个问题：这个请求的内容有没有被中间人篡改。

```
// utils/fingerprint.ts
export const FINGERPRINT_SALT = '59cf53e54c78'

export function computeFingerprint(
  messageText: string,
  version: string,
): string {
  const indices = [4, 7, 20]
  const chars = indices.map(i => messageText[i] || '0').join('')
  const fingerprintInput = `${FINGERPRINT_SALT}${chars}${version}`
  const hash = createHash('sha256').update(fingerprintInput).digest('hex')
  return hash.slice(0, 3)
}
```

算法是
`SHA256(硬编码盐 + 第一条用户消息的第 4、7、20 个字符 + 版本号)`，取前
3 个十六进制字符。这个 3 字符指纹附加到 attribution header
的版本号后面，形如 `cc_version=1.2.3.abc`。

设计意图很明确：服务端拿到请求后，可以用相同的算法从消息内容和版本号重新计算指纹，与
header 中的值比对。如果中间有代理层修改了消息内容（比如注入 system
prompt 或替换用户消息），指纹就会失配。

3 个字符（12 bit）的碰撞空间很小，只有 4096
种可能。这说明它的设计目标是统计性检测而非密码学级别的防篡改。服务端可以对大量请求做统计分析：如果某个
API key 的指纹失配率异常高，说明请求可能经过了代理篡改。

注释中有一行值得关注：

```
// IMPORTANT: Do not change this method without careful coordination with
// 1P and 3P (Bedrock, Vertex, Azure) APIs.
```

指纹算法需要和多个后端同步，任何修改都是跨团队协调。这也解释了为什么用了这么简单的算法：简单意味着容易在不同语言和平台上保持一致。

## 第四层：反蒸馏体系

前三层都是关于身份验证和完整性检查。反蒸馏层解决的问题不同：即使对方确实在用正版客户端，也要防止他把
Claude 的输出当作训练数据来蒸馏出竞品模型。

反蒸馏有两个独立的机制，分别作用于输入和输出。

**输入侧：fake\_tools
注入**。当特定条件满足时，客户端在请求体中加入
`anti_distillation: ['fake_tools']`
字段，告诉服务端注入假的工具定义。

```
// services/api/claude.ts (lines 301-313)
if (
  feature('ANTI_DISTILLATION_CC')
    ? process.env.CLAUDE_CODE_ENTRYPOINT === 'cli' &&
      shouldIncludeFirstPartyOnlyBetas() &&
      getFeatureValue_CACHED_MAY_BE_STALE(
        'tengu_anti_distill_fake_tool_injection',
        false,
      )
    : false
) {
  result.anti_distillation = ['fake_tools']
}
```

服务端收到这个信号后，会在工具列表中混入看起来合理但实际上无意义的虚假工具定义。如果有人录制
Claude Code
的请求-响应对来做训练数据，这些假工具定义就会污染训练集。模型学到的是一个包含虚假能力描述的工具使用范式，蒸馏出来的模型会尝试调用根本不存在的工具。

触发条件有三重门控：编译期 feature flag
`ANTI_DISTILLATION_CC`、入口点必须是 `cli`（排除
SDK 调用）、GrowthBook 远程开关
`tengu_anti_distill_fake_tool_injection`。三重门控意味着
Anthropic
可以在服务端精确控制这个功能的开关，而不需要发布新版客户端。

**输出侧：thinking signature 保护**。Claude 的 thinking
block 和 connector text 携带加密签名，这些签名绑定到生成它们的 API key
和模型。

```
// utils/messages.ts (lines 5060-5099)
/**
 * Strip signature-bearing blocks (thinking, redacted_thinking, connector_text)
 * from all assistant messages. Their signatures are bound to the API key that
 * generated them; after a credential change (e.g. /login) they're invalid and
 * the API rejects them with a 400.
 */
export function stripSignatureBlocks(messages: Message[]): Message[] {
  // ...filters out thinking blocks and connector text blocks
}
```

Signature 的核心约束是跨边界不可复用，而非隐藏 thinking
内容本身。正常使用时（同一个 API key、同一个模型、连续对话），signature
完全透明，thinking block
正常输出和回传，用户体验上感知不到它的存在。

Signature 阻止的是三种具体场景。第一种是换 API key 后重放：用户执行
`/login` 切换账号后，之前对话中的 thinking block 携带旧 key
的签名，新 key 验证失败，API 返回 400。Claude Code
的处理方式是在凭证变更后调用 `stripSignatureBlocks()`
暴力删除所有带签名的块，丢弃旧会话中的推理内容。第二种是跨模型回退：高负载时系统自动从
Capybara 回退到 Opus，Capybara 生成的 thinking block 发给 Opus
时签名不匹配，同样触发 400。这也是泄露源码中 Capybara
适配逻辑浮出水面的原因之一。第三种是蒸馏数据收集：如果有人系统性地录制请求-响应对来构建训练数据集，thinking
block 中的签名绑定了生成它的 API key。签名本身是明文，thinking
内容可读，但签名创建了一个追踪机制，Anthropic 可以据此追溯数据来源。

需要区分的是，`redact-thinking` beta header 是一个独立的
opt-in 机制，和 signature 解决的是两个层面的问题。它告诉 API
在返回前删除 thinking 内容，用于特定场景（ISP
模型集成、非交互式会话等不需要暴露推理过程的场合）。Claude Code
默认不启用这个 header，thinking 正常输出。API 文档中承诺输出 thinking
和这个 header
的存在互相兼容：默认行为是输出，`redact-thinking`
是额外选项，需要调用方主动开启。

这两个机制只对 1P CLI 启用，Bedrock、Vertex 和 SDK
调用不受影响。原因是 3P
用户已经通过云服务商的认证体系获得了使用授权，蒸馏风险主要来自直接 API
访问。

fake\_tools 注入和 thinking signature
保护的正是这部分高价值输入：工具定义塑造了模型的行为空间，thinking block
记录了模型的推理路径，两者合在一起就是蒸馏者最想获取的训练信号。

## 第五层：反调试与 token 保护

前面的层次都在对付外部威胁。反调试层防的是一个更隐蔽的场景：prompt
injection 攻击者通过让模型执行 shell 命令（比如
`gdb -p $PPID`）来从进程内存中抓取 API token。

```
// upstreamproxy/upstreamproxy.ts (lines 220-252)
/**
 * prctl(PR_SET_DUMPABLE, 0) via libc FFI. Blocks same-UID ptrace of this
 * process, so a prompt-injected `gdb -p $PPID` can't scrape the token from
 * the heap. Linux-only; silently no-ops elsewhere.
 */
function setNonDumpable(): void {
  if (process.platform !== 'linux' || typeof Bun === 'undefined') return
  try {
    const ffi = require('bun:ffi') as typeof import('bun:ffi')
    const lib = ffi.dlopen('libc.so.6', {
      prctl: {
        args: ['int', 'u64', 'u64', 'u64', 'u64'],
        returns: 'int',
      },
    } as const)
    const PR_SET_DUMPABLE = 4
    const rc = lib.symbols.prctl(PR_SET_DUMPABLE, 0n, 0n, 0n, 0n)
    // ...
  }
}
```

通过 Bun 的 FFI 调用 Linux 的 `prctl`
系统调用，将进程标记为不可 dump。效果是：即使攻击者获得了相同 UID
的执行权限，也无法通过 ptrace 附加到 Claude Code 进程来读取堆内存。

token 的生命周期管理同样值得关注。session token 从文件
`/run/ccr/session_token` 读取后，文件被立即 unlink。token
只存在于堆内存中，文件系统上不留痕迹。而且 unlink
的时机经过精心设计：必须在 relay 启动成功之后才执行。如果 CA
下载或端口监听失败，token 文件保留在磁盘上，supervisor 可以重试。

```
// Only unlink after the listener is up: if CA download or listen()
// fails, a supervisor restart can retry with the token still on disk.
await unlink(tokenPath).catch(() => {
  logForDebugging('[upstreamproxy] token file unlink failed', {
    level: 'warn',
  })
})
```

这层防御只在 CCR（Claude Code
Remote，即云端容器化运行）模式下启用，本地 CLI 不受影响。设计上遵循了
fail-open 原则：任何一步出错都只是 log warning
并禁用代理，绝不让安全机制的故障阻碍正常使用。

## 第六层：Gateway 检测

最后看一层面向基础设施的防御。Claude Code 在每次 API 响应后检查 HTTP
响应头，识别请求是否经过了 AI 代理网关。

```
// services/api/logging.ts (lines 66-105)
const GATEWAY_FINGERPRINTS: Partial<Record<KnownGateway, { prefixes: string[] }>> = {
  litellm:                 { prefixes: ['x-litellm-'] },
  helicone:                { prefixes: ['helicone-'] },
  portkey:                 { prefixes: ['x-portkey-'] },
  'cloudflare-ai-gateway': { prefixes: ['cf-aig-'] },
  kong:                    { prefixes: ['x-kong-'] },
  braintrust:              { prefixes: ['x-bt-'] },
}

const GATEWAY_HOST_SUFFIXES: Partial<Record<KnownGateway, string[]>> = {
  databricks: [
    '.cloud.databricks.com',
    '.azuredatabricks.net',
    '.gcp.databricks.com',
  ],
}
```

检测方法有两种：对于自托管网关（LiteLLM、Helicone、Portkey、Kong、Braintrust），检查响应头是否包含特征前缀；对于
SaaS 网关（Databricks），检查 `ANTHROPIC_BASE_URL`
的域名后缀。

检测结果被记录到遥测日志中。源码里没有检测到网关后立即阻断请求的逻辑，目前是纯粹的监控和数据采集。

理解这一层需要回到 gateway 在蒸馏链条中扮演的角色。AI
代理网关（LiteLLM、Helicone、Portkey
等）是蒸馏的基础设施层。攻击者通过这些网关可以大规模录制请求-响应对，统一管理多个
API key 的用量分配，在中间层注入、修改或过滤内容。换句话说，gateway
是从零散的 API 调用到系统化蒸馏流水线的关键跳板。

Claude Code 检测 gateway 的目的是掌握信息，而非即时阻断。Anthropic
可以通过遥测数据了解有多少流量经过代理网关，评估蒸馏风险的规模和分布，为后续制定针对性策略提供数据基础。这体现了前面提到的客户端做标记、服务端做决策的原则：客户端只负责识别和上报，决策权留在服务端。信息不对称本身就是防御的一部分，用户以为自己透明地使用了中间代理，但
Claude Code 已经识别出了这一事实并将其汇报给了服务端。

## 体系性观察

回看这六层防御，有几个设计原则贯穿始终。

**纵深分层，每层独立**。编译期消除、Zig
attestation、消息指纹、反蒸馏、反调试、gateway
检测，每一层都独立工作。攻破某一层（比如逆向了指纹算法）并不会让其他层失效。

**客户端做标记，服务端做决策**。所有客户端层面的机制都是在请求中附加信息（attestation、fingerprint、gateway
标记），最终的信任判定在服务端完成。这确保了即使客户端被完整逆向，服务端仍然可以更新验证逻辑。GrowthBook
feature flag
体系在其中扮演关键角色：`tengu_attribution_header`、`tengu_anti_distill_fake_tool_injection`、`tengu-off-switch`
等开关允许服务端在任意时刻改变客户端行为，而无需发版。

**fail-open
原则**。安全机制的故障绝对不能影响正常功能。upstreamproxy
的每一步都有 try/catch 和降级路径，`prctl` 调用在非 Linux
平台上静默跳过，attribution header 可以通过环境变量或 GrowthBook
关闭。这是 Claude Code
作为生产力工具（而非安全产品）的定位决定的：如果反蒸馏机制导致了一个用户的编程体验出问题，那这个机制就是在产生净负价值。

**选择绑定换安全**。Zig attestation 把 Claude Code
绑定到 Bun，`prctl` 把反调试绑定到 Linux，fake\_tools 只对 1P
CLI
启用。每一层防御都有明确的作用域边界和平台依赖。工程团队没有追求一个通用的、跨平台的安全方案，而是在每个具体场景中选择了最有效的特定方案。这是务实的工程判断。

最后一个观察：这套体系的真正目标可能是对手选择（adversary
selection）而非绝对防御。通过不断提高仿冒和蒸馏的技术门槛，让攻击者的成本持续上升。任何一层都可能被绕过，但绕过所有层的成本已经高到让大多数潜在攻击者去寻找其他目标。Claude
Code
的源码泄露本身就是这套体系的一次压力测试：即使攻击者拿到了完整源码，服务端的
attestation 验证和 GrowthBook 开关仍然构成最后的防线。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
