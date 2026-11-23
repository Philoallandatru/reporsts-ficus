# SSD Controller / IP Vendor 公开资料 Intake

调研日期：2026-08-12。

本 intake 用于整理控制器厂商、FPGA IP 和参考设计的公开资料入口。公开 controller brief 通常不会披露完整 FTL、ECC 或 RTL；它们主要用于补产品功能边界、host interface、form factor、security、telemetry、power 和 firmware update 语言。

更完整的抽取流程见 [控制器厂商数据采集与建模](../../wiki/concepts/controller-vendor-data-acquisition.md)。

机器可读采集矩阵见 [Controller Vendor Extraction Matrix](controller-vendor-extraction-matrix.yml)。如果要新增厂商入口或固定公开 brief，先把条目放进采集矩阵，再补本地文件、sha256 和抽取状态。

样本登记册见 [Controller Vendor Sample Registry](controller-vendor-sample-registry.yml)。如果你要检查哪些厂商已经有首批样本，先看这个登记册，再点具体 intake。

## 已固定样本

| 条目 | 本地 intake | 官方入口 |
|---|---|---|
| AMD PG329 NVMe Target Controller | [amd-pg329-nvmetc-intake.md](amd-pg329-nvmetc-intake.md) | https://docs.amd.com/r/en-US/pg329-nvme-target-controller |
| Microchip Flashtec NVMe Controller | [microchip-flashtec-nvme-intake.md](microchip-flashtec-nvme-intake.md) | https://www.microchip.com/en-us/products/storage/flashtec-nvme-controllers |
| Marvell SSD Controllers | [marvell-ssd-controllers-intake.md](marvell-ssd-controllers-intake.md) | https://www.marvell.com/products/ssd-controllers.html |
| Silicon Motion SSD Controllers | [silicon-motion-ssd-controller-intake.md](silicon-motion-ssd-controller-intake.md) | https://www.siliconmotion.com/products/client/detail ; https://www.siliconmotion.com/cht/products/enterprise/detail |
| Phison SSD Controller | [phison-ssd-controller-intake.md](phison-ssd-controller-intake.md) | https://www.phison.com/solutions/ssd/ ; https://www.phison.com/e28/ ; https://www.phison.com/e31t/ |
| InnoGrit SSD Controller | [innogrit-ssd-controller-intake.md](innogrit-ssd-controller-intake.md) | https://www.innogritcorp.com/ ; https://www.innogritcorp.com/ssdcontrollers/client/ ; https://www.innogritcorp.com/ssdcontrollers/enterprise/ |
| Maxio SSD Controllers | [maxio-ssd-controller-intake.md](maxio-ssd-controller-intake.md) | https://www.maxio-tech.com/product/11628/11631/ ; https://www.maxio-tech.com/product/11628/11631/11753/ ; https://www.maxio-tech.com/product/11628/11631/11753/11733/ |

## AMD / Xilinx NVMe Target Controller IP

- IP 入口：https://www.amd.com/en/products/adaptive-socs-and-fpgas/intellectual-property/ef-di-nvmetc.html
- Product guide：https://docs.amd.com/r/en-US/pg329-nvme-target-controller
- 可用资料：NVMe target controller、QDMA、PRP fetch、queue/register/interface、FPGA endpoint 模块边界。
- 适合抽取：NVMe 前端硬件模块、AXI/QDMA 边界、doorbell/queue handling、PRP/SGL walker 参考。
- 局限：这是 NVMe target IP，不是完整 SSD controller；不覆盖 NAND FTL、wear leveling、PLP 和 LDPC 产品实现。

### AMD 适合补的字段

- register map。
- queue / doorbell / interrupt 处理边界。
- PRP / SGL walker 的硬件职责划分。
- 与 DMA、AXI、PCIe endpoint 的接口约束。

## Microchip

- 入口：https://www.microchip.com/
- 推荐检索：`Microchip NVMe SSD controller`, `Flashtec NVMe controller`, `PCIe NVMe SSD controller`
- 可用资料：Flashtec NVMe controller 产品页、brief、firmware/security/enterprise feature 说明。
- 适合抽取：enterprise SSD controller 功能清单、PCIe/NVMe 版本、security、SR-IOV/virtualization、telemetry 术语。
- 局限：公开资料通常不含内部 FTL、ECC pipeline、RTL 接口和 NAND 参数。

### Microchip 适合补的字段

- 产品家族。
- PCIe / NVMe generation。
- security / telemetry / firmware update feature。
- enterprise management 和 diagnostic 语言。

## Marvell

- 入口：https://www.marvell.com/products/storage/storage-controllers.html
- 可用资料：storage controller、data center SSD controller、brochure/brief。
- 适合抽取：PCIe/NVMe 代际、enterprise feature、power/performance 定位、security/management 功能。
- 局限：控制器内部架构通常以 marketing block 表述，不能当作可实现模块接口。

### Marvell 适合补的字段

- controller family。
- supported SSD segment。
- power / performance / security claims。
- 可直接映射到主机可见 feature 的名词。

## Silicon Motion

- 入口：https://www.siliconmotion.com/
- 推荐检索：`PCIe NVMe SSD controller`, `SM226x`, `SM250x`, `enterprise SSD controller`
- 可用资料：client/enterprise NVMe controller 产品页、feature list、performance/power positioning。
- 适合抽取：DRAM-less/HMB、PCIe generation、NAND support、security feature、consumer/client SSD language。
- 局限：公开资料不提供完整固件状态机、NAND command path 或 LDPC decoder 细节。

### Silicon Motion 适合补的字段

- DRAM-less / HMB。
- NAND support 范围。
- client vs enterprise feature 分界。
- thermal / power positioning。

## Phison

- 入口：https://www.phison.com/
- 可用资料：consumer/enterprise SSD controller、PCIe Gen5/Gen6 positioning、firmware/security feature。
- 适合抽取：controller product taxonomy、enterprise/client feature 对比、thermal/power 约束。
- 局限：公开页更偏产品介绍；需要 datasheet 或 brief 才能进入参数层。

### Phison 适合补的字段

- controller taxonomy。
- PCIe generation。
- client / enterprise feature。
- firmware update / thermal / security language。

## Innogrit

- 入口：https://www.innogritcorp.com/
- 可用资料：PCIe NVMe SSD controller product pages、enterprise/client controller feature。
- 适合抽取：controller family、PCIe/NVMe version、NAND support、security/power feature。
- 局限：公开资料深度有限，不足以支撑 RTL 或 firmware 设计。

### Innogrit 适合补的字段

- family name。
- host interface。
- NAND support claim。
- power / reliability feature。

## Maxio

- 入口：https://www.maxio-tech.com/
- 可用资料：client NVMe controller product pages、controller feature and product positioning。
- 适合抽取：DRAM-less/client SSD controller feature、NAND support、PCIe generation。
- 局限：公开资料多为产品级介绍，不能替代 datasheet。

### Maxio 适合补的字段

- DRAM-less feature。
- client SSD positioning。
- PCIe generation。
- NAND support and security claims。

## 抽取模板

| 字段 | 示例 | 是否必须 |
|---|---|---|
| Vendor / product family | Microchip Flashtec, AMD PG329 | yes |
| Source URL / file | official page, product brief, guide, sha256 | yes |
| Host interface | PCIe generation, NVMe version, lanes, SR-IOV/namespace support | yes |
| NAND interface | channel count, ONFI/Toggle, supported NAND type | if disclosed |
| Memory architecture | DRAM, SRAM, HMB, cache | if disclosed |
| Reliability | ECC/LDPC, RAID/parity, PLP, telemetry | if disclosed |
| Security | AES, TCG Opal, secure boot, firmware signing | if disclosed |
| Firmware lifecycle | FW download/commit, rollback, dual image | if disclosed |
| Validation clue | supported logs, diagnostics, production test hooks | optional |

## 结论

控制器厂商公开资料适合补“产品需要声明什么能力”和“硬件模块边界有哪些常见名字”；不适合直接生成 FTL 或 RTL 设计。真正可实现的内部设计仍应优先参考规范、开源实现、论文和可获得的 product guide。
