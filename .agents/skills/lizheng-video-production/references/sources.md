# Sources

## Layout

Skill 与流水线实现分离，并列放在项目根下：

| 路径 | 内容 |
| --- | --- |
| `.agents/skills/lizheng-video-production/` | Skill 定义（`SKILL.md` + `references/`）。`Frank/skills/` 下同名目录是 symlink |
| `lizheng-video-production/` | 实现：`tools/`、`data/`、`README.md`。不在本知识库内 |

编辑 workflow 时改 `.agents/skills/lizheng-video-production/SKILL.md`。

历史 skill 名：`kdb-video-post-production`。

## Supporting

- 独立 skill `xhs-cover-title`：小红书封面+标题路线 B
- 可选：brief 类规则（后期产物反哺选题时）
