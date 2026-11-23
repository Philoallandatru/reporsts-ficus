# SSD 专利检索索引

本页不是法律意见，也不判断专利有效性或侵权风险。它只作为技术资料采集入口，帮助后续围绕 FTL metadata、掉电保护、LDPC、SLC cache、placement hint 等方向做公开专利阅读。

机器可读采集队列见 [patent-intake-matrix.yml](sources/patent-intake-matrix.yml)。如果要新增专利方向或补族信息，先把方向放进采集矩阵，再补 family、assignee 和 claim summary。

## 检索入口

| 入口 | URL | 用途 | 注意 |
|---|---|---|---|
| Google Patents Advanced Search | https://www.google.com/advanced_patent_search | 全文检索、按 assignee、CPC、日期过滤 | 适合先建立专利族候选；不要把搜索命中当作结论 |
| USPTO Patent Center / Patent Public Search | https://www.uspto.gov/patents/search | 美国专利官方检索 | 用于核对法律状态、公开日和权利要求 |
| Google Patents BigQuery dataset | https://www.kaggle.com/datasets/bigquery/google-patents-research | 批量分析、族群聚类、引用关系 | 需要 BigQuery/Kaggle 环境，适合后续规模化处理 |

## 推荐检索式

| 方向 | Google Patents 查询词 | 重点 assignee | 抽取字段 |
|---|---|---|---|
| FTL metadata recovery | `"flash translation layer" "metadata" "power loss"` | SanDisk/Western Digital, Samsung, Micron, Kioxia, SK hynix | checkpoint、journal、mapping rebuild、P2L、superblock |
| PLP backup | `"solid state drive" "power loss protection" volatile memory` | Samsung, Western Digital, Kioxia, Phison, Silicon Motion | capacitor、flush ordering、read-only fallback、backup window |
| LDPC soft decoding | `"NAND flash" "LDPC" "soft decoding" "read threshold"` | Western Digital/SanDisk, Samsung, Micron, SK hynix | LLR、read retry、threshold voltage、hard/soft escalation |
| SLC cache | `"solid state drive" "SLC cache" destage` | Samsung, Western Digital, Micron, Phison, Silicon Motion | cache admission、TLC/QLC fold、write cliff、background destage |
| Placement hints / streams | `"NVMe" streams "flash translation layer"` | Western Digital, Samsung, Kioxia, Meta, Microsoft | stream ID、FDP、ZNS、tenant placement、GC isolation |
| Controller hardware acceleration | `"SSD controller" "flash translation layer" hardware accelerator` | Samsung, Kioxia, Western Digital, Marvell, Microchip | DMA、queue manager、address translation engine、ECC offload |

## Seed Patents / Patent Pages

| Topic | Patent page | 可用信息 | 局限 |
|---|---|---|---|
| FTL apparatus | https://patents.google.com/patent/US7890693B2/en | 可作为 FTL 硬件/控制单元术语入口，包含 address converting、flash address register 等模块语言 | 年代较早，模块划分不能直接代表现代 NVMe SSD |
| PLP for SSD | https://patents.google.com/patent/US20170185335A1/en | 可用于抽取 PLP 电源、volatile memory、controller、NAND backup 的权利要求语言 | 只说明一种实现族，不能代替 OCP/NVMe 合规要求 |
| LDPC LLR in NAND | https://patents.google.com/patent/US9337865B2/en | 可用于理解 soft-decision LDPC、LLR、read threshold voltage 的专利表述 | 不等于具体 NAND vendor 的 retry table 或 decoder 实现 |
| Placement / AOS / ZNS | https://patents.google.com/patent/US20230289078A1/en | 可用于理解 append-only streams、ZNS、placement hint 与 GC 责任转移 | 术语与 NVMe FDP/streams 需要回到 NVMe 规范核对 |
| Flash power failure | https://patents.google.com/patent/US7350105B2/en | 可作为 power-failure transaction/recovery 的老专利入口 | 更偏 flash 文件系统，不是现代 SSD controller 专属 |
| SSD write cache backup | https://patents.google.com/patent/US20220342591A1/en | 可用于抽取 controller cache、backup cache、write failure fallback 的模式 | 申请状态和适用产品需另查 |

## 分类建议

### FTL Metadata / Recovery

抽取重点：

- mapping entry 生命周期：host write、journal、checkpoint、GC move、rebuild。
- 断电窗口：host completion before/after NAND program、mapping update before/after checkpoint。
- recovery source：journal、P2L、block metadata、superblock、sequence number。
- 幂等性：重复 replay、stale physical page、dual valid copies。

### LDPC / Read Retry

抽取重点：

- hard decode failure 后的 retry ladder。
- read threshold / LLR / soft information 的生成。
- telemetry：retry count、corrected bits、uncorrectable escalation。
- 对 latency、power、thermal 的影响。

### PLP / Cache Protection

抽取重点：

- 掉电检测阈值、hold-up time、capacitor health。
- volatile buffer、metadata buffer、host-completed data 的 flush priority。
- PLP failure 后是否 read-only、namespace offline 或进入 degraded mode。

### SLC Cache / Write Cliff

抽取重点：

- SLC admission 和 eviction。
- SLC-to-TLC/QLC fold 或 destage。
- cache full 时的 host write latency cliff。
- cache metadata 的 checkpoint/recovery。

### Placement / Streams / FDP / ZNS

抽取重点：

- host-provided grouping hint 如何映射到 erase block / superblock / reclaim unit。
- hint 错误或 tenant 混写时的 fallback。
- 与 GC isolation、write amplification、QoS 的关系。
- 与 NVMe streams、ZNS、FDP 规范术语的差异。

## 后续动作

1. 每个方向至少选 5 个同族专利，建立 `sources/patents/` intake 文件。
2. 对每个 patent family 记录 assignee、priority date、publication number、claim summary、设计启发和不确定点。
3. 只把专利用作工程启发和术语来源；合规、接口行为和测试要求仍回到 NVMe、ONFI、JEDEC、OCP 等规范。
4. 先在 [patent-intake-matrix.yml](sources/patent-intake-matrix.yml) 里确认方向和采集状态，再去写单篇 intake。
