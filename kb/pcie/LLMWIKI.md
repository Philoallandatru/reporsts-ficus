# 使用 llm-wiki-compiler 构建 PCIe 中文知识库

本项目使用 `sources/` 中已有的 PCIe 规范分析、协议层、TLP/DLLP、LTSSM、配置空间、中断、电源管理和 SR-IOV 页面作为本地输入，输出语言固定为简体中文。编译时必须保持规范引用、协议层边界和图文并茂的阅读体验。

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

- 每个适合结构化表达的核心页面至少包含一张解释性图：拓扑/协议栈用 Mermaid flowchart，LTSSM/电源/错误恢复用 Mermaid stateDiagram，TLP/DLLP/配置空间用 ASCII 位域图或 Markdown 表格。
- 图下必须写明“解释性重绘”或对应 PCIe Base Specification 章节/图号；不能把推断图伪装成规范原图。
- 图中保留层级、链路方向、请求/完成关系、状态分支和错误恢复边界；无法由来源确认的细节标为“实现示例”。
- 页面仍需提供中文解释、英文术语、规范引用和至少一个硬件/驱动实现视角的边界说明，图不能替代文字定义。
- 优先复用来源中的 Mermaid/ASCII 图；不要无依据创造寄存器位宽、编码规则或链路时序数值。

## 编译与审核

```powershell
npx -p llm-wiki-compiler llmwiki status --json
npx -p llm-wiki-compiler llmwiki compile --review --lang zh-CN --concurrency 3
npx -p llm-wiki-compiler llmwiki lint
npx -p llm-wiki-compiler llmwiki query "PCIe 三层协议、TLP/DLLP、LTSSM 和 NVMe endpoint 的边界是什么？" --lang zh-CN
npx -p llm-wiki-compiler llmwiki view --open
```

先审核候选页面，再批准进入 `wiki/`；存在错误或无法追溯引用的页面应拒绝或修正。
