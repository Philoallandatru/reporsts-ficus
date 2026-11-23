# LLMWiki 使用说明

本目录按 llmwiki 风格组织为可审阅 Markdown 知识库：

- `wiki/index.md`：知识库首页
- `wiki/concepts/`：概念页与框架页
- `SOURCES.md`：官方来源清单
- `CONCEPT_INDEX.md`：人工维护索引

当前版本是手工编译的知识库，没有运行 LLM 自动编译流程。原因是本任务需要精确核对快速变化的推理框架参数，手工写入能更好地固定参数语义、来源和调参解释。

如果后续要接入 `llm-wiki-compiler`：

1. 把官方参数页、CLI help 输出和源码 README 放入 `sources/`。
2. 运行 `llmwiki ingest` / `llmwiki compile --review`。
3. 对生成候选页逐页核对参数名、默认值和版本日期。
4. 运行 `llmwiki lint` 检查链接和引用。

建议每次刷新时记录：

- 框架版本或文档日期。
- 官方来源 URL。
- 新增/移除/重命名的参数。
- 对调参原理的影响。
