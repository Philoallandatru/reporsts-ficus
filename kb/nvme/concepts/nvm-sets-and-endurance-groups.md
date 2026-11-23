---
type: Concept
title: NVM Set 与 Endurance Group
description: NVM Set 是创建命名空间所用的一组逻辑、也可能物理分离的 NVM 资源。Endurance Group 则是统一管理耐久性的边界；它可只包含一个
  NVM Set，也可协调多个 NVM Set。 [PDF pp. 99-102](../_source/pages/page-099.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# NVM Set 与 Endurance Group

NVM Set 是创建命名空间所用的一组逻辑、也可能物理分离的 NVM 资源。Endurance Group 则是统一管理耐久性的边界；它可只包含一个 NVM Set，也可协调多个 NVM Set。 [PDF pp. 99-102](../_source/pages/page-099.md)

## 用“仓库分区与维护预算”理解

```text
Domain
`-- Endurance Group Y（共享耐久性预算）
    |-- NVM Set A
    |   |-- Namespace A1、A2
    |   `-- 未分配空间
    `-- NVM Set B
        |-- Namespace B1
        `-- 未分配空间
```

格式化命名空间完整地落在一个 NVM Set 内，并继承其最佳写入大小等属性。每个 NVM Set 只属于一个 Endurance Group，每个 Endurance Group 只属于一个 Domain。 [PDF pp. 99-102](../_source/pages/page-099.md)

## 一个隔离工作负载案例

管理员把高频日志写入的命名空间放到 NVM Set A，把较冷的归档数据放到 NVM Set B。若二者仍在同一个 Endurance Group，它们的耐久性管理仍有关联；若需要独立耐久性边界，就要由不同 Endurance Group 承载。 [PDF pp. 99-102](../_source/pages/page-099.md)

## ID 与容量该怎样理解

| 项目 | 规则 |
|---|---|
| NVM Set ID | 16 位、在 NVM 子系统内唯一，零保留/无效 |
| Endurance Group ID | 16 位、在 NVM 子系统内唯一，零保留/无效 |
| NVM Set 总容量 | 已格式化到命名空间的部分加未分配部分 |
| NVM Set List | 报告 ID、最佳写入大小、总/未分配容量及所属 Endurance Group |

命令未另行规定时，在需要这些 ID 的位置填写零会得到 Invalid Field in Command。 [PDF pp. 100-101](../_source/pages/page-100.md)

## 这些概念会出现在哪些操作中

Identify、Capacity Management、Namespace Management、部分 Feature、Connect、Create I/O Submission Queue 和部分日志页都会传递或报告 NVM Set ID。若不支持 NVM Set，相关字段清零；Endurance Group 仍可单独定义耐久性边界。 [PDF pp. 100-102](../_source/pages/page-100.md)

Endurance Group Event Configuration（`18h`）选择哪些非保留 Critical Warning 位写入该组的聚合事件日志。`ENDGID=0` 会禁用本次操作的告警掩码；不存在的组或保留告警位无效。 [PDF p. 410](../_source/pages/page-410.md)

## 规范依据

- [NVM Set、Endurance Group 定义和关系，PDF 第 99-102 页](../_source/pages/page-099.md)
- [Endurance Group 事件配置，PDF 第 410 页](../_source/pages/page-410.md)
