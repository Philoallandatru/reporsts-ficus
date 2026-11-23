# SSD 设计术语表

本术语表用于统一 `ssd-design-wiki` 的中文表达。涉及 NVMe/PCIe 的精确定义时，仍以本仓库 `nvme-wiki`、`pcie-wiki` 和官方规范为准。

## Host Interface

| 术语 | 中文 | 说明 |
|---|---|---|
| Controller | 控制器 | Host 可见的 NVMe 控制器，也是 SSD 内部硬件/固件系统的前端身份 |
| Namespace | 命名空间 | Host 看到的逻辑块地址空间，不等同物理 NAND 区域 |
| Submission Queue | 提交队列 | Host 写入命令，controller 拉取 |
| Completion Queue | 完成队列 | Controller 写入完成项，host 回收 |
| Doorbell | 门铃 | Host 通知 controller 队列 tail/head 变化的 MMIO 机制 |
| PRP | Physical Region Page | NVMe 用来描述 host buffer 的物理页指针 |
| SGL | Scatter Gather List | NVMe 可选的数据缓冲区描述符链 |
| CQE | Completion Queue Entry | 命令完成记录，包含 status 和 command identifier |
| MDTS | Maximum Data Transfer Size | 单命令最大传输大小限制 |
| VWC | Volatile Write Cache | 控制器易失写缓存能力/配置 |

## Firmware and FTL

| 术语 | 中文 | 说明 |
|---|---|---|
| FTL | 闪存转换层 | 把 LBA 块接口转换为 NAND append/program/erase 模型 |
| L2P | 逻辑到物理映射 | 从 LPN/LBA 找 physical page |
| P2L | 物理到逻辑反向映射 | GC 和恢复时从 physical page 找回 LPN |
| LPN | Logical Page Number | FTL 映射粒度下的逻辑页号 |
| PPN | Physical Page Number | 物理 NAND 页地址或抽象物理页号 |
| GC | 垃圾回收 | 搬迁有效页、擦除 victim block、释放 free block |
| WAF | 写放大系数 | NAND 写入量与 host 写入量之比 |
| Checkpoint | 检查点 | 持久化的一代完整或摘要元数据 |
| Journal | 日志 | 顺序记录映射和 block 状态变化，用于恢复 |
| Superblock | 超级块 | 指向当前 metadata generation、版本和布局的根记录 |
| Free Block Pool | 空闲块池 | 可分配写入的已擦除 block 集合 |
| Victim Block | 回收目标块 | GC 选择的待搬迁/擦除 block |
| Hot/Cold Data | 热/冷数据 | 按更新频率区分的数据类别 |

## NAND Media

| 术语 | 中文 | 说明 |
|---|---|---|
| Channel | 通道 | 控制器到一组 NAND devices 的共享数据路径 |
| Package | 封装 | 物理 NAND 封装，内部可含多个 die |
| Die/LUN | 晶粒/逻辑单元 | 可独立 busy 的 NAND 内部执行单元 |
| Plane | 平面 | die 内可参与 multi-plane 操作的区域 |
| Block | 块 | NAND erase 单位 |
| Page | 页 | NAND read/program 单位 |
| OOB/Spare | 备用区 | Page 附带的元数据/ECC 区域 |
| P/E Cycle | 擦写次数 | Program/erase 循环次数，是寿命核心指标 |
| Read Retry | 读重试 | 调整读参考电压或模式以恢复数据 |
| Read Disturb | 读干扰 | 反复读导致邻近 cell 出错 |
| Retention | 保持期 | 数据随时间和温度发生电荷漂移的可靠性问题 |

## Reliability and Product

| 术语 | 中文 | 说明 |
|---|---|---|
| ECC | 错误校正码 | 检测并纠正 NAND bit error |
| LDPC | 低密度奇偶校验码 | 现代 NAND 常用强纠错方案 |
| RBER | 原始误码率 | ECC 前的 bit error rate |
| UBER | 不可纠正误码率 | ECC 后仍不可恢复的数据错误率 |
| PLP | 掉电保护 | Power-loss protection，硬件能量加固件恢复协议 |
| SMART / Health | 健康信息 | 温度、寿命、错误、备用容量等健康指标 |
| Telemetry | 遥测 | 控制器内部诊断数据快照 |
| TBW | 总写入字节 | Endurance 规格中常见寿命指标 |
| Steady State | 稳态 | 写入和 GC 达到长期平衡后的性能状态 |
| SLC Cache | SLC 缓存 | 用 SLC 模式缓存写入，再搬迁到 TLC/QLC |
