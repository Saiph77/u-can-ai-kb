# 知识库阅读预览

本地 Web 界面，浏览本仓库的阅读目录（`by-audience/`、`by-format/`、`open-mic-archive/`、Frank、Jenny 等）。

## 启动

在仓库根目录：

```bash
python3 viewer/server.py
```

浏览器打开：<http://127.0.0.1:8766/>

可选参数：

```bash
python3 viewer/server.py --port 8766
python3 viewer/server.py --kb-root /path/to/this-repo
```

## 功能

- 按 **内容库** 切换：读者入口 / 内容形态 / 开放麦档案 / Jenny / Frank / 索引说明
- **子栏目** 筛选（如 `01-世界观与判断`、`03-视频逐字稿`）
- 标题 / 路径搜索
- Markdown 渲染预览 + 原文切换
- **重新扫描**：改完 markdown 后点此刷新目录

依赖：Python 3.9+ 标准库；前端 Markdown 用 CDN 上的 `marked` + `DOMPurify`。
