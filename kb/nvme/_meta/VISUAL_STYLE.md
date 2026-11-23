# 可视化语言

当 ASCII 可视化能够实质性地厘清层级、顺序、映射、所有权或状态时使用。保持其在纯 Markdown 下的可读性。

## 推荐形式

### 层级结构

```text
NVM Subsystem
`-- Domain
    `-- Endurance Group
        |-- NVM Set
        |   `-- Namespace
        `-- Reclaim Group
            `-- Reclaim Unit
```

### 时序

```text
Host             Submission Queue       Controller       Completion Queue
 |  write SQE ---------->|                   |                    |
|---|---|---|
 |  ring doorbell ------>|------------------>|                    |
|---|---|---|
 |                       |                   |---- write CQE ---->|
 |<---------------------- interrupt / poll -----------------------|

### 状态机

```
[Disabled] -- CC.EN=1 --> [Enabling] -- CSTS.RDY=1 --> [Ready]
     ^                                                   |
     `---------------------- CC.EN=0 --------------------'


### 位域（Bit field）

```text
 31                16 15                 0
+--------------------+--------------------+
||     upper field    |     lower field    ||
+--------------------+--------------------+

```
## 规则

- 标明图是解释性的还是根据某一编号 Figure 重绘的。
- 在每张图正下方标注来源页码。
- 保留方向、多重性、可选性与所有权，不要为简化而抹去。
- 精确数值优先使用 Markdown 表格，关系描述优先使用 ASCII 图。
- 不要重绘装饰性的图，也不要为一句即可定义的概念单独画图。
