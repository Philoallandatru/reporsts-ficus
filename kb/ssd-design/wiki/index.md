# Knowledge Wiki

## Concepts

- **[[开源-ssd-仿真平台|开源 SSD 仿真平台]]** — Cosmos+ OpenSSD、FEMU、SimpleSSD、MQSim 等开源仿真器提供从固件开发到性能建模的全栈验证环境，是 SSD 设计的重要参考实现。
- **[[主流-nand-技术路线图|主流 NAND 技术路线图]]** — BiCS FLASH（Kioxia/Sandisk）、V-NAND（Samsung）、4D NAND（SK hynix）、Xtacking（YMTC）四大 3D NAND 架构流派及其公开资料入口
- **[[专利检索入口工具链|专利检索入口工具链]]** — Google Patents（快速发现与家族链接）、USPTO Patent Public Search（权威美国专利检索）、USPTO Patent Center（申请状态查询）的适用场景与局限性分析。
- **[[cpc-专利分类体系与-ssd-领域映射|CPC 专利分类体系与 SSD 领域映射]]** — G06F 3/06（数字 I/O 到记录介质）、G06F 12/00（内存寻址/分配）、G11C 16/00（NAND 编程/读取/擦除）、H03M 13（LDPC/BCH 编码）、H10B（3D NAND 器件结构）等 CPC 分类号在 SSD/闪存专利检索中的应用与局限。
- **[[host-ftl-与-open-channel-ssd|Host FTL 与 Open-Channel SSD]]** — LightNVM、OCSSD-plus、SPDK FTL 等主机侧 FTL 实现路线与设计权衡
- **[[jedec-ssd-耐久性标准体系|JEDEC SSD 耐久性标准体系]]** — JESD218 定义 SSD 耐久性评级方法论，JESD219 定义耐久性测试工作负载，为企业级 SSD 容量规划与寿命评估提供合规基准。
- **[[linux-nvme-内核驱动架构|Linux NVMe 内核驱动架构]]** — Linux 内核 NVMe 子系统的模块划分：admin/I/O 路径、设备生命周期、特性与 quirk 策略
- **[[mqsim-多队列-ssd-模拟器|MQSim 多队列 SSD 模拟器]]** — 针对现代多队列 NVMe/SATA SSD 的性能建模模拟器，聚焦延迟和多队列调度研究
- **[[nand-厂商资料-intake-标签体系|NAND 厂商资料 Intake 标签体系]]** — 按厂商（Micron/Kioxia/Samsung/SK hynix/YMTC/WD-Sandisk）和按专利主题（PLP/SLC-cache/FDP-placement）两个维度的标签命名约定与使用场景。
- **[[nand-供应商公开资料采集方法论|NAND 供应商公开资料采集方法论]]** — 系统化采集 Micron、Kioxia、Samsung、SK hynix、YMTC、Western Digital/Sandisk 等 NAND 供应商官方公开资料的方法与入口
- **[[nand-vendor-public-material-intake|NAND Vendor Public Material Intake]]** — 系统性采集 Micron、Kioxia、Samsung、SK hynix、YMTC、Western Digital/Sandisk 等主要 NAND 原厂公开资料的方法论，包括着陆页、下载门户、代际页面和产品目录的优先级排序与适用条件。
- **[[nvme-24-规范版本状态|NVMe 2.4 规范版本状态]]** — 截至 2026-08-12，NVMe 2.4 已于 2026-08-04 发布，版本迭代速度加快，需固定 PDF 版本进行引用
- **[[nvme-规范体系|NVMe 规范体系]]** — NVM Express 规范家族定义主机可见协议、命令集、传输层、队列机制、复位行为、固件更新、遥测和电源管理，是 SSD 与主机通信的权威标准。
- **[[nvmeip-fpga-商业实现生态|NVMe/IP FPGA 商业实现生态]]** — AMD、Design Gateway 等厂商提供的 NVMe FPGA IP 模块边界与适用场景
- **[[ocp-数据中心-nvme-ssd-规范|OCP 数据中心 NVMe SSD 规范]]** — OCP 发布的数据中心级 NVMe SSD 规范补充了 NVMe 基础规范中的功耗管理、遥测字段和部署要求，适用于大规模基础设施集成。
- **[[ocp-data-center-nvme-ssd-规范|OCP Data Center NVMe SSD 规范]]** — OCP 文档包含数据中心 NVMe SSD 规格及数据中心级 SSD 需求，是超大规模数据中心场景下 SSD 设计的权威参考
- **[[onfi-闪存接口规范|ONFI 闪存接口规范]]** — Open NAND Flash Interface 规范定义 NAND 器件的命令、地址、数据、电气和时序模型，是 NAND 介质与控制器接口的权威标准。
- **[[spdk-ftl-库与主机侧闪存管理|SPDK FTL 库与主机侧闪存管理]]** — SPDK 提供的 FTL bdev 实现，包含 L2P 映射、缓存和恢复机制，是公开的主机侧闪存管理工程参考
- **[[spdklinux-作为-ssd-主机侧验证参考|SPDK/Linux 作为 SSD 主机侧验证参考]]** — SPDK 和 Linux 内核作为队列、命令、复位和互操作性验证的 host-side 参考
- **[[ssd-仿真与模拟平台生态|SSD 仿真与模拟平台生态]]** — FEMU、MQSim、SimpleSSD 等仿真平台覆盖从快级仿真到周期精确仿真的不同保真度层级，用于 SSD 设计验证和性能评估
- **[[ssd-技术领域专利查询模板|SSD 技术领域专利查询模板]]** — FTL/垃圾回收/磨损均衡、PLP/掉电保护、LDPC/软解码、SLC 缓存/pSLC、Placement/FDP/Streams、NAND 器件/干扰/保持力等六大方向的专利查询 Starter URL 与关键词扩展建议。
- **[[ssd-技术专利检索工具链|SSD 技术专利检索工具链]]** — Google Patents Advanced Search、USPTO Patent Public Search、USPTO Patent Center 的适用场景与分工
- **[[ssd-经典研究论文索引|SSD 经典研究论文索引]]** — DFTL、FAST、LDPC-in-SSD、LightNVM 等经典论文构成 SSD 学术研究的理论基石，涉及映射算法、垃圾回收、纠错编码等核心设计问题。
- **[[ssd-领域专利查询启动器|SSD 领域专利查询启动器]]** — FTL/GC/Wear Leveling、PLP/掉电保护、LDPC/软解码、SLC Cache/pSLC、Placement/FDP、NAND Disturb/Retention 等六大主题的专利查询模板与关键词策略
- **[[ssd-学术研究经典论文索引|SSD 学术研究经典论文索引]]** — DFTL、FAST、LDPC-in-SSD 等经典 SSD 论文的 DOI、源码与实验条件定位
- **[[ssd-子系统设计文档模板|SSD 子系统设计文档模板]]** — 设计目标、耐久状态、 volatile 状态、主状态机、失效案例、验证要点的结构化文档方法
- **[[ssdflash-专利-cpc-分类体系|SSD/Flash 专利 CPC 分类体系]]** — G06F 3/06（SSD控制器/FTL/GC）、G11C 16/00（NAND 器件物理）、H03M 13（LDPC/ECC）、H10B（3D NAND 结构）等关键 CPC 分类代码及用途
- **[[wd-与-sandisk-企业分离后的闪存资料归属|WD 与 Sandisk 企业分离后的闪存资料归属]]** — Western Digital 于 2025-02-24 完成闪存业务分离，BiCS 技术资料的历史归属与当前归属变化，以及对此后 NAND 资料采集来源的影响。
- **[[western-digital-与-sandisk-2025-年拆分事件|Western Digital 与 Sandisk 2025 年拆分事件]]** — Western Digital 于 2025-02-24 完成闪存业务拆分，后续 NAND/Flash 资料应追溯至 Sandisk，WD 历史页面仅作存档参考
- **[[ymtc-xtacking-架构|YMTC Xtacking 架构]]** — 长江存储自研的存储阵列与外围电路分离式 3D NAND 架构，及其对系统级性能与定制化 NAND 方案的影响

_30 pages | Generated 2026-08-16T06:06:40.481Z_
