---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 3972288e0c09261defe5caaeb919356d59c29c348862dba0cdb25d89dbf35e52
  pageDirectory: concepts
  sources:
    - pcie-sriov.md
  confidence: 0.9
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - sr-iov-启用流程
  citations:
    - file: pcie-sriov.md
      start: 3
      end: 9
    - file: pcie-sriov.md
      start: 582
      end: 593
    - file: pcie-sriov.md
      start: 280
      end: 305
    - file: pcie-sriov.md
      start: 265
      end: 276
    - file: pcie-sriov.md
      start: 203
      end: 218
    - file: pcie-sriov.md
      start: 161
      end: 186
    - file: pcie-sriov.md
      start: 307
      end: 330
    - file: pcie-sriov.md
      start: 190
      end: 201
    - file: pcie-sriov.md
      start: 332
      end: 352
    - file: pcie-sriov.md
      start: 220
      end: 234
    - file: pcie-sriov.md
      start: 356
      end: 376
    - file: pcie-sriov.md
      start: 378
      end: 395
    - file: pcie-sriov.md
      start: 580
      end: 606
    - file: pcie-sriov.md
      start: 555
      end: 578
title: SR-IOV 启用流程
description: 检测 SR-IOV 支持、初始化 PF、配置 Num VFs、启用 VF Enable 位的完整流程，可通过 Linux sysfs 接口操作
tags:
  - linux
  - sriov
  - 驱动开发
timestamp: "2026-08-16T06:48:14.181Z"
---


# SR-IOV 启用流程

SR-IOV (Single Root I/O Virtualization) 是 PCIe 规范的关键虚拟化特性，允许将单个物理设备虚拟为多个独立的虚拟功能（VF）直接分配给虚拟机使用。启用 SR-IOV 需要经过检测支持、驱动初始化、启用 VF 以及分配给虚拟机等步骤。

## 前置条件

在启用 SR-IOV 之前，需要确保系统满足以下条件：

- **硬件支持**：PCIe 设备必须支持 SR-IOV 扩展能力 ^[pcie-sriov.md:3-9]
- **IOMMU 启用**：需要 Intel VT-d 或 AMD-Vi 支持 DMA 隔离 ^[pcie-sriov.md:582-593]
- **BIOS 配置**：在 BIOS 中启用 VT-d/AMD-Vi 和 SR-IOV 选项 ^[pcie-sriov.md:582-593]
- **驱动支持**：操作系统驱动需要包含 SR-IOV 支持代码 ^[pcie-sriov.md:280-305]

## 检测 SR-IOV 支持

首先需要确认 PCIe 设备支持 SR-IOV 功能。使用 `lspci` 命令可以查看设备的 SR-IOV 能力信息：

```bash
lspci -vvv -s 01:00.0 | grep -i "SR-IOV"
```

典型输出包含以下关键信息 ^[pcie-sriov.md:265-276]：

```
Capabilities: [160] Single Root I/O Virtualization (SR-IOV)
    IOVCap: Migration-, Interrupt Message Number: 000
    IOVCtl: Enable+ Migration- Interrupt- MSE+ ARIHierarchy+
    IOVSta: Migration-
    Initial VFs: 256, Total VFs: 256, Number of VFs: 8, ...
    VF offset: 1, stride: 1, Device ID: 154c
```

各字段含义如下 ^[pcie-sriov.md:203-218]：

- **Initial VFs**（只读）：设备支持的最大 VF 数量，由硬件固定
- **Total VFs**（只读）：当前可用的 VF 数量，可能因系统资源限制而小于 Initial VFs
- **Number of VFs**（读写）：当前已启用的 VF 数量
- **VF offset**：第一个 VF 相对于 PF 的路由 ID 偏移
- **VF stride**：相邻 VF 之间的路由 ID 步长

## 驱动初始化 PF

驱动需要在初始化阶段完成 SR-IOV 能力的发现和配置。以下是 Linux 内核驱动的典型实现流程 ^[pcie-sriov.md:280-305]：

```c
int sriov_init(struct pci_dev *pdev)
{
    int pos, num_vfs;
    u16 total_vfs;
    
    // 1. 查找 SR-IOV Capability
    pos = pci_find_ext_capability(pdev, PCI_EXT_CAP_ID_SRIOV);
    if (!pos) {
        pr_err("SR-IOV not supported\n");
        return -ENODEV;
    }
    
    // 2. 读取 Total VFs
    pci_read_config_word(pdev, pos + PCI_SRIOV_TOTAL_VF, &total_vfs);
    pr_info("Device supports %d VFs\n", total_vfs);
    
    // 3. 配置 VF BARs (由 PCI 子系统处理)
    
    // 4. 设置系统页大小
    pci_write_config_dword(pdev, pos + PCI_SRIOV_SYS_PGSIZE, 0x00001000); // 4KB
    
    return 0;
}
```

SR-IOV Extended Capability 结构位于 PCIe 扩展配置空间 (0x100 地址以上)，包含以下关键寄存器 ^[pcie-sriov.md:161-186]：

| 偏移 | 字段 | 说明 |
|------|------|------|
| 0x00 | Capability ID | 0x0010 (SR-IOV) |
| 0x08 | SR-IOV Control | 控制寄存器，包含 VF Enable 位 |
| 0x0C | Initial VFs | 支持的 VF 总数 |
| 0x0E | Total VFs | 当前可用的 VF 总数 |
| 0x10 | Num VFs | 已启用的 VF 数量 |
| 0x14 | First VF Offset | 第一个 VF 的偏移 |
| 0x16 | VF Stride | VF 之间的步长 |
| 0x1A | VF Device ID | VF 的设备 ID |

## 启用 VF

驱动通过写入配置空间寄存器来启用 VF。启用过程包括写入 Num VFs 字段并设置 VF Enable 位 ^[pcie-sriov.md:307-330]：

```c
int enable_vfs(struct pci_dev *pdev, int num_vfs)
{
    int pos = pci_find_ext_capability(pdev, PCI_EXT_CAP_ID_SRIOV);
    u16 ctrl;
    
    // 1. 写入 Num VFs
    pci_write_config_word(pdev, pos + PCI_SRIOV_NUM_VF, num_vfs);
    
    // 2. 设置 VF Enable 位和 Memory Space Enable 位
    pci_read_config_word(pdev, pos + PCI_SRIOV_CTRL, &ctrl);
    ctrl |= PCI_SRIOV_CTRL_VFE | PCI_SRIOV_CTRL_MSE;
    pci_write_config_word(pdev, pos + PCI_SRIOV_CTRL, ctrl);
    
    // 3. 等待 VF 就绪
    msleep(100);
    
    pr_info("Enabled %d VFs\n", num_vfs);
    return 0;
}
```

SR-IOV Control Register 的关键位定义如下 ^[pcie-sriov.md:190-201]：

| 位 | 字段 | 说明 |
|----|------|------|
| 0 | VF Enable | 使能 VF (1=启用) |
| 1 | VF Migration Enable | 使能 VF 迁移 |
| 3 | VF MSE | VF 内存空间使能 |
| 4 | ARI Capable Hierarchy | ARI 层次结构 |

## Linux sysfs 接口

在 Linux 系统中，推荐通过 sysfs 接口管理 VF，这是最常用且最便捷的方法 ^[pcie-sriov.md:332-352]：

```bash
# 查看支持的 VF 数量
cat /sys/bus/pci/devices/0000:01:00.0/sriov_totalvfs
256

# 启用 8 个 VF
echo 8 > /sys/bus/pci/devices/0000:01:00.0/sriov_numvfs

# 验证 VF 已创建
lspci | grep "Virtual Function"
01:00.1 Ethernet controller: Intel Virtual Function
01:00.2 Ethernet controller: Intel Virtual Function
...

# 禁用所有 VF
echo 0 > /sys/bus/pci/devices/0000:01:00.0/sriov_numvfs
```

VF 创建后，系统会自动为其分配 BDF 地址。VF 的 BDF 地址计算公式为 ^[pcie-sriov.md:220-234]：

```
VF[i] BDF = PF BDF + First VF Offset + (i * VF Stride)
```

例如，如果 PF 地址为 `01:00.0`，First VF Offset 为 1，VF Stride 为 1，则 VF0 为 `01:00.1`，VF1 为 `01:00.2`，以此类推。

## VF 分配给虚拟机

创建完成的 VF 需要绑定到适当的驱动并分配给虚拟机使用。VFIO (Virtual Function I/O) 是现代 Linux 推荐的设备直通框架 ^[pcie-sriov.md:356-376]：

### 使用 VFIO 绑定 VF

```bash
# 1. 解绑 VF 当前驱动
echo 0000:01:00.1 > /sys/bus/pci/devices/0000:01:00.1/driver/unbind

# 2. 绑定到 vfio-pci 驱动
echo "8086 154c" > /sys/bus/pci/drivers/vfio-pci/new_id

# 3. 验证绑定
lspci -k -s 01:00.1
01:00.1 Ethernet controller: Intel Virtual Function
    Kernel driver in use: vfio-pci
```

### QEMU/KVM 配置

通过 QEMU 命令行将 VF 分配给虚拟机：

```bash
qemu-system-x86_64 \
  -device vfio-pci,host=01:00.1 \
  ...
```

### libvirt 配置

使用 libvirt 管理虚拟机时，可在 XML 配置文件中声明 VF 设备 ^[pcie-sriov.md:378-395]：

```xml
<domain type='kvm'>
  <name>vm-with-sriov</name>
  ...
  <devices>
    <hostdev mode='subsystem' type='pci' managed='yes'>
      <source>
        <address domain='0x0000' bus='0x01' slot='0x00' function='0x1'/>
      </source>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
    </hostdev>
  </devices>
</domain>
```

## 故障排查

启用 SR-IOV 时可能遇到的常见问题及排查方法 ^[pcie-sriov.md:580-606]：

| 问题 | 可能原因 | 排查命令 |
|------|----------|----------|
| VF 无法启用 | IOMMU 未启用 | `dmesg \| grep -i iommu` |
| VF 无法启用 | 内核参数缺少 iommu 配置 | `cat /proc/cmdline \| grep iommu` |
| VF 无法启用 | ACS 未正确配置 | `lspci -vvv -s 01:00.0 \| grep ACSCtl` |
| 性能问题 | 链路速度不足 | `lspci -vvv -s 01:00.1 \| grep "LnkSta:"` |
| 性能问题 | MSI-X 中断异常 | `cat /proc/interrupts \| grep vfio` |

内核启动参数应包含 `intel_iommu=on iommu=pt` 或等效的 AMD 配置以启用 IOMMU 支持。

## 性能优化建议

启用 SR-IOV 后，为获得最佳性能，建议考虑以下因素 ^[pcie-sriov.md:555-578]：

- **VF 数量规划**：高性能场景建议每个虚拟机使用 1-2 个 VF；密集整合场景可使用 4-8 个 VF，但需确保不超过物理资源限制
- **中断亲和性**：将 VF 中断绑定到与 VM vCPU 对应的宿主 CPU 上，可减少中断处理延迟
- **带宽隔离**：SR-IOV 提供 DMA 和中断隔离，但不提供物理链路带宽隔离，多 VF 共用时需注意带宽竞争

---

## Sources

- [SR-IOV 虚拟化详解](../pcie/pcie-sriov.md) — 完整的 SR-IOV 技术文档，包含架构、配置空间、启用流程和故障排查

---

## 相关概念

- [PCIe 配置空间](/concepts/pcie-配置空间.md) — SR-IOV 能力结构所在的配置空间详解
- BARs 详解 — VF BARs 配置和地址映射机制
- MSI-X 中断 — VF 使用的中断机制
- [VFIO 设备直通](/concepts/vfio-设备直通.md) — 安全的 VF 分配给虚拟机的方法
- IOMMU — SR-IOV 隔离所依赖的 DMA 重映射技术

# Citations

1. [pcie-sriov.md:3-9](/references/pcie-sriov-08f3fcbf.md)
2. [pcie-sriov.md:582-593](/references/pcie-sriov-08f3fcbf.md)
3. [pcie-sriov.md:280-305](/references/pcie-sriov-08f3fcbf.md)
4. [pcie-sriov.md:265-276](/references/pcie-sriov-08f3fcbf.md)
5. [pcie-sriov.md:203-218](/references/pcie-sriov-08f3fcbf.md)
6. [pcie-sriov.md:161-186](/references/pcie-sriov-08f3fcbf.md)
7. [pcie-sriov.md:307-330](/references/pcie-sriov-08f3fcbf.md)
8. [pcie-sriov.md:190-201](/references/pcie-sriov-08f3fcbf.md)
9. [pcie-sriov.md:332-352](/references/pcie-sriov-08f3fcbf.md)
10. [pcie-sriov.md:220-234](/references/pcie-sriov-08f3fcbf.md)
11. [pcie-sriov.md:356-376](/references/pcie-sriov-08f3fcbf.md)
12. [pcie-sriov.md:378-395](/references/pcie-sriov-08f3fcbf.md)
13. [pcie-sriov.md:580-606](/references/pcie-sriov-08f3fcbf.md)
14. [pcie-sriov.md:555-578](/references/pcie-sriov-08f3fcbf.md)
