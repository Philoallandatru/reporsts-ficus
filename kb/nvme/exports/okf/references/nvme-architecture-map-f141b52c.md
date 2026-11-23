# 架构图（Architecture map）

由 Theory of Operation 与 Architecture 节综合而来的解释性概览：

```text
                              NVM Subsystem
        +----------------------------------------------------------+
Host <--+--> Controller(s) <-- command sets --> Namespace(s)       |
        |        ^                                  |              |
|---|---|
        |        | properties / queues              v              |
        +----------------------------------------------------------+
             ^                                      ^
             | memory-based transport               | message-based transport
             | (e.g. PCIe)                          | (e.g. Fabrics)
```

Controller 是面向 host 的 NVM 子系统接口；namespace 是可寻址的存储抽象；transport 定义命令、completion 与数据如何跨越边界。[PDF pp. 39-46](../_source/pages/page-039.md) [PDF p. 58](../_source/pages/page-058.md)

对 Fabrics 而言，Discovery Service 在 host 连接前指明可达子系统的路径；随后所要求的 secure-channel 与 in-band-authentication 门控对命令接受施加约束。[PDF pp. 45-46](../_source/pages/page-045.md)

该架构由 Base Specification 治理，由 I/O Command Set 规范扩展，并由 transport 特定的 binding 承载；这种"家族关系"是适用范围的延展，而不是另一层架构。[PDF p. 23](../_source/pages/page-023.md)

对远端导出而言，[Exported NVM Subsystem](../concepts/exported-and-underlying-resources.md) 是对底层 namespace 与 port 的逻辑呈现。Namespace Sharing 可局限在同一子系统中，也可跨 participating 子系统成为 dispersed namespace。[PDF pp. 30-31, 33-36](../_source/pages/page-030.md)

Controller 有两类相互独立的分类：子系统从 static/dynamic 分配模型中二选一，而每个 controller 又属于一种功能类型（I/O、Administrative、Discovery）。Memory-based controller 为静态；Discovery controller 为动态。所有类型都保留公共 Admin Queue pair，仅 I/O controller 提供用户数据 I/O。[PDF pp. 58-62](../_source/pages/page-058.md)

[Controller Property 空间](../concepts/controller-properties.md) 是一组公共的、与 transport 无关的控制面。Message-based controller 通过 Property Get/Set 访问；memory-based controller 使用 binding 定义机制；capability 字段约束控制器使能之前所选择的配置。[PDF pp. 71-79](../_source/pages/page-071.md)

Memory-based controller 可暴露两种相互独立的 [Controller Memory Window](../concepts/controller-memory-windows.md)：CMB 支持 queue/list/data placement；PMR 具备显式的 readiness 与 persistence-barrier 契约。它们已使能的控制器地址范围不得重叠。[PDF pp. 86-94](../_source/pages/page-086.md)

Shared namespace 在所挂接 controller 间保持唯一的 NSID 与 Identify Namespace 视图，但命令原子性取决于接收端 controller，跨 controller 的顺序仍是 host/应用的责任。独立 port 提供 reset-failure 隔离；按 controller 维度访问特性仍可能非对称。[PDF pp. 55-57](../_source/pages/page-055.md)

## 存储资源层级

```text
NVM Subsystem
`-- Domain
    `-- Endurance Group
        `-- either NVM Set(s) -> Namespace
            or Reclaim Group(s) -> Reclaim Unit(s) -> Namespace
```

此解释性图保留规范中对 Endurance Group 的两种可选组织，而不是把两条分支同时呈现为包含关系。该层级已与 Figure 11-15 的渲染图核对；namespace 可共享一个 NVM Set，也可在一 Endurance Group 内跨多个 Reclaim Group。[PDF pp. 46-51](../_source/pages/page-046.md)

在多 Domain 子系统中，[Domains and Divisions](../concepts/domains-and-divisions.md) 提供显式的通信/故障边界。Division 可能划分子系统认知与 namespace 访问；reservation 恢复通过 ANA 控制访问，直至状态被同步或被声明为 persistently lost。[PDF pp. 104-107](../_source/pages/page-104.md)

对 message-based transport，预建立的 transport 连接在自身创建的 queue 上承载 Connect。得到的 queue pair 可被认证门控；SQ 容量通过有序的 `SQHD` 更新释放，或者当 SQ flow control 被禁用时由 host 自行管理；Completion Queue 不存在 NVMe 层面的指针流控。[PDF pp. 114-119](../_source/pages/page-114.md)

[Command arbitration](../concepts/command-ordering-and-arbitration.md) 选择的是 Submission Queue，而非全局执行顺序。Round robin 将所有 queue 等同对待；可选的加权机制在绝对的 Admin 与 Urgent 类之后再施加强 High/Medium/Low 加权服务。Fused pair 在此独立的处理模型下保持相邻与原子。[PDF pp. 120-123](../_source/pages/page-120.md)

[Controller initialization](../concepts/controller-initialization.md) 在 transport 特定的 bootstrap 之后汇合：memory-based controller 配置 Admin queue 属性；Fabrics controller 建立连接、Connect 那个 Admin pair，并在被请求时执行认证。两者随后选择合法的 capability 配置、enable、Identify、枚举 namespace 并创建 I/O queue。[PDF pp. 124-127](../_source/pages/page-124.md)

Initialization 涉及两种 readiness 契约：ready-with-media 将 `CSTS.RDY` 与完整介质可用性耦合；ready-independent-of-media 允许一个由 `CRTO.CRIMT` 限定、更早的命令处理里程碑和一个由 `CRTO.CRWMT` 限定、更晚的介质里程碑。Shutdown 状态是一个独立的轴：subsystem shutdown 覆盖 controller shutdown，`CSTS.ST/SHST` 在 `CC.EN/CSTS.RDY` 仍被置位时也能指示其范围与进度。[PDF pp. 128-134](../_source/pages/page-128.md)

[NVM Subsystem Shutdown](../concepts/controller-enable-shutdown-reset.md) 在单 Domain 拓扑中作用于整个 subsystem 范围，而在多 Domain 拓扑中作用于 Domain 或整个 subsystem 范围。仅 NVM Subsystem Reset 能清除可移植的 post-shutdown 边界；该 reset 在其范围内扇出为 Controller Level Reset，并让 PMR 被 disable。Queue Level Reset 的范围更窄：删除并重建受影响的 I/O queue。[PDF pp. 135-141](../_source/pages/page-135.md)

[NVM Capacity Model](../concepts/nvm-capacity-model.md) 沿 `Domain -> Endurance Group -> NVM Set -> formatted Namespace` 向下分配容量；Media Unit 分配给 Endurance Group/NVM Set，并接到 Channel 上。这两种是相互补充的分配与数据通路视图，并非 namespace 之下的额外嵌套层。[PDF pp. 141-143](../_source/pages/page-141.md)

[Flexible Data Placement](../concepts/flexible-data-placement-configurations.md) 在已 enable 的 Endurance Group 内把 NVM Set 分支替换为 host 指定的 `Reclaim Group -> Reclaim Unit` placement。一条命令选择一个 namespace-local 的 Placement Handle 与 Reclaim Group；该 handle 解析为每个 group 中的一个 Reclaim Unit，并在该单元写满时可被重新指向。[PDF pp. 538-541](../_source/pages/page-538.md)

同一 extended-capability 区域还关闭了 write-placement 路径、定义全 subsystem 的 Host-Initiated Refresh，并将 controller migration 扩展为由 MMC 管理的源/目的工作流。[Key Per I/O](../concepts/key-per-io.md) 进一步为每条读/写添加 key-tag 选择，同时把密钥供应留在 NVMe 之外；management address 与 namespace allocation 仍是相互独立的管理平面。[PDF pp. 543-550](../_source/pages/page-543.md)

Namespace allocation 将 controller 选定的存储 placement 与持久化的 controller 挂接分开，删除通知按请求路径与启用的通知类别进行扇出。[Namespace Write Protection](../concepts/namespace-write-protection.md) 添加一个由 subsystem 强制执行的持久化状态机与介质修改门控。[Power State Descriptors](../concepts/power-state-descriptors.md) 将 host 策略、自主空闲进入和必选的 I/O 自非运行态唤醒联系起来。[PDF pp. 551-558](../_source/pages/page-551.md)

Power 策略进一步延伸到 PCIe D3cold 与 Composite-Temperature 缓解。[Predictable Latency Mode](../concepts/predictable-latency-mode.md) 对每个 NVM Set 预算确定性工作量并调度维护窗口；[Reachability reporting](../concepts/namespace-topology-and-change-logs.md) 通过 controller-relative 的 group 关联与特征约束跨 namespace 的操作。[PDF pp. 559-567](../_source/pages/page-559.md)

Reachability 通知使对应的 topology 快照失效。Read Recovery Level 在每个 NVM Set 上用延迟换取恢复深度；[RPMB](../concepts/replay-protected-memory-block.md) 提供一个独立的、被认证与计数器保护的存储面，其 target-0 configuration 同样门控 Boot Partition 与 namespace write protection。[PDF pp. 567-575](../_source/pages/page-575.md)

RPMB 数据与 configuration 写入分别使用独立的单调计数器与有符号的 result 取出。Namespace reservation 在此之上将访问权限绑定到 Host Identifier 而非 controller 路径；在命令开始处理的那一刻即固化冲突决策，并应用 6 种 holder/registrant 策略之一。[PDF pp. 575-583](../_source/pages/page-575.md)

Reservation 的注册与抢占原子地重塑 shared namespace 的权利，并可附加尽力而为的命令中止屏障。Rotational media 把 spindle 状态耦合到 non-operational power 与 Domain reset 的 spinup 策略。Sanitize 之后贯穿全部持有用户数据的子位置，覆盖处理、可选的 audit verification、以及一次 deallocation 阶段。[PDF pp. 583-591](../_source/pages/page-583.md)

Sanitize 状态机将 restricted 与 unrestricted completion 策略分开，但保留公共的处理、progress、verification 与事件契约。处理成功、处理失败、进入 verification 都是显式变迁；reset 或 composition 变化会通过置位 `MVCNCLD` 取消后续 verification，而非中止后台擦除。[PDF pp. 591-599](../_source/pages/page-591.md)

Sanitize 恢复路径由显式的失败退出、audit verification 以及一个保留策略的 post-verification deallocation 分支构成。其命令限制作用于全 subsystem，并通过 Underlying Namespace 关联传导到 exported 视图。SQ Association 在 queue 创建时附加可选的 NVM Set QoS hint；Telemetry 使用经 generation 校验的累积快照用于诊断。[PDF pp. 599-607](../_source/pages/page-607.md)

Vendor-specific UUID 选择把稳定的命令数字标识与由实体定义的 payload 模式分开；tombstone 保留 firmware 索引的兼容性。PCIe 内存设施随之被分为易失低延迟的 CMB placement、可选的 controller-owned HMB 容量，以及显式 readiness/health/write-barrier 语义的 PMR 访问。[PDF pp. 608-615](../_source/pages/page-608.md)

Power Loss Signaling 将 transport 上的通知转换为 Domain 范围内的 Forced Quiescence 或 Emergency Power Fail 处理，显式定义命令命运、port 可用性与恢复时机。紧邻其侧的 virtualization 模型把可移动的 VQ/VI 资源从 primary controller 池分配，同时保留 private 资源与连续的 secondary 标识符。[PDF pp. 615-623](../_source/pages/page-615.md)

Media Unit 组织方式随后在性能权衡间选择：单一 group/set 可跨所有 Channel 以聚合带宽；竖直 group 可让每个 Channel 上各只有一个 set 以实现隔离；横向的 SLC/QLC group 各自跨全部 Channel，并以不同容量调整。容量核算在最近的可用父级处读取与更新。[PDF pp. 143-146](../_source/pages/page-143.md)

[Keep Alive](../concepts/keep-alive.md) 添加一个 per-controller 的通信 watchdog。Command Based 模式要求周期性的 Keep Alive 完成；Traffic Based 模式把已被取走的 Admin/I/O 命令视作存活动作，可能在最后一次取走后用 `2 * KATT` 来探测失败。控制器超时设置致命状态，并在 message-based transport 上拆除 association。[PDF pp. 146-151](../_source/pages/page-146.md)

[Firmware Update Lifecycle](../concepts/firmware-update-lifecycle.md) 通过 download 与 commit 对镜像分段进行串行化，然后立即或在所报告的 reset 边界处激活。Reset 激活将控制器重新接入 initialization 与 I/O queue 分配。[PDF pp. 152-154](../_source/pages/page-152.md)

[Common Command Format](../concepts/common-command-format.md) 为 Admin 与 I/O 命令提供共享的 64 字节 SQE 信封。`CDW0.PSDT` 选择 metadata 与 data pointer 走 PRP 还是 SGL；transport 决定合法编码；Fabrics 命令使用单独的共用 SQE。[PDF pp. 155-159](../_source/pages/page-155.md)

[Completion Queue Entry and Status](../concepts/completion-queue-entry-and-status.md) 闭合该命令信封：`CID` 与（Fabrics 之外的）`SQID` 关联命令；`SQHD` 返回已消费的 SQ 容量；Status 把 retry/log 提示与 `SCT`/`SC` 结果码分开。Fabrics 保留结果编码，仅保留针对内存 queue 的字段。[PDF pp. 160-163](../_source/pages/page-160.md)

其 status families 进一步将 opcode-specific rejection、介质/数据完整性失败、路径相关失败分开。对于内存型 Completion Queue，期望的 Phase Tag 在控制器每次 Tail wrap 时翻转，使 host 能在不重写已消费槽位的前提下区分新投递条目与陈旧内容。[PDF pp. 166-173](../_source/pages/page-166.md)

[Data Pointer Layouts](../concepts/data-pointer-layouts.md) 将命令信封扩展为内存覆盖。PRP 通过固定的 64 位 entry 命名按页大小的区域，并支持 packed/chained PRP List；SGL 描述带类型、带长度的数据与 segment 描述符。[PDF pp. 173-175](../_source/pages/page-173.md)

SGL segment 形成一个受限的描述符图：仅末条描述符可继续链接；Last Segment 终止该图；Bit Bucket 描述符可在不放置目标字节的前提下消费目标流字节。[PDF pp. 175-180](../_source/pages/page-175.md)

[Feature Values and Scope](../concepts/feature-values-and-scope.md) 把控制器配置接到 reset 范围。整 subsystem 的 reset 会从 saved/default 恢复受影响的 Feature；而仅影响多 controller 或多 Domain 子系统一部分的 reset，则保留更宽 resource-scoped 的值不变，除非该 Feature 的定义另行指定。[PDF pp. 181-183](../_source/pages/page-183.md)

[Identity, Name, and List Formats](../concepts/identity-name-and-list-formats.md) 把全局持久身份与本地命令句柄分开：NQN 标识一个 subsystem；EUI64/NGUID/UUID 标识一个 namespace；subsystem NQN 加上 `CNTLID` 在全局标识一个 controller。Protocol 携带的 UTF-8 名称按原始字节比较。[PDF pp. 183-190](../_source/pages/page-183.md)

[Identify Command Model](../concepts/identify-command-model.md) 暴露的是一个 capability 目录，而非一堆独立标志位。可选 Admin 命令、log、firmware 激活、host memory、capacity 与 RPMB 字段之间存在跨字段门控；例如 live-migration 支持压过 `HMPRE`；capacity-management 支持要求 capacity reporting；非零 RPMB count 要求 Security Send/Receive。其延续部分把 operational capability 接到 ANA、Sanitize 与 quiesce 限制，再定义 queue geometry 与 aggregate I/O 命令支持。[PDF pp. 327-342](../_source/pages/page-327.md)

Identify Controller 的最后一个区域在到达 power-state 描述符数组之前，宣告 Format/cache/atomicity、namespace protection、Copy/SGL 行为、挂接与 refresh 限制、被追踪的 migration/CDQ 容量、subsystem NQN，以及 Fabrics capsule/controller 属姓。[PDF pp. 343-350](../_source/pages/page-343.md)

[Power State Descriptors](../concepts/power-state-descriptors.md) 把这一数组转成 host 策略面，覆盖 operational 可用性、transition latency、relative performance、空闲/活动/最大功率，以及 power-loss vault/recovery 时序。随后 Identify 切到按页的 namespace/NVM Set 身份与受 CSI 限定的 capability 视图。[PDF pp. 350-358](../_source/pages/page-350.md)

[Identify Command Model](../concepts/identify-command-model.md) 进一步把 namespace 的运行时就绪、format 进度、access/reachability 成员关系以及 storage-resource 成员关系接到一个 cursor-based 目录家族上。其 I/O Command Set Combination 向量约束哪些命令集可同时被启用；Supported Controller State Formats 提供供 migration 命令使用的版本与厂商 UUID 下标。[PDF pp. 359-366](../_source/pages/page-359.md)

[Controller Virtualization Resources](../concepts/controller-virtualization-resources.md) 将 primary controller 的 VQ/VI 容量拆分为与 secondary controller 共享的 flexible 池与 private 容量。Secondary 目录即便在 offline 控制器上也让 online 状态、SR-IOV VF 身份与当前 VQ/VI 分配可见。Message-based Identify 单独暴露带 generation 计数的 [Underlying Namespace 与 Port 目录](../concepts/exported-and-underlying-resources.md)，用于组装 exported Fabrics 资源。[PDF pp. 366-370](../_source/pages/page-366.md)

扩展 virtualization 模型把 Offline 状态作为 resource-configuration 门控：secondary 需要一个 Admin 与 I/O VQ pair，并在支持 VI 时还需要中断向量 0；之后 Controller Level Reset 才在 Online 变迁前暴露已分配的容量。SR-IOV 把 PF 映射到 primary、把它们的 VF 映射到关联的 secondary。IP-fabric 上的 [Fabrics Discovery and Authentication](../concepts/fabrics-discovery-and-authentication.md) 在 Connect 之前通过 DNS-SD PTR/SRV/TXT/A/AAAA 记录 bootstrap 控制器地址；`_cdc` 查询用于协调 DDC-to-CDC 注册行为。[PDF pp. 624-631](../_source/pages/page-624.md)

[Command and Feature Lockdown](../concepts/command-and-feature-lockdown.md) 将只读侧清单与 subsystem-wide 的写入侧强制命令分开。[Controller Migration](../concepts/controller-migration.md) 使用所宣告的 state-format 下标获取控制器状态；suspension 加 reset/property 稳定性决定了快照一致性；一条 completion-ordered `SEQIND` 序列在 Resume 之前完成 transfer、verify、commit 与 I/O queue state 的重建。[PDF pp. 370-383](../_source/pages/page-370.md)

migration 写入路径 suspends 命令获取、按需协调 User Data Migration Queue、传输一份完整镜像或一份有序分片序列，并且只在最后一片经 verify 之后才 commit。标准镜像重建有序的 I/O SQ/CQ 创建属性与活动指针；只要收到的状态尚未 commit，Resume 即被阻塞。[PDF pp. 375-383](../_source/pages/page-375.md)

[Namespace Management](../concepts/namespace-management-lifecycle.md) 将 subsystem 分配与 controller 挂接分开：create 只分配而不挂接；挂接穿越 reset；delete 会移除所有挂接。[Sanitize](../concepts/sanitize-operation-lifecycle.md) 启动一项 subsystem-wide 的后台操作，其命令的 CQE 仅确认启动；其 status log 跟踪实际的进度与结果。[PDF pp. 383-390](../_source/pages/page-383.md)

[Security Protocol Exchange](../concepts/security-protocol-exchange.md) 是一个与具体协议无关的 Send/Receive 载体，所选的安全协议负责 payload 与关联语义。[Feature Values and Scope](../concepts/feature-values-and-scope.md) 定义通用可变策略面：saveability、scope、memory-buffer 属姓、UUID 限定、completion 顺序以及重新发现。最初的 [common controller Features](../concepts/common-controller-features.md) 把该策略面应用到仲裁、power、temperature 与 volatile cache。[PDF pp. 390-398](../_source/pages/page-390.md)

Feature 策略进一步连接通知、时间与 power 行为：AER configuration mask 启用事件族；APST 与 permissive non-operational mode 独立地选择空闲进入与后台工作的合法性；Timestamp 暴露 origin/continuity 限制；Keep Alive 仍受 transport 约束；Predictable Latency configuration 把 mode/windows 与告警阈值绑定到一个 NVM Set。[PDF pp. 399-407](../_source/pages/page-407.md)

Host Behavior Support 在控制器使用 retry、telemetry、dispersed-namespace 或 Copy-format 行为之前显式建立兼容性握手。随后的 Features 配置 subsystem 的 Sanitize 策略、Endurance Group 事件、controller 命令集组合、rotational spinup、power-loss signaling、FDP activation/events，以及一个可被 sanitize 复位的人类可读 namespace label。[PDF pp. 407-415](../_source/pages/page-407.md)

Feature 面还驱动 host/controller 协调：CDQ 头端释放与一次性 tail 事件；management-agent URI 发现；原子类型化 metadata 注解；预启动进度标记；以及用于关联 controller 与 reservation 权限的 Host Identifier 注册。[PDF pp. 415-423](../_source/pages/page-415.md)

Reservation mask 与 PTPL 配置要上报哪些 namespace reservation 变更，以及 reservation 状态是否在掉电后保留。Namespace 与 Boot Partition 的 write-protection Feature 控制可写性；memory-based transport 的 Feature 协商 queue 数、中断合并以及 controller-exclusive 的 Host Memory Buffer 所有权。[PDF pp. 424-431](../_source/pages/page-424.md)

HMB 描述符将按 controller page 大小组织的 host memory 区间映射起来，并暴露当前分配属性。Migration 面随后把 Track Send 与 destructive Track Receive 上报配对：一种模式把 namespace 数据变更记录到 User Data Migration Queue；另一种模式记录由一个选定控制器写入的 host memory 区间，直到 suspension 关闭变更窗口。[PDF pp. 431-438](../_source/pages/page-431.md)

Memory tracking 在资源不足时协商回退的粒度/容量。PCIe queue 管理按 CQ 在前、SQ 在后的顺序创建，删除时则先 SQ 后 CQ，并以 SQ 的成功删除作为最终的显式/隐式 command-completion barrier。Shadow Doorbell/EventIdx 页面提供面向仿真的镜像；Virtualization Management 则通过 secondary 的 Offline/Assign/Online 生命周期重新分配 VQ/VI 资源。[PDF pp. 439-447](../_source/pages/page-439.md)

Message-based Admin 管理将 exported 配置与底层存储分开：exported subsystem 在选定访问模式下为空；清除 exported 配置会保留 underlying namespace 与 subsystem。Discovery Information Management 通过 key 化的 register、de-register、atomic update 任务独立维护 CDC/DDC 的注册记录。[PDF pp. 448-455](../_source/pages/page-448.md)

Discovery 注册条目随后附带类型化、带长度界限的 Host Identifier 与 admin-label 属性。[Fabric Zoning](../concepts/fabric-zoning-data-transfer.md) 单独把 lookup 数据映射到 Zoning Data Key，并以 offset 片段传输 Zoning 结构；exported-resource management 把一个 ENSID 关联到一个已挂接的 underlying namespace，而不隐式地把 exported namespace 挂接到 controller。[PDF pp. 455-462](../_source/pages/page-455.md)

export-management 平面同时控制可达性与暴露：Allowed Host Lists 按 exported subsystem 与 port 限制 host；Exported Port 把这些 subsystem 绑定到底层 transport port。CDC 可以将分段后的 Discovery、Host Discovery 或 AVE Discovery log 字节推给一个 pull-model DDC；DDC 的完成可在一次更新之后请求未来的一次 resend。[PDF pp. 463-470](../_source/pages/page-463.md)

Fabrics 命令平面使用一个 opcode，配合带类型 functions。Authentication Send/Receive 携带外部 security protocol；Admin Connect 分配一个 controller 并建立身份；I/O Connect 继承该身份，同时协商每对的 SQ 流控；Disconnect 的 response 即为最后一条 CQE，并不直接删除 transport 连接。[PDF pp. 471-479](../_source/pages/page-471.md)

Fabrics Property 命令把 message capsule 映射到通用 controller-property 表面。Common I/O 平面随后增加三条控制路径：Cancel 选取已取走的 I/O 命令以进行 immediate 或 deferred abort；Flush 创建一条 volatile-to-non-volatile 完成屏障；I/O Management Receive 返回与操作相关的状态，例如 FDP Reclaim Unit Handle 状态。[PDF pp. 479-487](../_source/pages/page-479.md)

I/O Management Send 把 FDP Placement Identifier 重新指向空的 Reclaim Unit，并显式声明 partial failure 与 concurrent-write 语义。Namespace reservation 形成另一个独立的 shared-access 状态机：host 注册 key、获取或抢占有类型的 reservation、release 或 clear 状态、选择 power-loss persistence，并跨 dispersed participant 查看带 generation 计数的 registrant 记录。[PDF pp. 487-495](../_source/pages/page-495.md)

ANA 把访问建模为 controller-to-group 关系。Group 成员在同一 Domain 内共同变迁；每个 controller 可报告 Optimized、Non-Optimized、Inaccessible、Persistent Loss 或瞬态 Change。通知暴露重要变迁；adverse state 选择性地改变命令可用性、重试路由以及上报的 capacity，而不是关闭整个 Admin 平面。[PDF pp. 497-503](../_source/pages/page-497.md)

IP-based centralized discovery 把注册与访问控制接成一条控制链：host/DDC 通过 push 或 pull 向 CDC 汇集记录，CDC 返回经过 Zoning 过滤的 Discovery log；变更再由 AER 驱动 host 重读。Pull 模式由 CDC 反向 Connect 到 DDC 并用 `Get Log Page(LID=70h)` 替换该 DDC 的旧快照。[PDF pp. 632-636](../_source/pages/page-632.md)

[Fabric Zoning Model](../concepts/fabric-zoning-model.md) 将配置态 `ZoneDBConfig` 与强制态 `ZoneDBActive` 分离。ZoneGroup 是 activation unit，Zone 是 access-control unit；成员与 properties 位于 Zone 的可变尾部，而 [Fabric Zoning Data Transfer](../concepts/fabric-zoning-data-transfer.md) 负责对这些结构做 key lookup 与 fragment transfer。[PDF pp. 637-639](../_source/pages/page-637.md)

Zoning operations 在相同语义上提供两种控制方向：push DDC 以 FZL 获得 compact key 后主动 FZR/FZS；pull DDC 先用异步事件与 request log 交付 Transaction ID，再由 CDC 主动 FZR/FZS。GAZ 以完整快照为读取边界，AAZ 以锁、全片接收和 generation 递增为提交边界，RAZ 则受相同的存在性、锁定与 originator 授权检查约束。[PDF pp. 647-654](../_source/pages/page-647.md)

Pull-model zoning 用统一 operation-status 集合结束 GAZ/AAZ/RAZ，并复用 AEN/request-log 通道触发 CDC 以 SDLP 反向投递 Discovery log。相邻的 export 管理流程先发现 underlying namespace/port，再创建 subsystem、关联 namespace 与 port、配置 host access；删除则按 port、namespace、subsystem 的依赖逆序执行。[PDF pp. 655-661](../_source/pages/page-655.md)

Fabrics 安全入口有两个独立门：transport-specific secure channel 必须在 TREQ 要求时先于 capsule 传输建立；Connect 后的 NVMe in-band authentication 则通过 Authentication Send/Receive 完成。二者可以同时存在，并使用不同的 transport 与 NVMe 身份。[PDF pp. 661-662](../_source/pages/page-661.md)

带内认证是 queue-local 的 soft-state transaction：Discovery well-known NQN 只适合单向认证，unique Discovery Service NQN 才能绑定双向身份。认证可以在不安全 Admin connection 上派生 TLS PSK，随后必须断开旧连接并以该 PSK 建立新的安全 Admin/I/O queue；重认证超时不会撤销先前认证。[PDF pp. 663-670](../_source/pages/page-663.md)

DH-HMAC-CHAP 在同一 `T_ID` 下把参数协商、controller challenge、host proof 与可选的反向 proof 串成严格状态机。NULL DH 会降级为 HMAC-CHAP，且不能与 secure-channel concatenation 同用；任何消息顺序、payload 或 proof 错误都以有方向的 AUTH_Failure 结束并断开连接。[PDF pp. 671-678](../_source/pages/page-671.md)

AVE 把 verification 从 NVMe entity 委托给按 NQN 索引 key 的服务；entity 通过 TLS 1.3 + `PSKea` 发送携带交易上下文的 Access-Request，AVE 回传匹配 ID 的 Access-Result。AVE 地址可配置或经 Discovery controller 发现。[PDF pp. 687-689](../_source/pages/page-687.md)

[通信丢失恢复](../concepts/communication-loss-and-command-retry.md) 先以 association termination、Keep Alive/transport detection 和 CQT 等待建立“原命令不再被处理”的屏障，再把 outstanding command 分为 Unrestricted、Delayed 或 State-Dependent Retry。这个顺序是防止数据破坏和多 host 状态意外变化的关键。[PDF pp. 691-695](../_source/pages/page-691.md)

Zone member 类型决定 enforcement 可使用的身份维度，从 NQN-only 到 NQN/IP/protocol/service/PortID 的精确组合；未编码的维度不得参与匹配。Zone 只允许 host 与 NVM subsystem 互通，激活时展开 ZoneAlias，并可通过 property 请求逐包网络级强制。[PDF pp. 640-646](../_source/pages/page-640.md)

Extended capability 操作随后把早期命令格式重新接到运行时语义：Boot Partition protection 把控制权从 Set Features 永久交给 RPMB；Capacity Management 更新嵌套的核算并级联删除；Lockdown 强制 per-interface 的 subsystem 策略；CDQ 用 phase tag 同步生产者/消费者进度；self-test 在冲突命令前后 suspend，同时保留后台 segment 状态。[PDF pp. 511-519](../_source/pages/page-511.md)

Self-test 寿命随后按操作类型拆开：短测试对 reset 敏感；扩展测试持久存在并可恢复；Format、Sanitize、显式 abort 与 namespace 删除构成共用的终止边界。[Directive Exchange](../concepts/directive-exchange.md) 通过 Host Identifier 身份协调 per-namespace 的启用；随后 Streams 把 I/O hint 映射到 namespace-exclusive 或 subsystem-shared 的跟踪资源。[PDF pp. 519-527](../_source/pages/page-519.md)

Streams 进一步暴露 subsystem 与 namespace/host 视图、显式分配与释放操作、以及对开放标识符的有序观察。Data Placement 共享 Directive 编码，却将 placement 委托给 FDP，而非定义自己的 Send/Receive 操作。[Dispersed Namespace Lifecycle](../concepts/dispersed-namespace-lifecycle.md) 把 namespace 身份扩展到 participating subsystem：本地的 NSID 可以不同，而同一份 NGUID 或 UUID 身份固定住 migration 与 replication 路径。[PDF pp. 528-535](../_source/pages/page-535.md)

[Admin Command Model](../concepts/admin-command-model.md) 将管理操作划分为通用、内存特有、消息特有三组，但保留单一的 Admin Queue 信封。Format 与 sanitize 把可运行的命令集收窄到一份显式的恢复/控制白名单。[PDF pp. 191-193](../_source/pages/page-191.md)

[Command Abort Semantics](../concepts/command-abort-semantics.md) 区分 immediate effects barrier 与 deferred cancellation：Abort 的 CQE 上报是否发生 immediate abort，而目标命令的 CQE 对于后续 deferred abort 是否成功仍保持权威。[PDF pp. 194-195](../_source/pages/page-194.md)

[Asynchronous Event Reporting](../concepts/asynchronous-event-reporting.md) 让长寿命 Admin 命令对控制器发起通知保持可用。大多数事件类型在上报后被屏蔽并通过读取相关 log 清除；immediate 与 one-shot 事件使用不同的保留规则。[PDF pp. 195-202](../_source/pages/page-195.md)

[Capacity Management Operations](../concepts/capacity-management-operations.md) 将 capacity 层级变成 Admin 生命周期：固定模式实例化一份预定义 configuration；可变模式显式创建/删除 Endurance Group 与 NVM Set，使用显式字节容量与受包含关系约束的删除。[PDF pp. 203-206](../_source/pages/page-203.md)

[Controller Data Queues](../concepts/controller-data-queues.md) 在稳定的 host memory 映射中提供由控制器产生的数据流；Base 定义的 User Data Migration Queue 记录 controller migration 期间被修改的用户数据。[PDF pp. 206-210](../_source/pages/page-206.md)

[Device Self-test](../concepts/device-self-test.md) 是一个 controller/subsystem 作用域的状态机，其结果日志记录 start 与 abort 变迁。[Directive Exchange](../concepts/directive-exchange.md) 则提供一组按类型选择的 host→controller 与 controller→host 传输信封。[PDF pp. 210-214](../_source/pages/page-210.md)

[Format NVM](../concepts/format-nvm-lifecycle.md) 按 `FNS`/`SENS` 在 namespace、attached-controller 或 subsystem 范围内应用所选介质格式与可选安全擦除；在完成前它门控与之冲突的 I/O。[PDF pp. 217-220](../_source/pages/page-217.md)

[Controller Data Queues](../concepts/controller-data-queues.md) 增加一条由 controller-to-host 投递、仅由 host memory 支撑的路径。创建返回 controller-local 标识符；删除或 reset 终止该队列寿命；所定义的 User Data Migration Queue 为所选 controller 记录修改。[PDF pp. 206-210](../_source/pages/page-206.md)

[Device Self-test](../concepts/device-self-test.md) 是一项有状态的 Admin 操作，其作用域可为 controller-local 或 subsystem-wide。在测试进行中，标准 start 被拒绝；abort 按定义顺序更新 self-test 日志再完成。[PDF pp. 210-212](../_source/pages/page-210.md)

[Directive Exchange](../concepts/directive-exchange.md) 提供对称的 Admin 信封，分别承载 host→controller 与 controller→host 的类型化数据。Directive Type 与 Operation 拥有 payload 与 status 语义；通用命令拥有方向、buffer 与 length。[PDF pp. 212-214](../_source/pages/page-212.md)

[Log Page Retrieval](../concepts/log-page-retrieval.md) 是覆盖 controller、namespace、Domain、subsystem、Endurance Group 作用域的诊断读取面。其 offset 模型对 byte slice 普遍支持，索引条目仅在所选 LID 公开声明该能力时才支持。[PDF pp. 223-228](../_source/pages/page-223.md)

[Error and Health Logs](../concepts/error-and-health-logs.md) 把诊断分为最近的离散失败与较长寿命的健康状态。错误记录关联命令与参数；SMART/Health 状态提供预警、温度、备用与耐久度指示。[PDF pp. 229-231](../_source/pages/page-229.md)

SMART/Health 随后用保留的活动、power、error 与 thermal 计数器扩展该快照。Firmware-slot 与 changed-namespace 日志暴露待生效的操作状态；[Commands Supported and Effects](../concepts/command-effects-and-support.md) 目录让 host 可以串行化潜在冲突的命令，并在声明变更后重新发现 capability。[PDF pp. 232-238](../_source/pages/page-238.md)

[Device Self-test](../concepts/device-self-test.md) 日志将命令状态机接到观测：它报告当前进度并按最新优先顺序保留最新的二十项已完成或已中止结果。[PDF pp. 238-239](../_source/pages/page-239.md)

Self-test 结果保留 validity-gated 的失败位置与按类型的完成状态。[Telemetry Capture Logs](../concepts/telemetry-capture-logs.md) 提供一份更广泛的厂商诊断快照：host 可以显式冻结状态，或者消费一条持久化的控制器触发捕获，并通过 `RAE=0` 应答其异步事件可用性。[PDF pp. 240-246](../_source/pages/page-240.md)

在 storage-resource 作用域下，Endurance Group 日志将 host 流量与物理介质写入进行对比，并报告备用、寿命、错误以及容量状态。[Predictable Latency Mode](../concepts/predictable-latency-mode.md) 暴露按 NVM Set 的 deterministic/non-deterministic 窗口与待处理事件聚合。[PDF pp. 247-250](../_source/pages/page-247.md)

ANA 日志是 controller-relative 的组状态与 attached namespace 快照，受 global/per-group change count 保护。[Persistent Event Log](../concepts/persistent-event-log.md) 则保留 subsystem-global 历史，并冻结 reporting context 以便分段读取保持一致。[PDF pp. 250-255](../_source/pages/page-250.md)

Persistent-event framing 将通用的 controller/time/port 信封与独立修订的事件数据分开。其第一批标准化记录保留周期健康快照以及 firmware、timestamp、跨 controller reset 与硬件错误证据；其 support bitmap 让 parser 可发现后续的可选家族。[PDF pp. 256-263](../_source/pages/page-256.md)

Hardware-error 记录附上在失败时捕获的 PCIe、warning、CQE、power-loss 或 readiness 状态。Namespace、Format、Sanitize 与 Set Feature 记录随后形成一个 operational 日志，把接受的参数与完成状态及 partial failure 分开。[PDF pp. 263-271](../_source/pages/page-263.md)

Persistent events 以 telemetry、thermal、media-verification、vendor 与 TCG 扩展记录收尾。在资源作用域中，Endurance Group 事件聚合指向组级健康细节；Media Unit Status 与 Supported Capacity Configuration 日志暴露当前物理分配与备选 Domain configuration。[PDF pp. 272-279](../_source/pages/page-272.md)

Supported configuration 扩展为有序的 Endurance Group、NVM Set、Channel 与 Media Unit 描述符树。相邻的 effects 目录暴露按接口划分的 Feature 与 NVMe-MI 支持以及可能的范围与状态变更；[Command and Feature Lockdown](../concepts/command-and-feature-lockdown.md) 为带内与带外路径提供一份独立的强制清单。[PDF pp. 279-286](../_source/pages/page-279.md)

[Boot Partitions](../concepts/boot-partitions.md) 也可以通过 `Get Log Page` 读取：选择子选定一个分区，返回的 header 描述 active 分区与 size，而不改变基于寄存器的传输状态。[PDF pp. 286-287](../_source/pages/page-286.md)

[Flexible Data Placement](../concepts/flexible-data-placement-configurations.md) 把一份静态 Endurance Group configuration 接到三份运行时视图：handle ownership、饱和的写/擦统计，以及一份已启用 oldest-first 事件历史。Placement Identifier 的解释依赖于 configuration，因为 `RGIF` 决定高位是否用来选择 Reclaim Group。[PDF pp. 294-301](../_source/pages/page-294.md)

两份有状态日志使用不同的消费契约。[Reservation Notification](../concepts/reservation-notification-log.md) 是一条 destructive-read FIFO，其序号暴露已丢失的通知；[Sanitize Status](../concepts/sanitize-operation-status.md) 是一份跨 reset 保留的对操作进度、结果、估算及当前/失败状态的观测。[PDF pp. 301-305](../_source/pages/page-301.md)

Fabrics 的 [Discovery log](../concepts/fabrics-discovery-and-authentication.md) 协商 host 过滤的、port 局的、包含全部 subsystem 的以及带扩展条目的视图。Multi-command 读取是一个 generation-validated 快照；每条记录既可以是一条 referral、一个具备 namespace 能力的 subsystem 路径、也可以是回到当前 Discovery Service 的另一路径。[PDF pp. 306-311](../_source/pages/page-306.md)

同一个 discovery 平面还暴露已注册 host 与 AVE 清单，以及一个 pull-model DDC-to-CDC 请求通道。[Identify Command Model](../concepts/identify-command-model.md) 则提供通用的 4 KiB 自省操作：`CNS` 选定结构并决定 namespace、controller、command-set 或 UUID qualifier 是否参与。[PDF pp. 312-319](../_source/pages/page-312.md)
