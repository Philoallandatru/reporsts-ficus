---
title: Class Code 寄存器
summary: 24位寄存器用于标识设备类型和功能，格式为Base Class(8位)+Sub-Class(8位)+Programming Interface(8位)，如NVMe控制器为0x010802
sources:
- pcie-config-space.md
kind: concept
createdAt: '2026-08-16T06:36:11.075Z'
updatedAt: '2026-08-16T06:36:11.075Z'
tags:
- pcie
- device-identification
- classification
aliases:
- class-code-寄存器
- CC寄
confidence: 0.9
provenanceState: extracted
modelId: MiniMax-M2.7
promptVersion: v1
type: Concept
description: Class Code（类别代码）是 PCI/PCIe 配置空间中用于标识设备类型的标准分类字段，位于 Type 0 Header 的偏移
  `0x09` 处，共 24 位。^[pcie-config-space.md:114-116]
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Class Code 寄存器

Class Code（类别代码）是 PCI/PCIe 配置空间中用于标识设备类型的标准分类字段，位于 Type 0 Header 的偏移 `0x09` 处，共 24 位。^[pcie-config-space.md:114-116]

## 功能概述

Class Code 提供了设备的标准化分类信息，使操作系统和驱动程序能够识别设备类型并加载相应的驱动。该字段是只读的，由设备制造商在硬件设计时设定。^[pcie-config-space.md:116]

## 寄存器格式

Class Code 采用三层结构，总共 24 位：^[pcie-config-space.md:117-124]

```
┌──────────────┬──────────────┬──────────────┐
│ Base Class   │ Sub-Class    │ Prog IF      │
│   (8 bits)   │   (8 bits)   │  (8 bits)    │
└──────────────┴──────────────┴──────────────┘
```

| 字段 | 宽度 | 说明 |
|------|------|------|
| **Base Class** | 8 位 | 设备大类，如存储、网络、显示等 |
| **Sub-Class** | 8 位 | 大类下的具体子类 |
| **Prog IF** | 8 位 | 编程接口，指示特定功能或协议变体 |

## 常见设备类别

以下是 PCI-SIG 定义的常见 Class Code 映射：^[pcie-config-space.md:126-134]

| Base Class | Sub-Class | Prog IF | 设备类型 |
|------------|-----------|---------|---------|
| 0x01 | 0x08 | 0x02 | NVMe 控制器 |
| 0x02 | 0x00 | 0x00 | 以太网控制器 |
| 0x03 | 0x00 | 0x00 | VGA 兼容控制器 |
| 0x06 | 0x04 | 0x00 | PCI-to-PCI Bridge |

### 主要 Base Class 分类

- **0x01** — 存储控制器（Mass Storage Controller）
- **0x02** — 网络控制器（Network Controller）
- **0x03** — 显示控制器（Display Controller）
- **0x04** — 多媒体控制器（Multimedia Controller）
- **0x06** — 桥接设备（Bridge Device）
- **0x0C** — 串行总线控制器（Serial Bus Controller）

## 代码示例

### FEMU 设置 NVMe 设备类别

```c
// 设置 NVMe 设备类别
pci_config_set_class(pci_conf, PCI_CLASS_STORAGE_EXPRESS);
// 展开为：0x010802
// Base=0x01 (存储), Sub=0x08 (NVMe), Prog IF=0x02
```

该示例展示了如何使用 QEMU/FEMU 提供的便捷函数设置 Class Code，其中 `PCI_CLASS_STORAGE_EXPRESS` 是预定义的宏，等同于十六进制值 `0x010802`。^[pcie-config-space.md:135-140]

## 相关概念

Class Code 通常与以下配置空间字段配合使用：

- 配置空间布局 — Class Code 所在的完整配置空间结构
- Vendor ID — 设备制造商标识，与 Class Code 共同完成设备识别
- Device ID — 设备型号标识
- BAR — 地址映射寄存器，与设备功能配合使用
- 能力结构 — 设备能力声明，扩展设备功能信息

## 总结

Class Code 是 PCI/PCIe 设备身份识别的核心字段之一，采用三层分类结构（Base Class、Sub-Class、Prog IF）提供精确的设备类型信息。操作系统通过读取该字段来匹配相应的驱动程序，实现设备的即插即用功能。

---

## Sources

- [配置空间布局详解](../../sources/pcie-config-space.md)

---

*最后更新：2026-07-06*

