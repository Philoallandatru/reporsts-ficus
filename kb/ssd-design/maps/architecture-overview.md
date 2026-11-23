# SSD 控制器架构总览

```mermaid
flowchart LR
  Host["Host software<br/>Linux / SPDK / nvme-cli / fio"]
  PCIe["PCIe endpoint<br/>BAR / MSI-X / DMA"]
  NVMe["NVMe front end<br/>registers / queues / PRP-SGL"]
  FW["Firmware scheduler<br/>admin / io / background"]
  FTL["FTL<br/>L2P / P2L / GC / wear leveling"]
  BUF["SRAM / DRAM / HMB<br/>contexts / buffers / mapping cache"]
  META["Metadata service<br/>superblock / checkpoint / journal"]
  ECC["ECC / LDPC / crypto<br/>scrambler / AES / CRC"]
  FLASH["Flash scheduler<br/>channel / die / plane arbitration"]
  NAND["NAND media<br/>page / block / plane / die / channel"]
  PLP["Power-loss protection<br/>detector / hold-up / emergency commit"]
  TELE["Logs / SMART / telemetry<br/>health / debug / counters"]

  Host --> PCIe --> NVMe --> FW
  NVMe <--> BUF
  FW --> FTL
  FTL <--> BUF
  FTL --> META
  FTL --> FLASH
  FLASH --> ECC --> NAND
  PLP --> META
  PLP --> FW
  FW --> TELE
  FTL --> TELE
  ECC --> TELE
```

## 阅读入口

- [SSD 系统架构](../wiki/concepts/ssd-system-architecture.md)
- [控制器硬件模块边界](../wiki/concepts/controller-hardware-module-boundaries.md)
- [FTL 与固件职责](../wiki/concepts/firmware-ftl.md)
- [FTL 元数据格式与恢复约定](../wiki/concepts/ftl-metadata-format-and-recovery-conventions.md)
