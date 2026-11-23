# 使用 llm-wiki-compiler 构建 NVMe 中文知识库

本项目使用 `sources/` 中已有的 NVMe Base 2.1 术语、架构图、概念页和文档映射作为本地输入，输出语言固定为简体中文。编译时必须保持规范引用、概念边界和图文并茂的阅读体验。

## Provider

本机配置位于项目根目录 `.env`，不要提交或在日志中打印密钥：

```text
LLMWIKI_PROVIDER=anthropic
ANTHROPIC_BASE_URL=https://api.minimaxi.com/anthropic
LLMWIKI_MODEL=MiniMax-M2.7
LLMWIKI_OUTPUT_LANG=zh-CN
LLMWIKI_COMPILE_CONCURRENCY=3
```

## 图文并茂要求

- 每个适合结构化表达的核心页面至少包含一张解释性图：架构用 Mermaid flowchart，生命周期用 Mermaid stateDiagram，命令/寄存器/队列布局用 ASCII 位域图或 Markdown 表格。
- 图下必须写明“解释性重绘”或对应规范页码；不能把推断图伪装成规范原图。
- 图中保留方向、层级、队列归属、可选分支和 reset/错误边界；无法由来源确认的细节标为“实现示例”。
- 页面仍需提供中文解释、英文术语、规范引用和至少一个工程视角的边界说明，图不能替代文字定义。
- 优先复用来源中的 Mermaid/ASCII 图；不要无依据创造寄存器位宽、时序数值或 transport 行为。

## 编译与审核

```powershell
npx -p llm-wiki-compiler llmwiki status --json
npx -p llm-wiki-compiler llmwiki compile --review --lang zh-CN --concurrency 3
npx -p llm-wiki-compiler llmwiki lint
npx -p llm-wiki-compiler llmwiki query "NVMe controller、queue pair、namespace 和 PCIe transport 的边界是什么？" --lang zh-CN
npx -p llm-wiki-compiler llmwiki view --open
```

先审核候选页面，再批准进入 `wiki/`；存在错误或无法追溯引用的页面应拒绝或修正。
