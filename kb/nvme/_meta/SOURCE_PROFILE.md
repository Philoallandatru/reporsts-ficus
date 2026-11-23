# 源资料概貌（Source profile）

- Title：NVM Express Base Specification
- Revision：2.1，于 2024 年 8 月 5 日被批准（ratified）
- Length：707 页 PDF；规范正文页 1 对应 PDF 第 23 页
- Structure：未加密的纯文本，892 个书签
- Visual inventory：762 个唯一编号的 Figure
- Normative density：超过 2,100 处 `shall`

## 为什么抽取必须以概念为主导

本规范同时是一份架构描述、寄存器契约、命令协议、数据结构目录以及状态机的集合。大量编号 Figure 实际上是位域表（bit-field tables）或命令/数据布局。

因此 wiki 区分以下几类：

1. 架构概念与所有权边界；
2. transport、queue、command 生命周期；
3. 命令、特性（Features）、log pages 与状态值；
4. 寄存器、属性、结构与位域；
5. 状态机、错误恢复、电源、sanitize 与安全行为。

定义不会被盲目提升为独立页面。低层字段仍然嵌套在为它们赋予意义的概念或协议操作之下。
