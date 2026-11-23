---
type: Concept
title: Identify 命令模型（Identify Command Model）
description: Identify 是 NVMe 的“设备说明书读取命令”。主机通过一个 `CNS` 选择子取得固定 4,096 字节的结构：可以是 controller、namespace、Domain、Endurance
  Group、命令集或相关目录。 [PDF pp. 317-319](../_source/pages/page-317.md)
tags:
- nvme
- storage
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Identify 命令模型（Identify Command Model）

Identify 是 NVMe 的“设备说明书读取命令”。主机通过一个 `CNS` 选择子取得固定 4,096 字节的结构：可以是 controller、namespace、Domain、Endurance Group、命令集或相关目录。 [PDF pp. 317-319](../_source/pages/page-317.md)

## 先问什么，再读哪份说明书

```text
Identify 命令
   |
   +-- CNS ------> 要哪一种结构/列表？
   +-- NSID -----> 哪个 namespace？（仅适用 CNS 使用）
   +-- CNTID ----> 哪个 controller？（仅适用 CNS 使用）
   +-- CSI ------> 哪个 I/O Command Set？（仅适用 CNS 使用）
   +-- CNSSID ---> 该 CNS 定义的额外选择子
   `-- UIDX -----> 支持 UUID 限定时的视图
                    |
                    v
              4,096 字节结果
```

图是 Figures 306-310 的学习用归纳，并不复制全部 CNS 取值表。 [PDF pp. 317-319](../_source/pages/page-317.md)

## 一个驱动启动案例

驱动启用 controller 后，首先读取 Identify Controller 了解队列大小、可选命令、日志、HMB、FDP、ANA 等能力；然后列举 active namespace，再对每个 NSID 读取 Identify Namespace 和身份描述符。之后才按已发现的能力启用 Feature、创建 I/O 队列或选择多路径策略。 [PDF pp. 317-319, 321-366](../_source/pages/page-317.md)

## 通用规则：所有 CNS 都返回同样大小，但含义不同

| 规则 | 含义 |
|---|---|
| 结果大小 | 每个 Identify 操作返回 4,096 字节；未使用条目/空间补零 |
| 数据指针 | PRP 模式下不把 data pointer 当 PRP List，因为结果至多跨一个页边界 |
| 未使用选择子 | host 清零；controller 忽略未使用 `CNTID`，未使用 `CSI` 为零 |
| 不支持的选择 | 不支持 `CNS` 返回 Invalid Field in Command；命令集关联不兼容返回 Invalid I/O Command Set |
| 传输分区 | 共用、内存型专用、消息型专用结构各在对应章节定义 |

[PDF pp. 317-319](../_source/pages/page-317.md)

## CNS 不必死记，先按“要解决什么问题”分组

| 类别 | 常见结果 | 典型用途 |
|---|---|---|
| 活动 namespace 管理 | controller data、active NSID list、namespace descriptor、NVM Set list | 枚举当前可访问的存储 |
| controller / namespace 管理 | allocated NSID、controller list、primary/secondary data、UUID list | 管理配置与拓扑 |
| 资源/命令集目录 | Domain、Endurance Group、I/O command set、underlying namespace/port | 查看资源分层与命令能力 |
| 迁移/分配视图 | 已分配的命令集 namespace、independent namespace、controller state formats | 迁移与高级管理 |

完整 CNS 矩阵跨多个 PDF 页，带有必需/可选条件和选择子适用性，不能用一张简化表替代。标准 `CSI` 包含 `00h`-`04h`，厂商范围为 `30h`-`3Fh`，其余区间保留。 [PDF pp. 319-320](../_source/pages/page-319.md)

## Identify Controller：一次读出“这台 controller 能做什么”

Identify Controller 是 capability profile，而不是配置命令。它报告身份、队列/传输限制、Admin/I/O 命令能力、日志/Feature、功耗/温度、内存、容量、迁移和 Fabrics 属性；主机必须把相关字段按依赖关系一起解释。 [PDF pp. 321-350](../_source/pages/page-321.md)

```text
Identify Controller
 |-- 身份：型号、NQN、controller type、FRU 等
 |-- 控制面：OACS、AER、firmware、日志、Feature
 |-- 数据面：SQ/CQ entry、MAXCMD、NN、ONCS、FUSES、SGL
 |-- 资源面：HMB、容量、RPMB、namespace attachment、CDQ
 `-- Fabrics：capsule、connection、Discovery 属性
```

### 容易漏掉的跨字段依赖

| 能力簇 | 不能单独理解的规则 |
|---|---|
| Host memory 与 migration | `HMPRE` 非零才表示 HMB，且至少为 `HMMIN`；若任一 subsystem controller 宣告 Host Managed Live Migration，`HMPRE` 为零 |
| Firmware 与 logs | `FRMW` 报告 Domain firmware slot；`LPA` 独立决定 telemetry、Persistent Event、扩展 Get Log Page、effects log、per-namespace SMART |
| Sanitize/thermal/self-test | 支持的命令需要相应非零能力字段，并再受 Feature/阈值/状态机限制 |
| ANA | 不只一个开关；还需 transition time、最大 ANA Group ID、group count 和具体 reportable state |
| 队列/namespace | `MAXCMD` 是每队列的并发处理建议，不是 SQ 深度；`NN` 是最大有效 NSID，不是现有 namespace 数 |
| SGL/Copy | `SGLS=00b` 时不允许 SGL，无论单独描述符位为何；`CDFS` 列 Copy descriptor format |

[PDF pp. 328-350](../_source/pages/page-328.md)

## 一个能力解释案例

控制器报告 `ONCS` 有某项可选 I/O 能力，只说明在它支持或继承的命令集集合中存在该能力；并不能证明当前选择的某个 I/O Command Set 一定支持该命令。需要再读 Commands Supported and Effects log，并结合当前 `CC.CSS`/profile。 [PDF pp. 340-342](../_source/pages/page-340.md)

## Identify Namespace：把“可创建”与“当前状态”分开

```text
namespace capability + 当前状态
        |
        +-- FPI ------ 格式化进度支持/剩余百分比
        +-- NSTAT ---- ready + I/O 性能影响
        +-- KPIOS ---- Key Per I/O 支持/启用 -> MAXKT
        `-- 资源归属
             +-- ANAGRPID / RGRPID 访问与可达性组
             `-- NVMSETID / ENDGID 存储分配层级
```

普通 NSID 返回一个具体 namespace 的数据；`NSID=FFFFFFFFh` 在支持时可返回创建/格式化时的 capability-only 模板，能力字段保留而非能力字段清零。inactive namespace 返回全零结构。 [PDF pp. 355-360](../_source/pages/page-355.md)

Namespace Identification Descriptor 是变长列表，`NIDL=0` 结束；同一列表不重复 descriptor type，且至少含一个耐久全局身份（EUI64、NGUID 或 UUID）。当启用多 I/O Command Set 时，它还带 namespace 的 CSI。身份 descriptor 在 namespace 生命周期内跨 reset/format 保留。 [PDF pp. 353-354](../_source/pages/page-353.md)

## 目录式结果都要分页读取

```text
CNS 02h：active NSID，输入 cursor 后最多 1,024 个递增 NSID
CNS 04h：NVM Set list，从 NVMSETID cursor 起最多 31 个有序 entry
CNS 10h：allocated NSID，最多 1,024 个递增 NSID
CNS 12h/13h：controller list，从 CNTID 起最多 2,047 个 ID
CNS 18h/19h：Domain / Endurance Group，从资源 ID 起的有序 entry
```

列表不是统一的“下一页”语义：NSID 使用严格大于 cursor，controller list 使用大于或等于 `CNTID`，Domain/Endurance Group 从资源 cursor 处或之后开始。主机必须按各结果的规定推进 cursor。 [PDF pp. 353-356, 361-364](../_source/pages/page-353.md)

## I/O Command Set 与迁移目录

I/O Command Set Combination 是一组可同时使用的命令集向量。组合零的 index 为零，后续支持组合顺序编号；I/O Command Set Profile Feature 选择活动向量，未选中的命令集被视为不支持。 [PDF pp. 364-365](../_source/pages/page-364.md)

Supported Controller State Formats 是迁移目录：一部分按 index 列出 NVMe Controller State 结构版本，另一部分用 UUID 列出厂商状态格式。Migration Receive/Send 使用这些 index，厂商 payload 的实际格式不在 Base Specification 中定义。 [PDF pp. 365-366](../_source/pages/page-365.md)

## 初学者最常踩的坑

- `CNTID=0h` 是合法 controller ID；是否有意义由 CNS 决定，不由数值是否为零决定。
- 面向 Revision 1.0/1.1 controller 时，只能发对应修订已经定义的 CNS；其他结果不确定。
- `MDTS=0h` 表示该字段不施加最大传输限制，不是禁止传输。
- 零值含义取决于字段：`NSSL=0` 是延迟未报告，`HMMIN=0` 是可请求任意可行值，零基数上限/计数则可能表示一个条目。
- `FNA.FNVMBS=1` 表示不支持 broadcast Format，且迫使 format/secure-erase 的独立 scope 位清零。
- `MNAN=0` 不表示零 namespace，而是回退到不超过 `NN` 的限制。 [PDF pp. 318, 322, 327-347](../_source/pages/page-318.md)

## 规范依据

- [Identify 命令格式、选择子与 CNS 矩阵，PDF 第 317-320 页](../_source/pages/page-317.md)
- [Identify Controller 能力 profile，PDF 第 321-350 页](../_source/pages/page-321.md)
- [Namespace、NVM Set 和命令集视图，PDF 第 351-360 页](../_source/pages/page-351.md)
- [已分配/拓扑/资源目录与迁移格式，PDF 第 361-366 页](../_source/pages/page-361.md)
