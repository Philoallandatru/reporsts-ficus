---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: be26a6eb282dbd70595423149eece6bc72161d8e027eaf2262d3adb7d52b9a79
  pageDirectory: concepts
  sources:
    - pcie-aspm.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - aspm-l1-状态-low-power
    - AL状(P
  citations:
    - file: pcie-aspm.md
      start: 133
      end: 139
    - file: pcie-aspm.md
      start: 135
      end: 139
    - file: pcie-aspm.md
      start: 138
      end: 138
    - file: pcie-aspm.md
      start: 139
      end: 139
    - file: pcie-aspm.md
      start: 251
      end: 251
    - file: pcie-aspm.md
      start: 141
      end: 144
    - file: pcie-aspm.md
      start: 148
      end: 157
    - file: pcie-aspm.md
      start: 160
      end: 168
    - file: pcie-aspm.md
      start: 247
      end: 254
    - file: pcie-aspm.md
      start: 258
      end: 264
    - file: pcie-aspm.md
      start: 185
      end: 206
    - file: pcie-aspm.md
      start: 329
      end: 343
    - file: pcie-aspm.md
      start: 488
      end: 556
    - file: pcie-aspm.md
      start: 631
      end: 635
title: ASPM L1 状态 (Low Power)
description: 深度低功耗状态，双向握手进入，关闭链路时钟，退出延迟 2-4μs，功耗节省 60-90%
tags:
  - pcie
  - power-management
  - low-power
timestamp: "2026-08-16T06:33:29.160Z"
---


# ASPM L1 状态 (Low Power)

## 概述

ASPM L1 状态（Low Power State）是 PCIe 链路电源管理中的低功耗状态之一，相比 L0s 待机状态 提供更深度的节能效果。当链路处于空闲状态且时间超过阈值时，硬件会自动触发从 L0 活动状态切换到 L1 低功耗状态，以降低电源消耗。^[pcie-aspm.md:133-139]

## L1 状态特点

L1 状态具有以下核心特征：

- **深度低功耗**：发送器（TX）和接收器（RX）电路均进入低功耗模式 ^[pcie-aspm.md:135-139]
- **时钟管理**：链路时钟被关闭，部分实现可选关闭 PLL（锁相环） ^[pcie-aspm.md:138]
- **退出延迟**：2-4 微秒，取决于具体硬件配置 ^[pcie-aspm.md:139]
- **功耗节省**：相比 L0 活动状态可节省 60-90% 的电能 ^[pcie-aspm.md:251]

## 进入条件

L1 状态并非无条件进入，需要满足以下条件 ^[pcie-aspm.md:141-144]：

1. **双方支持**：链路两端设备都必须支持 L1 状态
2. **空闲超时**：链路空闲时间超过预设阈值
3. **双向握手**：完成 PM_Enter_L1 DLLP 握手协议

## 状态转换机制

### L0 → L1 转换

当链路需要进入 L1 状态时，会执行以下握手流程 ^[pcie-aspm.md:148-157]：

```
1. Downstream Port 发送 PM_Enter_L1 DLLP
2. Upstream Port 确认
3. 双方发送 EIOS（Electrical Idle Ordered Set）
4. 进入 Electrical Idle（静电状态）
5. 关闭 PLL（可选）
6. 关闭链路时钟
```

### L1 → L0 转换

从 L1 状态唤醒恢复到 L0 活动状态需要以下步骤 ^[pcie-aspm.md:160-168]：

```
1. 检测到唤醒事件（WAKE# 信号或 Beacon 低频信号）
2. 启动 PLL
3. 等待时钟稳定
4. 执行链路训练（TS1/TS2 训练序列）
5. 恢复到 L0 活动状态
```

时序图如下：

```
L0               L1                  L0
 │  空闲超时      │    唤醒事件        │
 │  PM_Enter_L1   │                   │
 ├───────────────>│                   │
 │  确认          │                   │
 │  EIOS          │   Beacon/WAKE#    │
 │  关闭时钟      │                   │
 │                ├──────────────────>│
 │                │   启动 PLL        │
 │                │   链路训练        │
                   │                   │
            延迟: 2-4 μs
```

## 延迟与功耗对比

L1 状态在功耗节省和恢复延迟之间取得平衡，下表展示了各状态的对比 ^[pcie-aspm.md:247-254]：

| 状态 | 功耗节省 | 退出延迟 | 应用场景 |
|------|---------|---------|---------|
| L0 | 0%（基准） | 0 | 活动传输 |
| L0s | 10-20% | 200-500 ns | 短暂空闲 |
| **L1** | **60-90%** | **2-4 μs** | **较长空闲** |
| L1.1 | 90-95% | 8-16 μs | 长时间空闲 |
| L1.2 | 95-99% | 16-100 μs | 极长空闲 |

### 功耗示例

以典型 PCIe Gen 3 x4 链路为例 ^[pcie-aspm.md:258-264]：

```
L0 (Active):        ~1.5 W
L1:                 ~0.3 W (节省约 80%)
```

## L1 子状态

L1 状态还有两个子状态 L1.1 和 L1.2，在 PCIe 3.1 规范中引入，提供更深的节能效果 ^[pcie-aspm.md:185-206]：

| 子状态 | 特点 | 退出延迟 |
|--------|------|---------|
| L1.1 | 关闭 PLL，保持参考时钟 | 8-16 μs |
| L1.2 | 关闭 PLL 和参考时钟 | > 16 μs |

L1.2 状态需要平台支持 CLKREQ# 信号来动态控制参考时钟的开启和关闭。

## 配置与控制

### Link Control 寄存器

通过配置空间的 PCIe Capability 结构可以控制 ASPM L1 状态 ^[pcie-aspm.md:329-343]：

```
Bit 1-0: ASPM Control
  00b = 禁用 ASPM
  01b = 仅启用 L0s
  10b = 仅启用 L1
  11b = 启用 L0s 和 L1
```

### 操作系统配置

在 Linux 系统中，可以通过以下方式查看和配置 L1 状态 ^[pcie-aspm.md:488-556]：

```bash
# 使用 lspci 查看
lspci -vvv -s 01:00.0 | grep -i aspm
  LnkCap: Port #0, Speed 8GT/s, Width x4, ASPM L0s L1, Exit Latency L1 <4us
  LnkCtl: ASPM L1 Enabled

# 使用 setpci 启用 L1
setpci -s 01:00.0 CAP_EXP+10.w=0002

# 通过 sysfs 设置省电策略
echo powersave > /sys/module/pcie_aspm/parameters/policy
```

## 使用建议

根据不同应用场景，建议如下 ^[pcie-aspm.md:631-635]：

- **台式机/服务器**：性能优先，可禁用 L1 或仅启用 L0s
- **笔记本**：平衡模式，建议启用 L0s + L1
- **低频访问设备**（如系统盘）：可启用 L1 以获得显著节能效果

## 相关概念

- ASPM L0s 状态 - 快速待机状态
- ASPM L1.1 状态 - L1 子状态 1
- ASPM L1.2 状态 - L1 子状态 2（超低功耗）
- ASPM 概述 - ASPM 电源管理机制完整介绍

---

## Sources

- ASPM (Active State Power Management) 电源管理](pcie-aspm.md) — 概述、L1 状态详解、配置与控制、实用技巧

# Citations

1. [pcie-aspm.md:133-139](/references/pcie-aspm-a410e8dc.md)
2. [pcie-aspm.md:135-139](/references/pcie-aspm-a410e8dc.md)
3. [pcie-aspm.md:138-138](/references/pcie-aspm-a410e8dc.md)
4. [pcie-aspm.md:139-139](/references/pcie-aspm-a410e8dc.md)
5. [pcie-aspm.md:251-251](/references/pcie-aspm-a410e8dc.md)
6. [pcie-aspm.md:141-144](/references/pcie-aspm-a410e8dc.md)
7. [pcie-aspm.md:148-157](/references/pcie-aspm-a410e8dc.md)
8. [pcie-aspm.md:160-168](/references/pcie-aspm-a410e8dc.md)
9. [pcie-aspm.md:247-254](/references/pcie-aspm-a410e8dc.md)
10. [pcie-aspm.md:258-264](/references/pcie-aspm-a410e8dc.md)
11. [pcie-aspm.md:185-206](/references/pcie-aspm-a410e8dc.md)
12. [pcie-aspm.md:329-343](/references/pcie-aspm-a410e8dc.md)
13. [pcie-aspm.md:488-556](/references/pcie-aspm-a410e8dc.md)
14. [pcie-aspm.md:631-635](/references/pcie-aspm-a410e8dc.md)
