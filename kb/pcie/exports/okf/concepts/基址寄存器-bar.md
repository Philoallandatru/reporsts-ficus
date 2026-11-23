---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: adcfe376e6611d86dd9bf0c419cf570e8414ffa03808ce1185fd51cf7ef89889
  pageDirectory: concepts
  sources:
    - pcie-config-space.md
  confidence: 0.95
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - 基址寄存器-bar
  citations:
    - file: pcie-config-space.md
      start: 201
      end: 203
    - file: pcie-config-space.md
      start: 50
      end: 61
    - file: pcie-config-space.md
      start: 207
      end: 226
    - file: pcie-config-space.md
      start: 228
      end: 242
    - file: pcie-config-space.md
      start: 249
      end: 256
    - file: pcie-config-space.md
      start: 583
      end: 589
    - file: pcie-config-space.md
      start: 269
      end: 272
    - file: pcie-config-space.md
      start: 258
      end: 267
    - file: pcie-config-space.md
      start: 164
      end: 173
    - file: pcie-config-space.md
      start: 168
      end: 173
    - file: pcie-config-space.md
      start: 468
      end: 491
    - file: pcie-config-space.md
      start: 597
      end: 602
title: 基址寄存器 (BAR)
description: 用于声明设备需要映射的内存或IO地址空间的寄存器，通过写入全1再回读的方式探测所需地址空间大小，支持32位和64位地址
tags:
  - pcie
  - memory-mapping
  - addressing
timestamp: "2026-08-16T06:35:18.163Z"
---


# 基址寄存器 (BAR)

**基址寄存器（Base Address Register，BAR）** 是 PCIe/PCI 配置空间中的关键寄存器，用于定义设备所需的内存地址空间或 I/O 地址空间。系统在枚举设备时通过 BAR 了解设备需要多大的地址空间，并为其分配可用的物理地址。^[pcie-config-space.md:201-203]

## BAR 在配置空间中的位置

在 Type 0 配置空间 Header 中，共包含 6 个 BAR 寄存器，排列在偏移 0x10 至 0x27 之间。每个 BAR 占 32 位（4 字节），可独立或配对使用。^[pcie-config-space.md:50-61]

```
偏移      BAR 寄存器
0x10      BAR 0
0x14      BAR 1
0x18      BAR 2
0x1C      BAR 3
0x20      BAR 4
0x24      BAR 5
```

## BAR 格式

BAR 的最低位（Bit 0）用于区分地址空间类型，不同类型有不同的编码规则。^[pcie-config-space.md:207-226]

### 内存 BAR（Bit 0 = 0）

```
┌────────────────────────────────────────────────────────┬──┬──┬─┐
│         Base Address [31:4] or [63:4]                  │Pf│Ty│0│
└────────────────────────────────────────────────────────┴──┴──┴─┘
 Bit 0:    0 = Memory Space
 Bit 2-1:  Type (00=32位, 10=64位, 01=保留)
 Bit 3:    Prefetchable (1=可预取)
 Bit 31-4: Base Address (16字节对齐)
```

### I/O BAR（Bit 0 = 1）

```
┌────────────────────────────────────────────────────────────┬─┐
│         Base Address [31:2]                                │1│
└────────────────────────────────────────────────────────────┴─┘
 Bit 0:    1 = I/O Space
 Bit 1:    保留
 Bit 31-2: Base Address (4字节对齐)
```

## BAR 大小探测

系统通过**写入全 1 然后回读**的方式来探测 BAR 所需的地址空间大小。^[pcie-config-space.md:228-242]

探测步骤如下：

```c
// 读取原始值
uint32_t original = pci_read_config_dword(dev, PCI_BASE_ADDRESS_0);

// 写入全 1
pci_write_config_dword(dev, PCI_BASE_ADDRESS_0, 0xFFFFFFFF);
uint32_t size_mask = pci_read_config_dword(dev, PCI_BASE_ADDRESS_0);

// 恢复原始值
pci_write_config_dword(dev, PCI_BASE_ADDRESS_0, original);

// 计算大小（假设内存 BAR）
size_mask &= ~0xF;  // 清除低 4 位
uint32_t size = ~size_mask + 1;  // 取反加一
```

**计算示例**：

| 回读值 | 计算得到的大小 |
|--------|---------------|
| `0xFFFF0000` | 64 KB |
| `0xFFFFC000` | 16 KB |
| `0xFFFFFF00` | 256 bytes |

## 64 位 BAR

当内存 BAR 的 Type 字段（Bit 2-1）为 `10b` 时，表示该 BAR 为 64 位模式，需要占用两个连续的 BAR 寄存器。^[pcie-config-space.md:249-256]

```
BAR n   (0x10 + n*4): 低 32 位 (Type = 10b)
BAR n+1 (0x14 + n*4): 高 32 位
```

64 位 BAR 的优势在于可以映射到 4GB 以上的物理地址空间，适合现代大内存系统。^[pcie-config-space.md:583-589]

## 常见应用场景

在实际设备中，各 BAR 通常有明确的分工：^[pcie-config-space.md:269-272]

- **BAR0**：设备寄存器区域（如 NVMe Controller Registers）
- **BAR1**：MSI-X 中断表和 PBA（Pending Bit Array）
- **BAR2-5**：额外的内存区域或设备特定功能

以 NVMe 控制器为例，注册 64 位 BAR 的代码如下：^[pcie-config-space.md:258-267]

```c
// 初始化内存区域
memory_region_init_io(&n->iomem, OBJECT(n), &nvme_mmio_ops, n,
                      "nvme", n->reg_size);

// 注册为 BAR0（64 位，可预取）
pci_register_bar(pci_dev, 0,
                 PCI_BASE_ADDRESS_SPACE_MEMORY |
                 PCI_BASE_ADDRESS_MEM_TYPE_64 |
                 PCI_BASE_ADDRESS_MEM_PREFETCH,
                 &n->iomem);
```

## 访问方法

读取 BAR 分配的地址后，操作系统需要将其映射到虚拟地址空间才能访问：^[pcie-config-space.md:164-173]

1. 确保 Command Register 的 **Bit 1 (Memory Space Enable)** 已设置
2. 读取 BAR 值获取物理地址
3. 调用映射函数将物理地址映射到内核虚拟地址空间

Linux 驱动中可以通过 `pci_enable_device_mem()` 函数一并完成地址空间启用和映射。^[pcie-config-space.md:168-173]

## 调试与查看

可以使用 `lspci` 命令查看设备 BAR 分配情况：^[pcie-config-space.md:468-491]

```bash
# 查看设备信息（包含 BAR 地址）
lspci -vvv -s 01:00.0

# 使用 setpci 读取 BAR0
setpci -s 01:00.0 10.L
```

典型输出示例：
```
Memory at f7e00000 (64-bit, non-prefetchable) [size=16K]
```

## 总结

基址寄存器是 PCIe 设备地址映射的核心机制，其设计要点包括：^[pcie-config-space.md:597-602]

- 通过 Bit 0 区分内存空间和 I/O 空间
- 支持 32 位和 64 位两种地址宽度
- 系统通过写入全 1 的方式探测 BAR 大小
- 64 位 BAR 占用两个连续的 BAR 寄存器
- 各 BAR 可独立配置用于不同功能区域

---

## Sources

- [配置空间布局详解](pcie-config-space.md) — 第 50-61、201-273、583-589 行

# Citations

1. [pcie-config-space.md:201-203](/references/pcie-config-space-e97358dd.md)
2. [pcie-config-space.md:50-61](/references/pcie-config-space-e97358dd.md)
3. [pcie-config-space.md:207-226](/references/pcie-config-space-e97358dd.md)
4. [pcie-config-space.md:228-242](/references/pcie-config-space-e97358dd.md)
5. [pcie-config-space.md:249-256](/references/pcie-config-space-e97358dd.md)
6. [pcie-config-space.md:583-589](/references/pcie-config-space-e97358dd.md)
7. [pcie-config-space.md:269-272](/references/pcie-config-space-e97358dd.md)
8. [pcie-config-space.md:258-267](/references/pcie-config-space-e97358dd.md)
9. [pcie-config-space.md:164-173](/references/pcie-config-space-e97358dd.md)
10. [pcie-config-space.md:168-173](/references/pcie-config-space-e97358dd.md)
11. [pcie-config-space.md:468-491](/references/pcie-config-space-e97358dd.md)
12. [pcie-config-space.md:597-602](/references/pcie-config-space-e97358dd.md)
