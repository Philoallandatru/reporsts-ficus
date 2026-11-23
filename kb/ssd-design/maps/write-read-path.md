# 读写路径图

## Write Path

```mermaid
sequenceDiagram
  participant H as Host
  participant Q as NVMe Queue Manager
  participant D as DMA / Buffer
  participant F as FTL
  participant M as Metadata Journal
  participant N as NAND Backend
  participant C as Completion

  H->>Q: SQE + doorbell
  Q->>D: Fetch SQE and validate PRP/SGL
  D->>D: DMA host data into buffer
  D->>F: Dispatch write LBA range
  F->>F: Allocate physical pages
  F->>N: Program NAND pages
  N-->>F: Program complete or fail
  F->>M: Append mapping/block-state journal
  M-->>F: Durable commit point
  F->>C: Build CQE status
  C->>H: CQE + interrupt/polling visibility
```

## Read Path

```mermaid
sequenceDiagram
  participant H as Host
  participant Q as NVMe Queue Manager
  participant F as FTL
  participant N as NAND Backend
  participant E as ECC / LDPC
  participant D as DMA
  participant C as Completion

  H->>Q: SQE + doorbell
  Q->>F: Dispatch read LBA range
  F->>F: L2P lookup
  F->>N: Schedule NAND read
  N-->>E: Raw data and metadata
  E-->>F: Corrected data or retry/fail
  F->>D: DMA data to host
  D-->>C: Transfer complete
  C->>H: CQE + interrupt/polling visibility
```

## 阅读入口

- [SSD 内部的 NVMe 命令生命周期](../wiki/concepts/nvme-command-lifecycle-in-ssd.md)
- [FTL 设计深水区](../wiki/concepts/ftl-design-deep-dive.md)
- [ECC、LDPC 与可靠性管理](../wiki/concepts/ecc-ldpc-reliability.md)
- [掉电保护与恢复](../wiki/concepts/power-loss-recovery.md)
