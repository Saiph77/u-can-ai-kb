# U can AI 知识库

给 U can AI 群友的知识库。想维护或让 AI 改这个仓库，请看 [`AGENTS.md`](AGENTS.md)。

## 怎么读

| 你想… | 打开 |
|------|------|
| 从哪里读起 | [`index-by-audience.md`](index-by-audience.md) → [`by-audience/`](by-audience/) |
| 按文章 / 视频 / Skill 形态找 | [`index-by-format.md`](index-by-format.md) → [`by-format/`](by-format/) |
| 读开放麦第 1–7 期 | [`index-of-open-mic.md`](index-of-open-mic.md) → [`open-mic-archive/`](open-mic-archive/) |
| 读 Jenny 写的成文 | [`Jenny/`](Jenny/) |
| 读 Frank 访谈与指令 | [`Frank/`](Frank/) |
| 在浏览器里翻 | `python3 viewer/server.py` → http://127.0.0.1:8766 |

建议路径：先读 `index-by-audience.md` 里「从这里开始」的 3 篇锚点；通勤用 `by-audience/05-视频精选/`；开放麦用档案索引按主题 / 嘉宾 / 工具跳。

## 开放麦怎么分

`open-mic-archive/` 是开放麦的**唯一目录**（知识页、逐字稿、AI 总结、原稿都在各期文件夹里）。Jenny 成文另放 `Jenny/`，不要混读。

| 类型 | 是什么 | 在哪 |
|------|--------|------|
| 知识页 | 可带走的判断、工具、观众价值 | `open-mic-archive/0N-…/知识页.md` |
| 逐字稿 | 修订后的现场原文（保留原文件名） | 各期文件夹内含「逐字稿」的文件 |
| AI 总结 | 复盘稿 / 工作稿 | 各期 `AI总结-*.md`（若该文件就是成文，见 Jenny） |
| Jenny 成文 | 对外发表的评述 | `Jenny/` |

## 目录

```
u-can-ai-kb/
├── readme.md                 # 给人读（本文件）
├── AGENTS.md                 # 给 AI / 协作者
├── index-by-audience.md
├── index-by-format.md
├── index-of-open-mic.md
├── by-audience/              # 按读者入口
├── by-format/                # 按内容形态
├── open-mic-archive/         # 开放麦原文
├── Jenny/                    # Jenny 成文（第 1–7 期）
├── Frank/                    # 访谈、指令、mems、skills
├── viewer/                   # 本地预览，端口 8766
└── upstream/                 # 立正 / Infra 子模块（完整源库，非阅读入口）
```

本仓库自包含，不依赖其他本地目录。维护方式见 [`AGENTS.md`](AGENTS.md)。
