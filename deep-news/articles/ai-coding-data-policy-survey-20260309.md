---
title: "AI 编程工具数据政策调研报告（2026年3月）"
date: 2026-03-09
source: https://yage.ai/share/ai-coding-data-policy-survey-20260309.html
slug: ai-coding-data-policy-survey-20260309
lang: zh
---
# AI 编程工具数据政策调研报告（2026年3月）

发布于 2026 年 3 月 9 日 · [查看原网页](https://yage.ai/share/ai-coding-data-policy-survey-20260309.html)

调研日期：2026年3月9日 | 调研方法：5组并行 librarian agent +
交叉验证

> 免费和个人版大多会拿你的代码训练，企业版大多不会。
> 真正的风险不只在训练，还在永久授权、保留期限和名存实亡的 opt-out。
> 想用强模型又尽量保住隐私，API key 往往比消费者订阅更可靠。

本报告对 11 款主流 AI
编程工具的用户协议和数据政策进行系统调研，重点关注用户代码是否被用于模型训练、数据保留期限、是否存在”不可撤销的永久授权”条款、以及企业版与个人版的差异。

## 核心发现

调研最重要的结论可以用一句话概括：**免费/个人版几乎都会用你的数据训练模型，企业版几乎都不会，但”几乎”二字里藏着关键差异**。

具体来看：

**第一梯队（隐私保护最强）**：通义灵码和 Tabnine
在所有层级都明确承诺不存储、不训练用户代码。Tabnine 甚至支持完全断网的
air-gapped 部署，是对数据安全要求最极端的场景的唯一选项。

**第二梯队（企业版安全，个人版需注意）**：GitHub
Copilot、Windsurf、Google Gemini Code Assist、Amazon Q Developer
的企业版均提供零数据保留和不训练承诺，但免费/个人版默认会收集数据。其中
Gemini Code Assist 的免费版尤其值得警惕，默认开启数据收集且需主动
opt-out。

**第三梯队（存在明确风险）**：火山引擎 Coding Plan、智谱
AI、Kimi/Moonshot
均包含”永久授权”或类似条款，且退出机制要么不存在、要么执行存疑。火山引擎的条款最为激进，明确写明”授权期限为永久”且”技术上无法撤回”。

**特殊情况**：Anthropic 在 2025 年 8
月的消费者条款更新中，将 Claude Code（个人账户）的数据保留期从 30
天延长至 5 年（用户同意训练时），引发开发者社区强烈反弹。OpenAI
的消费者条款中存在”永久的、不可撤销的”许可授权条款，但
API/企业版不受此约束。

---

## 一、总览对比

### 1.1 用户代码是否用于模型训练

| 工具 | 免费/个人版 | 企业版/API |
| --- | --- | --- |
| **通义灵码** | ❌ 不训练，不存储 | ❌ 不训练，支持 VPC |
| **Tabnine** | ❌ 不训练，零保留 | ❌ 不训练，支持 air-gapped |
| **GitHub Copilot** | ⚠️ 可能（需用户设置允许） | ❌ 不训练，IDE 零保留 |
| **Windsurf** | ⚠️ 聊天内容可能用于训练（可 opt-out） | ❌ 不训练，零保留默认开启 |
| **Google Gemini** | ⚠️ 免费版默认开启 | ❌ Standard/Enterprise 不训练 |
| **Amazon Q** | ⚠️ 免费版默认开启（可 opt-out） | ❌ Pro 自动 opt-out |
| **Anthropic Claude Code** | ⚠️ 默认 opt-out 训练（2025.8 新政） | ❌ API/企业版不训练 |
| **OpenAI Codex** | ⚠️ 默认可能用于训练（可 opt-out） | ❌ API/企业版不训练 |
| **Cursor** | ⚠️ Privacy Mode 关闭时可能训练 | ⚠️ Business Plan + Privacy Mode 不训练 |
| **火山引擎 Trae** | ✅ 明确用于训练 | ⚠️ 企业版支持 VPC 零存储 |
| **智谱 GLM/CodeGeeX** | ✅ 明确用于训练 | ❌ 基础政策相同，无独立企业条款 |
| **Kimi/Moonshot** | ✅ 明确用于训练 | ⚠️ 可谈判 DPA，但默认同个人版 |

### 1.2 数据保留期限

| 工具 | 个人版 | 企业版/API |
| --- | --- | --- |
| **Tabnine** | 零保留（即时处理后删除） | 零保留 |
| **通义灵码** | 代码上下文不存储 | 不存储，AES-256 加密传输 |
| **GitHub Copilot** | Prompt 保留 28 天 | IDE 零保留，CLI 28 天 |
| **Windsurf** | 取决于设置 | 零保留（即时删除） |
| **Anthropic Claude Code** | 同意训练：**5 年**；拒绝：30 天 | API 7-30 天，ZDR 可选 |
| **OpenAI Codex** | 未明确 | 30 天（ZDR 可选） |
| **Amazon Q** | 免费版可能保留 | Pro 不收集 |
| **Google Gemini** | 未明确 | Stateless 架构，不存储 |
| **Cursor** | Privacy Mode 下零保留 | Business 零保留 |
| **火山引擎** | **永久** | 企业版零云端存储 |
| **智谱 AI** | 协议终止后仍保留（匿名化） | 同个人版 |
| **Kimi** | 无明确期限 | 可谈判 |

### 1.3 “不可撤销的永久授权”条款

这是本次调研中最值得关注的维度。所谓”永久授权”，指的是用户在使用服务时授予平台一项对自己数据的永久性使用权利，且即使用户后续终止服务，已授权的数据使用也无法撤回。

| 工具 | 是否存在永久授权条款 | 具体内容 |
| --- | --- | --- |
| **火山引擎** | ✅ **明确存在，最激进** | “授权期限为永久”，“技术上无法撤回”，终止授权即停止服务 |
| **智谱 AI** | ✅ **明确存在** | “永久的、免费的许可使用”，“可再许可第三方使用” |
| **OpenAI** (消费者) | ✅ **存在** | “perpetual, irrevocable license”用于 User Content（API/企业版不适用） |
| **Kimi** | ⚠️ **可能存在** | 第三方分析指出”perpetual training data usage”框架 |
| **Windsurf** | ⚠️ 仅限 Feedback | 用户反馈授予 perpetual license，代码不受此约束 |
| **Anthropic** | ❌ 未发现 | 消费者条款未包含永久授权条款 |
| **GitHub Copilot** | ❌ 未发现针对 Copilot 的 | 平台通用条款有许可授予，非 Copilot 专用 |
| **Tabnine** | ❌ 不存在 | 明确”不保留任何代码” |
| **通义灵码** | ❌ 不存在 | “代码信息完全由您所有及控制” |
| **Google Gemini** | ❌ 未发现 |  |
| **Amazon Q** | ❌ 未发现 |  |

### 1.4 IP 赔偿（知识产权侵权保护）

IP 赔偿意味着如果 AI
生成的代码被指控侵犯第三方知识产权，服务商会为用户承担法律辩护和赔偿。

| 工具 | 个人版 | 企业版 |
| --- | --- | --- |
| **Google Gemini** | ❌ | ✅ Standard 起即有（$19/月） |
| **GitHub Copilot** | ❌ | ✅ Business/Enterprise |
| **Amazon Q** | ❌ | ✅ Pro ($19/月) |
| **Windsurf** | ❌ | ✅ Enterprise |
| **Tabnine** | ❌ | ✅ Enterprise |
| **Anthropic** | ❌ | ✅ 商业/API 客户 |
| **OpenAI** | ❌ | ✅ API/Enterprise |
| **Cursor** | ❌ | 未明确 |
| **火山引擎** | ❌ | 未明确 |
| **智谱 AI** | ❌ “自行处理” | 未明确 |
| **Kimi** | ❌ | 未明确 |

### 1.5 Opt-out 机制详解

能否方便地退出数据训练，是衡量一家 AI
编程工具数据政策实际友好程度的关键指标。有些工具虽然默认收集数据，但提供了便捷的
opt-out 开关；有些则在条款中写了 opt-out
但实际执行困难；还有些根本不提供退出选项。

| 工具 | Opt-out 可用性 | 操作方式 | 实际便利度 | 备注 |
| --- | --- | --- | --- | --- |
| **通义灵码** | 🟢 无需 opt-out | N/A | ★★★★★ | 从不训练、从不存储代码，无需任何操作 |
| **Tabnine** | 🟢 无需 opt-out | N/A | ★★★★★ | 所有层级零保留零训练，架构层面杜绝 |
| **GitHub Copilot** | 🟢 设置面板一键关闭 | Settings → “Allow GitHub to use my code snippets for product improvements” 取消勾选 | ★★★★☆ | Individual 层级可自助切换，Business/Enterprise 默认不训练 |
| **Windsurf** | 🟢 设置面板切换 | User Settings → code sharing options | ★★★★☆ | Individual 可自助 opt-out 聊天训练，Teams/Enterprise 默认零保留 |
| **Anthropic Claude Code** | 🟢 设置面板切换 | Settings → Privacy → “Help improve Claude” 关闭 | ★★★☆☆ | 可自助切换，但 2025.8 政策变更后默认开启，UI 设计被批评有引导倾向；用 API Key 登录可完全绕开 |
| **OpenAI Codex** | 🟢 设置面板切换 | Settings → Data controls → opt-out（[说明](https://openai.com/policies/how-your-data-is-used-to-improve-model-performance/)） | ★★★☆☆ | 可自助 opt-out，但消费者条款中仍保留 perpetual license 条款；用 API 可绕开 |
| **Amazon Q** | 🟡 需分环境设置 | Console: AWS Organizations AI services opt-out policy; IDE: 每个 IDE 单独设置; CLI: `qct configure` | ★★★☆☆ | Free 版需手动 opt-out 且各环境独立，容易遗漏；Pro 版自动 opt-out |
| **Cursor** | 🟡 需手动启用 Privacy Mode | Settings → Privacy Mode 开启 | ★★★☆☆ | 可自助切换，但 Privacy Mode 有 Legacy/New 两个版本，差异不明显标注；Business Plan 默认强制开启 |
| **Google Gemini** | 🟡 免费版需 opt-out | 具体操作方式未在文档中详细说明 | ★★☆☆☆ | 免费版默认开启数据收集，opt-out 路径不够清晰；Standard/Enterprise 版无需操作 |
| **Kimi** | 🔴 名义上可退出，实际困难 | 联系 [[email protected]](/cdn-cgi/l/email-protection) 申请 | ★☆☆☆☆ | 官方 ToS 写有 opt-out，但社区报告客服要求删除账户才能退出；已训练数据不可逆 |
| **智谱 AI** | 🔴 无 opt-out 机制 | 无 | ☆☆☆☆☆ | 用户协议中未找到任何退出选项，永久授权 + 可再许可第三方 |
| **火山引擎** | 🔴 无实质 opt-out | 可联系客服”终止授权”，但终止即停用服务，且已使用数据”技术上无法撤回” | ☆☆☆☆☆ | 形式上提供终止路径，但代价是失去服务，且已有数据无法删除，实质上不构成有效 opt-out |

总结来看，opt-out 的友好程度大致分为四档：第一档是根本不需要 opt-out
的（通义灵码、Tabnine），从架构上就不收集不训练；第二档是提供了便捷的自助
opt-out 开关的（GitHub
Copilot、Windsurf、Anthropic、OpenAI），用户可以在设置中一键切换；第三档是
opt-out 存在但操作不够便捷或有遗漏风险的（Amazon
Q、Cursor、Gemini）；第四档是 opt-out
名存实亡或不存在的（Kimi、智谱、火山引擎）。

---

## 二、分产品详细分析

### 2.1 火山引擎 Coding Plan / Trae（字节跳动）

火山引擎的数据授权协议是本次调研中条款最激进的。

**核心条款原文**（[豆包助手专区服务专用条款](https://www.volcengine.com/docs/82379/2047627)）：

> 3.1
> 授权目的：本规则项下的授权将用于**开发机器学习、人工智能相关技术和豆包助手专区服务的优化、开发、使用等之目的**。
>
> 3.2
> 授权范围：您同意，您将授予火山引擎一项非独家的、不可转让的、不可分许可的（但可分许可给火山引擎关联方以及为达成授权目的第三方外包服务商）、免费的权利，允许火山引擎为达成授权目的而**传输、存储、使用、复制、下载、修改或以其他方式处理客户数据**。
>
> 3.3
> 授权期限：**授权期限为永久**。……**您进一步充分知悉、理解并同意，即便您完成了终止操作，但由于机器学习和人工智能技术的特殊性，一旦您授权火山引擎使用相关客户数据，且相关客户数据已被使用的，则对该部分客户数据的使用将在技术上无法撤回**。……如您终止授权，您将无法继续使用本服务。

该协议同时适用于 Coding
Plan、豆包助手、PromptPilot、全域AI搜索等多条产品线。群里讨论的”不可撤销永久授权”说法**完全属实**，且火山引擎是调研对象中唯一明确写出”技术上无法撤回”的厂商。

**Trae IDE
额外争议**：独立安全研究者发现，即便用户关闭遥测功能，Trae IDE
仍在 7 分钟内发起约 500 次网络请求，累计上传 26MB 数据（[来源](https://www.letsclouds.com/news/trae-ide-data-privacy-controversy)）。官方回应称关闭的只是
VS Code 相关遥测，Trae 自身遥测不受该设置控制。GitHub 上的研究项目（[segmentationf4u1t/trae\_telemetry\_research](https://github.com/segmentationf4u1t/trae_telemetry_research)）记录了详细的数据收集范围，包括系统信息、设备
ID、使用数据、性能指标、位置与区域、工作区信息等。

**企业版差异**：Trae CN 企业版支持 VPC
部署、全链路代码加密传输、零云端存储。换言之，企业版可以规避上述数据风险，但需额外付费。

### 2.2 智谱 AI (GLM / CodeGeeX)

**核心条款原文**（[用户协议](https://docs.bigmodel.cn/cn/terms/user-agreement)）：

> 您免费授予智谱及其关联公司非排他的、无地域限制的、**永久的、免费的许可使用**（包括存储、使用、复制、修订、编辑、发布、展示、翻译、分发上述信息或制作派生作品，以已知或日后开发的形式、媒体或技术将上述信息纳入其他作品内等）及**可再许可第三方使用的权利**，以及可以自身名义对第三方侵权行为取证及提起诉讼的权利。

另一条关于模型训练：

> 为了改善我们向您提供的产品和服务的质量，我们可能利用您使用大模型平台或平台内模型过程中产生的数据，定位、维护和优化我们的产品和服务，但是您与智谱另有约定的除外。

智谱的永久授权条款与火山引擎类似，但有一个值得注意的区别：智谱的条款包含”可再许可第三方使用”，意味着智谱有权将你的数据授权给任何第三方。协议中未找到任何
opt-out
机制。在中国/国际版差异方面，调研仅找到中国版（bigmodel.cn）的协议，未发现独立的国际版用户协议。CodeGeeX
作为智谱的编程助手，遵循平台统一协议，无独立数据政策。

### 2.3 Kimi / Moonshot（月之暗面）

**核心条款原文**（[开放平台服务协议](https://platform.moonshot.cn/docs/agreement/modeluse)）：

> 为不断改善Kimi智能助手的服务质量，Kimi智能助手可能使用您输入Kimi智能助手的和Kimi智能助手向您输出的内容进行进一步的开发训练。您完全理解并接受该种使用，并不因该种使用而向Kimi智能助手主张权利或主张Kimi智能助手侵犯您的权益。

**Opt-out 机制**：官方 Terms of Service 中写明可联系
[[email protected]](/cdn-cgi/l/email-protection) 退出训练。但社区反馈显示执行存疑。有用户在 Reddit
报告客服回复”需要删除账户才能退出”（[来源](https://www.reddit.com/r/kimi/comments/1qpeknq/terms_of_service_clarification_how_can_paid/)）。Hugging
Face 社区讨论中也有用户指出”即使付费 API 也会使用你的数据”（[来源](https://huggingface.co/moonshotai/Kimi-K2-Thinking/discussions/24)）。

**数据主权问题**：作为中国注册公司，月之暗面须遵守《网络安全法》、《数据安全法》和《个人信息保护法》，政府机关可依法调取用户数据。这对海外用户而言是额外的合规考量。

### 2.4 通义灵码（阿里巴巴）

通义灵码是国内厂商中数据政策最友好的。

**核心条款原文**（[隐私政策](https://terms.alicdn.com/legal-agreement/terms/privacy_policy_full/20231023213159724/20231023213159724.html)）：

> 2.2.3
> 您基于本基础功能或服务上传、生成的代码信息**完全由您所有及控制**，除本协议所列使用场景及目的外，**我们不会存储，也不会将其用于其他任何非经您授权的场景，包括不会用于模型训练**。

**官方 FAQ**（[来源](https://help.aliyun.com/zh/lingma/support/faq)）进一步澄清：

> 代码补全时，上下文信息不会被存储或用于其他任何目的。研发智能问答时，仅会在您点踩/点赞后，仅针对聊天记录（不包含代码），并将数据进行脱敏、去标识化处理后，用于算法的升级、迭代。

阿里云大模型服务平台也明确声明”绝不会将您的数据用于模型训练”，且传输数据经过
AES-256 加密（[来源](https://help.aliyun.com/zh/model-studio/privacy-notice)）。企业专属版支持
VPC 私有化部署。

### 2.5 Anthropic Claude Code

2025 年 8 月 28
日的消费者条款更新是本次调研中争议最大的政策变动之一。

**核心变更**（[官方公告](https://www.anthropic.com/news/updates-to-our-consumer-terms)）：

> We will train new models using data from Free, Pro, and Max accounts
> **when this setting is on** (including when you use Claude
> Code from these accounts).

> We are also extending data retention to five years, if you allow us
> to use your data for model training.

关键要点：免费/Pro/Max 用户（包括通过这些账户使用 Claude Code
时）默认可以被用于训练（opt-out 模式）；同意训练的用户数据保留期从 30
天延长至 5 年；2025 年 10 月 8
日前用户须做出选择，否则无法继续使用。

**API 和企业版不受影响**：Commercial Terms 覆盖的 Claude
for Work、API 使用、Amazon Bedrock 和 Google Vertex 均不适用此政策。API
数据保留期从 30 天缩短至 7 天（2025 年 9 月 15
日起）。企业客户可申请零数据保留（ZDR）。

**社区反应**：Reddit r/ClaudeAI
上有帖子标题为”Anthropic’s New Privacy Policy is Systematically Screwing
Over Solo Developers”（[来源](https://www.reddit.com/r/ClaudeAI/comments/1nd73si/anthropics_new_privacy_policy_is_systematically/)），批评这创造了一个”双层系统”，独立开发者的代码成为竞争对手的免费训练数据。TechCrunch
也指出 Anthropic 的 UI 设计可能在引导用户同意数据共享（[来源](https://techcrunch.com/2025/08/28/anthropic-users-face-a-new-choice-opt-out-or-share-your-data-for-ai-training/)）。

**实操建议**：使用 Claude Code 时，如果用 API Key
登录则受 API 条款保护（不训练，7
天保留）；如果用个人账户登录则受消费者条款约束。

### 2.6 OpenAI Codex

**消费者条款**（[Terms of
Use](https://openai.com/policies/row-terms-of-use/)）包含一个值得注意的授权条款：

> By uploading any User Content you hereby grant and will grant OpenAI
> and its affiliated companies a **nonexclusive, worldwide, royalty
> free, fully paid up, transferable, sublicensable, perpetual, irrevocable
> license** to copy, display, upload, perform, distribute, store,
> modify and otherwise use your User Content for any OpenAI-related
> purpose in any form, medium or technology now known or later
> developed.

这是典型的”永久不可撤销许可”条款，适用于消费者上传的 User Content。但
API/Business/Enterprise 条款明确排除了训练：

> We will not use Customer Content to develop or improve the
> Services.

Codex 作为 coding agent 的数据政策取决于访问方式：通过 ChatGPT
Plus/Pro 访问受消费者条款约束，通过 API 访问受 API 条款保护，通过
Enterprise 访问受企业条款保护。API 数据默认保留 30
天用于滥用监控，企业版可申请 ZDR。

### 2.7 GitHub Copilot

**Business/Enterprise 层级**（[官方说明](https://github.com/orgs/community/discussions/152229)）：

> No. GitHub uses neither Copilot Business nor Enterprise data to train
> the GitHub model.

IDE 内的代码补全和聊天采用零保留策略，数据生成后立即删除。CLI 和
Coding Agent 保留 28 天。

**Individual/Free
层级**：默认情况下不用于训练，但用户可以在设置中选择允许。免费版在数据使用方面更宽松。

**第三方模型提供商**：GitHub Copilot 通过 AWS Bedrock
使用 Claude Sonnet，通过 GCP 使用
Gemini，均有零保留协议。用户可选择禁用特定第三方模型。

**版权诉讼**：Doe v. GitHub 案件仍在进行中，2026 年 2
月第九巡回上诉法院举行了口头辩论。核心争议在于 AI
生成代码与开源代码的相似性是否构成版权侵权。该案结果将影响整个 AI
编程工具行业。

### 2.8 Cursor

**Privacy Mode 是关键**。Cursor 有两种隐私模式：

Privacy Mode (Legacy)
提供最强保护：零数据保留，代码从不被存储或训练。Privacy Mode (New)
略有变化：第三方模型提供商零保留，但 Cursor
自身可能存储一些代码数据以提供额外功能（如远程索引、记忆等），但仍不用于训练。Privacy
Mode 关闭时：Cursor 可能使用代码数据来改进 AI 功能和训练模型。

**Business Plan**：Privacy Mode 默认强制开启。OpenAI 和
Anthropic 不保留 Business 用户数据。

**社区争议**：围绕 Cursor
的隐私讨论相当激烈。主要焦点包括：隐私模式变更缺乏透明度（Legacy vs
New），代码索引生成的 embeddings 存储在 Cursor
服务器上且用户无法完全控制，.cursorignore 文件可能被 AI agent 绕过。有
LinkedIn 帖子警告企业”远离 Cursor”，称其会将 .env
等敏感文件发送到外部服务器（[来源](https://www.linkedin.com/posts/devansh-devansh-516004168_ive-spent-hundreds-of-hours-evaluating-cursor-activity-7318693323135684608-NI7Z)）。

### 2.9 Windsurf（原 Codeium）

**Teams/Enterprise**（[ToS](https://windsurf.com/terms-of-service-teams)）：

> Customer Data is not used for any other purpose, including the
> training of language models. Customer Data is encrypted during transit
> and is not stored at rest.

零数据保留默认开启。代码所有权明确归属用户：

> Exafunction agrees that you own all Suggestions. Exafunction hereby
> assigns to you all of its right, title, and interest in and to any
> Suggestions.

**Individual/Pro**（[ToS](https://windsurf.com/terms-of-service-individual)）：聊天内容可能用于模型改进，可在设置中
opt-out。代码补全不用于训练。

Windsurf 与 OpenAI 有零数据保留协议，企业管理员可禁用 OpenAI
模型。提供自托管和混合部署选项。

### 2.10 Tabnine

Tabnine 是所有调研对象中隐私保护最彻底的（[Privacy
Documentation](https://docs.tabnine.com/main/welcome/readme/privacy)）：

> When using Tabnine models, your code remains private. Tabnine NEVER
> retains or shares any of your code with third parties. Tabnine has a
> no-train-no-retain policy. This is in place regardless which model is
> being used.

> Tabnine doesn’t use third-party APIs or models to deliver our
> service. Instead, we’ve developed proprietary models based on our own
> deep experience in generative AI.

所有层级（包括免费版）均为零数据保留。不使用任何第三方模型或
API。模型仅在开源许可代码上训练。支持完全 air-gapped
部署，零遥测数据外泄。SOC 2 Type 2、ISO 27001、GDPR、HIPAA
均已认证。

代价是模型能力可能不如使用大厂基础模型的竞品。

### 2.11 Google Gemini Code Assist 和 Amazon Q Developer

**Gemini Code Assist**（[Data
Governance](https://developers.google.com/gemini-code-assist/docs/data-governance)）：Standard 和 Enterprise 版不使用 prompts 或 responses
训练模型。免费版需注意，据 DevClass
报道默认可能使用数据改进模型。Enterprise 提供 stateless 架构、HIPAA
BAA、FedRAMP High 授权。IP 赔偿从 Standard
版即开始提供（$19/月），是所有工具中门槛最低的。

**Amazon Q Developer**（[FAQs](https://aws.amazon.com/q/developer/faqs/)）：Pro 版自动
opt-out 数据收集和模型训练，提供 IP 赔偿。Free 版默认收集数据，需手动
opt-out，且各环境（Console、IDE、CLI）需分别设置。

---

## 三、交叉验证与矛盾发现

### 3.1 多源确认的高可信结论

以下结论在多个独立来源中得到交叉验证：

1. **火山引擎的”永久授权+技术不可撤回”条款确实存在**。在豆包助手、PromptPilot、全域AI搜索等多条产品线的独立协议中均出现了相同或几乎相同的措辞。
2. **通义灵码确实不存储代码数据**。官方隐私政策、FAQ、阿里云平台说明三个独立来源一致确认。
3. **Anthropic 2025 年 8 月确实将消费者数据保留期延长至 5
   年**。官方公告、TechCrunch、Reddit 讨论均确认。
4. **Tabnine
   确实在所有层级实施零保留**。官方文档、第三方评测、竞品对比均确认。

### 3.2 需要注意的矛盾或模糊地带

1. **Kimi 的 opt-out 执行问题**：官方 Terms of Service
   明确写有 opt-out
   机制，但社区用户报告实际执行时被要求删除账户。这构成条款承诺与实际执行的矛盾，需持续关注。
2. **Cursor 的 Privacy Mode 变更**：从 Legacy 到 New
   版本，Cursor
   增加了”可能存储一些代码数据以提供额外功能”的例外。社区对此变更的透明度提出质疑。
3. **智谱 AI
   的”可再许可第三方”**：条款授予智谱将数据再许可给第三方的权利，但隐私政策又声称”不会进行任何未获授权的使用及披露”。这两个条款之间存在张力。
4. **GitHub Copilot Free vs Individual
   的数据使用差异**：文档中对 Free tier 的数据政策描述不如
   Business/Enterprise 清晰，需要用户仔细阅读设置选项。

### 3.3 单一来源信息（需谨慎引用）

以下结论仅来自单一来源：

- Trae IDE 的 500 次/7 分钟网络请求数据来自一个独立安全研究项目
- OpenAI 消费者条款中的”perpetual irrevocable license”引用来自 TOS
  Tracker 分析
- Kimi”已训练数据无法从模型中删除”的说法来自第三方隐私分析

---

## 四、给不同角色的建议

### 4.1 独立开发者

如果你用个人账户写 side project，最安全的选择是
Tabnine（所有层级零保留）或通义灵码（明确不存储不训练）。如果偏好 Claude
或 GPT 的模型能力，务必使用 API Key 而非个人账户登录 Claude Code /
Codex，这样受 API 条款保护而非消费者条款。火山引擎、智谱、Kimi
的个人版在数据保护方面风险较高。

### 4.2 企业用户

几乎所有主流工具的企业版都提供了足够的数据保护。选择时关注以下维度：

- 需要 air-gapped 部署 → Tabnine（唯一选项）
- 需要最低价 IP 赔偿 → Google Gemini Standard ($19/月) 或 Amazon Q Pro
  ($19/月)
- 已在 AWS 生态 → Amazon Q Developer
- 已在 Google Cloud 生态 → Gemini Code Assist
- 需要 HIPAA/FedRAMP → Gemini Enterprise 或 Tabnine Enterprise
- 国内企业合规 → 通义灵码企业专属版（VPC 部署）或 Trae 企业版（VPC
  部署）

### 4.3 使用国内工具的注意事项

国内工具普遍面临两个结构性问题：一是用户协议中的”永久授权”条款在中国法律框架下的合规性存疑（《个人信息保护法》要求数据处理应有明确、合理的目的和期限）；二是所有国内平台均须依法配合政府数据调取。

如果必须使用国内工具处理敏感代码，优先考虑支持
VPC/私有化部署的企业版，避免将核心商业逻辑或用户数据通过个人版上传。

---

## 五、GDPR 与数据合规分析

### 5.1 GDPR 适用性

GDPR（通用数据保护条例）的适用基于两个触发条件（Article
3）：在欧盟设有机构处理数据，或虽不在欧盟但向欧盟居民提供商品/服务或监控其行为。对于本报告调研的工具，适用情况如下：

**明确受 GDPR 管辖的工具**：GitHub Copilot、Anthropic
Claude、OpenAI Codex、Cursor、Windsurf、Tabnine、Google Gemini Code
Assist、Amazon Q
Developer。这些工具面向全球用户提供服务，在欧盟有大量用户，且多数已声明
GDPR 合规（如 Tabnine 已通过 GDPR 认证，GitHub 有 EU
数据保护协议）。

**可能不直接受 GDPR 管辖的工具**：火山引擎
Trae（主要面向中国市场，产品名含”CN”）、智谱 AI（主要通过 bigmodel.cn
服务中国用户）、Kimi/Moonshot（虽有国际用户但主要市场在中国）、通义灵码（主要服务阿里云中国区客户）。但如果有欧盟居民使用这些服务，GDPR
仍可能被触发。

### 5.2 各工具与 GDPR 核心条款的合规性

GDPR 中与 AI 编程工具数据政策最相关的条款包括：

**Article 7(3)
撤回同意权**：数据主体有权随时撤回同意，且撤回的便利程度不得低于给予同意时。

**Article 7(4)
同意的自由性**：评估同意是否”自由给予”时，应最大程度考虑合同的履行是否以同意处理非必要个人数据为条件（即禁止
bundling）。

**Article 17 被遗忘权**：用户有权要求删除个人数据。

**Article 5(1)(e)
存储限制原则**：数据保存期限应限于实现处理目的所需的期间。

| 工具 | Art.7(3) 撤回权 | Art.7(4) 非捆绑 | Art.17 删除权 | Art.5(1)(e) 存储限制 | 综合评估 |
| --- | --- | --- | --- | --- | --- |
| **通义灵码** | ✅ 无需撤回 | ✅ 不收集 | ✅ 不存储 | ✅ 不保留 | 🟢 合规 |
| **Tabnine** | ✅ 无需撤回 | ✅ 不收集 | ✅ 零保留 | ✅ 零保留 | 🟢 合规（已认证） |
| **GitHub Copilot** | ✅ 可撤回 | ✅ 未捆绑 | ✅ 可删除 | ⚠️ 28天保留 | 🟢 基本合规 |
| **Windsurf** | ✅ 可撤回 | ✅ 未捆绑 | ✅ 可删除 | ✅ 企业零保留 | 🟢 基本合规 |
| **Amazon Q** | ✅ 可撤回 | ✅ 未捆绑 | ✅ 可删除 | ⚠️ 免费版可能保留 | 🟢 基本合规 |
| **Google Gemini** | ⚠️ 免费版opt-out不清晰 | ⚠️ 免费版默认收集 | ✅ 可删除 | ✅ 付费版stateless | 🟡 免费版存疑 |
| **Anthropic** | ⚠️ 可撤回但UI有引导 | ⚠️ 需选择才能继续使用 | ⚠️ 5年保留期较长 | ⚠️ **5年**保留 | 🟡 边界操作 |
| **OpenAI** | ✅ 可撤回 | ⚠️ 消费者条款有perpetual license | ⚠️ perpetual license与删除权矛盾 | ⚠️ 未明确期限 | 🟡 消费者条款存疑 |
| **Cursor** | ✅ 可撤回 | ✅ 未捆绑 | ⚠️ embeddings存储 | ⚠️ 未明确期限 | 🟡 存在模糊地带 |
| **火山引擎** | ❌ **“技术上无法撤回”** | ❌ **终止授权=停止服务** | ❌ **永久保留** | ❌ **永久** | 🔴 明显冲突 |
| **智谱 AI** | ❌ **无opt-out** | ❌ **使用即授权** | ⚠️ 匿名化后继续保留 | ❌ **永久授权** | 🔴 明显冲突 |
| **Kimi** | ⚠️ 名义可撤回，实际困难 | ⚠️ 使用即同意训练 | ⚠️ 已训练不可逆 | ⚠️ 无明确期限 | 🔴 多处冲突 |

### 5.3 火山引擎条款的 GDPR 冲突分析

火山引擎是调研对象中与 GDPR 冲突最明显的。具体来看：

**Art.7(3) 撤回同意权**：GDPR
明确规定”数据主体有权随时撤回同意”，且撤回的便利程度不得低于给予同意时。火山的”技术上无法撤回”直接与此矛盾。虽然火山提供了”联系客服终止授权”的形式路径，但附带条件是”终止授权即停止服务”，这构成了对行使撤回权的惩罚。

**Art.7(4) 同意的非捆绑原则**：GDPR 的 Recital 43
指出，当合同的履行以同意处理非合同必要数据为条件时，该同意不应被视为自由给予。火山将数据训练授权与服务使用捆绑（不同意=不能用），正是
GDPR 试图禁止的 bundling 模式。

**Art.17
被遗忘权**：用户有权要求删除个人数据。“已用于训练的数据在技术上无法撤回”意味着平台无法履行删除义务。值得注意的是，“技术上做不到”在
GDPR 框架下不是合规抗辩。GDPR
的逻辑是：如果你无法满足删除义务，那你一开始就不应该以这种方式处理数据。这也是
Tabnine 选择”根本不保留”路线的法律逻辑所在，从架构上绕开删除义务。

**Art.5(1)(e)
存储限制原则**：“永久”保留与数据最小化原则直接矛盾。

### 5.4 为什么这些条款实践中能存在

理解了法律冲突后，一个自然的问题是：为什么这些条款能存在？原因有几个层面。

**管辖权层面**：火山引擎、智谱、Kimi
的主要市场在中国，它们大概率不认为自己受 GDPR
管辖。激进的数据条款之所以能写入协议，恰恰是因为这些工具不打算接受 GDPR
的约束。

**中国法律层面**：中国的《个人信息保护法》（PIPL）在条文上与
GDPR 有类似要求。PIPL 第 15
条规定个人有权撤回同意，且个人信息处理者应提供便捷的撤回方式；第 47
条规定个人有权请求删除个人信息。火山的条款与 PIPL 之间同样存在张力。但
PIPL
对”匿名化处理后的数据”有豁免条款，而火山和智谱的协议中都提到了匿名化，这可能是它们在国内法律框架下的合规论据。更重要的是，PIPL
的执法力度与 GDPR 存在实质差异。

**行业层面**：AI
训练数据的不可逆性是全行业面临的技术事实，Anthropic 在 2025 年 8 月的
FAQ 中也暗示了类似逻辑。区别在于，受 GDPR 管辖的厂商（如
Anthropic、OpenAI）选择了提供 opt-out
机制并设定有限保留期来应对这个问题；而不直接受 GDPR
管辖的国内厂商则选择了在条款中直接写明”永久”和”不可撤回”。

### 5.5 对用户的实际影响

对于身处欧盟或关心 GDPR 合规的用户，建议如下：

选择已通过 GDPR 认证或明确声明合规的工具（Tabnine、GitHub Copilot
Enterprise、Windsurf Enterprise）。使用国际厂商工具时，确认 opt-out
已生效。避免在未确认数据保护条款的情况下使用国内工具的个人版。企业场景下，如必须使用国内工具，应选择支持
VPC/私有化部署的企业版，并签署包含 GDPR
对等保护条款的数据处理协议（DPA）。

需要特别指出的是，Anthropic 的 5 年数据保留期虽然在 GDPR
框架下存在争议（存储限制原则），但它仍然保留了用户撤回同意和切换设置的权利，且
EU 数据主体可依据 GDPR
独立主张权利。这与火山引擎”永久+不可撤回+捆绑服务”的三重限制有本质区别。

---

## 六、信息来源汇总

### 官方政策文档

- 火山引擎数据授权使用协议：https://www.volcengine.com/docs/82379/2047627
- 智谱 AI
  用户协议：https://docs.bigmodel.cn/cn/terms/user-agreement
- 智谱 AI
  隐私政策：https://docs.bigmodel.cn/cn/terms/privacy-policy
- Kimi
  开放平台服务协议：https://platform.moonshot.cn/docs/agreement/modeluse
- Kimi
  开放平台隐私政策：https://platform.moonshot.cn/docs/agreement/userprivacy
- 通义灵码隐私政策：https://terms.alicdn.com/legal-agreement/terms/privacy\_policy\_full/20231023213159724/20231023213159724.html
- 通义灵码 FAQ：https://help.aliyun.com/zh/lingma/support/faq
- Anthropic
  消费者条款更新：https://www.anthropic.com/news/updates-to-our-consumer-terms
- Anthropic 隐私中心：https://privacy.claude.com/
- OpenAI Terms of
  Use：https://openai.com/policies/row-terms-of-use/
- OpenAI Service
  Terms：https://openai.com/policies/service-terms/
- GitHub Copilot
  附加产品条款：https://docs.github.com/site-policy/github-terms/github-terms-for-additional-products-and-features
- Cursor 隐私政策：https://cursor.com/privacy
- Cursor 数据使用概览：https://cursor.com/data-use
- Windsurf Teams ToS：https://windsurf.com/terms-of-service-teams
- Windsurf Individual
  ToS：https://windsurf.com/terms-of-service-individual
- Windsurf 安全页面：https://windsurf.com/security
- Tabnine
  隐私文档：https://docs.tabnine.com/main/welcome/readme/privacy
- Tabnine 代码隐私：https://www.tabnine.com/code-privacy/
- Gemini Code Assist
  数据治理：https://developers.google.com/gemini-code-assist/docs/data-governance
- Amazon Q Developer
  FAQs：https://aws.amazon.com/q/developer/faqs/

### 社区讨论与第三方分析

- Trae IDE
  隐私争议：https://www.letsclouds.com/news/trae-ide-data-privacy-controversy
- Trae
  遥测研究：https://github.com/segmentationf4u1t/trae\_telemetry\_research
- Kimi Reddit
  讨论：https://www.reddit.com/r/kimi/comments/1qpeknq/
- Kimi Hugging Face
  讨论：https://huggingface.co/moonshotai/Kimi-K2-Thinking/discussions/24
- Kimi
  隐私分析：https://gist.github.com/gadgetb0y/11931119946c2e9dcae0a438fdefe0d5
- Claude
  隐私政策争议：https://www.reddit.com/r/ClaudeAI/comments/1nd73si/
- TechCrunch Anthropic
  报道：https://techcrunch.com/2025/08/28/anthropic-users-face-a-new-choice-opt-out-or-share-your-data-for-ai-training/
- Cursor
  论坛隐私讨论：https://forum.cursor.com/t/concerns-about-privacy-mode-and-data-storage/5418
- GitHub Copilot
  数据讨论：https://github.com/orgs/community/discussions/152229
- OpenAI TOS
  变更追踪：https://tostracker.app/document/openai/version/6839

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
