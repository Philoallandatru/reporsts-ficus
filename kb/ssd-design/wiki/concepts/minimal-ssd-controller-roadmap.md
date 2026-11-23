---
type: Concept
title: 最小 SSD 控制器实现路线
description: 如果目标是做一个教学或原型 SSD 控制器，不要一开始就实现完整 FTL、ECC、PLP 和多 namespace。更稳的路线是先让 host
  能枚举和读写，再逐层替换内部存储模型。
tags:
- ssd
- controller
- nand
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# 最小 SSD 控制器实现路线

如果目标是做一个教学或原型 SSD 控制器，不要一开始就实现完整 FTL、ECC、PLP 和多 namespace。更稳的路线是先让 host 能枚举和读写，再逐层替换内部存储模型。

## 阶段 0：可枚举的 NVMe 设备

目标：Linux 能发现设备，`nvme list` 能看到 controller。

最小能力：

- PCIe endpoint 或 emulator 设备可枚举。
- BAR 暴露 NVMe controller properties。
- 支持 controller enable/disable。
- 支持 Admin Queue 初始化。
- 支持 Identify Controller 和 Identify Namespace。

验收：

- Linux probe 不崩溃。
- `nvme id-ctrl` 和 `nvme id-ns` 返回一致字段。
- Reset 后可以重新 enable。

## 阶段 1：RAM-backed namespace

目标：实现 read/write，但数据只落在 DRAM 或 host 文件中。

最小能力：

- I/O Submission Queue 和 Completion Queue。
- PRP/SGL 或先只支持 PRP。
- Read、Write、Flush 的基本路径。
- CQE status、phase tag、command identifier 正确。

验收：

- `fio --verify` 通过。
- 多 queue、多 queue depth 不丢完成。
- Controller reset 后 RAM 数据按设计清空或保留，行为可解释。

## 阶段 2：简单 FTL

目标：把写入从 RAM 转到 NAND model 或 flash backend。

最小能力：

- L2P page mapping。
- Free page/block allocator。
- Sequential append writes。
- Old page invalidation。
- P2L 或 block valid count。

暂不实现：

- 复杂 GC。
- Wear leveling。
- SLC cache。
- Power-loss recovery。

验收：

- 覆盖写后读不到旧数据。
- 写满前 free block 计数一致。
- 每个 LPN 有且只有一个最新 physical page。

## 阶段 3：GC 和前向进展

目标：设备在随机覆盖写下不会写满后停止。

新增能力：

- Victim block selection。
- Valid page migration。
- Block erase。
- Emergency free block watermark。
- Host write throttling。

验收：

- 长时间随机写后仍可写入。
- WAF 可统计。
- GC 期间读写数据一致。
- 注入 GC 中断或 reset 后状态可恢复。

## 阶段 4：持久化元数据

目标：reset 或掉电后恢复 L2P 和 block state。

新增能力：

- Superblock。
- Checkpoint。
- Metadata journal。
- Sequence number、CRC、commit marker。
- Recovery replay。

验收：

- 任意写路径阶段掉电注入后，恢复状态符合持久化模型。
- Journal 半写入不会被重放。
- Checkpoint 半写入会回退到上一代。

## 阶段 5：NAND 错误与可靠性

目标：把 NAND 从“理想介质”变成“会出错的介质”。

新增能力：

- Bad block table。
- Program/erase fail。
- Correctable/uncorrectable read。
- ECC correction count。
- Read retry。
- Scrub/refresh。

验收：

- Program fail 不丢旧数据。
- High correction count 触发搬迁。
- Uncorrectable read 返回正确 NVMe status 并记录日志。

## 阶段 6：性能/QoS 和后台任务

目标：在合理 workload 下表现稳定。

新增能力：

- 多 channel/die 调度。
- Read priority。
- GC budget。
- Thermal/power throttling hook。
- Latency histogram。
- Telemetry。

验收：

- p99/p999 延迟可观测。
- GC 不无限阻塞读。
- 写满、低 OP、混合读写场景下设备不死锁。

## 最小代码模块

```text
nvme_frontend/
  registers
  admin_queue
  io_queue
  prp_sgl
  cqe
firmware/
  command_dispatch
  namespace
  ftl
  gc
  recovery
  telemetry
backend/
  ram_namespace
  nand_model
  flash_scheduler
  ecc_model
common/
  metadata_format
  tracing
  fault_injection
```

## 关键来源

- NVM Express Specifications: https://nvmexpress.org/specifications/
- Linux Kernel NVMe documentation: https://docs.kernel.org/nvme/index.html
- FEMU: https://github.com/MoatLab/FEMU
- Cosmos+ OpenSSD: https://github.com/Cosmos-OpenSSD/Cosmos-plus-OpenSSD
- SimpleSSD: https://github.com/SimpleSSD/SimpleSSD
