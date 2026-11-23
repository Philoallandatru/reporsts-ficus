# NVMe Base 2.1 知识上下文

源自 NVM Express Base Specification Revision 2.1 的概念 wiki 的权威词汇表。

## 规范模型（Specification model）

**Base Specification**:
与 transport 无关的控制器协议及通用 I/O Command Set 基础。

**Transport Binding**:
将 NVMe 协议行为与控制器属性映射到某一具体 transport 的方式。

**0's-based value**:
一种编码计数方式，其中 `0h` 表示 1，而 0 本身无法表示。

## 系统模型（System model）

**NVM Subsystem**:
包含 controllers、ports、namespaces 及其底层 NVM 资源的边界。

**Controller**:
面向 host 的 NVM 子系统接口，暴露属性、处理命令、访问 namespaces。

**Static Controller Model**:
一种全子系统范围的控制器分配模型，其控制器身份与已保存状态在 Controller Level Reset 后保留；对 Fabrics 而言还可能在跨 association 时保持。

**Dynamic Controller Model**:
一种全子系统范围的控制器分配模型，控制器按需分配，不保留任何先前 association 的状态。

**I/O Controller**:
通过一个或多个 I/O Command Set 访问用户数据、也可提供管理能力的控制器。

**Discovery Controller**:
仅返回发现信息、不具备 I/O queue、也不访问非易失存储的控制器。

**Administrative Controller**:
仅有管理能力、不具备 I/O queue、无 namespace 挂接、无用户数据访问的控制器。

**Asymmetric Controller Behavior**:
随子系统配置或访问该 namespace 所用控制器不同而变化的命名空间访问特性。

**Namespace**:
被一个或多个控制器以 logical-block 存储抽象形式呈现的、已格式化的一块 NVM。

**Namespace Identifier (NSID)**:
用于 namespace 的控制器命令句柄，其分配作用域为子系统，其 active/inactive 状态相对于各控制器。

_Avoid_: Namespace identity when durable identity is intended

**Active NSID**:
一个已分配的 NSID，其对应的 namespace 已挂接到执行此判断的控制器。

**Allocated NSID**:
一个有效的 NSID，指向 NVM 子系统中已存在的 namespace。

**Association**:
一个 host 与一个 controller 之间排他的关系，涵盖该控制器的 Admin Queue 及全部 I/O Queue。

_Avoid_: Connection when referring to the controller-level relationship

**Candidate Command**:
已被传入控制器、并被判定准备好处理的一条已提交命令。

**Command Arbitration**:
选择从哪一个 Submission Queue 开始处理下一条 candidate command 或 fused pair 的机制。

**Arbitration Burst**:
控制器从被选中的 Submission Queue 启动命令处理的最大连续条数，之后再次进行仲裁。

**Fused Operation**:
在同一 Submission Queue 中相邻提交的两条命令组成的一个可选操作，作为整体单元按序执行。

**Outstanding Command**:
host 既未收到完成、也未获得协议定义的"控制器不可能进一步处理"证据的、已提交的命令。

**Common Command Format**:
Admin 与 I/O 命令共用的 64 字节 Submission Queue Entry，包含公共命令身份、namespace、metadata、data-pointer 及命令特定字段。

**Completion Queue Entry (CQE)**:
由控制器产出的记录，将已完成的命令关联起来，报告已消费的 Submission Queue 位置，并携带命令特定结果与 Status。

**Completion Status**:
CQE 的结果编码，由 retry/log 提示加上 Status Code Type 与 Status Code 组成。

**Phase Tag**:
基于内存的 Completion Queue 槽位代次位（generation bit），每次控制器投递位置绕回队列时其期望投递值翻转。

**Physical Region Page (PRP) Entry**:
一个 64 位指针，描述一个物理内存页；命令允许且 `CC.MPS` 也允许时，可在命令第一条 entry 上设置偏移。

**PRP List**:
一个紧凑、按页对齐的 PRP entry 数组，其最后一条 entry 可链接到下一页 entry。

**Scatter Gather List (SGL)**:
一组带类型、带长度的描述符，按 qword 对齐组织为段（segment），用于描述命令数据缓冲区。

**SGL Segment**:
一段 qword 对齐的连续 16 字节 SGL 描述符组成的段，其末条描述符可链接到下一段或最后一段。

**Bit Bucket Descriptor**:
一个 SGL 描述符，在描述目标缓冲区时消耗但不放置源数据的一部分。

**Feature Value**:
以 Feature Identifier 寻址的控制器运行参数，包含 current 值、不可变的 default 值，以及可选的 saved 值。

**Feature Scope**:
Feature 值所作用的边界，可以是 controller、namespace、subsystem、Domain、Endurance Group 或 NVM Set。

**NVMe Qualified Name (NQN)**:
host 或 NVM 子系统的永久、全局唯一、以 `\0` 结尾的 UTF-8 名称，使用 domain-authority 或 UUID 形式编码。

**Namespace Global Identifier**:
用 EUI64、NGUID 或 UUID 表示的命名空间持久化身份，与作为命令句柄的 NSID 相区分。

**Controller Global Identity**:
由全局唯一的 NVM subsystem identifier 与该子系统内唯一的 controller identifier 共同组成的复合标识。

**Protocol UTF-8 String**:
由 NVMe 承载的 UTF-8 字节串，接收时不做 Unicode normalization 或 locale 相关的处理。

**Command Retry Delay (CRD)**:
CQE 中一个建议性的重试选择子，取值为"立即重试"或 Identify Controller 中的三个延时值之一，仅在允许重试且启用 Advanced Command Retry 时生效。

**PRP or SGL for Data Transfer (PSDT)**:
Command Dword 0 的选择子，决定通用命令的 metadata 与 data pointers 走 PRP 还是 SGL 形式。

**Keep Alive Timeout Time (KATT)**:
通过 `KATO` 配置的、作用于每个控制器的看门狗有效间隔，受 transport 限制与控制器 `KAS` 粒度约束。

**Command Based Keep Alive**:
一种看门狗模式，控制器把"成功处理 Keep Alive 命令"视为其存活证据。

**Traffic Based Keep Alive**:
一种看门狗模式，控制器把取走的 Admin 或 I/O 命令视为存活证据，让普通流量可省去显式的 Keep Alive 命令。

**Capsule**:
NVMe over Fabrics 的交换单位，内含一条 command 或 response，并可选携带 data 与 SGL。

**In-Capsule Data Offset (ICDOFF)**:
Identify Controller 中的一个值，定位命令 capsule 中从其首部起 `64 + ICDOFF * 16` 字节处的命令数据。

**Submission Queue Flow Control**:
Fabrics 上每个 queue pair 的约定：依据 `SQHD` 完成值释放已消费的 Submission Queue 槽位以便 host 复用；可在 Connect 协商中禁用。

**Individual I/O Queue Deletion**:
一种 Fabrics 上双向支持的能力，允许通过 Disconnect 或 transport 错误删除单个 I/O queue pair 而不终止其 association。

**NVM Subsystem Port**:
NVM 子系统与一个 fabric 之间一个 NVMe over Fabrics 协议接口，由一个或多个物理 fabric 接口组成。

**Discovery Service**:
一种 NVM 子系统，仅包含 Discovery controller，向 host 提供可达子系统与路径信息。

**Discovery Log Page Entry**:
一条 host 可见的记录，说明如何连接到目标 NVM 子系统，或把 host 引向另一个 Discovery Service。

**Discovery Log Snapshot**:
一次原子获取的 discovery log（可在单条命令内完成），或在跨多条命令时通过 Generation Counter 未变化来校验。

**Extended Discovery Log Page Entry**:
带固定连接头、并以 total-length 与 count 字段框住零个或多个扩展属性的 Discovery 记录。

**Host Discovery Log**:
Discovery controller 对已注册 host 的清单，可按请求的 Host NQN 过滤，并以携带 Host Identifier 属性的变长条目呈现。

**AVE Discovery Log**:
discovery 平面上对 Authentication Verification Entity 及其 IPv4 或 IPv6 TCP transport 记录的清单。

**Identify Controller or Namespace Structure (CNS)**:
Identify 命令的选择子，决定返回的 4,096 字节结构，并指示 namespace、controller、command-set 等限定字段是否有效。

**I/O Command Set Independent Identify Controller Structure**:
由 `CNS=01h` 选择的通用 4,096 字节控制器描述，包含 subsystem/controller 标识、传输限制、事件支持以及横切性 capability 属性。

**Maximum Data Transfer Size (MDTS)**:
Identify Controller 中以 2 的幂次（按最小内存页计）给出的限制，表示 host 可访问内存与控制器之间单次命令的数据上限；该字段为 0 表示无此字段层面的限制。

**Identify Controller Capability Directory**:
I/O Command Set Independent Identify Controller 结构中受依赖门控的区域，用于声明管理面、可选 Admin 命令与 log、firmware 与 power 行为、host memory 需求、capacity，以及受保护内存支持。

**Identify Controller I/O Envelope**:
Identify Controller 中的一个区域，报告必需与最大的 I/O queue entry 大小、每个队列的 outstanding command 引导值、最大的合法 NSID、可选命令聚合支持，以及 fused operation 支持。

**Command Quiesce Time (CQT)**:
控制器在 Keep Alive 超时或其它通信中断后、为 outstanding commands 满足 Immediate Abort 要求所需的最坏间隔。

**Explicit Persistent Discovery Connection**:
Discovery controller 使用非零 Keep Alive Timer 请求的连接，借助 Keep Alive 与异步发现变更通知来维持。

**Fabric Secure Channel**:
一种 transport 安全门，要求在控制器对该 NVMe Transport 接受任何命令之前必须先建立。

**NVMe In-band Authentication**:
Connect 之后的一道认证门；在认证完成之前，新建的 queue 仅可处理认证命令。

**Authentication Transaction**:
由 `T_ID` 关联、在单个 queue 上通过 Authentication Send/Receive 推进的 soft-state 交换；初始认证门控普通命令，重认证不先撤销已有认证。

**Secure Channel Concatenation**:
在不安全 Admin Queue 上用认证事务生成 PSK、断开该连接，再用所得 PSK 为后续 Admin 与 I/O Queue 建立 secure channel 的流程。

**Unique Discovery Service NQN Authentication**:
host 先通过 well-known Discovery Service NQN 单向认证并取得 unique NQN，再以 unique NQN 重连，从而安全地双向认证特定 Discovery subsystem。

## 通信（Communication）

**Transport Model**:
host 与 NVM 子系统之间传输命令、响应与数据的基于内存或基于消息的通信模型。

**Queue Pair**:
一对互相配合的 Submission Queue 与 Completion Queue，用于提交命令并回收其完成。

**Command Set**:
一组有共同目的与队列处理规则的命令族，例如 Admin、I/O 或 Fabrics。

**Admin Command Set**:
通过 Admin Submission Queue 提交的命令，划分为通用、基于内存的 transport 特有、以及基于消息的 transport 特有三类。

**Immediate Abort**:
在 Abort 命令自身 CQE 投递之前完成的中止，并被约束为不能产生目标命令的更晚效果。

**Deferred Abort**:
可选的、在 Abort 命令 CQE 之后才执行的中止，其成败通过目标命令的完成状态观察到。

**Asynchronous Event Request (AER)**:
一种无超时的 Admin 命令，在控制器有异步事件需要通知 host 时被完成。

**Controller Data Queue (CDQ)**:
由控制器管理、由 host memory 支撑的队列，控制器向其中投递特定类型的数据；其返回的标识只在创建它的控制器范围内有效。

**User Data Migration Queue**:
与一个控制器关联的 Controller Data Queue，在 controller migration 期间记录用户数据修改。

**Device Self-test Operation**:
一种短、自扩展、Host-Initiated Refresh 或厂商特定的诊断操作，其活动作用域按 `SDSO` 为 controller-local 或 subsystem-wide。

**Directive**:
一种类型化的 host/controller 信息交换机制，由成对的 Directive Receive 与 Directive Send Admin 命令承载。

**Pending Asynchronous Event**:
在事件发生时没有相应 AER outstanding、而保留的事件信息，等待后续 AER（不包括 immediate-event 语义）。

**Log Page Identifier (LID)**:
Get Log Page 的选择子，命名 log 内容，并通过该 log 的定义决定其作用域与寻址能力。

**Index Offset**:
Get Log Page 的起始位置，以 entry 索引表示，仅当所选 LID 声明支持 Index Offset 时合法。

**Error Information Log**:
按最新优先顺序的 controller-global 最近命令相关与非命令相关错误历史。

**SMART / Health Information Log**:
面向寿命的健康视图，包含预警状态、温度、备用容量、耐久度与活动信息。

**Changed Attached Namespace List**:
一个 controller log，记录自上次读取以来 namespace 的挂接、解除挂接、删除或 Identify 数据变化；溢出时需完全重枚举。

**Commands Supported and Effects Log**:
控制器发布的、按 opcode 组织的命令支持目录，给出可能的影响作用域、提交/执行建议，以及 capability 或数据变更。

**Feature Identifiers Supported and Effects Log**:
按 FID 的接口实例级目录，给出对每个 Feature 的支持、单一作用域、UUID 选择，以及可能的能力或数据变更。

**NVMe-MI Commands Supported and Effects Log**:
按 NVMe-MI Send 携带命令的管理 opcode 目录，记录 controller 支持、单一作用域以及可能的 capability 或数据变更。

**Command and Feature Lockdown**:
一种可选的 subsystem 能力，按 Admin Queue 与 Management Endpoint 接收路径分别禁止选定的命令 opcode 或 Set Features identifier。

**Command Scope**:
命令可能影响的资源层级，从 namespace 向上经 controller、NVM Set、Endurance Group、Domain 到 NVM subsystem。

**Telemetry Host-Initiated Log**:
host 触发、按 generation 编号的快照，以 512 字节数据块承载控制器或 NVM 子系统实现自定义状态。

**Telemetry Controller-Initiated Log**:
控制器触发的持久化诊断捕获，以 `RAE=0` 成功读取作为其带内可用性的应答。

**Telemetry Data Area**:
从第 1 块开始、逐步有界的遥测数据块前缀区，其最末块字段决定该区域的范围。

**Predictable Latency Mode**:
一种 NVM-Set 运行模式，在有界 Deterministic Window 与面向准备的 Non-Deterministic Window 之间交替。

**ANA Group Descriptor**:
一个 controller-relative 记录，包含 ANA Group 的 state、optional change count，以及 attached namespace 成员关系。

**Persistent Event Log Reporting Context**:
一个被冻结的、由厂商维护的 persistent event 选择，用于让分段 Persistent Event Log 检索在内部自洽。

**NVM Subsystem Hardware Error Event**:
一种持久化、厂商支持的硬件故障记录，使用标准化错误码并附带可选的、与错误码相关的附加信息。

**Media Unit Status Descriptor**:
一个 Domain 作用域内、单个 Media Unit 的资源分配、磨损指示、容量调整与所连 Channel 的记录。

**Persistent Event Format**:
一种自定界的事件记录，由通用的 controller、timestamp、port 归属开头，后接可选的厂商信息，以及独立修订的类型特定数据。

**Controller Support Requirement**:
某个命令、log page 或 Feature 在特定控制器类型上的 Mandatory、Optional、Prohibited 或条件支持分类。

**Power State Descriptor**:
一种按 power state 记录的 I/O 运行状态、转换延迟、相对性能、功率估算，以及可选的 power-loss 处理时间。

**Controller Property**:
位于公共控制面的 dword 或 qword 控制器属性，按 transport 定义的机制在起始偏移处以其声明宽度访问。

**Controller Capabilities (CAP)**:
强制的 64 位只读属性，描述约束合法控制器配置的限制与底层行为。

**Controller Configuration (CC)**:
通过 host 选择运行参数、使能或禁用控制器所借助的强制属性。

**Controller Status (CSTS)**:
强制的只读属性，报告 readiness、shutdown 进度/类型、致命状态、处理暂停以及子系统 reset 观测情况。

**Controller Reset**:
将 `CC.EN` 由 1 清为 0 触发的 Controller Level Reset，删除 I/O queues 并将控制器处理返回到一个 idle 禁用状态。

**NVM Subsystem Reset**:
影响 NVM subsystem 范围的 reset，可通过 `NSSR` 触发，并需要用于在 NVM Subsystem Shutdown 完成后恢复。

**Controller Memory Buffer (CMB)**:
可选的、与控制器关联的内存，其声明的 capability 决定是否能将 queue、list 与命令数据放入其中。

**Persistent Memory Region (PMR)**:
可选的持久化、与控制器关联的内存，具备显式的 enable/readiness、health、error 与 write-persistence barrier 语义。

**Boot Partition**:
两个等大小的、可选的、驻留在控制器上的分区之一，其内容可被复制到 host 选定的内存缓冲区以供 boot 使用。

**Capability/Configuration Handshake**:
host 读取 `CAP` 限制、选择合法的 `CC` 设置，并在 enable 控制器或创建 I/O queue 之前初始化 queue entry size 的过程。

**Controller Initialization**:
transport 特定的 bootstrap，紧接其后的 configuration、enablement、identification、namespace 发现、I/O queue 创建，以及可选的异步事件建立。

**Controller Ready Timeout (CRTO)**:
enable 一个控制器后，就绪带介质（及在支持时的与介质无关的 ready）所需的最坏等待时间。

**Controller Ready With Media**:
一种就绪模式，其中 `CSTS.RDY=1` 意味着命令处理、attached namespace 及 Admin 命令所需的介质都已就绪。

**Controller Ready Independent of Media**:
一种就绪模式，其中非介质命令处理在 attached namespace 与介质之前先行就绪，分别具有 `CRTO.CRIMT` 与 `CRTO.CRWMT` 截止时间。

**Controller Shutdown**:
通过 `CC.SHN` 触发的、针对单一控制器的 shutdown；`CSTS.ST=0` 用于将其进度与 NVM Subsystem Shutdown 相区分。

**NVM Subsystem Shutdown**:
由一个控制器发起、覆盖其所属 Domain 内每个 controller 或整个 NVM subsystem 的 shutdown，恢复常规执行前需要一次 NVM Subsystem Reset。

**Queue Level Reset**:
对一个 I/O queue 或 queue pair 的删除并重建，包含 transport 特定的 delete/disconnect 与 create/connect 流程。

**Firmware Update Sequence**:
一条互不重叠的 Firmware Image Download 与 Firmware Commit 命令序列，在到达 commit 阶段前都集中在同一控制器或同一 Management Endpoint 上。

**Pending Firmware Activation**:
已被 commit、等待 Controller Level、NVM Subsystem 或 Conventional Reset 才激活的固件镜像。

**Format NVM**:
一项 Admin 操作，修改介质格式属性，并可在 capability 选定的 namespace 作用域内可选地擦除用户数据。

**User Data Erase**:
Format NVM 的一种安全擦除模式，移除受影响的所有用户内容，但不规定擦除后介质的数据形态。

**Cryptographic Erase**:
Format NVM 的一种安全擦除模式，通过删除受影响用户内容的加密密钥使其变得不可访问。

**I/O Command Set Association**:
在 namespace 创建时选择的、恰好为 1 的绑定，固化其数据模型与命令解释，直到该 namespace 生命周期结束。

**Multi-Path I/O**:
在 1 个 host 与 1 个 namespace 之间两条或更多完全独立的路径。

**Namespace Sharing**:
两个或多个 host 通过不同 controller 访问同一公共 shared namespace。

## 存储资源（Storage resources）

**Domain**:
一个 NVM 子系统内部的存储资源分组，包含 Endurance Group。

**Division**:
一种可能打断 NVM 子系统内部 Domain 间通信的事件或动作，可能对全局状态或 namespace 访问造成划分。

**Domain Identifier**:
一种 subsystem-scoped 标识符，用于把 controller 与 Endurance Group 与共享 Domain（以及潜在故障边界）相关联。

**Endurance Group**:
一个 Domain 内部的存储资源分组，提供耐久度与资源管理边界。

**NVM Set**:
一个 Endurance Group 内的一组 NVM，可以从中分配 namespace。

**NVM Set Identifier**:
一个非零、subsystem-unique 的 16 位标识符，用以选定与此动作关联的 NVM Set。

**Endurance Group Identifier**:
一个非零、subsystem-unique 的 16 位标识符，用于选定耐久度管理边界。

**Reclaim Group**:
一个 Endurance Group 内部面向 placement 的分组，包含 Reclaim Unit。

**Reclaim Unit**:
在 Reclaim Group 内部、为 host 指导 placement 行为而管理的最细粒度资源。

**Reclaim Unit Handle**:
一种 Endurance Group 作用域的 FDP 间接寻址，每个 Reclaim Group 中引用一个 Reclaim Unit；当该单元写满时可以被重新指向。

**NVM Capacity Model**:
一种可选的上报与分配层级，覆盖 subsystem、Domain、Endurance Group、NVM Set、已格式化 namespace 与 Media Unit 的视图。

**Fixed Capacity Management**:
通过选择一种预定义的 configuration 来配置容量，该 configuration 会实例化其 Endurance Group 与 NVM Set。

**Variable Capacity Management**:
通过显式创建或删除 Endurance Group 与 NVM Set、并指定字节容量来配置容量。

**Media Unit**:
一个物理介质组件，恰好属于一个 Endurance Group（在支持 NVM Set 时还恰好属于一个 NVM Set），并连接到一条或多条 Channel。

**Channel**:
一条连接到一条或多条 Media Unit 的数据传输路径；Media Unit 跨 Channel 的组织方式影响带宽与隔离性。

**Exported NVM Subsystem**:
将底层 NVM 资源呈现给远端的逻辑 NVM 子系统。

**Dispersed Namespace**:
可同时通过两个或多个 participating NVM subsystem 中的 controller 访问的 shared namespace。

**Idempotent Command**:
重复提交（且其间无其它命令）能够在子系统层面产生相同终态与结果的命令。

**Reachability Group**:
挂接到同一 controller 的一组 namespace，共享同一可达性属性。

**Reachability Association**:
一个 controller-relative 的 Reachability Group 集合，所代表的 namespace 间操作具有共享的可达性特征。

**FDP Configuration**:
Endurance Group 作用域内的静态 placement configuration，描述 Reclaim Group、Reclaim Unit Handle、placement 限制及当前有效性。

**FDP Runtime Views**:
Endurance Group 作用域内的 Reclaim Unit Handle Usage、FDP Statistics、FDP Events 三种 log，用于观察当前 configuration 的所有权、寿命介质活动以及已启用的 placement 事件。

**Reservation Notification Log**:
一个 controller-local 的 destructive-read 队列，记录未屏蔽的 reservation 变更；其序号可暴露丢失的通知。

**Sanitize Status Log**:
对 sanitize 进度以及最近一次操作结果的持久化观测，可穿越 reset 与 power cycle 保留。

**Management Address**:
一类带类型的、以 `\0` 结尾的 UTF-8 URI，用于标识 NVM 子系统的管理代理或 fabric 接口管理器。

**I/O Command Set Combination**:
一个位图下标集合，描述控制器可同时支持的 I/O Command Set 组合；所选的 I/O Command Set Profile 仅允许启用该组合内的命令集。

**Supported Controller State Formats**:
Identify 中的一个目录，其下标的 NVMe 版本与厂商 UUID 列表指名 migration 操作中可用的 controller-state 格式。

**Virtual Queue Resource (VQ Resource)**:
为 primary controller 及其关联 secondary controller 提供 queue 容量所用的私有或柔性控制器资源。

**Virtual Interrupt Resource (VI Resource)**:
为 primary controller 及其关联 secondary controller 提供中断容量所用的私有或柔性控制器资源。

**Controller State Snapshot**:
Migration Receive 返回的状态镜像；仅当 target 保持 suspended、且 reset/property-change 条件在获取期间得到满足时，镜像才在内部自洽。

**Controller Suspension**:
一种 migration 状态：target 停止取新命令、除 outstanding AER 外排干已取走的命令、停止发起 transport 事务，而属性、CMB 与 PMR 在限定限制下仍可访问。

**Controller State Transfer Sequence**:
一条 `SEQIND=11b` Migration Send 命令，或者一条按完成顺序的 `01b` + 零或多条 `00b`/`10b` 序列，用于传送、校验、提交 controller-state 镜像。

**Namespace Attachment**:
使一个已分配的 namespace 在某个 I/O controller 上处于 active 的持久化关系；其管理与 namespace 的创建/删除相互独立。

**Sanitize Command Completion**:
指后台 sanitize 操作被成功启动的确认，并不证明擦除、校验或校验后的 deallocation 已完成。

**Security Protocol Exchange**:
Security Send/Receive 承载形式，NVMe 定义其方向与选择子，而所选的外部 security protocol 定义 payload 与 request/result 关联。

**Temperature Threshold Hysteresis**:
一个以 Kelvin 表示的裕量，用于改变当前过/欠温事件的恢复边界，而不改变其初始触发阈值。

**Autonomous Power State Transition (APST)**:
一项控制器策略：在一段配置的连续空闲间隔后，从某个源 power state 移动到所选的非运行状态。

**Non-Operational Power State**:
一种不处理 I/O 命令的控制器 power state，仍可保留受定义的控制、内存窗口、Admin 命令以及 host-initiated 后台操作访问，并在收到 I/O 时返回到最近一个运行状态。

**Non-Operational Power State Permissive Mode**:
一项允许控制器发起的后台工作临时突破非运行状态功率上限、达到最近一个运行状态上限的策略。

**Host Behavior Support**:
一种 replace-not-merge 特性，host 通过它显式许可依赖 host retry、telemetry、namespace-identity 或 command-format 行为的控制器功能。

**Namespace Admin Label**:
一个保存下来的、以 `\0` 结尾的 UTF-8 标签，用于人类识别的命名空间名称；成功 Sanitize 后会被复位为全零。

**Host Metadata Feature**:
一种不可保存的、4 KiB 的原子类型化描述符集合，描述 host 平台、controller 视图或 controller 特定的 namespace 视图。

**Controller Data Queue Tail Trigger**:
一种一次性特性条件，当控制器向选定的 CDQ 槽位投递一条 entry 时上报，并在触发后自行清除。

**Persist Through Power Loss (PTPL)**:
一种命名空间 reservation 状态，决定 reservation 与 registrants 是否在掉电后保留。

**Namespace Write Protection**:
一种由 subsystem 强制执行的命名空间状态机，它管理涉及修改介质的命令，并在进入保护态前提交易失性命名空间数据。

**Namespace Deletion Notice Fan-out**:
依据请求路径而产生的 controller 集合；当一个 namespace 被删除时，它们会上报启用的 attached-namespace 与 allocated-namespace 变更事件。

**Host Memory Buffer (HMB)**:
由 host memory 分配、专供控制器使用的内存区域，直至一次成功的 disable 完成才归还所有权给 host。

**Migration Change Tracking**:
Track Send/Track Receive 协议，记录命名空间用户数据变更，或上报在 migration 期间由选定控制器修改的 host memory 区间。

**Shadow Doorbell Buffer**:
一份由 host 更新、按页对齐的内存型 queue doorbell 镜像，配合一份由控制器更新的 EventIdx 页，用于仿真型控制器。

**Secondary Controller Resource Lifecycle**:
Virtualization Management 的操作序列：把 secondary controller 设为 offline、分配柔性 VQ/VI 资源、然后将其返回 online。

**Discovery Information Management**:
基于消息的 Admin 协议，host、Direct Discovery Controller 或 Centralized Discovery Controller 据此对保存在 CDC 或 DDC 中的、带 key 的 discovery 记录进行注册、反注册或原子更新。

**Discovery Entry Key**:
匹配 Discovery Information Management entry 与既有注册记录时所用的选定字段；host entry 使用基于 transport address 的 key，而 subsystem entry 可改用基于 port ID 的 key。

**Fabric Zoning Data Key (ZDK)**:
由 CDC 分配、在 Fabric Zoning Lookup 中返回的 key；DDC 据此选择一个 Zoning data 结构进行分片传输。

**Exported Namespace Association**:
Exported Namespace ID 与一个已挂接 active 的 Underlying Namespace 之间的映射，独立于后续对 Exported Namespace 的 controller 挂接。

**Allowed Host List**:
每个 Exported-NVM-Subsystem 上的一组 Host Identifier/NQN 条目，用于在访问模式受限的情况下通过选定的 exported port 建立连接。

**Send Discovery Log Page (SDLP)**:
CDC 向 pull-model DDC 发送的命令，用于传输 Discovery 族 log 字节，并支持一次性 resend 注册。

**Fabrics SQ Flow Control Negotiation**:
Connect 握手中的环节：SQ 流控只在 host 请求且控制器以 `SQHD=FFFFh` 应答时禁用。

**Disconnect Final-Response Barrier**:
一条 Fabrics 上的规则：一次 Disconnect response 是被删除的 I/O queue pair 的最后一条 CQE，并终结该 pair 上的后续命令处理。

**I/O Cancel**:
一条 I/O-queue 上的取消请求；其 CQE 计入 immediate abort 与 deferred-abort 候选，而目标 CQE 仍为最终结果提供权威判定。

**Flush Persistence Barrier**:
将已完成的命名空间数据与 metadata 从启用的 volatile write cache 提交到非易失介质的有序点。

**Namespace Registrant**:
已为某个 namespace 注册了 reservation key、可参与 reservation 访问策略的 host。

**Reservation Holder**:
当前持有某类型命名空间 reservation 的 registrant host。

**ANA Group**:
一种 subsystem-unique 的分组，其成员 namespace 在 controller-relative 维度上共享同一 asymmetric access state，并共同发生状态变迁。

**ANA Persistent Loss**:
一种终止的 controller-to-ANA-Group 关系：用户数据保持不可访问，且该关系无法再转入任何其它 ANA state。

**All Paths Down**:
一种 host 观察到的条件：在 1 个 ANATT 间隔内，对某 ANA Group 都没有出现 Optimized 或 Non-Optimized 的非 Persistent-Loss 路径。

**Boot Partition Update Sequence**:
在单一 controller 或单一 Management Endpoint 上、有序进行的、下载镜像、解锁并 commit、按需 verify、选中 active、重新锁定的流程。

**Controller Data Queue Phase Tag (CDQP)**:
一个按槽位设置的位，host 初始化、由控制器在每次队列 wrap 时翻转；它最后被写入，从而使新 phase 标识一条"已完整投递"的新 entry。

**Capacity Adjustment Factor**:
从 subsystem unallocated capacity 中移除的容量与新建 Endurance Group 总容量之间的整数百分比。

**Directive Enable State**:
一种 per-namespace 状态，决定是否可使用某种可选的 Directive Type；在共享非零 Host Identifier 的已启用 controller 之间保持协调。

**Streams Directive**:
一种可选的 I/O Command Directive，通过 host 分配的 Stream Identifier 关联 User Data Out 命令，使用 namespace-exclusive 或 subsystem-shared 的跟踪资源。

**Shared Stream Identifiers (SSID)**:
一种 NVM-subsystem-wide 策略，决定一个 Stream Identifier 在不同非零 Host Identifier 之间是 namespace 范围共有，还是按 Host Identifier 限定。

**Namespace Streams Allocated (NSA)**:
在 SSID 选定的 Host Identifier 共享作用域内、独占授予某 namespace 的 Stream 资源数。

**Participating NVM Subsystem**:
一个 NVM 子系统，其内 controller 可以对同一 dispersed namespace 的同一实例提供访问。

**Dispersed Namespace Global Identity**:
相同的 NGUID（缺失时为 UUID），用于在本地 NSID 不同的 participating NVM subsystem 间关联同一 dispersed namespace。

**Host Dispersed Namespace Support (HDISNS)**:
一种 Host Behavior Support 声明：host 按全局标识关联分散实例，并在全部 participating NVM subsystem 之间使用同一唯一的 Host Identifier。

**Dispersed Namespace Reservation Support (DISNSRS)**:
一种针对 reservation command 的声明：host 接受跨 participating 的 reservation 报告，包括远程 controller 标记 `CNTLID=FFFDh`。

**Migration Management Controller (MMC)**:
一种 I/O 或 Administrative controller，向独立的 Migratable Controller 提供 Host Managed Live Migration 操作的特权，本身不可迁移。

**Migration Management Host (MMH)**:
与 MMC 关联的 host，负责校验目标兼容性，并在源与目的 NVM subsystem 之间转移 namespace 数据与 controller state。

**Key Per I/O**:
一种能力：通过 namespace-specific Key Tag 在 namespace 读/写命令中注入加密密钥，而密钥生命周期留在 NVMe Base 之外。

**Runtime D3 (RTD3)**:
PCIe D3cold 区间：主控制器电源被移除，以所报告的正常关机进入与初始化 I/O 恢复延迟为界。

**Deterministic Window (DTWIN)**:
Predictable Latency Mode 中的一段时间：一个 NVM Set 在 host 消耗未超所报告预算时可提供确定性的读/写延迟。

**Read Recovery Level (RRL)**:
一种 NVM Set 属性，选择读完成时间与恢复开销之间的折衷，从可选的最大恢复到强制的 Fast Fail 依次排序。

**Replay Protected Memory Block (RPMB)**:
不依附于 namespace 的存储，按 target 提供一次性写入密钥、authenticated frames、nonce echo 与不可复位的 write counter 保护。

**RPMB Device Configuration Block Counter**:
target-0 上的单调计数器，只由认证的 Device Configuration Block 写入推进，与 RPMB 数据区 write counter 相互独立。

**Reservation Conflict Check Point**:
控制器开始处理一条命令的瞬间；之后发生的 reservation 变更无法使该命令追溯地产生 Reservation Conflict。

**Preempt and Abort Barrier**:
一种 reservation 操作：原子地变更 registration/reservation 状态，请求对受影响 namespace 命令做尽力中止，并把这些命令全部完成后再返回自身完成。

**Post-Verification Deallocation**:
在 Media Verification 中成功完成 host audit 之后、对全部用户数据介质进行 deallocation 的 sanitize 状态；其后进入 Idle 或一个匹配的失败状态。

**Restricted Sanitize Completion**:
`AUSE=0` 的 sanitize 策略：其处理失败将进入 Restricted Failure，并需要后续一次 restricted-completion sanitize 操作才能恢复。

**Unrestricted Sanitize Completion**:
`AUSE=1` 的 sanitize 策略：其处理失败将进入 Unrestricted Failure，允许该状态下定义的更宽泛的恢复选项。

**SQ Association**:
I/O Submission Queue 创建时的一个可选 hint，命名一个 NVM Set，其 namespace 应优先使用本 queue 以维持 Predictable Latency 行为。

**Telemetry Generation Validation**:
host 的协议动作：在数据块检索前后各读取一次 telemetry generation；值变化即丢弃该快照。

**NVMe Invalid UUID**:
UUID 列表中的保留型墓碑条目，用于替代已移除的厂商特定定义、并永久保留该下标以防被复用。

**PMR Write Barrier**:
PMR（或 `PMRSTS`）的读取机制，将之前的 posted write 进行排序；状态形式还会报告这些更新是否在无错误的前提下成为持久化。

**Power Loss Notification (PLN)**:
一个 transport-set 的控制器变量：当其跳变为 asserted 时，向同一 Domain 内的所有 controller 通报掉电即将发生。

**Power Loss Acknowledge (PLA)**:
一个可选的 controller-set 变量，报告当前是否在进行 Forced Quiescence 或 Emergency Power Fail 处理，以及端口通信模式。

**Forced Quiescence (FQ)**:
掉电准备阶段：停止取新命令，同时完成或中止已取走的命令，并保留 host-controller 之间的连通性。

**Emergency Power Fail (EPF)**:
掉电准备阶段：丢弃已取走和已排队的带外任务，并按照 Domain 内一致的 enabled/disabled-port 行为处理。

**NVMe-oF DNS-SD Bootstrap**:
基于 IP 的 fabric 发现流程：通过 PTR、SRV、TXT 与地址记录解析 `_nvme-disc` 或 `_cdc` 服务查询，然后在进行 Fabrics Connect 之前完成。

**Virtual Queue Resource Online Floor**:
分配给 secondary controller 的最少 2 个 VQ Resource：一个 Admin Queue pair 与至少一个 I/O Queue pair。

**Centralized Discovery Registration**:
host 或 DDC 将 discovery 信息显式 push 到 CDC，或由 CDC 通过 pull 反向连接 DDC 并读取 Discovery log；后续 pull 以最新完整集合替换该 DDC 的旧快照。

**Kickstart Discovery Connection**:
DDC 发起的短寿命 NVMe/TCP 协商连接，用 `ICReq/ICResp` 与 `KDReq/KDResp` 向 CDC 提交 pull-registration 参数；成功后拆除，再由 CDC 建立实际 pull 连接。

**ZoneDBConfig**:
CDC Zoning database 中保存 configured ZoneGroups 与 ZoneAliases 的配置集合，不代表当前已强制执行的规则。

**ZoneDBActive**:
CDC Zoning database 中当前生效的 ZoneGroup 集合，驱动 Discovery-log filtering、change notification 与可选网络限制。

**ZoneGroup**:
Fabric Zoning 的 activation unit，由 `{ZoneGroup Name, ZoneGroup Originator}` 唯一标识，并拥有 compact key 与 update generation。

**Zone**:
Fabric Zoning 的 access-control unit；同一 Zone 的成员依该 Zone 的规则互相通信。

**Zone Member**:
一个固定 256-byte 的类型化匹配项，以 Role 加上 NQN、IP、协议、服务端口或 PortID 的选定组合标识 host 或 NVM subsystem；类型未包含的维度不得参与强制。

**ZoneAlias**:
ZoneDBConfig 中可复用的 NVMe entity 分组；ZoneGroup 激活时 alias 引用被解析，而 ZoneAlias 不得再包含 ZoneAlias 类型成员。

**Fabric Enforced Zone Property**:
Zone 上的一个 TLV 提示，请求以逐包网络限制强制该 Zone；它不改变 Zone 成员的 host↔subsystem 通信矩阵。

**Get Active ZoneGroup (GAZ)**:
读取 `ZoneDBActive` 中完整 ZoneGroup 的操作；push model 使用 lookup key 与 FZR，pull model 使用 Transaction ID 与 FZS，接收方在全部 fragment 到齐前不得处理结果。

**Add/Replace Active ZoneGroup (AAZ)**:
对 active ZoneGroup 的带锁原子更新；CDC 只在完整定义到达后更新并递增 generation，push model 超过 30 秒未收齐会丢弃数据并解锁。

**Remove Active ZoneGroup (RAZ)**:
从 `ZoneDBActive` 删除指定 `{ZoneGroup Originator, ZoneGroup Name}` 的操作；目标缺失、被锁或 originator 未授权都会使操作失败。

**DH-HMAC-CHAP Authentication Transaction**:
由同一 `T_ID` 绑定的严格消息序列：协商 hash/DH 参数，controller challenge，host proof，以及可选的 subsystem 反向 proof；顺序、payload 或 proof 失败都会终止连接。

**NULL DH Exchange**:
`DHgID=00h` 的 DH-HMAC-CHAP 模式，不交换 DH exponential、退化为 HMAC-CHAP，并禁止用于 secure-channel concatenation。

**DH-HMAC-CHAP Secret Representation**:
`DHHC-1:xx:<Base64>:` 形式的可交换 secret；hash identifier 决定是否将 secret 与 NQN 绑定派生为 key，Base64 payload 末尾的 CRC-32 用于配置录入校验。

**Authentication Verification Entity (AVE)**:
代表 host 或 controller 验证 DH-HMAC-CHAP 响应的服务；以 NQN 标识，通过 TLS 1.3 PSK 连接，并为每个受验证实体维护 NQN、verification key 与 AVE-connection PSK。

**AVE Connection PSK (PSKea)**:
某一 NVMe entity 与 AVE 共享的 TLS PSK，其派生上下文绑定 `NQNAVE` 与 `NQNe`，与 host-controller 认证产生的 TLS PSK 不是同一用途。

**Controller Processing Stop Barrier**:
通信丢失后，host 通过终止 message association、等待 loss detection，再等待 CQT 或可配置时间，建立原 outstanding command 不再被 controller 处理的边界。

**Unrestricted Retry**:
幂等且仅改变 ancillary state 的 outstanding command，通信丢失后可不等待停止处理屏障而立即重试。

**Delayed Retry**:
幂等但会改变 user data 或 subsystem state 的 outstanding command；在原命令仍可能处理时必须延迟 retry 或最终结果上报。

**State-Dependent Retry**:
非幂等或可影响其他 host 行为的 outstanding command；其恢复动作需由能判定原命令处理程度的上层软件决定。
