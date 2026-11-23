---
type: Concept
title: Feature 的取值与作用域（Feature Values and Scope）
description: Feature 是控制器的可配置运行参数。主机用 Feature Identifier 配合 Get Features/Set Features
  查询或修改；一个 Feature 有自己的作用域，并可能同时拥有默认值、当前值和保存值。 [PDF pp. 181-183](../_source/pages/page-181.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Feature 的取值与作用域（Feature Values and Scope）

Feature 是控制器的可配置运行参数。主机用 Feature Identifier 配合 Get Features/Set Features 查询或修改；一个 Feature 有自己的作用域，并可能同时拥有默认值、当前值和保存值。 [PDF pp. 181-183](../_source/pages/page-181.md)

## 三种值，像“出厂设置、正在使用、下次启动恢复”

```text
厂商默认值（不能直接改）
          |  reset 后的后备值
          v
当前值 <----- Set Features ----- 保存值
 |                                  ^
 `-- 控制器此刻实际采用            `-- SV=1 且可保存时更新
```

图是值关系的解释性模型。设备不支持保存值时只剩默认值和当前值；某些不可保存 Feature 仍可能由其定义决定跨 reset 或掉电保留当前值。 [PDF p. 181](../_source/pages/page-181.md)

## 一个配置案例

管理员调整某个可保存的队列或电源策略时，可以只改当前值做临时测试；确认后再以 `SV=1` 同时更新保存值。若该 Feature 不可保存，带 `SV=1` 的请求会得到 Feature Identifier Not Saveable。 [PDF pp. 392-395](../_source/pages/page-392.md)

## Get Features 的 `SEL` 是在问哪一种值

| `SEL` | 返回内容 |
|---|---|
| `000b` | 当前值 |
| `001b` | 默认值 |
| `010b` | 保存值；不支持保存或没有保存值时返回默认值 |
| `011b` | 支持能力 |

查询支持能力时，CQE Dword 0 会说明值能否改变、是否命名空间范围、是否可保存。可改变不表示每一个目标值都合法，具体 Feature 仍可能有值相关限制。 [PDF pp. 220-223](../_source/pages/page-220.md)

## Feature 属于谁，决定 NSID 怎么填

| 作用域 | 常规 NSID 规则 |
|---|---|
| 控制器 | `0h` 或 `FFFFFFFFh`；带有效 NSID 的 Set 会失败 |
| 命名空间 | active NSID 选择一个；仅控制器允许时 `FFFFFFFFh` 才可设置全部已挂接命名空间 |
| 子系统、Domain、Endurance Group、NVM Set | NSID 应为 `0h`；非零值无效 |

命名空间范围的 Get Features 中，`FFFFFFFFh` 不是“汇总读取”，通常会以 Invalid Namespace or Format 失败。 [PDF pp. 182-183](../_source/pages/page-182.md)

## reset 后会怎样

```text
reset 覆盖整个子系统：每个受影响作用域恢复保存值；没有保存值则回到默认值
reset 只覆盖子系统的一部分：控制器/每控制器命名空间范围恢复；更宽作用域通常保持不变，除非 Feature 另有规定
```

该图是 Figures 124-125 的教学性概括。多主机同时修改跨控制器作用域的 Feature 时，主机之间必须自行协调；Base Specification 不定义协调协议。 [PDF pp. 181-182](../_source/pages/page-181.md)

## 修改后的边界

Set Features 完成后，新提交的命令使用新设置；已经执行的命令可能使用旧值或新值。若应用需要干净边界，应先排空相关工作，再修改并重新发现或初始化受影响能力。 [PDF p. 395](../_source/pages/page-395.md)

Host Behavior Support（`16h`）是反向能力声明：由 host 告诉 controller 哪些 host 行为可以依赖。它不可保存且采用替换而非合并语义。 [PDF pp. 407-409](../_source/pages/page-407.md)

## 规范依据

- [默认/当前/保存值与 reset 规则，PDF 第 181-183 页](../_source/pages/page-181.md)
- [Get Features 选择子与支持能力，PDF 第 220-223 页](../_source/pages/page-220.md)
- [Set Features、保存位和更新顺序，PDF 第 392-395 页](../_source/pages/page-392.md)
- [Host Behavior Support，PDF 第 407-409 页](../_source/pages/page-407.md)
