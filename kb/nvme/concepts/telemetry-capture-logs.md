---
type: Concept
title: Telemetry 捕获日志（Telemetry Capture Logs）
description: Telemetry 日志把控制器或 NVM 子系统内部、实现定义的状态装进标准化外壳：512 字节头部加以 512 字节为单位的数据块。Host-Initiated
  由主机按需抓取，Controller-Initiated 则暴露控制器已保存的一份主动抓取结果。 [PDF pp. 241-246](../_source/pages/page-241.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Telemetry 捕获日志（Telemetry Capture Logs）

Telemetry 日志把控制器或 NVM 子系统内部、实现定义的状态装进标准化外壳：512 字节头部加以 512 字节为单位的数据块。Host-Initiated 由主机按需抓取，Controller-Initiated 则暴露控制器已保存的一份主动抓取结果。 [PDF pp. 241-246](../_source/pages/page-241.md)

## 先把它当作“故障现场快照”

```text
byte 0                                               byte 511
+--------------------- 标准化头部 ----------------------+
block 1       block 2                    block n
+-------------+-------------+ ... +----------------------+
| Data Area 都从 block 1 开始；每区报告累计的末 block 边界 |
+--------------------------------------------------------+
```

各 Area 不是互不相交的连续分区，而是逐渐增大的前缀，所以从 Area 1 到最高支持 Area 的末 block 值不会下降。传输长度和日志偏移都必须是 512 字节的倍数。 [PDF pp. 241-245](../_source/pages/page-241.md)

## 一个排障快照案例

主机发现异常后，对 `LID=07h` 的 Get Log Page 设置 `CTHID=1`。控制器先抓取当前内部状态并递增 generation，主机随后读取头部和需要的数据块。读取完后再检查 generation；若前后不一致，就丢弃这次结果并重试，避免把两个快照拼在一起。 [PDF pp. 241-244](../_source/pages/page-241.md)

## Host-Initiated：主机要求现在就拍一张

```text
Get Log Page, LID=07h
  CTHID=1 --> 捕获 + generation++
  MCDA ----> 可选：限制最多生成到哪个 Area
                |
                v
头部：厂商 OUI | Area 末端 | scope | generation | 原因
```

捕获结果一直稳定到下一次请求捕获、Firmware Commit 或上电 reset。控制器报告 `MCDAS` 时，主机可用 `MCDA` 限制只生成 Area 1、Area 1-2、Area 1-3 或 Area 1-4；否则该请求字段被忽略。 [PDF pp. 241-244](../_source/pages/page-241.md)

Revision 2.1 中 scope 为 Controller 或 NVM 子系统，8 位 generation 从 `FFh` 回绕到 `00h`。头部还镜像 controller-initiated 的可用性与 generation，方便一次读取关联两条捕获流。 [PDF p. 243](../_source/pages/page-243.md)

## Controller-Initiated：控制器自己留下的现场

| 差异 | Host-Initiated | Controller-Initiated |
|---|---|---|
| 触发者 | 主机设置 `CTHID` | 厂商定义的控制器条件 |
| 保留时间 | 到重新捕获、Firmware Commit 或上电 reset | Area 1-3 跨所有 reset；Area 4 可跨 Controller Level Reset |
| 确认事件 | 没有可用性清除规则 | 成功的带内读取且 `RAE=0` 清除可用标志 |
| LID | `07h` | `08h` |

Controller-Initiated 的可用标志和 generation 跨电源状态/reset 保留。可用标志为一时，只有成功的带内 Get Log Page 且 `RAE=0` 才清除；带外 Management Endpoint 的可见性可能不受该标志影响。 [PDF pp. 244-246](../_source/pages/page-244.md)

## Area 4 为什么需要主机声明

`DA4S` 表示控制器支持 Area 4，Host Behavior Support 的 `ETDAS` 表示主机能处理扩展的 Area 4 边界。两者都为真时，可变日志大小按 Area 4 计算；否则即使设备支持，主机可见大小也止于 Area 3。适用末边界之后的数据未定义。 [PDF pp. 242, 244-245](../_source/pages/page-242.md)

## 规范依据

- [Host-Initiated 触发、稳定性和 Area 4 协商，PDF 第 241-244 页](../_source/pages/page-241.md)
- [Controller-Initiated 保留、可用性与 generation，PDF 第 244-246 页](../_source/pages/page-244.md)
