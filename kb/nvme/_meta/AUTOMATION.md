# 自动化运行手册

处理 `_meta/progress.json` 中接下来的 8 个源页面。两侧各包含一个邻居页面以及与本批次相交的所有书签条目。

## 每次运行的契约

1. 编辑前先校验源哈希。
2. 抽取概念、关系、不变量（invariants）、规范性需求、标识符、状态变迁以及交叉引用。
3. 优先更新已有的权威概念页（canonical concept pages），而非制造同义词或为每个字段单独建页。
4. 对每个触及的概念页，添加有用的 ASCII 图、紧凑的 Markdown 表格，或明确给出 `visual not useful` 的判断。
5. 将精确的寄存器/命令/数据布局以及跨页表格先放入 `review_queue`，待与渲染后的页面比对。
6. 每一条实质性陈述和每一张图都必须引用本地 PDF 页面。
7. 当术语趋于稳定时，同步更新概念索引、相关 maps 和 `CONTEXT.md`。
8. 运行 `tools/check_wiki.py nvme-wiki`；只有检查通过后才推进进度。
9. 完成最后一页之后，进行链接、别名、术语、图示以及矛盾点的多轮检查，再把 `status` 设为 `complete`。

## 概念页形态

```markdown
# 权威概念

简短定义。

## 心理模型（Mental model）
ASCII 图或一段简短解释，说明为什么此处不需要图。

## 契约与不变量（Contract and invariants）
## 生命周期或结构（Lifecycle or structure）
## 关系（Relationships）
## 边界情况（Edge cases）
## 证据（Evidence）
```
