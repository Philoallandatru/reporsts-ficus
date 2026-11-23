---
type: Concept
title: 验证证据与故障注入闭环
description: 验证资产如果只停留在矩阵和样例日志，最后会变成“知道要测什么，但不知道怎么判定”。这一页把故障注入、hook、证据 schema 和 pass/fail
  判定连成一条闭环。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 验证证据与故障注入闭环

验证资产如果只停留在矩阵和样例日志，最后会变成“知道要测什么，但不知道怎么判定”。这一页把故障注入、hook、证据 schema 和 pass/fail 判定连成一条闭环。

## 这页要解决什么

- 让每个故障注入场景都有对应的证据类型。
- 让 emulator hook、host command 和 fault injection 的日志字段能互相对上。
- 让 pass/fail 判定不依赖口头解释，而依赖可重复的证据。

## 闭环结构

一个完整的验证闭环应该包含：

1. **场景定义**：要注入什么故障，或者要跑什么 host 命令。
2. **hook / command**：故障或命令在什么时刻触发。
3. **证据记录**：run header、hook event、fault injection event、host command event。
4. **解析与判定**：把原始日志和 schema 对齐，输出 pass/fail/inconclusive。
5. **可追溯性**：test id、requirement id、hook id、command map id、spec artifact id 都能串起来。

## 证据类型怎么用

| 证据类型 | 作用 | 什么时候必须有 |
|---|---|---|
| run_header | 证明一次运行可复现 | 每次测试都要有 |
| hook_event | 证明 hook 真正触发 | 依赖 emulator hook 的测试 |
| fault_injection_event | 证明注入点和注入时刻 | fault-driven 测试 |
| host_command_event | 证明 host 侧命令和输出 | nvme-cli / SPDK / libnvme 测试 |
| pass_fail_decision | 给出最终判定 | 每次测试都要有 |

## 故障注入怎么落证据

故障注入不是“脚本里写了就算”。要满足下面几个条件：

- fault id 必须对应 `fault-injection.yml`。
- 如果有 hook matrix，hook id 必须对应 `emulator-hook-matrix.yml`。
- 注入发生时间要能在日志里看到。
- 恢复开始和恢复完成要能区分。
- 最终数据结果和状态码要能回到具体 test id 和 requirement id。

## Host 命令怎么落证据

host command event 是把 `nvme-cli`、`libnvme` 或 SPDK 命令接进来的一层。它至少应该能回答：

- 发了什么命令。
- 命令模板是什么。
- 实际 argv 是什么。
- 预期观察是什么。
- 观察到的字段是什么。
- 原始 stdout / stderr 在哪里。
- 这个命令对应哪条规范 artifact 和 topic。

## 判定原则

| 原则 | 含义 |
|---|---|
| 证据先于结论 | 没有原始日志，不给 pass |
| ID 对齐 | test id、requirement id、hook id、command map id 必须一致 |
| 结果可复现 | 同一个场景重复跑，判定不能摇摆 |
| 恢复可解释 | 掉电、reset、retry、rollback 都要能解释最终状态 |
| 不确定就不判 pass | 证据不够时只能 inconclusive 或 blocked |

## 常见断点

- 有 hook 但没记录触发时间。
- 有 host 命令但没有 raw stdout/stderr。
- 有 fault id 但没有对应的 test id。
- 只有最终状态，没有恢复过程。
- 有日志，但字段没有绑定到 schema。
- pass/fail 由人工口述，不是由证据驱动。

## 和现有资产的关系

这页是下面这些资产之间的桥：

- [SSD 验证矩阵](ssd-verification-matrix.md)
- [Verification Evidence Schema](../../tests/requirements/verification-evidence-schema.yml)
- [Emulator Hook Matrix](../../tests/requirements/emulator-hook-matrix.yml)
- [机器可读故障注入清单](../../tests/faults/fault-injection.yml)
- [掉电恢复状态表](../../tests/faults/power-loss-state-table.yml)
- [Firmware Update 状态表](../../tests/faults/firmware-update-state-table.yml)

## 推荐使用方式

1. 先在验证矩阵里找场景。
2. 再到 hook matrix 或 fault matrix 里找注入点。
3. 再按 evidence schema 记录 run header、事件和原始日志。
4. 最后输出 pass/fail decision。

## 关键来源

- [SSD 验证矩阵](ssd-verification-matrix.md)
- [Verification Evidence Schema](../../tests/requirements/verification-evidence-schema.yml)
- [Emulator Hook Matrix](../../tests/requirements/emulator-hook-matrix.yml)
- [机器可读故障注入清单](../../tests/faults/fault-injection.yml)
- [掉电恢复状态表](../../tests/faults/power-loss-state-table.yml)
- [Firmware Update 状态表](../../tests/faults/firmware-update-state-table.yml)
