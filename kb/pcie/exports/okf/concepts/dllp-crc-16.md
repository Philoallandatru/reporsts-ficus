---
type: concept
x-llmwiki:
  schemaVersion: "0.1"
  contentHash: 51da8185ef5d4d3dac829f593a3caf5aedc676c8d26f4c51c49d70a81f3a29ab
  pageDirectory: concepts
  sources:
    - pcie-dllp-format.md
  confidence: 1
  provenanceState: extracted
  freshnessStatus: fresh
  aliases:
    - dllp-crc-16
  citations:
    - file: pcie-dllp-format.md
      start: 419
      end: 452
    - file: pcie-dllp-format.md
      start: 56
      end: 57
    - file: pcie-dllp-format.md
      start: 419
      end: 427
    - file: pcie-dllp-format.md
      start: 56
      end: 69
    - file: pcie-dllp-format.md
      start: 423
      end: 423
    - file: pcie-dllp-format.md
      start: 438
      end: 438
    - file: pcie-dllp-format.md
      start: 430
      end: 446
    - file: pcie-dllp-format.md
      start: 425
      end: 425
    - file: pcie-dllp-format.md
      start: 449
      end: 451
    - file: pcie-dllp-format.md
      start: 451
      end: 451
    - file: pcie-dllp-format.md
      start: 583
      end: 594
    - file: pcie-dllp-format.md
      start: 83
      end: 100
    - file: pcie-dllp-format.md
      start: 124
      end: 127
    - file: pcie-dllp-format.md
      start: 172
      end: 175
    - file: pcie-dllp-format.md
      start: 223
      end: 238
    - file: pcie-dllp-format.md
      start: 284
      end: 301
    - file: pcie-dllp-format.md
      start: 338
      end: 348
    - file: pcie-dllp-format.md
      start: 400
      end: 410
    - file: pcie-dllp-format.md
      start: 48
      end: 48
    - file: pcie-dllp-format.md
      start: 466
      end: 469
    - file: pcie-dllp-format.md
      start: 69
      end: 69
    - file: pcie-dllp-format.md
      start: 459
      end: 469
    - file: pcie-dllp-format.md
      start: 535
      end: 538
title: DLLP CRC-16
description: DLLP使用CRC-16-IBM多项式校验前6字节内容，CRC错误时丢弃DLLP（不重传）
tags:
  - pcie
  - error-detection
  - crc
timestamp: "2026-08-16T06:37:50.818Z"
---

# DLLP CRC-16

DLLP CRC-16 是用于保护数据链路层包（Data Link Layer Packet, DLLP）完整性的 16 位循环冗余校验码。它位于每个 DLLP 的最后 2 个字节，用于检测传输过程中可能发生的数据损坏。 ^[pcie-dllp-format.md:419-452]

## 基本特性

| 特性 | 值 |
|------|-----|
| **字段位置** | DLLP 字节 6-7（最后 2 字节） |
| **字段宽度** | 16 位（2 字节） |
| **多项式** | CRC-16-IBM (x¹⁶ + x¹⁵ + x² + 1) |
| **初始值** | 0xFFFF |
| **计算范围** | DLLP 前 6 字节（Type + Content） |

^[pcie-dllp-format.md:56-57, pcie-dllp-format.md:419-427]

## 在 DLLP 结构中的位置

所有 DLLP 的长度固定为 8 字节（64 位），其结构如下：

```
┌────────────────────────────────────────────────────┐
│  Byte 0-1: DLLP Type + Reserved                    │  2 字节
├────────────────────────────────────────────────────┤
│  Byte 2-5: DLLP Content (Type-Specific)            │  4 字节
├────────────────────────────────────────────────────┤
│  Byte 6-7: CRC-16                                  │  2 字节  ← CRC-16 位置
└────────────────────────────────────────────────────┘
```

DLLP 的 CRC-16 与 TLP 使用的 LCRC（32 位）形成对比：DLLP 采用更短的 16 位 CRC，而 TLP 使用 32 位的 LCRC。这一差异反映了两种包的不同特性——DLLP 是固定长度的控制包，而 TLP 是可变长度的数据包。 ^[pcie-dllp-format.md:56-69]

## 计算方法

### 多项式

CRC-16 采用 IBM 标准多项式，其二进制表示为 `0x8005`（x¹⁶ + x¹⁵ + x² + 1）。该多项式广泛用于通信协议中的错误检测。 ^[pcie-dllp-format.md:423, 438]

### 计算算法

计算时对 DLLP 的前 6 个字节逐字节处理：

```c
uint16_t calculate_dllp_crc(uint8_t *dllp_data) {
    uint16_t crc = 0xFFFF;  // 初始值
    
    for (int i = 0; i < 6; i++) {  // 前 6 字节
        crc = crc ^ (dllp_data[i] << 8);
        for (int j = 0; j < 8; j++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x8005;  // 多项式
            } else {
                crc = crc << 1;
            }
        }
    }
    
    return crc;
}
```

^[pcie-dllp-format.md:430-446]

### 覆盖范围

CRC-16 覆盖 DLLP 的以下部分：
- **字节 0-1**：DLLP 类型字段及保留位
- **字节 2-5**：DLLP 类型特定内容（因 DLLP 类型而异）

这意味着 CRC 保护了 DLLP 的类型信息和所有有效载荷数据，但不包含 CRC 字段本身（这是 CRC 计算的标准做法）。 ^[pcie-dllp-format.md:425]

## 错误处理

当接收方计算收到的 CRC 并与 DLLP 中携带的 CRC 值进行比较时，会产生两种结果：

| 校验结果 | 处理方式 |
|----------|----------|
| **CRC 正确** | 正常处理 DLLP |
| **CRC 错误** | 丢弃 DLLP |

 ^[pcie-dllp-format.md:449-451]

### 与 TLP 重传机制的区别

一个关键的设计决策是：**DLLP 不会被重传**。当 CRC 校验失败时，DLLP 直接被丢弃，不会触发重传请求。这与 TLP 的处理方式不同。 ^[pcie-dllp-format.md:451]

原因是 DLLP 丢失后，依赖上层机制进行恢复：
- **Ack/Nak DLLP 丢失**：发送方有超时重传机制
- **UpdateFC DLLP 丢失**：接收方会继续发送新的 UpdateFC
- **PM DLLP 丢失**：电源状态变更有超时和重试机制

这种设计避免了递归确认问题（确认的确认）。 ^[pcie-dllp-format.md:449-451, pcie-dllp-format.md:583-594]

## CRC-16 在各类 DLLP 中的应用

CRC-16 存在于所有类型的 DLLP 中，包括：

| DLLP 类型 | Type 值 | CRC-16 作用 |
|-----------|---------|-------------|
| Ack | 0x00 | 保护 AckNak Seq Number 字段 |
| Nak | 0x10 | 保护 AckNak Seq Number 字段 |
| InitFC1-P/NP/Cpl | 0x50/0x60/0x70 | 保护 HdrFC 和 DataFC 字段 |
| InitFC2-P/NP/Cpl | 0xC0/0xD0/0xE0 | 保护 HdrFC 和 DataFC 字段 |
| UpdateFC-P/NP/Cpl | 0x80/0x90/0xA0 | 保护 HdrFC 和 DataFC 字段 |
| PM_Enter_L1/L23 | 0x20/0x21 | 保护保留字段 |
| PM_Request_Ack | 0x30 | 保护保留字段 |
| Vendor-Specific | 0x40 | 保护厂商自定义内容 |

 ^[pcie-dllp-format.md:83-100, pcie-dllp-format.md:124-127, pcie-dllp-format.md:172-175, pcie-dllp-format.md:223-238, pcie-dllp-format.md:284-301, pcie-dllp-format.md:338-348, pcie-dllp-format.md:400-410]

## 设计考量

### 1. 固定长度简化计算

由于所有 DLLP 都是固定 8 字节，CRC 计算范围始终是前 6 字节，无需额外的长度字段来指示 CRC 范围。这简化了硬件实现。 ^[pcie-dllp-format.md:48, 425]

### 2. 16 位长度的权衡

选择 16 位 CRC 而非更长的 CRC：
- **优点**：开销小（仅 2 5% 的包长），对链路带宽影响有限
- **缺点**：检测能力有限，漏检概率约为 1/65536

考虑到 DLLP 是控制包，丢失后有上层恢复机制，16 位 CRC 在效率和可靠性之间取得了合理的平衡。 ^[pcie-dllp-format.md:449-451, pcie-dllp-format.md:583-594]

### 3. 与物理层编码的关系

DLLP 与 TLP 在物理层使用相同的编码方式传输。CRC-16 仅在数据链路层提供保护，物理层还有自己的 8b/10b 或 128b/130b 编码提供额外的错误检测能力。 ^[pcie-dllp-format.md:466-469]

## 与相关概念的对比

| 特性 | DLLP CRC-16 | TLP LCRC | TLP ECRC（可选）|
|------|-------------|----------|------------------|
| 位置 | 数据链路层 | 数据链路层 | 事务层 |
| 宽度 | 16 位 | 32 位 | 32 位 |
| 覆盖范围 | DLLP 前 6 字节 | 整个 TLP | 整个 TLP（可选）|
| 错误处理 | 丢弃 | 重传 | 报告错误 |

 ^[pcie-dllp-format.md:69, pcie-dllp-format.md:459-469]

## 调试建议

当怀疑 DLLP 传输存在问题时，可通过以下方式诊断：

1. **使用 PCIe 协议分析仪**：实时捕获 DLLP，验证 CRC 值
2. **检查链路错误统计**：通过 `lspci -vvv` 查看 Data Link Protocol Error 计数
3. **验证 Ack/Nak 时序**：确保重传机制正常工作 ^[pcie-dllp-format.md:535-538]

---

## 总结

DLLP CRC-16 是 PCIe 数据链路层错误检测机制的重要组成部分。它使用 CRC-16-IBM 多项式，对 DLLP 的前 6 字节进行校验，初始值为 0xFFFF。当 CRC 校验失败时，DLLP 被丢弃，但不会触发重传——DLLP 丢失的影响由上层机制（如 TLP 超时重传）来消化。这种设计体现了 PCIe 协议在控制平面和数据平面采用不同可靠性策略的思路。 ^[pcie-dllp-format.md:419-452, pcie-dllp-format.md:449-451, pcie-dllp-format.md:583-594]

---

## Sources

- [DLLP 格式详解](pcie-dllp-format.md)

# Citations

1. [pcie-dllp-format.md:419-452](/references/pcie-dllp-format-55680021.md)
2. [pcie-dllp-format.md:56-57](/references/pcie-dllp-format-55680021.md)
3. [pcie-dllp-format.md:419-427](/references/pcie-dllp-format-55680021.md)
4. [pcie-dllp-format.md:56-69](/references/pcie-dllp-format-55680021.md)
5. [pcie-dllp-format.md:423-423](/references/pcie-dllp-format-55680021.md)
6. [pcie-dllp-format.md:438-438](/references/pcie-dllp-format-55680021.md)
7. [pcie-dllp-format.md:430-446](/references/pcie-dllp-format-55680021.md)
8. [pcie-dllp-format.md:425-425](/references/pcie-dllp-format-55680021.md)
9. [pcie-dllp-format.md:449-451](/references/pcie-dllp-format-55680021.md)
10. [pcie-dllp-format.md:451-451](/references/pcie-dllp-format-55680021.md)
11. [pcie-dllp-format.md:583-594](/references/pcie-dllp-format-55680021.md)
12. [pcie-dllp-format.md:83-100](/references/pcie-dllp-format-55680021.md)
13. [pcie-dllp-format.md:124-127](/references/pcie-dllp-format-55680021.md)
14. [pcie-dllp-format.md:172-175](/references/pcie-dllp-format-55680021.md)
15. [pcie-dllp-format.md:223-238](/references/pcie-dllp-format-55680021.md)
16. [pcie-dllp-format.md:284-301](/references/pcie-dllp-format-55680021.md)
17. [pcie-dllp-format.md:338-348](/references/pcie-dllp-format-55680021.md)
18. [pcie-dllp-format.md:400-410](/references/pcie-dllp-format-55680021.md)
19. [pcie-dllp-format.md:48-48](/references/pcie-dllp-format-55680021.md)
20. [pcie-dllp-format.md:466-469](/references/pcie-dllp-format-55680021.md)
21. [pcie-dllp-format.md:69-69](/references/pcie-dllp-format-55680021.md)
22. [pcie-dllp-format.md:459-469](/references/pcie-dllp-format-55680021.md)
23. [pcie-dllp-format.md:535-538](/references/pcie-dllp-format-55680021.md)
