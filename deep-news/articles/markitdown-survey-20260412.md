---
title: "MarkItDown：8 万 Star 的文件转 Markdown\n工具，到底好不好用？"
date: 2026-04-12
source: https://yage.ai/share/markitdown-survey-20260412.html
slug: markitdown-survey-20260412
lang: zh
---
# MarkItDown：8 万 Star 的文件转 Markdown 工具，到底好不好用？

发布于 2026 年 4 月 12 日 · [查看原网页](https://yage.ai/share/markitdown-survey-20260412.html)

你大概率是在朋友圈、群聊或公众号里看到了 MarkItDown
的推荐。典型的转发文案是这样的：“微软开发了一款工具，可以将几乎任何格式转换为
Markdown 文件。没有自定义解析器。没有损坏的布局。没有混乱的文本。”

如果你因此产生了兴趣——想了解这个工具的真实水平，或者正好需要把一些文件转成纯文本/Markdown
却不知道该用什么——这篇文章会帮你省掉自己踩坑的时间。

先说结论：MarkItDown
的效果因格式而异，差异非常大。Word、Excel、PowerPoint 这类 Office
文档的转换效果确实可以，API 也足够简洁。但 PDF
的转换质量在同类工具中排名垫底，标题和表格几乎完全丢失。如果你手头主要是
Office 文档，它是一个合理的选择；如果你需要处理
PDF，应该用别的工具。

## 一个时间线上的意外

很多人以为 MarkItDown 是最近才出现的新工具。实际上，它的 [GitHub 仓库](https://github.com/microsoft/markitdown)创建于
2024 年 11 月 13 日，第一个 PyPI 预发布版也是同一天。到 2024 年 12
月，它就在社交媒体上引起了第一波传播，两周内拿到了 25,000 颗 star。到
2026 年 4 月，累积 star 已经超过 87,000。

换句话说，这个工具已经存在了将近一年半。它不是刚出炉的新东西，而是一个在社交媒体的周期性传播中反复被”重新发现”的项目。这个事实本身就说明：它的传播力来自微软的品牌效应和”万能转换器”的故事吸引力，而不是来自技术社区的持续推荐。在真正做文档处理的开发者中间，选型讨论的主角早已是
Docling 和 Marker。

## 按格式拆解：哪些能用，哪些不行

### Word 文档：这是它最强的格式

MarkItDown 把 .docx 文件转成 Markdown
的效果确实不错。标题层级、列表、加粗/斜体、链接都能准确保留。[Real Python
的评测](https://realpython.com/python-markitdown/)直接说 “MarkItDown did a great job converting the document to
Markdown”。

底层用的是 [mammoth](https://github.com/mwilliamson/python-mammoth)
这个库，先转成 HTML 再转成 Markdown。mammoth 本身是一个成熟的 Word
处理库，设计理念是优先保留语义结构。MarkItDown 在这里做的是把 mammoth
的输出进一步清理成干净的 Markdown 格式。

如果你手头主要是 Word 文档，MarkItDown 是一个合理的选择。

### Excel：可以接受

通过 pandas + openpyxl 读取数据，输出为 Markdown 表格。多 Sheet
也能处理。对于结构规整的电子表格，效果可以接受。Hacker News
上有用户分享了用 `uvx markitdown my-excel.xlsx` 把 Excel 转成
GitLab 可渲染表格的[实际经验](https://news.ycombinator.com/item?id=42410803)。

### PowerPoint：提取文本还行，别期待完美还原

能提取幻灯片标题和要点文本，按幻灯片编号分隔。但它提取的是文本内容，不是视觉布局。如果你的目的是”让
AI 读懂这个 PPT
讲了什么”，够用。如果你期望原样还原幻灯片的排版，这不是它的设计目标。

顺便提一下，MarkItDown 和底层的 python-pptx
都只解决”读”的问题。如果你还需要让 AI 修改 PPT（改文字、换图片、加
slide）并且能渲染成图片验证效果，我们自己做了一个 [pptx\_skill](https://github.com/grapeot/knowledge_working/tree/main/tools/pptx_skill)，把读、写、渲染封装成了
CLI + Python library，AI 改完可以自己渲染检查，不用人工打开 PowerPoint
截图反馈。

### PDF：核心场景，但质量垫底

这是最关键的部分，也是转发文案中”没有损坏的布局、没有混乱的文本”与现实偏差最大的地方。

[OpenDataLoader
Benchmark](https://opendataloader.org/docs/benchmark) 对 12 个 PDF 转 Markdown 引擎做了量化评测。MarkItDown
排名倒数第二，综合得分 0.589（满分 1.0）。作为对比，排名第一的 Docling
得分 0.882。

几个关键分项更能说明问题：

| 指标 | MarkItDown | Docling | Marker | MinerU |
| --- | --- | --- | --- | --- |
| 标题层级保持 | **0.000** | 0.824 | 0.796 | 0.743 |
| 表格保真度 | 0.273 | 0.887 | 0.808 | 0.873 |
| 阅读顺序 | 0.844 | 0.898 | 0.890 | 0.857 |

标题层级 0.000 的意思是：MarkItDown 完全不区分 PDF
中的标题和正文，所有文字都输出为同一级别的纯文本。表格保真度 0.273
意味着表格结构基本崩溃。

这不是 benchmark 独有的发现。[systenics.ai
用一份真实的银行对账单 PDF 做了对比测试](https://systenics.ai/blog/2025-07-28-pdf-to-markdown-conversion-tools)，MarkItDown 的输出被描述为
“a long, jumbled list of
text”。交易表格被按列拆散——先列出所有日期，再列出所有金额——数据关联完全丢失。同一文档用
Docling 转换，表格完美保留。

GitHub issues 也大量印证这一点。[Issue #296](https://github.com/microsoft/markitdown/issues/296)
的原文：“PDF isn’t supported. Not really, because it fails most relevant
tests: recognizing headings, footers, tables, and more is not possible.”
[Issue
#41](https://github.com/microsoft/markitdown/issues/41) 是一位用户尝试转换 SEC 10-K 财报，结果 “no structure”。

原因很清楚：MarkItDown 处理 PDF 时默认使用
pdfminer.six，这个库只做文本流提取，不做版面分析，不做
OCR，不做表格识别。它可以通过接入 Azure Document Intelligence
来改善质量（微软自家的付费云服务，提供版面分析 + 表格提取 +
OCR），但那已经不是”开箱即用”了，而且涉及额外的费用和配置。

### 图片和音频

图片默认只提取 EXIF 元数据。如果你想获得图片的文字描述，需要额外配置
OpenAI GPT-4o 等 LLM 作为后端。音频转录使用 Google 的 SpeechRecognition
API。这些功能存在但依赖外部服务，不是本地自包含的能力。

## 它本质上是一个粘合层

[InfoWorld](https://www.infoworld.com/article/3963991/markitdown-microsofts-open-source-tool-for-markdown-conversion.html)
在分析文章中指出，MarkItDown “functions largely as a wrapper around
existing third-party libraries rather than offering novel conversion
capabilities”。这个批评基本准确。

Word 转换靠 mammoth，Excel 靠 pandas + openpyxl，PowerPoint 靠
python-pptx，PDF 靠 pdfminer.six，HTML 靠 BeautifulSoup +
markdownify。MarkItDown 自身的技术贡献是：用一个统一的
`convert()`
接口把这些库封装起来，让你不用关心底层用的是什么。

这是否意味着它没有价值？不是。统一接口本身就是价值——如果你需要处理的文件格式很杂（今天
Word 明天 Excel 后天
HTML），一个统一的入口比分别调用五个不同的库要方便。MarkItDown 还提供了
plugin 机制和 MCP server（可以与 Claude Desktop、Cursor 等 AI
工具直接集成），这些是底层库不提供的。

但如果你主要处理某一种格式（比如
PDF），直接用专门优化过的工具会好很多。MarkItDown
的价值在于”广度”和”便利”，不在于任何单一格式上的”深度”。

## 如果不用 MarkItDown，用什么？

这取决于你的实际需求。以下是一个简明的选型指南：

**主要处理 PDF，追求转换质量**：用 [Docling](https://github.com/DS4SD/docling)（IBM Research
开发）。在 OpenDataLoader benchmark
中综合得分最高（0.882），表格和标题保持都是同类最佳。MIT
许可证，LangChain 和 LlamaIndex 都有原生集成。需要安装 PyTorch（约 1
GB），有 GPU 时 0.49 秒/页，纯 CPU 也能跑（3.1 秒/页）。Red Hat
已将其集成进 RHEL AI，是目前企业采用最多的方案。

**大量 PDF 批量处理，速度优先**：考虑 [MinerU](https://github.com/opendatalab/MinerU)（OpenDataLab）。GPU
上 0.21 秒/页，最快。表格识别也很强（0.873）。但 AGPL-3.0
许可证限制商用，且不支持 macOS。

**主要处理 Office 文档和杂格式**：MarkItDown
的格式广度和零 GPU
要求在这个场景下确实是优势。安装简单（`pip install 'markitdown[all]'`，约
251 MB），不需要 PyTorch。

**需要极轻量的方案**：[Kreuzberg](https://github.com/Goldziher/kreuzberg)（71
MB，Apache-2.0，Rust 核心）或 [PyMuPDF4LLM](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/)（速度最快
0.091 秒/页，但 AGPL 许可证）。

**商用场景下的许可证注意事项**：MarkItDown（MIT）和
Docling（MIT）对商用没有限制。Marker 用
GPL，商用需要向作者购买商业许可。MinerU 和 PyMuPDF4LLM 都是
AGPL，意味着基于它们构建的服务需要开源或购买商业许可。

|  | MarkItDown | Docling | Marker | MinerU |
| --- | --- | --- | --- | --- |
| PDF 综合质量 | 0.589 | **0.882** | 0.861 | 0.831 |
| 表格保真 | 0.273 | **0.887** | 0.808 | 0.873 |
| 格式支持数 | ~25 种 | ~38 种 | 3 种 | 3 种 |
| 需要 GPU | 否 | 推荐 | 是 | 是 |
| 安装体积 | ~251 MB | ~1 GB | 较大 | 较大 |
| 许可证 | MIT | MIT | GPL | AGPL |
| macOS | 支持 | 支持 | 支持 | 不支持 |

## 总结

MarkItDown 是一个有明确适用范围的工具：Office 文档转换效果可以，API
简洁，格式覆盖广，不需要 GPU，MIT
许可证友好。作为一个”把各种杂格式统一转成文本”的粘合层，它有自己的位置。

但它不是那条转发文案所暗示的”万能转换器”。它的各格式转换质量参差不齐：Office
文档可以信赖，PDF 则在 12
个同类工具中排名倒数第二（标题识别为零、表格基本崩溃）。了解这个差异，才能决定它是否适合你手头的具体需求。如果你确实需要处理
PDF，Docling 是目前综合最优的开源方案。

87,000 颗 star
说明这个项目的故事讲得好，不说明它在每种格式上都做得好。选工具跟选其他东西一样：最好的不是最火的那个，而是在你的实际场景里能稳定完成任务的那个。

---

*数据来源：[OpenDataLoader
Benchmark](https://opendataloader.org/docs/benchmark)、[systenics.ai
实测](https://systenics.ai/blog/2025-07-28-pdf-to-markdown-conversion-tools)、[GitHub
Issues](https://github.com/microsoft/markitdown/issues)、[Real
Python](https://realpython.com/python-markitdown/)、[InfoWorld](https://www.infoworld.com/article/3963991/markitdown-microsofts-open-source-tool-for-markdown-conversion.html)、[PyPI](https://pypi.org/project/markitdown/)*

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
