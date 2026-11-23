---
okf_version: "0.1"
---

# Knowledge Bundle

## Concepts

* [多队列中断并行](/concepts/多队列中断并行.md) - MSI-X 核心优势，每个 I/O 队列独立中断向量绑定不同 CPU，实现并行处理和负载均衡，显著提升 NVMe 和网卡性能
* [高级错误报告 AER](/concepts/高级错误报告-aer.md) - 提供不可纠正和可纠正错误的详细检测、日志记录和报告机制，包括 DLP、POISON_TLP、ECRC 等错误类型
* [基址寄存器 (BAR)](/concepts/基址寄存器-bar.md) - 用于声明设备需要映射的内存或IO地址空间的寄存器，通过写入全1再回读的方式探测所需地址空间大小，支持32位和64位地址
* [可视化内容分类原则](/concepts/可视化内容分类原则.md) - 适合用图表达的内容（拓扑、协议栈、状态机）与适合用位域图或表格表达的内容（TLP header、配置空间、BAR）的分类指导
* [设备枚举与链路训练](/concepts/设备枚举与链路训练.md) - PCIe 设备的发现、配置过程以及 LTSSM 链路训练状态机在枚举中的作用
* [页面引用来源规则](/concepts/页面引用来源规则.md) - 引用只能指向 sources/ 中存在的文件，页码不确定时引用文件级来源并标注“不确定页码”的引用规范
* [中断亲和性与 NUMA 优化](/concepts/中断亲和性与-numa-优化.md) - 将中断绑定到特定 CPU 核心，结合 NUMA 拓扑优化内存访问局部性，减少跨节点访问延迟
* [ACK/NAK 协议](/concepts/acknak-协议.md) - 数据链路层的可靠传输协议，通过序列号、确认/否定应答和重试缓冲区确保TLP正确到达目的地
* [Ack/Nak Protocol](/concepts/acknak-protocol.md) - 确认/否认机制，通过序列号累计确认保证TLP可靠传输，丢失时触发重传
* [ASPM (主动状态电源管理)](/concepts/aspm-主动状态电源管理.md) - 利用 LTSSM 省电状态实现的节能机制，支持 L0s/L1/L2 等低功耗状态，可在延迟和功耗间权衡
* [ASPM (Active State Power Management)](/concepts/aspm-active-state-power-management.md) - PCIe 链路级电源管理机制，通过在空闲时自动切换到低功耗状态（L0s/L1/L1.2）来节省能源
* [ASPM 配置与控制](/concepts/aspm-配置与控制.md) - 通过 Link Capabilities 和 Link Control 寄存器配置 ASPM 支持级别和启用状态，Linux 下可通过 sysfs 和 setpci 工具控制
* [ASPM L0s 状态 (Standby)](/concepts/aspm-l0s-状态-standby.md) - 快速低功耗待机状态，关闭发送器保持接收器运行，退出延迟 200-500ns，功耗节省 10-20%
* [ASPM L1 状态 (Low Power)](/concepts/aspm-l1-状态-low-power.md) - 深度低功耗状态，双向握手进入，关闭链路时钟，退出延迟 2-4μs，功耗节省 60-90%
* [ASPM L1.2 子状态](/concepts/aspm-l12-子状态.md) - PCIe 3.1+ 最低功耗状态，关闭 PLL 和参考时钟，退出延迟 16-100μs，功耗节省 95-99%，需要 CLKREQ# 信号控制
* [BDF 地址分配方案](/concepts/bdf-地址分配方案.md) - SR-IOV 设备使用 Bus:Device.Function 地址格式，VF 通过 First VF Offset 和 VF Stride 计算得出
* [BDF 地址格式](/concepts/bdf-地址格式.md) - PCIe 设备的唯一标识格式 Bus:Device.Function，用于在系统中定位和访问特定设备
* [Byte Enable 字段](/concepts/byte-enable-字段.md) - TLP中用于指示数据负载中首尾DW有效字节的字段，包含First DW BE和Last DW BE两个4位字段
* [Class Code 寄存器](/concepts/class-code-寄存器.md) - 24位寄存器用于标识设备类型和功能，格式为Base Class(8位)+Sub-Class(8位)+Programming Interface(8位)，如NVMe控制器为0x010802
* [DLLP (Data Link Layer Packet)](/concepts/dllp-data-link-layer-packet.md) - 数据链路层专用控制包，用于链路管理、流控制和可靠性保证，固定8字节长度
* [DLLP (Data Link Layer Packet) 协议](/concepts/dllp-data-link-layer-packet-协议.md) - 数据链路层数据包，包含ACK/NAK确认机制、流量控制初始化和重试缓冲
* [DLLP CRC-16](/concepts/dllp-crc-16.md) - DLLP使用CRC-16-IBM多项式校验前6字节内容，CRC错误时丢弃DLLP（不重传）
* [DLLP Type Encoding](/concepts/dllp-type-encoding.md) - DLLP类型字段编码，定义Ack/Nak/FC/PM/Vendor等16种DLLP类型及其方向
* [DLLP vs TLP Comparison](/concepts/dllp-vs-tlp-comparison.md) - DLLP与TLP的对比：DLLP为8字节固定长度控制包，TLP为可变长度数据包，两者协议栈位置和用途不同
* [ECAM 机制](/concepts/ecam-机制.md) - 增强配置访问机制，通过内存映射IO方式访问PCIe配置空间，物理地址由ECAM基址、总线号、设备号、功能号和偏移计算得出
* [ECRC (端到端CRC校验)](/concepts/ecrc-端到端crc校验.md) - TLP的可选端到端CRC校验字段，用于数据完整性保护，由TD位指示是否存在
* [FEMU NVMe模拟器](/concepts/femu-nvme模拟器.md) - 基于QEMU的开源NVMe over PCIe模拟器实现,用于研究和学习PCIe协议
* [Flow Control (InitFC/UpdateFC)](/concepts/flow-control-initfcupdatefc.md) - 流控制机制，通过InitFC1/InitFC2初始化和UpdateFC运行时更新信用信息防止缓冲区溢出
* [FTS (Fast Training Sequence)](/concepts/fts-fast-training-sequence.md) - 从 L0s 快速恢复到 L0 所需的训练序列，用于接收器快速锁定时钟
* [LCRC 与 ECRC 错误检测](/concepts/lcrc-与-ecrc-错误检测.md) - 链路CRC保护单跳传输，端到端CRC保护整个通信路径，两者在协议栈不同层次协同工作
* [LTSSM (链路训练与状态状态机)](/concepts/ltssm-链路训练与状态状态机.md) - PCIe 物理层的核心状态机，管理链路从检测到正常通信的完整生命周期，包含 11 个主要状态
* [LTSSM 链路训练状态机](/concepts/ltssm-链路训练状态机.md) - 管理PCIe链路整个生命周期的状态机，包含Detect、Polling、Configuration、L0、Recovery等状态
* [LTSSM链路训练状态机](/concepts/ltssm链路训练状态机.md) - 物理层链路训练和状态状态机,负责检测、协商、训练链路以建立高速通信
* [Mermaid 解释性重绘规范](/concepts/mermaid-解释性重绘规范.md) - llmwiki 编译 PCIe 页面时使用 Mermaid 语法绘制协议层边界图的模板规则，要求明确标注为“解释性重绘”而非规范原图
* [MSI-X 中断机制](/concepts/msi-x-中断机制.md) - 通过内存写操作传递中断信号，支持最多 2048 个独立向量，比传统 INTx 中断更高效灵活
* [MSI-X Capability 结构](/concepts/msi-x-capability-结构.md) - 位于 PCIe 配置空间的能力结构，包含控制寄存器、Table 位置信息和 PBA 位置信息，Cap ID 为 0x11
* [MSI-X Message Address 格式](/concepts/msi-x-message-address-格式.md) - x86/x64 架构 MSI 地址格式，固定前缀 0xFEE00000，包含目标 CPU APIC ID (Bits 19-12) 和重定向提示位
* [MSI-X Message Data 格式](/concepts/msi-x-message-data-格式.md) - 中断数据格式，包含中断向量号 (Bits 7-0)、投递模式 (Bits 10-8) 和触发模式 (Bit 15)
* [MSI-X Table 结构](/concepts/msi-x-table-结构.md) - 存储在 BAR 空间中的中断配置表，每个 Entry 16 字节，包含 Message Address (64-bit)、Message Data (32-bit) 和 Vector Control
* [NVMe over PCIe 集成](/concepts/nvme-over-pcie-集成.md) - NVMe 存储协议通过 PCIe 传输的实现模式，包括 BAR 映射、MSI-X 中断配置和 DMA 数据传输
* [P2P 对等通信](/concepts/p2p-对等通信.md) - PCIe 设备之间无需经过 Root Complex 的直接通信方式，位于同一 Switch 下的设备可实现，需 ACS 支持
* [PBA (Pending Bit Array)](/concepts/pba-pending-bit-array.md) - 位图数组，用于记录被屏蔽的中断挂起状态，当中断被屏蔽时触发则设置对应位，解除屏蔽后由 OS 检查处理
* [PCI Express (PCIe) 技术](/concepts/pci-express-pcie-技术.md) - 一种高速串行计算机扩展总线标准，用于连接硬件设备，支持多通道传输和分层协议架构
* [PCIe 电源管理状态](/concepts/pcie-电源管理状态.md) - 链路状态(L0/L0s/L1/L2/L3)和设备状态(D0/D1/D2/D3)的电源管理机制与ASPM
* [PCIe 扩展能力](/concepts/pcie-扩展能力.md) - 位于配置空间0x100偏移之后的增强能力结构，包括AER错误报告、SR-IOV虚拟化、ARI备选路由ID等高级特性
* [PCIe 链路宽度协商](/concepts/pcie-链路宽度协商.md) - 多 Lane 设备间协商激活 Lane 数量的过程，支持 x1/x2/x4/x8/x16/x32 等宽度配置
* [PCIe 链路速度与编码](/concepts/pcie-链路速度与编码.md) - PCIe 各代际的速度 (2.5-32 GT/s) 及编码方案 (8b/10b/128b/130b)，影响有效带宽
* [PCIe 流控制机制](/concepts/pcie-流控制机制.md) - 基于信用的流控制机制，接收方向发送方通告可用缓冲区空间，防止发送方超出接收方处理能力
* [PCIe 流量控制机制](/concepts/pcie-流量控制机制.md) - 基于信用的流量控制，分为Posted、Non-Posted和Completion三类信用类型
* [PCIe 能力结构](/concepts/pcie-能力结构.md) - 可扩展的能力链表机制，允许设备声明支持的特性如 MSI、PCIe Capability、电源管理等
* [PCIe 能力链表](/concepts/pcie-能力链表.md) - 通过链表结构声明设备支持的可选功能（如MSI、电源管理、PCie能力），通过偏移0x34的能力指针遍历各能力结构
* [PCIe 配置空间](/concepts/pcie-配置空间.md) - PCIe设备的标准化配置寄存器区域，包含设备识别、地址映射、能力声明等关键配置，分为256字节标准区域和4096字节扩展区域
* [PCIe 配置空间与BARs](/concepts/pcie-配置空间与bars.md) - PCIe设备的标准配置区域，包含配置寄存器、基址寄存器(BAR)用于地址映射和资源分配
* [PCIe 三层协议架构](/concepts/pcie-三层协议架构.md) - PCIe协议采用事务层、数据链路层、物理层的三层分层架构，每层负责特定功能并通过标准化接口通信
* [PCIe 三层协议模型](/concepts/pcie-三层协议模型.md) - 事务层(TL)、数据链路层(DLL)、物理层(PHY)组成的分层通信架构
* [PCIe 三层协议栈](/concepts/pcie-三层协议栈.md) - PCIe 协议分为事务层、数据链路层和物理层的三层架构，各层职责分明实现通信功能
* [PCIe 三层协议栈模型](/concepts/pcie-三层协议栈模型.md) - PCIe 规范定义的事务层、数据链路层和物理层三层架构，以及层间的 TLP/DLLP 协议数据单元流转关系
* [PCIe 设备枚举过程](/concepts/pcie-设备枚举过程.md) - 系统启动时通过 BIOS/UEFI 自动发现 PCIe 设备的递归扫描过程，包括链路训练、配置读取、总线编号分配和 BAR 配置
* [PCIe 树形拓扑结构](/concepts/pcie-树形拓扑结构.md) - PCIe 采用的层次化树形架构，以 Root Complex 为根节点，通过 Switch 扩展连接多个 Endpoint 端点设备
* [PCIe 数据编码方案](/concepts/pcie-数据编码方案.md) - PCIe使用8b/10b编码(Gen1/2)和128b/130b编码(Gen3+)，后者效率更高达到98.5%
* [PCIe 拓扑结构](/concepts/pcie-拓扑结构.md) - 由Root Complex、Switch、Endpoint等组件构成的总线拓扑，包括总线、设备、功能层级结构
* [PCIe 虚拟通道](/concepts/pcie-虚拟通道.md) - 通过Traffic Class映射到Virtual Channel实现QoS，支持VC0-VC7多个独立缓冲区的流量分类
* [PCIe 训练序列 (TS1/TS2)](/concepts/pcie-训练序列-ts1ts2.md) - 链路初始化过程中交换的训练序列，用于建立位锁定、符号锁定以及协商链路参数
* [PCIe Endpoint 端点设备](/concepts/pcie-endpoint-端点设备.md) - PCIe 拓扑的叶子节点，代表实际功能设备，分为 Type 0 标准端点、Type 1 桥接端点和 RC 集成端点三类
* [PCIe Recovery 状态](/concepts/pcie-recovery-状态.md) - LTSSM 中用于从链路错误恢复或执行速度切换的状态，包含多个子状态完成重锁定和重新配置
* [PCIe Switch 带宽分配](/concepts/pcie-switch-带宽分配.md) - Switch 上行链路带宽与下行链路总带宽的关系，当上行带宽不足时会导致设备竞争带宽的性能瓶颈
* [PCIe Switch 交换机](/concepts/pcie-switch-交换机.md) - 扩展 PCIe 连接数量的桥接设备，具有上行端口和多个下行端口，支持透明和非透明两种工作模式
* [Physical Function (PF)](/concepts/physical-function-pf.md) - 完整的 PCIe 功能实体，包含 SR-IOV 扩展能力，负责管理和配置 VF，充当 VF 与物理硬件之间的桥梁
* [Power Management DLLP](/concepts/power-management-dllp.md) - 电源管理DLLP，包括PM_Enter_L1/L23和PM_Request_Ack用于协商低功耗状态
* [Root Complex 根复合体](/concepts/root-complex-根复合体.md) - PCIe 拓扑的根节点，通常集成在 CPU 或芯片组中，负责连接 CPU 和内存、生成配置事务、处理中断和错误
* [SR-IOV 单根 IO 虚拟化](/concepts/sr-iov-单根-io-虚拟化.md) - 允许单个物理设备通过 PF 和 VF 机制虚拟为多个独立虚拟功能，支持高效硬件虚拟化
* [SR-IOV 概述](/concepts/sr-iov-概述.md) - Single Root I/O Virtualization 是 PCIe 规范的硬件虚拟化扩展，允许单个物理设备虚拟为多个独立 Virtual Function 直接分配给虚拟机
* [SR-IOV 配置空间结构](/concepts/sr-iov-配置空间结构.md) - SR-IOV Extended Capability 位于 PCIe 扩展配置空间 (0x100+)，包含 Num VFs、VF Offset、VF Stride、VF BARs 等关键寄存器
* [SR-IOV 启用流程](/concepts/sr-iov-启用流程.md) - 检测 SR-IOV 支持、初始化 PF、配置 Num VFs、启用 VF Enable 位的完整流程，可通过 Linux sysfs 接口操作
* [TLP (事务层数据包)](/concepts/tlp-事务层数据包.md) - 事务层数据包，是PCIe中携带实际事务信息的基本单元，包含Header、Data Payload和可选的ECRC
* [TLP (Transaction Layer Packet) 格式与事务类型](/concepts/tlp-transaction-layer-packet-格式与事务类型.md) - 事务层数据包结构，支持Memory、I/O、Configuration、Message和Completion五类事务
* [TLP 处理流程](/concepts/tlp-处理流程.md) - TLP发送方和接收方的完整处理流程，包括流控制检查、Header构建、路由判断、Completion生成等步骤
* [TLP 类型详解](/concepts/tlp-类型详解.md) - PCIe定义的五种TLP类型：Memory Read/Write、IO Read/Write、Configuration Read/Write、Message、Completion，通过Fmt/Type组合标识
* [TLP 路由机制](/concepts/tlp-路由机制.md) - PCIe三种TLP路由方式：基于地址路由(Address-Based)、基于ID路由(ID-Based)、隐式路由(Implicit Routing)
* [TLP 事务层包](/concepts/tlp-事务层包.md) - PCIe 通信的基本单元，包含 Header、Data Payload、ECRC 和 LCRC，用于内存读写、IO、配置和消息传输
* [TLP Header 格式](/concepts/tlp-header-格式.md) - TLP头部的标准结构，分为3 DW(32位地址)和4 DW(64位地址)两种格式，包含Fmt、Type、Length、Requester ID等关键字段
* [Type 0 配置头](/concepts/type-0-配置头.md) - PCIe端点设备的标准化配置空间头结构，包含Vendor ID、Device ID、Command/Status、BARs、能力指针等关键字段的布局定义
* [VF BARs 配置](/concepts/vf-bars-配置.md) - VF 的 Base Address Registers 在 PF 的 SR-IOV 能力中配置，每个 VF 获得独立的 BAR 地址空间
* [VFIO 设备直通](/concepts/vfio-设备直通.md) - Virtual Function I/O 是现代 Linux 的设备直通框架，提供安全的用户空间设备访问，是 SR-IOV VF 分配的首选方法
* [Virtual Function (VF)](/concepts/virtual-function-vf.md) - 轻量级 PCIe 功能，专注于数据传输路径，共享 PF 资源，可直接分配给虚拟机使用
