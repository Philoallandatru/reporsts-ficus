# 概念索引

本索引按功能分类组织了 NVMe 规范的核心概念，帮助你快速定位需要了解的内容。

## 系统模型

理解 NVMe 系统的整体架构和组成部分：

- [规范族与适用范围](concepts/specification-family-and-scope.md) - NVMe 规范的组织结构
- [NVM 子系统](concepts/nvm-subsystem.md) - 系统边界与组成
- [控制器](concepts/controller.md) - 静态/动态模型；I/O、管理、发现三种类型
- [控制器虚拟化资源](concepts/controller-virtualization-resources.md) - 主/从控制器的虚拟队列和中断资源池
- [命名空间](concepts/namespace.md) - 存储抽象的基本单元
- [命名空间标识符](concepts/namespace-identifiers.md) - 有效性、分配、控制器挂载、广播、身份
- [命名空间访问模型](concepts/namespace-access-models.md) - 私有/共享/分散命名空间、多路径 I/O、非对称访问
- [命名空间拓扑与变更日志](concepts/namespace-topology-and-change-logs.md) - 分散参与者、可达性组/关联、变更追踪
- [命名空间管理生命周期](concepts/namespace-management-lifecycle.md) - 创建/删除分配、持久化控制器挂载
- [命名空间写保护](concepts/namespace-write-protection.md) - 保护状态、转换限制、缓存提交屏障
- [传输模型](concepts/transport-models.md) - 端口、网络接口、胶囊、SGL/数据放置
- [关联与命令生命周期](concepts/association-and-command-lifecycle.md) - 连接建立与命令执行
- [Fabrics 发现与认证](concepts/fabrics-discovery-and-authentication.md) - 过滤器协商、一致性快照、推荐、安全门控
- [Fabric 分区数据传输](concepts/fabric-zoning-data-transfer.md) - 查询、密钥/事务上下文、分片收发、错误共享

## 通信机制

命令和数据如何在主机与控制器间传输：

- [数据表示](concepts/data-representation.md) - 数据编码和字节序
- [传输模型](concepts/transport-models.md) - 基于内存和基于消息的传输
- [队列对](concepts/queue-pair.md) - 内存和消息模式的创建、流量控制、容量、删除
- [命令集](concepts/command-sets.md) - 队列路由与命名空间生命周期绑定
- [命令排序与仲裁](concepts/command-ordering-and-arbitration.md) - 融合操作、候选选择、优先级、未完成命令
- [命令生命周期](concepts/association-and-command-lifecycle.md) - 从提交到完成的全过程
- [公共命令格式](concepts/common-command-format.md) - 64 字节提交队列条目、CDW0、NSID、元数据和数据指针
- [数据指针布局](concepts/data-pointer-layouts.md) - PRP 条目/列表和 SGL 段边界
- [完成队列条目与状态](concepts/completion-queue-entry-and-status.md) - 关联、消费、状态族、重试提示、阶段标签
- [特性值与作用域](concepts/feature-values-and-scope.md) - 默认/当前/保存值、重置恢复、作用域选择器
- [通用控制器特性](concepts/common-controller-features.md) - 仲裁、电源、温度阈值、滞后、易失性缓存
- [安全协议交换](concepts/security-protocol-exchange.md) - Security Send/Receive 信封、发现、NVMe RPMB 选择
- [身份、名称与列表格式](concepts/identity-name-and-list-formats.md) - EUI64/NGUID/UUID、NQN、有序列表、UTF-8 处理
- [主机元数据与管理地址](concepts/host-metadata-and-management-addresses.md) - 代理 URI、类型化的控制器/命名空间注解
- [主机内存缓冲区](concepts/host-memory-buffer.md) - 主机内存所有权、描述符列表、禁用屏障、电源状态限制
- [识别命令模型](concepts/identify-command-model.md) - CNS 选择的 4 KiB 结构、依赖门控的能力、运行时限制
- [电源状态描述符](concepts/power-state-descriptors.md) - 操作状态、延迟、相对性能、功耗、掉电时序
- 胶囊与胶囊内数据（参见[传输模型](concepts/transport-models.md)）

## 存储组织

底层存储资源如何组织和管理：

- [存储资源层级](concepts/storage-resource-hierarchy.md) - NVM 集与回收组的组织方式
- [NVM 集与持久组](concepts/nvm-sets-and-endurance-groups.md) - 容量和耐久性管理单元
- [NVM 容量模型](concepts/nvm-capacity-model.md) - 容量分配、介质单元、通道、组织权衡
- [灵活数据放置配置](concepts/flexible-data-placement-configurations.md) - 配置目录、放置标识符拆分、运行时使用、统计、事件
- [域与分区](concepts/domains-and-divisions.md) - 故障边界、标识符、ANA/预留恢复
- [导出与底层 NVM 资源](concepts/exported-and-underlying-resources.md) - 目录、创建/清除、命名空间关联、删除门控
- 域（参见[域与分区](concepts/domains-and-divisions.md)）
- 持久组
- NVM 集
- 回收组
- 回收单元
- 介质单元

## 控制平面

控制器配置、管理和监控：

- [控制器属性](concepts/controller-properties.md) - 访问约定、能力/配置握手、版本、中断屏蔽
- [控制器内存窗口](concepts/controller-memory-windows.md) - CMB 与 PMR 地址、能力、就绪状态、健康
- [引导分区](concepts/boot-partitions.md) - 引导镜像存储
- [控制器支持需求](concepts/controller-support-requirements.md) - 按控制器类型划分的命令、日志页、特性
- [管理命令模型](concepts/admin-command-model.md) - 操作码分类、传输划分、Format/Sanitize 门控
- [命令中止语义](concepts/command-abort-semantics.md) - 立即/延迟中止、效果屏障
- [公共 I/O 控制命令](concepts/common-io-control-commands.md) - 取消选择、刷新持久化、I/O 管理交换
- [异步事件报告](concepts/asynchronous-event-reporting.md) - AER 生命周期、屏蔽、日志清除、事件族
- [容量管理操作](concepts/capacity-management-operations.md) - 固定/可变配置、持久组与 NVM 集生命周期
- [控制器数据队列](concepts/controller-data-queues.md) - 主机内存队列生命周期、用户数据迁移队列
- [设备自检](concepts/device-self-test.md) - 作用域、启动/中止转换、日志交互
- [指令交换](concepts/directive-exchange.md) - 共享的 Directive Send/Receive 信封
- [日志页检索](concepts/log-page-retrieval.md) - LID 选择、偏移量、作用域、支持发现
- [预留通知日志](concepts/reservation-notification-log.md) - 破坏性读取队列、序号间隙、通知类型、命名空间
- [命名空间预留生命周期](concepts/namespace-reservation-lifecycle.md) - 注册、获取、抢占、释放、持久化、状态报告
- [清理操作状态](concepts/sanitize-operation-status.md) - 持久化进度、结果、时间估算、状态详情、擦除证据
- [清理操作生命周期](concepts/sanitize-operation-lifecycle.md) - 后台擦除启动、介质验证、选项门控、串行化
- [资源与管理清单日志](concepts/resource-and-management-inventory-logs.md) - 旋转介质生命周期数据、管理 URI
- [错误与健康日志](concepts/error-and-health-logs.md) - 最近错误、命令关联、SMART 警告与状态
- [命令效果与支持](concepts/command-effects-and-support.md) - 操作码支持、影响作用域、串行化、能力变更
- [命令与特性锁定](concepts/command-and-feature-lockdown.md) - 按标识符命名空间与提交路径划分的可锁定与禁止操作
- [控制器迁移](concepts/controller-migration.md) - 状态格式选择、快照一致性、挂起/恢复/恢复生命周期
- [迁移变更追踪](concepts/migration-change-tracking.md) - UDMQ 日志、破坏性主机内存变更范围报告
- [遥测捕获日志](concepts/telemetry-capture-logs.md) - 主机/控制器捕获、块区域、保留、可用性、生成
- [可预测延迟模式](concepts/predictable-latency-mode.md) - NVM 集窗口、预算、估算、事件聚合
- [持久事件日志](concepts/persistent-event-log.md) - 持久化历史、冻结报告上下文、生成验证、重置与硬件错误证据
- Fabrics 命令集
- I/O 命令集
- [特性值与作用域](concepts/feature-values-and-scope.md)
- [日志页检索](concepts/log-page-retrieval.md)
- [异步事件报告](concepts/asynchronous-event-reporting.md)
- [Fabrics 发现与认证](concepts/fabrics-discovery-and-authentication.md)
- [识别命令模型](concepts/identify-command-model.md)

## 生命周期与弹性

系统初始化、错误恢复和电源管理：

- [控制器启用、关机与重置](concepts/controller-enable-shutdown-reset.md) - 控制器/子系统关机、重置作用域
- [控制器初始化](concepts/controller-initialization.md) - 基于内存和 Fabrics 的引导序列
- [控制器就绪模式与超时](concepts/controller-ready-modes.md) - 独立于介质的就绪、截止时间、超时失败
- [保活机制](concepts/keep-alive.md) - 配置、激活、命令/流量看门狗模式、超时清理
- [固件更新生命周期](concepts/firmware-update-lifecycle.md) - 下载、提交、激活、重置、串行化
- [格式化 NVM 生命周期](concepts/format-nvm-lifecycle.md) - 格式化作用域、安全擦除、并发、拒绝
- 电源状态
- [清理操作状态](concepts/sanitize-operation-status.md)
- [错误与健康日志](concepts/error-and-health-logs.md)

## 补充归档索引（Governance Auto-Synced）

- [通信丢失与命令重试](concepts/communication-loss-and-command-retry.md) — 在 NVMe 系统中，主机（Host）与控制器（Controller）之间的通信链路可能会意外中断。当通信丢失发生时，主机面临一个关键问题：**那些已经提交但尚未收到完成响应的命令（Outstanding Commands）究竟执行了没有？**
- [分散命名空间生命周期（Dispersed Namespace Lifecycle）](concepts/dispersed-namespace-lifecycle.md) — 分散命名空间（Dispersed Namespace）是一种特殊的逻辑命名空间（Logical Namespace），允许主机（Host）通过两个或多个 NVM 子系统（NVM Subsystem）中的控制器（Controller）同时访问同一个命名空间。这一特性支持在线迁移和数据复制，而无需在 Base 规范中引入跨子系统的分散机制。
- [Fabric 分区模型（Fabric Zoning Model）](concepts/fabric-zoning-model.md) — Fabric Zoning（Fabric 分区）是由 CDC（Centralized Discovery Controller，中央化发现控制器）维护的集中式访问控制模型。它的主要作用是控制主机（Host）能够发现哪些 NVM 子系统端口（NVM Subsystem Ports）。
- [Key Per I/O（基于密钥标签的 I/O 加密）](concepts/key-per-io.md) — Key Per I/O 是 NVMe 2.1 规范引入的一项加密功能，它允许主机（Host）在执行命名空间（Namespace）的读写操作时，通过指定一个密钥标签（Key Tag）来选择使用哪个加密密钥。这个功能的核心特点是：
- [断电信号机制（Power Loss Signaling）](concepts/power-loss-signaling.md) — 断电信号机制（Power Loss Signaling，简称 PLS）是 NVMe 规范中一项重要的电源管理功能，作用范围覆盖整个 Domain（域）。该机制基于 PCIe 的能力实现，允许系统在电源即将断开时提前通知控制器（Controller），从而为数据保护争取宝贵时间。
- [重放保护内存块（Replay Protected Memory Block, RPMB）](concepts/replay-protected-memory-block.md) — 重放保护内存块（RPMB）是控制器可访问的非命名空间存储区域，它通过为每个目标（target）配置独立的密钥、随机数回显（nonce echo）、单调递增的写计数器以及消息认证码（MAC）来保护已认证的读写操作，防止篡改和重放攻击。
- [ANA非对称命名空间访问](wiki/concepts/ana非对称命名空间访问.md) — ANA 将命名空间按访问特性划分为不同的 **ANA Group（ANA 组）**。属于同一组的成员在同一个 Domain 内共同变迁——当组的访问状态发生变化时，所有成员同步更新。^[nvme-architecture-map.md:146]
- [Command Queue Mechanism](wiki/concepts/command-queue-mechanism.md) — In NVMe, the **Command Queue Mechanism** is the fundamental architecture by which a host submits I/O commands to a [[controller|Controller]] and receives asynchronous completion...
- [ControllerMemoryWindow控制器内存窗口](wiki/concepts/controllermemorywindow控制器内存窗口.md) — [[controller|Controller]] Memory Window（控制器内存窗口，简称 CMW）是 NVMe 规范中定义的一组内存寻址机制，供 memory-based 控制器向 host 暴露可用于 I/O 操作的内存区域。^[nvme-architecture-map.md:30]^
- [Controller类型与分类](wiki/concepts/controller类型与分类.md) — 在 NVMe 架构中，**Controller** 是面向 [[NVM Subsystem]] 的 host 接口，承担着命令收发、队列管理以及存储资源与主机之间的协调工作。^[nvme-architecture-map.md:18]
- [DH-HMAC-CHAP Authentication](wiki/concepts/dh-hmac-chap-authentication.md) — DH-HMAC-CHAP（Diffie-Hellman Hash-based Message Authentication Code Challenge-Handshake Authentication Protocol）是 [[nvme-over-fabrics|NVMe over Fabrics]] 协议中用于在 host 与 [[controll...
- [Fabric Zoning](wiki/concepts/fabric-zoning.md) — Fabric Zoning 是 [[nvme-over-fabrics|NVMe over Fabrics]] (NVMe-oF) 架构中的一种访问控制机制，用于在共享的存储 fabric 上隔离不同租户或应用组之间的通信。^[nvme-context.md:695-696]
- [Fabrics发现与认证](wiki/concepts/fabrics发现与认证.md) — Fabrics 发现与认证（Fabrics Discovery and Authentication）是 [[nvme-over-fabrics|NVMe over Fabrics]] 协议栈中两个相互独立但协同工作的安全入口，共同确保远端子系统访问的可控性与身份可信性。
- [Fabrics队列生命周期](wiki/concepts/fabrics队列生命周期.md) — Fabrics（NVMe over Fabrics）采用基于消息的传输模型，其队列生命周期与基于内存的 PCIe 模型有显著区别。在 Fabrics 模式下，每个 I/O 提交队列必须与一个 I/O 完成队列一对一映射，不支持多对一的 I/O 队列映射，这与基于内存的传输模型不同。^[nvme-queue-pair.md:31-34]
- [FabricZoningModel网络分域模型](wiki/concepts/fabriczoningmodel网络分域模型.md) — [[fabric-zoning|Fabric Zoning]] Model 是 [[nvme-over-fabrics|NVMe over Fabrics]] 架构中用于在 IP 网络上实现访问控制的机制。该模型通过在 NVM 子系统和 Host 之间建立逻辑分区，限制特定 Host 只能访问被授权的存储资源，从而实现多租户环境下的安全隔离。
- [FlexibleDataPlacement灵活数据放置](wiki/concepts/flexibledataplacement灵活数据放置.md) — Flexible Data Placement（FDP）是 NVMe 规范中一项用于控制数据写入位置的高级功能。该特性在已启用的 Endurance Group 内提供了一种替代 NVM Set 的 host 驱动数据放置机制，使 host 能够更细粒度地管理写入数据的物理位置。^[nvme-architecture-map.md:60]
- [I/O 队列创建顺序](wiki/concepts/io-队列创建顺序.md) — 在 NVMe 控制器初始化流程中，I/O 队列的创建需要遵循特定的顺序，以确保命令能正确提交和完成处理。
- [Mermaid 流程图模板](wiki/concepts/mermaid-流程图模板.md) — Mermaid 流程图模板是一套用于在 Wiki 页面中可视化复杂系统关系的标准化图表规范。模板采用 `flowchart LR`（从左到右布局），以简洁的结构呈现核心组件及其交互关系 ^[visualization-guidelines.md:7-14]。
- [Namespace and Namespace Identifier](wiki/concepts/namespace-and-namespace-identifier.md) — 在 NVMe Base 规范中，**Namespace（命名空间）** 是 NVMe 存储系统中的核心抽象概念，代表由一个或多个控制器以逻辑块（logical-block）存储抽象形式呈现的一块已格式化非易失性存储器（NVM）。^[nvme-context.md:42-43]
- [NamespaceReservation命名空间预留](wiki/concepts/namespacereservation命名空间预留.md) — Namespace Reservation（命名空间预留）是 NVMe 规范中一种用于在多主机环境下控制共享 namespace 访问权限的机制。它将访问权限绑定到 **Host Identifier** 而非 [[controller|Controller]] 路径，在命令开始处理的那一刻固化冲突决策。 ^[nvme-architecture-map...
- [NVM 子系统端口](wiki/concepts/nvm-子系统端口.md) — NVM 子系统端口（NVM Subsystem Port）是 NVMe 传输层架构中的一个核心概念，定义为主机与 NVM 子系统之间的协议接口。
- [NVMe Fabrics](wiki/concepts/nvme-fabrics.md) — NVMe Fabrics 是 NVMe 规范中定义的远程直接内存访问（RDMA）或基于网络的传输架构，它将 NVMe 的高性能命令集扩展到网络互联环境中。与传统的 PCIe 本地连接不同，Fabrics 通过消息传递模型实现主机与存储子系统之间的通信，使分布式存储资源能够像本地 NVMe 设备一样被访问。 ^[nvme-controller.md:38]
- [NVMe-oF Fabrics 初始化](wiki/concepts/nvme-of-fabrics-初始化.md) — NVMe-oF Fabrics 初始化是一个基于消息传输的启动过程，用于在 [[nvme-over-fabrics|NVMe over Fabrics]] 网络中建立主机与控制器之间的连接并完成必要的配置。与基于内存的 PCIe 传输不同，Fabrics 初始化通过消息队列和远程过程调用实现控制器的发现与配置。 ^[nvme-controller-in...
- [NVMe over Fabrics](wiki/concepts/nvme-over-fabrics.md) — NVMe over Fabrics（简称 NVMe-oF）是一种将 NVMe 协议扩展到网络存储场景的传输架构。它基于**消息传输模型**（Message-Based Transport），通过 Fabrics（网络结构）实现主机与 NVM 子系统之间的远程通信。与传统的基于内存的传输（如 PCIe）不同，NVMe over Fabrics 使用封装的...
- [NVMe 仲裁机制](wiki/concepts/nvme-仲裁机制.md) — NVMe 仲裁机制（Arbitration Mechanism）决定了控制器如何从多个提交队列中选择命令进行处理。NVMe 协议支持多种仲裁策略，以满足不同的性能和优先级需求。控制器首先从各个提交队列中挑选候选命令，然后通过仲裁器根据优先级选择一个队列进行处理，同时通过仲裁突发（Arbitration Burst）限制单次从同一队列启动的命令数量。 ^...
- [NVMe 传输架构分层](wiki/concepts/nvme-传输架构分层.md) — NVMe 采用清晰的分层架构设计，将传输无关的NVMe核心协议与具体的传输实现分离。这种设计确保了 NVMe 能够在多种物理连接和传输协议上保持统一的接口和行为规范。NVMe 规范定义了主机（Host）与 NVM 子系统（NVM Subsystem）之间的两种基本通信模型：基于内存的传输（Memory-Based Transport）和基于消息的传输（...
- [NVMe 传输模型](wiki/concepts/nvme-传输模型.md) — NVMe 规范定义了主机（Host）与 NVM 子系统（NVM Subsystem）之间的两种基本通信模型：**基于内存的传输**（Memory-Based Transport）和**基于消息的传输**（Message-Based Transport）。传输层（Transport Layer）负责决定命令、响应和数据如何在主机和存储子系统之间传递。这两...
- [NVMe 传输绑定 (Transport Binding)](wiki/concepts/nvme-传输绑定-transport-binding.md) — 传输绑定（Transport Binding）是 NVMe 架构中连接NVMe 主机与 [[NVMe 控制器]] 的通信层协议。它定义了命令和数据如何在主机软件与控制器之间传输，是 NVMe 实现多种物理介质和网络拓扑的基础。
- [NVMe 命令排序与独立性](wiki/concepts/nvme-命令排序与独立性.md) — NVMe 协议在处理命令时采用了一种相对灵活的设计理念：**命令之间通常被视为相互独立的**。这意味着提交队列（Submission Queue, SQ）中命令的排列顺序**不会强制决定**它们的处理顺序、完成顺序或在存储介质上的执行顺序。 ^[nvme-command-ordering.md:5]
- [NVMe 命令队列机制](wiki/concepts/nvme-命令队列机制.md) — NVMe（Non-Volatile Memory Express）命令队列机制是 NVMe 协议中用于处理主机（Host）与控制器（Controller）之间 I/O 请求与响应的核心架构NVMe 架构。该机制采用**提交队列（Submission Queue, SQ）** 和**完成队列（Completion Queue, CQ）** 配对工作的模式...
- [NVMe 命名空间 (Namespace)](wiki/concepts/nvme-命名空间-namespace.md) — NVMe 命名空间（Namespace，简称 NS）是 NVMe 协议中用于组织和管理存储逻辑块地址（LBA）空间的抽象概念。每个命名空间代表主机可以访问的一片独立存储区域，类似于传统存储协议中的"逻辑单元号（LUN）"或"卷"。一个 NVMe 控制器可以管理一个或多个命名空间，这为存储资源的灵活划分提供了基础架构。
- [NVMe 图文规范](wiki/concepts/nvme-图文规范.md) — 本文档定义了 NVMe 相关页面在图文呈现方面的规范要求，旨在确保页面内容准确、易读且引用规范。
- [NVMe 控制器](wiki/concepts/nvme-控制器.md) — NVMe 控制器是主机进入 NVM 子系统的“服务窗口”。它从主机提交的队列中取命令，协调数据访问，再把结果放入完成队列；主机不会直接操作底层闪存。^[nvme-controller.md:3]
- [NVMe 控制器架构](wiki/concepts/nvme-控制器架构.md) — NVMe（Non-Volatile Memory Express）控制器架构是 NVMe 协议的核心组成部分，负责在主机软件与存储介质之间协调命令执行和数据传输。该架构定义了控制器与主机软件、提交队列（Submission Queue）、完成队列（Completion Queue）、命名空间（Namespace）以及传输层（Transport）之间的交...
- [NVMe 控制器生命周期](wiki/concepts/nvme-控制器生命周期.md) — NVMe 控制器（Controller）是 NVMe 主机软件与存储介质之间的核心通信桥梁，负责管理命令的提交与完成、命名空间资源分配以及传输层绑定等关键功能。控制器生命周期涵盖从初始化到关闭/重置的完整过程，是 NVMe 规范中的核心概念。
- [NVMe 规范来源引用规范](wiki/concepts/nvme-规范来源引用规范.md) — 本文档定义了 llmwiki 编译 NVMe 相关页面时必须遵守的**来源引用规范**，涵盖视觉呈现、引用规则及质量要求。
- [PCIe 控制器启动序列](wiki/concepts/pcie-控制器启动序列.md) — PCIe 控制器启动序列是 NVMe 控制器初始化流程中针对 PCIe 传输类型的特定实现，属于一种依赖于传输类型的引导过程（transport-specific bootstrap process）。该序列的核心目标是在主机与 NVMe 设备之间建立通信基础，使控制器从禁用状态过渡到就绪状态，从而支持后续的存储操作。^[nvme-controller...
- [Static and Dynamic Controller Models](wiki/concepts/static-and-dynamic-controller-models.md) — 静态控制器模型（Static [[controller|Controller]] Model）与动态控制器模型（Dynamic [[controller|Controller]] Model）是 NVMe 规范中定义的两种全子系统范围的控制器分配模型，它们在控制器的生命周期管理、身份保留和行为特性方面存在本质差异。 ^[nvme-context.md:...
- [主从控制器](wiki/concepts/主从控制器.md) — 在 NVMe 规范中，**主从控制器**（Primary [[controller|Controller]] / Subordinate Controller）是控制器在**虚拟化资源管理**维度上的分类。这一维度回答的核心问题是：虚拟化资源如何分配和管理。
- [加权轮询与紧急优先级仲裁](wiki/concepts/加权轮询与紧急优先级仲裁.md) — 在 NVMe 存储系统中，**仲裁机制**（Arbitration Mechanism）决定了控制器如何从多个提交队列（Submission Queue, SQ）中选择命令进行处理。当多个队列同时有待处理的命令时，仲裁机制需要决定哪个队列的命令优先获得处理机会。
- [发现控制器](wiki/concepts/发现控制器.md) — 发现控制器（Discovery Controller）是 NVMe-oF 架构中的一种特殊控制器，专门用于发现可用的存储目标。它是 NVMe 存储网络化架构中的核心组件，帮助主机动态发现和连接到可用的 NVMe 目标设备。^[nvme-controller-initialization.md:93-94]
- [命令处理无序性](wiki/concepts/命令处理无序性.md) — 命令处理无序性（Out-of-Order Command Processing）是 NVMe 规范中的一项核心特性，指控制器在处理来自提交队列的命令时，不保证按照主机的提交顺序完成这些命令。^[nvme-queue-pair.md:62-71]^
- [命令集选择](wiki/concepts/命令集选择.md) — 命令集选择涉及两个关键寄存器的交互：
- [命名空间](wiki/concepts/命名空间.md) — 命名空间是 NVMe 子系统中主机实际进行数据读写操作的逻辑存储对象。控制器负责命令处理和队列协作，而命名空间才是承载用户数据的实体。^[nvme-controller.md:8-13]
- [基于内存的传输](wiki/concepts/基于内存的传输.md) — 在基于内存的传输模型中，主机和控制器共享同一内存空间。控制器能够直接访问主机内存中的提交队列（SQ）、完成队列（CQ）以及数据缓冲区。整个通信过程通过内存映射 I/O（MMIO）和直接内存访问（DMA）机制完成。^[nvme-transport-models.md:15]
- [基于消息的传输](wiki/concepts/基于消息的传输.md) — 基于消息的传输（Message-Based Transport）是 NVMe 规范定义的两种基本通信模型之一。在这种模型中，主机和控制器通过网络结构（Fabric）交换封装的消息，命令和响应被打包成**胶囊**（Capsule），通过网络协议传递。^[nvme-transport-models.md:27-31]
- [异步事件通知](wiki/concepts/异步事件通知.md) — 异步事件通知（Asynchronous Event Notification, AEN）是 NVMe 规范中的一种机制，允许控制器主动向主机（Host）上报重要事件，而无需主机主动轮询。
- [影子门铃与事件索引缓冲区](wiki/concepts/影子门铃与事件索引缓冲区.md) — 影子门铃与事件索引缓冲区是 NVMe 规范为仿真（emulated）控制器提供的一种优化机制，通过在主机内存中维护队列门铃的镜像副本，减少主机与控制器之间的寄存器访问开销。^[nvme-queue-pair.md:302-303]
- [循环缓冲区状态判断](wiki/concepts/循环缓冲区状态判断.md) — 在 NVMe 协议中，提交队列（Submission Queue, SQ）和完成队列（Completion Queue, CQ）均采用**循环缓冲区**（Circular Buffer）作为底层数据结构。正确判断循环缓冲区的状态，是驱动软件实现可靠队列操作的前提。
- [控制器初始化](wiki/concepts/控制器初始化.md) — 控制器初始化（Controller Initialization）是一个依赖于传输类型的启动过程（transport-specific bootstrap process）。^[nvme-controller-initialization.md:3]
- [控制器四维分类模型](wiki/concepts/控制器四维分类模型.md) — 控制器四维分类模型是 NVMe 规范中用于系统化描述 NVMe 控制器（Controller）属性的框架。该模型认为，描述一个控制器的完整特性需要从四个独立维度进行刻画——传输模型、分配模型、功能角色和资源角色。这四个维度彼此正交，任意控制器的特征都可以用这四个维度的取值组合来唯一确定。
- [控制器类型](wiki/concepts/控制器类型.md) — 在 NVMe 规范中，控制器是主机访问 NVM 子系统 的“服务窗口”。控制器并非单一概念，而是可以从多个维度进行分类，不同类型的控制器承担不同的职责。
- [提交队列与完成队列](wiki/concepts/提交队列与完成队列.md) — 提交队列（Submission Queue，SQ）和完成队列（Completion Queue，CQ）是 NVMe 协议中主机与控制器之间进行命令通信的核心机制。控制器作为主机进入 NVM 子系统的"服务窗口"，从提交队列中取命令，协调数据访问，再将结果放入完成队列；主机不会直接操作底层闪存。^[nvme-controller.md:3]
- [提交队列与完成队列映射](wiki/concepts/提交队列与完成队列映射.md) — 提交队列（Submission Queue，SQ）与完成队列（Completion Queue，CQ）之间的映射关系是 NVMe 协议的核心设计之一，它决定了命令提交与完成通知之间的关联方式。映射规则因传输模型的不同而存在显著差异。^[nvme-queue-pair.md:3, nvme-queue-pair.md:24-35]
- [未完成命令（Outstanding Commands）](wiki/concepts/未完成命令outstanding-commands.md) — 在 NVMe 协议中，**未完成命令**（Outstanding Command）是指从主机提交给控制器开始，直到命令处理终止并被证明为止，仍处于等待完成状态的命令。理解未完成命令的边界定义对于资源管理、错误恢复和系统关机流程都至关重要。^[nvme-command-ordering.md:160-163]
- [管理队列配置](wiki/concepts/管理队列配置.md) — 管理队列（Admin Queue，简称 AQ）是 NVMe 控制器中用于承载管理命令的专用队列，是主机与控制器之间建立通信的初始通道。所有管理操作——包括控制器识别、命名空间枚举、I/O 队列创建以及功能配置——均通过管理队列完成。
- [胶囊机制](wiki/concepts/胶囊机制.md) — 在 [[nvme-over-fabrics|NVMe over Fabrics]] 协议中，**胶囊（Capsule）** 是主机与 NVM 子系统之间信息交换的基本单元。^[nvme-transport-models.md:95]
- [融合操作（Fused Operation）](wiki/concepts/融合操作fused-operation.md) — 融合操作为 I/O 命令提供了原子性保证，是 NVMe 协议处理命令依赖关系的两种特殊机制之一，另一种是由特定 I/O 命令集（I/O Command Set）规范定义的命令集特定原子操作。^[nvme-command-ordering.md:7-10]
- [队列对](wiki/concepts/队列对.md) — 队列对是 NVMe 协议中的核心通信机制，由两部分组成：主机用于提交命令的**提交队列（Submission Queue）**和控制器用于发布完成通知的**完成队列（Completion Queue）**。管理队列负责管理和控制操作；I/O 队列承载 I/O 命令集的命令。 ^[nvme-queue-pair.md:3]
- [队列级别重置](wiki/concepts/队列级别重置.md) — 队列级别重置是一种通过删除并重建队列来恢复队列正常状态的机制。该操作不同于连续的线上维护，而是对问题队列进行完整的重建流程。 ^[nvme-queue-pair.md:258-259]
- [静态与动态控制器](wiki/concepts/静态与动态控制器.md) — 在 NVMe 规范中，控制器（Controller）按照**分配模型（Allocation Model）**可分为**静态控制器（Static Controller）**和**动态控制器（Dynamic Controller）**两类。这一维度描述的是控制器何时被创建、连接断开后状态如何保留。
