---
title: "飞书和钉钉发 CLI，是对 MCP-first\n路线的一次现实否决"
date: 2026-03-29
source: https://yage.ai/share/feishu-dingtalk-cli-reject-mcp-first-20260329.html
slug: feishu-dingtalk-cli-reject-mcp-first-20260329
lang: zh
---
# 飞书和钉钉发 CLI，是对 MCP-first 路线的一次现实否决

发布于 2026 年 3 月 29 日 · [查看原网页](https://yage.ai/share/feishu-dingtalk-cli-reject-mcp-first-20260329.html)

*2026-03-29*

## 为什么这件事重要

2026 年 3 月底，钉钉和飞书在不到 24 小时内先后在 GitHub
开源了各自的命令行工具。钉钉首批开放 10 项核心能力，飞书直接覆盖 2500+
API、11 个业务域和 19 个 AI Agent
Skills。两个中国最大的企业协作平台，几乎同时把 CLI 推到了产品正面。

这件事回答了一个过去一年反复被争论但始终缺少平台方硬数据的问题：当企业协作平台认真面对
Agent 接入的时候，它们会从哪条路径开始？答案很清楚，先发一套当前主流
Agent 能直接消费的命令行接口，而不是先发一个 MCP server。

这个选择，放在当前 shell-based agent
工作流已经成为主流开发范式的背景下看，构成了对 MCP-first
集成路线的一次现实否决。被否决的不是 MCP 所有可能的长期价值，而是把 MCP
当作平台原生 Agent 接入首要入口这个优先级排序。

## Shell-native agent 直接消费 CLI

理解平台为什么做这个选择，得先看消费端。当前最活跃的一批 Agent
runtime，Claude Code、Cursor、Codex 以及各种基于 shell 的 coding
agent，天然运行在终端环境里。它们最稳定、摩擦最低的动作是读文件、写文件、执行命令。CLI
对这类 agent 来说是默认就会使用的接口形态，不需要额外的适配层。

从平台侧看，飞书和钉钉原本就有完整的开放平台 API。将已有 API
整理成命令、子命令、参数和帮助文档，工程成本可控，覆盖面高，也容易和现有开发者习惯衔接。CLI
的 `--help` 天然就是一个可读的能力索引，对 agent
来说可以直接充当 skill 文档。这条路径比部署一个 MCP server、处理
transport 层配置、管理 tool schema 注册和认证授权要短得多。

飞书这次直接把 2500+ API 整理进 CLI，背后的判断很直接：先让 Agent
能完整地使用平台能力，再谈更高层的协议抽象。

## MCP-first 在这里被否决的原因

如果 MCP 仅仅是在开发者采用速度上输给了
CLI，这件事的意义有限。真正值得讨论的是 MCP
在协议层面已经暴露的几个压力点，这些压力点让平台方有充分理由不把 MCP
作为首选路径。

第一个压力点是 context 哲学的碰撞。MCP
的设计核心假设是所有信息交换都应流经 LLM 的 context
window，模型对工具调用和返回结果保持完整可见性。这个假设在 Anthropic
的科研环境里合理，但在工程现实中已经反复碰壁。GUI
渲染、长结构化数据、确定性执行这些场景，强行让所有信息通过 context
window 会降低模型智能、增加推理成本、引入不确定性。OpenAI 在 Apps SDK
中用 `_meta` 域绕过 context window 来传递 GUI
状态，恰恰说明最大的 MCP 使用方之一已经在实践中否定了这个设计假设。

第二个压力点是 dialect
的漂移，而且这个漂移已经从预警变成了正在发生的现实。`_meta`
域的故事没有停在 Apps SDK 发布那一天。OpenAI 后续将 MCP Apps
作为正式产品路径推进，`_meta` 和 `openai/*`
扩展从临时绕行变成了事实上的官方化 extension path，携带嵌套 GUI
状态、组件声明和交互逻辑。这意味着任何深度使用 Apps SDK 的开发者写出的
MCP server，在 Anthropic 或其他 host 上都无法直接运行。

与此同时，协议的其他层也在分裂。SSE transport 被废弃，迁移到
streamable HTTP 的过程中出现了 breaking change，已经部署的 server
需要重写传输层。OAuth 2.1 的引入本身就伴随了安全漏洞的集中爆发，包括多个
CVE 和 localhost 相关的攻击面暴露，后续的修复又引入了新的 breaking
change，让已经上线的企业客户承受额外的迁移成本。在客户端层面，互操作性的承诺也在具体场景中失效：Kiro
CLI 在对接部分 MCP server 时出现了兼容性故障，Websets 的 auth 机制在跨
host 场景下也发生了
breakage。这些不是理论风险，而是已经有开发者踩到的现实问题。

这和 SQL dialect
的历史路径非常相似：标准名义上存在，各家的实现之间已经不能直接互换。对平台方来说，选择一个正在分裂中的协议作为首要接入路径，意味着额外承担
dialect 兼容性的持续维护成本。

第三个压力点是 discovery 的实际负担。一个 MCP server
如果把几十上百个工具的 schema 一次性塞进上下文，token
消耗和工具选择准确率都会受到直接冲击。围绕这个问题已经出现了 lazy
loading、registry-based dispatch、skills 索引等补偿机制，但这些机制不是
MCP 协议的内建能力，而是社区在协议之外叠加的组织层。Discovery
问题本身不是 MCP 最深层的协议缺陷，context 哲学和 dialect 漂移才是。但
discovery
的混乱放大了采用摩擦，让平台方在评估接入成本时更倾向选择组织成本更低的
CLI 路径。

这三个压力点叠加在一起，就不只是采用节奏快慢的问题了。它们构成了一个更实质的判断：在当前这个阶段，对于企业协作平台的
Agent 接入场景，MCP-first
路线带来的协议层摩擦高于它带来的标准化收益。

## Google Workspace 生态的旁证

飞书和钉钉是中文企业协作市场的代表，但 shell-native agent
作为一个消费者类别的兴起，不只发生在中文社区。Google Workspace
生态下也出现了一个值得关注的信号：`googleworkspace/cli`（gws）。这是
Google Workspace 组织下的一个实验性 CLI 项目，由 DevRel 团队维护，为
Google Workspace 的核心服务（Gmail、Drive、Calendar、Sheets
等）提供终端接口。

需要明确的是，gws 不是 Google 的强官方产品发布，它更接近一个
DevRel-style 的 experimental sample，没有和 Google Cloud CLI
同等的产品承诺。因此，它不能被写成 Google 正式选择 CLI 替代 MCP
的证据。

但它仍然说明了一件有意义的事情：即使在 Google Workspace
这样已经有完整 REST API 和 SDK
体系的生态里，终端场景也被认为足够重要，值得为之做一套 serious 的
CLI。这和飞书、钉钉的判断指向同一个方向：shell-native agent
已经构成了一个真实的消费者类别，平台方开始为这个类别单独提供接口。

值得一提的是，gws 本身还内置了 `gws mcp` 命令，也就是说
Google 的这个项目并没有在 CLI 和 MCP
之间做非此即彼的选择。这恰恰让它成为一个更诚实的参照：CLI 和 MCP
可以共存，但当平台方评估优先级的时候，CLI
是先被做出来的那个。在飞书和钉钉的案例里，这个优先级判断更加明确，因为它们连
MCP 都没有同步发布。

## 边界

两个边界需要明确。

被现实否决的是 MCP-first 作为当前平台原生 Agent 接入的首选路径，不是
MCP 每一种可能的长期用途。一旦场景进入跨 runtime 分发、安全隔离、多
dialect 兼容，协议层的重要性会回升。MCP
的问题不在于它试图解决的那类抽象本身无价值，而在于它以当前的设计成熟度和生态状态，承担不了首选入口的角色。而
dialect 漂移的压力已经从半年前的预警变成了有具体 CVE 编号、有 breaking
change 记录、有客户端互操作失败案例的现实。这让平台方回避 MCP-first
的决策有了比半年前更充分的依据。

关于信号的覆盖范围：最明确的信号来自中文企业协作平台（飞书、钉钉），它们直接跳过了
MCP 发布 CLI。Google Workspace 生态提供了方向一致但力度更弱的旁证，因为
gws 同时包含了 CLI 和
MCP，且项目本身的官方程度有限。其他市场和平台的节奏可能不同，这篇文章的判断主要基于
shell-native agent runtime 这条主线上已经发生的事实。

## 方法说明

本文基于以下材料：飞书 `larksuite/cli` 与钉钉
`dingtalk-workspace-cli`
的仓库信息，`googleworkspace/cli`（gws）的仓库和功能结构，此前关于
MCP 的两篇文章（mcp.md, mcp-revisited.md），以及关于 MCP Apps
官方化、OAuth/CVE 集群、SSE 废弃迁移、Kiro CLI 和 Websets auth
互操作故障的外部讨论。未对上述 CLI 做端到端实测。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
