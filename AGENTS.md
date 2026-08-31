# AGENTS.md — u-can-ai-kb

给在本仓库工作的 AI agent 与协作者。给人看的导航在 [`readme.md`](readme.md)。

本仓库自包含：clone 后即可阅读、预览。不依赖任何 sibling 目录。没有构建脚本；增删改文章直接改对应文件夹里的 Markdown。

## 目录

| 路径 | 角色 | 怎么改 |
|------|------|--------|
| `by-audience/` | 按读者入口放的正文 | 直接改文件；同步改 [`index-by-audience.md`](index-by-audience.md) |
| `by-format/` | 按内容形态放的正文 | 直接改文件；同步改 [`index-by-format.md`](index-by-format.md) |
| `open-mic-archive/` | 开放麦唯一副本 | 直接改各期文件夹 |
| `Jenny/` | 开放麦对外成文 | 直接改；与 archive 里的源文件对应，不要把成文当逐字稿 |
| `Frank/` | 访谈、指令、mems、skills | 直接改 |
| `index-*.md` | 给人跳转的索引 | 改目录时一起改链接 |
| `viewer/` | 本地预览（8766） | `python3 viewer/server.py` |
| `upstream/` | 立正 / Infra 的 git 子模块（完整源库） | `git submodule update`；不要当阅读入口 |
| `data/stars.json` | 当初从 upstream 挑文的收藏清单（历史记录） | 不必为日常编辑去动 |

## 开放麦文件怎么认

同一期文件夹里可以同时有逐字稿、AI 总结、Jenny 源文件。对外成文以 `Jenny/` 为准。

| 文件 | 角色 |
|------|------|
| `知识页.md` | 可带走的判断、工具、观众价值 |
| 文件名含「逐字稿」、不含「转写原始」 | 修订逐字稿 |
| `AI总结-*` 且不是站点版 / 工作副本 / `Jenny/` 那篇 | AI 复盘 |
| `文章-*` 或站点版 | Jenny 源，阅读用 `Jenny/` |

## 预览

```bash
python3 viewer/server.py
# http://127.0.0.1:8766/
```

只改 markdown 时，网页里点「重新扫描」。改了 `viewer/server.py` 才需要重启进程。

## 子模块

```bash
git clone --recurse-submodules <repo-url>
git submodule update --init --recursive
```

| 路径 | 仓库 |
|------|------|
| `upstream/lizheng-open-context` | https://github.com/sunyuzheng/lizheng-open-context.git |
| `upstream/context-infrastructure` | https://github.com/grapeot/context-infrastructure.git |

阅读用 `by-audience/` / `by-format/`，不要让读者去翻 `upstream/`。
