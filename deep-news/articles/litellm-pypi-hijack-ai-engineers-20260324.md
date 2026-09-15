---
title: "LiteLLM PyPI 包被劫持：AI 工程师需要知道的事"
date: 2026-03-24
source: https://yage.ai/share/litellm-pypi-hijack-ai-engineers-20260324.html
slug: litellm-pypi-hijack-ai-engineers-20260324
lang: zh
---
# LiteLLM PyPI 包被劫持：AI 工程师需要知道的事

发布于 2026 年 3 月 24 日 · [查看原网页](https://yage.ai/share/litellm-pypi-hijack-ai-engineers-20260324.html)

---

如果你是一个日常使用 Python 写 AI 应用的工程师，LiteLLM
这个名字大概率不陌生。它帮你用一套统一接口调用
OpenAI、Anthropic、Azure、Bedrock 等各家模型 API，省去了适配多个 SDK
的麻烦。很多人直接用它做 model
gateway，也有很多人并不是直接装的它，而是通过 DSPy、CrewAI
等框架间接把它拉进了自己的依赖树。

2026 年 3 月 24 日，LiteLLM 在 PyPI
上的官方包被短暂劫持了。攻击者用窃取的发布凭证，往 PyPI
上传了两个伪造版本（`1.82.7` 和
`1.82.8`），里面嵌入了凭证窃取代码。这两个版本在 LiteLLM 的
GitHub 仓库里没有任何对应的 tag 或 release。从上传到 PyPI
将包隔离，暴露窗口大约两到三个小时（UTC 10:39 至约
11:25）。最后一个干净版本是 `1.82.6`。

先说最重要的判断：这是一起 Python
包发布通道的入侵，和模型层完全无关。没有任何证据表明
OpenAI、Anthropic、Google
等模型提供商本身被攻破，也没有证据表明模型权重或推理 API
被篡改。被攻击的是 LiteLLM 这个 Python 包在 PyPI 上的发布权限。

但这里有一个需要特别注意的点，也是这件事值得 Python-heavy AI
工程师额外重视的原因：其中 `1.82.8` 这个版本的影响范围远超
LiteLLM 自身的调用路径。它在安装时会往 `site-packages`
目录里放一个 `.pth` 文件。Python
解释器有一个大多数开发者不太会接触到的机制：每次启动时，它会自动扫描
`site-packages` 里的 `.pth` 文件，如果其中某行以
`import` 开头，就直接执行（这是 Python 标准库 [`site`
模块](https://docs.python.org/3/library/site.html)的设计）。这意味着，只要 `1.82.8` 被安装进了某个
Python 环境，该环境里启动的任何 Python
进程都会执行恶意代码，不管你跑的是 Flask、Jupyter、pytest
还是一个完全不相关的脚本，也不需要你 import
LiteLLM。换句话说，这不只是”用了某个 LiteLLM
的功能才会中招”，而是”装了这个版本，同一环境里所有 Python
程序都可能受影响”。

为什么这件事值得 AI 工程师特别关注，而不只是又一个 PyPI
投毒新闻？因为 LiteLLM
在你的工作流中占据的位置比一般工具库敏感得多。一个典型的 LiteLLM
部署（无论是当库用还是当 proxy 跑）持有通往多个模型提供商的 API
key，可能还有数据库连接串和云基础设施凭证。恶意代码一旦在这样的环境里执行，泄露的不是某一个
key，而是一整组跨提供商、跨服务的凭证集合。

更关键的是，你可能从未主动装过 LiteLLM，但它就在你的环境里。DSPy 用
LiteLLM 做模型调用的主要通道，CrewAI
在部分路径下也依赖它。如果你在暴露窗口内装过或更新过这些框架，且依赖版本没有锁定，pip
的依赖解析可能已经帮你拉入了恶意版本。

那么，你现在需要做什么？如果你的 Python 环境在 3 月 24 日 UTC 10:39
到 11:25 之间有过安装或更新操作，并且涉及
LiteLLM（直接或间接），建议你先跑一下 `pip show litellm`
看版本号。如果是 1.82.7 或 1.82.8，按凭证已泄露处理。如果你的版本一直在
1.82.6
或更早，且暴露窗口内没有更新操作，这次事件对你来说主要是一个需要吸取的教训。后文会给出更详细的自查边界。

---

## 恶意代码做了什么

两个伪造版本都嵌入了凭证窃取代码，区别在于触发方式。

`1.82.7` 把恶意代码藏在
`litellm/proxy/proxy_server.py` 里（经过双重 Base64
编码）。只有你用了 LiteLLM 的 proxy 功能，比如通过
`litellm --proxy` 启动或者代码里 import 了
`litellm.proxy.proxy_server`，它才会执行。

`1.82.8` 的触发方式就是前面提到的 `.pth`
机制，影响整个 Python 环境，不限于 LiteLLM 的调用路径。

恶意代码本身做三件事（[Endor Labs
分析](https://www.endorlabs.com/learn/teampcp-isnt-done)，[Wiz
分析](https://www.wiz.io/blog/threes-a-crowd-teampcp-trojanizes-litellm-in-continuation-of-campaign)）：第一，收割环境变量、SSH 密钥、AWS/GCP/Azure 凭证、Kubernetes
配置、Docker 配置、数据库密码、`.env`
文件等一切可达的凭证。第二，用 AES-256 加密收集到的数据，密钥再用内嵌
RSA 公钥封装，发送到攻击者的域名。第三，如果检测到 Kubernetes
服务账户令牌，尝试横向移动：读取集群所有 namespace 的
secrets，在节点上部署特权 Pod，通过 `chroot`
进入宿主机安装持久化后门（`sysmon.py` + systemd 服务），每 50
分钟轮询 C2 服务器。

由于外传数据在发送前已经加密，受影响用户无法通过分析网络流量来判断自己的凭证是否被实际窃取。

---

## 这件事的背景：攻击者怎么拿到了 LiteLLM 的发布权限

LiteLLM 自己的代码没有漏洞。攻击链的起点在更上游，涉及一个很多 AI
工程师可能用过但不一定留意过的工具：Trivy。

Trivy 是 Aqua Security 维护的一个开源安全扫描器，很多团队把它集成在
CI/CD
流水线里，用来检查容器镜像、代码依赖是否有已知漏洞。因为它的工作性质，Trivy
在流水线中通常拥有比较高的权限：它需要读取仓库代码、拉取依赖信息，经常能接触到流水线上下文中的
token 和 secrets。

2026 年 3 月初，一个叫 TeamPCP 的攻击者入侵了 Trivy 的 GitHub
Actions。具体来说，Aqua Security
之前发现了一次凭证泄露，并且尝试轮换（替换）受影响的凭证。但这个轮换过程做得[不完整](https://www.aquasec.com/blog/trivy-supply-chain-attack-what-you-need-to-know/)：替换操作本身仍然给攻击者留下了可用的访问路径，或者在替换过程中暴露了新的
token。攻击者利用这个窗口控制了 Trivy 的 GitHub Actions。

一旦 Trivy 的 CI
组件被控制，攻击者就能读取所有使用该组件的下游项目流水线中的
secrets。LiteLLM 的 CI/CD 流水线恰好使用了 Trivy
做安全扫描，流水线中存放着 PyPI 的发布凭证。攻击者由此拿到了 LiteLLM 在
PyPI 上的发布权限，上传了两个恶意版本。同样的路径也被用来入侵了 [Checkmarx
KICS](https://www.sysdig.com/blog/teampcp-expands-supply-chain-compromise-spreads-from-trivy-to-checkmarx-github-actions)。

事件的发现本身带有偶然性。安全公司 [FutureSearch](https://futuresearch.ai/blog/litellm-pypi-supply-chain-attack/)
注意到，一个运行在 Cursor 里的 MCP 插件把 LiteLLM
作为传递依赖拉入后，恶意代码中 `.pth` 启动器的一个 bug
触发了进程的指数级复制，把机器内存吃光了。如果这个 bug
不存在，恶意代码本来会安静执行。

---

## 谁需要立即自查，谁主要吸取教训

核心判断依据只有一个：你的 Python 环境在暴露窗口（2026-03-24 UTC
10:39 至约 11:25）内是否可能安装或更新了 LiteLLM。

**建议按凭证泄露处理的情况**，满足以下任一条：

在暴露窗口内直接运行过 `pip install litellm`
或类似的安装/更新命令。在暴露窗口内安装或更新了 DSPy、CrewAI 等将
LiteLLM 列为依赖的框架，且没有用 lock file 锁定依赖版本。CI/CD 流水线或
Docker 构建在暴露窗口内跑了不带版本锁定的 LiteLLM 安装。使用 Cursor、VS
Code 等 IDE 的 MCP 插件或 AI 辅助功能，这些功能可能在后台创建 Python
环境并自动拉取依赖。

如果你确认安装了 1.82.7 或
1.82.8，应当假设该环境中所有可达的凭证已经泄露，轮换所有 API key、SSH
密钥、云凭证、数据库密码。如果运行在 Kubernetes 中，审计
`kube-system` namespace 中是否有异常的特权 Pod（镜像
`alpine:latest`，名称前缀 `node-setup-`），检查
`~/.config/sysmon/sysmon.py` 是否存在。

**主要吸取教训即可**，同时满足以下条件：

使用的是官方 LiteLLM proxy Docker 镜像部署（LiteLLM 维护者在 [GitHub Issue
#24518](https://github.com/BerriAI/litellm/issues/24518) 中确认官方镜像未受影响，因为镜像通过 requirements.txt
锁定了依赖版本）。或者从 GitHub 源码安装而非 PyPI。或者版本一直在 1.82.6
或更早，且暴露窗口内未做过更新。所有依赖通过 lock
file（`uv.lock`、`poetry.lock`、`pip-compile`
输出等）锁定到具体版本。

**快速自查步骤：** 运行 `pip show litellm`
查看版本号。在 `site-packages` 目录里搜索
`litellm_init.pth`。检查
`~/.config/sysmon/sysmon.py`
是否存在。三步做完，基本能判断你是否在影响范围内。

---

## 这件事给 AI 工程团队留下的教训

这次事件有几个点值得在日常实践中回溯。

**依赖锁定。** AI
领域迭代快，框架更新频繁，很多人习惯用宽松版本约束甚至直接
`pip install`
不指定版本。在供应链攻击面前，这个习惯从理论风险变成了现实代价。如果你在用
`uv`，`uv.lock` 默认已经做了锁定。如果用 poetry 或
pip-tools，确保 CI/CD 和 Docker 构建只从 lock file 安装。

**传递依赖的可见性。** 你可能从没主动选择过 LiteLLM，但
DSPy、CrewAI 等框架把它拉进了你的环境。AI agent 框架的依赖图通常比传统
Web 应用更深，因为它们要对接多种模型
SDK、工具集成和向量数据库客户端。定期用 `pip list` 或
`uv tree`
审计一下你的环境里实际装了什么，特别关注那些你没有主动选择的包。

**集中式 model gateway 是高价值目标。** LiteLLM Proxy
这类服务天然持有多组 API key 和基础设施凭证。部署时用官方容器镜像比直接
pip install 更安全，API key 通过 secrets manager
注入比写在环境变量里更可控，网关节点的网络出站规则也值得收紧。

**CI/CD 里的安全工具本身也需要被安全管理。**
这次攻击的根因是 Trivy 的 GitHub Actions 被入侵后，攻击者借此窃取了
LiteLLM
的发布凭证。安全扫描器在流水线中通常以高权限运行，却往往不受和应用代码同等严格的版本管控。GitHub
Actions 中引用的第三方 action 应该锁定到完整的 commit SHA 而非版本
tag，因为 tag 可以被 force-push 覆盖，Trivy 的入侵正是利用了这一点。

---

## 结语

这次事件不需要恐慌，但需要认真对待。

它的关键信号不在于攻击手法有多新颖。凭证窃取和 PyPI
投毒都是已知模式。它的关键信号在于，当 AI
工程栈中一个看似普通的中间层组件被入侵时，影响半径远超同类型的传统
Python 包。LiteLLM 这样的 model gateway 和 agent framework runtime
天然聚合了大量凭证和权限，它们在依赖图中的位置决定了一个入侵点可以辐射到整个
AI 基础设施。

对于大多数 AI
工程师，这是一个检查依赖管理实践和凭证隔离策略的好时机。不必等到自己成为受害者。

---

*核心信息来源：[FutureSearch
原始披露](https://futuresearch.ai/blog/litellm-pypi-supply-chain-attack/)、[GitHub Issue
#24512](https://github.com/BerriAI/litellm/issues/24512)、[GitHub Issue
#24518](https://github.com/BerriAI/litellm/issues/24518)、[Endor Labs
分析](https://www.endorlabs.com/learn/teampcp-isnt-done)、[Wiz
分析](https://www.wiz.io/blog/threes-a-crowd-teampcp-trojanizes-litellm-in-continuation-of-campaign)、[Aqua
Security 官方声明](https://www.aquasec.com/blog/trivy-supply-chain-attack-what-you-need-to-know/)、[Sysdig
分析 (KICS)](https://www.sysdig.com/blog/teampcp-expands-supply-chain-compromise-spreads-from-trivy-to-checkmarx-github-actions)。*

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
