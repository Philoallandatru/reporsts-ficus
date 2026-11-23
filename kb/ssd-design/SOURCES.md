# SSD 固件与硬件设计资料来源目录

本目录优先收录一手来源。每条资料都标注用途，方便后续用 `llmwiki ingest` 或人工阅读。调研日期为 2026-08-12；涉及“最新版本”的条目应在使用前回到官方页面确认。

## 规范级资料

| 来源 | URL | 类型 | 覆盖主题 | 使用注意 |
|---|---|---|---|---|
| NVM Express Specifications | https://nvmexpress.org/specifications/ | 官方规范入口 | NVMe Base、Command Set、Transport、Management Interface | 主机接口和合规行为的最高优先级来源；硬件内部实现仍由厂商决定 |
| NVM Express Base Specification | https://nvmexpress.org/specification/nvm-express-base-specification/ | 官方规范 | Controller model、Submission/Completion Queue、Namespace、Admin/NVM 命令 | 截至 2026-08-12，官方页面显示 NVMe 2.4 已在 2026-08-04 发布；使用时固定版本 |
| ONFI Specifications | https://onfi.org/specs.html | 官方规范入口 | NAND flash electrical/protocol interface、timing、command/address/data phase | 适合建立 NAND controller 与 flash interface 术语，不替代具体 NAND datasheet |
| JEDEC JESD230G | https://www.jedec.org/ | 官方标准入口 | NAND Flash Interface Interoperability | 站内搜索 `JESD230G`；用于 NAND 互通，不替代 ONFI PDF 或 vendor datasheet |
| JEDEC JESD218 | https://www.jedec.org/standards-documents/docs/jesd218b02 | 官方标准 | SSD endurance rating method | 常与 JESD219 workload 一起看；偏可靠性与寿命评估 |
| JEDEC JESD219 | https://www.jedec.org/standards-documents/docs/jesd219a | 官方标准 | SSD endurance workloads | 适合定义 client/enterprise endurance workload |
| PCI-SIG Specifications | https://pcisig.com/specifications | 官方规范入口 | PCIe Base、CEM、M.2/related form factor specs | 部分规范需会员权限；公开页可作为入口 |
| OCP Data Center NVMe SSD Specification | https://www.opencompute.org/documents | 开放计算规范入口 | 数据中心 NVMe SSD 管理、telemetry、power、thermal、reliability | 版本较多，使用时固定具体 PDF 版本 |
| SNIA Solid State Storage Initiative | https://www.snia.org/forums/cmsi/knowledge/formfactors | 行业资料入口 | SSD form factor、管理、互操作与术语 | 作为产业视角补充，不替代 NVMe/PCIe/ONFI 规范 |
| SNIA | https://www.snia.org/ | 行业组织入口 | 存储网络、性能测试、持久内存和固态存储资料 | 用于行业术语、测试方法和白皮书入口 |
| Standards version pins | [sources/standards-version-pins.yml](sources/standards-version-pins.yml) | 本地机器可读版本清单 | NVMe、ONFI、JEDEC、PCI-SIG、OCP、SNIA 的目标版本和访问条件 | 区分版本已识别、访问受限、需人工核验和 hash 待补 |
| Standards public audit | [sources/standards-public-audit-2026-08-12.yml](sources/standards-public-audit-2026-08-12.yml) | 本地机器可读审计记录 | NVMe、OCP、SNIA、ONFI、JEDEC 公开页面/PDF 的版本核验结果 | 记录官方 URL、版本、访问条件、是否仍需人工确认 |
| Source artifact manifest | [sources/source-artifact-manifest.yml](sources/source-artifact-manifest.yml) | 本地机器可读下载/hash 清单 | NVMe、ONFI、JEDEC、PCI-SIG、OCP、SNIA 的 PDF/受限资料保存策略和 sha256 字段 | 只有 `downloaded_hash_verified` 状态才表示本地文件已存在且 hash 可验 |
| PDF artifact index | [sources/pdf-artifact-index.yml](sources/pdf-artifact-index.yml) | 本地机器可读 PDF 结构索引 | 已下载 PDF 的页数、主题路由、关联页面和后续抽取任务 | 由 `tools/validate_source_artifacts.py` 校验 PDF 魔数、sha256 和页数 |
| PDF topic locator | [sources/pdf-topic-locator.yml](sources/pdf-topic-locator.yml) | 本地机器可读主题定位索引 | Identify Controller、Firmware Commit、Sanitize、FDP、Telemetry、ZNS 等主题在已验证 PDF 中的候选页 | 由 `tools/locate_pdf_topics.py` 生成；命中页需要人工审读后才能作为设计结论 |

## 主机栈与驱动

| 来源 | URL | 类型 | 覆盖主题 | 使用注意 |
|---|---|---|---|---|
| Linux Kernel NVMe documentation | https://docs.kernel.org/nvme/index.html | 官方内核文档 | Linux NVMe subsystem、feature/quirk policy、NVMe PCI endpoint target | 可对照 `drivers/nvme/` 源码阅读 |
| Linux NVMe source | https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/nvme | 官方源码 | Host driver、target、PCI transport、fabrics | 行为受内核版本影响，记录 commit 或 kernel release |
| SPDK NVMe Driver | https://spdk.io/doc/nvme.html | 官方文档 | User-space polled-mode NVMe driver、queue pair、controller attach | 适合理解高性能主机侧访问模型 |
| SPDK source | https://github.com/spdk/spdk | 官方源码仓库 | NVMe driver、bdev、FTL module、examples | SPDK 的 FTL 更偏软件存储栈，不等同 SSD 控制器固件 |
| SPDK FTL | https://spdk.io/doc/ftl.html | 官方文档 | Host-side/block-device FTL、L2P、relocation、metadata recovery | 可借鉴工程化 FTL 结构，但边界不同于 SSD 内部 firmware |
| nvme-cli | https://github.com/linux-nvme/nvme-cli | 官方/社区源码 | Identify、log、format、sanitize、fw download/commit | 适合作为命令生成和设备调试工具 |
| libnvme | https://github.com/linux-nvme/libnvme | 官方/社区源码 | NVMe C library、spec structures、command helper | 适合写测试工具；协议字段仍以 NVMe spec 为准 |
| xNVMe | https://xnvme.io/ | 官方项目文档 | NVMe userspace library、命令、backend、testing | 适合跨 backend 写 NVMe 测试和实验工具 |
| fio | https://github.com/axboe/fio | 官方源码 | Flexible I/O workload、verify、latency histogram | 性能和数据一致性测试常用工具；配置要固定 |

## 开源 SSD/仿真平台

| 来源 | URL | 类型 | 覆盖主题 | 使用注意 |
|---|---|---|---|---|
| Cosmos+ OpenSSD documentation | https://cosmos-plus-openssd-doc.readthedocs.io/ | 官方项目文档 | FPGA SSD controller、固件结构、NAND request、scheduler、buffer | 最适合读“固件如何组织请求”的公开教材级项目 |
| Cosmos+ OpenSSD repository | https://github.com/Cosmos-OpenSSD/Cosmos-plus-OpenSSD | 官方源码 | 固件、RTL、host interface、flash controller | 代码与板卡/工具链绑定，先读 docs 再读源码 |
| OpenSSD Project | https://www.openssd-project.org/ | 官方项目站点 | OpenSSD boards、历史资料、开发套件 | 部分旧链接可能失效，需归档备份 |
| FEMU | https://github.com/MoatLab/FEMU | 官方源码 | QEMU-based NVMe SSD emulator、BlackBox/WhiteBox/OpenChannel/ZNS modes | 适合系统实验和协议/FTL 交互，不代表产品级时序 |
| SimpleSSD | https://github.com/SimpleSSD/SimpleSSD | 官方源码 | Full-system SSD simulator、controller/FTL/NAND model | 适合架构实验和教学 |
| MQSim | https://github.com/CMU-SAFARI/MQSim | 官方源码 | Multi-queue SSD simulation、channel/package/die/plane model、I/O scheduling | 适合论文复现实验；参数需校准 |
| FlashSim | https://github.com/flashsim/flashsim | 源码仓库 | SSD simulation、FTL experiments | 较旧，适合作为历史算法参考 |
| LightNVM / Open-Channel SSD docs | https://openchannelssd.readthedocs.io/ | 项目文档 | Open-channel SSD host-managed FTL | 适合理解把部分 FTL 责任移到 host 的设计 |
| Open-source implementation pins | [sources/open-source-implementation-pins.yml](sources/open-source-implementation-pins.yml) | 本地机器可读版本清单 | FEMU、SimpleSSD、MQSim、SPDK、Cosmos+、Linux NVMe、nvme-cli、libnvme 等 commit pins | 只固定阅读版本；构建环境和 smoke test 仍需后续补齐 |
| Open-source implementation smoke-test matrix | [sources/implementation-smoke-test-matrix.yml](sources/implementation-smoke-test-matrix.yml) | 本地机器可读复现矩阵 | 为每个 pinned 项目定义 clone/build/smoke command/expected signal/log path 口径 | 尚未执行构建；用于下一轮本地复现实验 |

## 经典论文与研究资料

| 来源 | URL | 类型 | 覆盖主题 | 使用注意 |
|---|---|---|---|---|
| DFTL | https://dl.acm.org/doi/10.1145/1508244.1508271 | 论文 DOI | Demand-based page mapping cache、DRAM 受限 FTL | 经典 FTL 论文，实验模型较早 |
| DFTL PDF | https://www.cse.psu.edu/~buu1/papers/ps/dftl-asplos09.pdf | 作者/学校 PDF | DFTL 算法细节、FlashSim | 与 DOI 搭配引用 |
| FAST | https://link.springer.com/chapter/10.1007/11807964_88 | 论文 DOI | Log block、fully associative sector translation | 适合理解 hybrid mapping 设计 |
| LDPC-in-SSD | https://www.usenix.org/conference/fast13/technical-sessions/presentation/zhao | USENIX 论文页 | LDPC、soft decoding、read latency、SSD ECC pipeline | 理解 LDPC 与 read-retry/latency 取舍的核心资料 |
| LightNVM FAST'17 | https://www.usenix.org/conference/fast17/technical-sessions/presentation/bjorling | USENIX 论文页 | Open-channel SSD、Linux host-managed FTL | 连接主机栈与 FTL 边界 |
| FEMU FAST'18 | https://www.usenix.org/system/files/conference/fast18/fast18-li.pdf | USENIX 论文 PDF | NVMe SSD emulator 设计、准确性边界 | 与 FEMU 源码一起读 |
| MQSim FAST'18 | https://www.usenix.org/conference/fast18/presentation/tavakkol | USENIX 论文页 | Multi-queue SSD simulation、端到端延迟 | 参数需和源码配置对应 |

## NAND、ECC、可靠性与硬件资料

| 来源 | URL | 类型 | 覆盖主题 | 使用注意 |
|---|---|---|---|---|
| ONFI | https://onfi.org/ | 官方组织 | NAND interface ecosystem | 先从规格页下载 PDF |
| JEDEC standards search | https://www.jedec.org/standards-documents | 官方标准库 | SSD endurance、UFS、NAND package/interface standards | 需按标准号固定引用 |
| University/SAFARI SSD research | https://safari.ethz.ch/projects_and_seminars/ | 研究主页 | NAND errors、retention、read disturb、SSD architecture | 研究论文需要结合模型假设使用 |
| Micron technical notes | https://www.micron.com/support/technical-notes | 厂商技术资料 | NAND behavior、ECC、power-loss、wear | 厂商资料有产品代际差异 |
| Micron NOR and NAND Flash Guide | https://assets.micron.com/adobe/assets/urn%3Aaaid%3Aaem%3Ae98bc653-e42d-45a7-9b8c-03cb3d488f05/renditions/original/as/nor-nand-flash-guide.pdf | 厂商 PDF | raw NAND、managed NAND、NOR/NAND 取舍、ECC/bad block/wear leveling 责任边界 | 已本地固定为 `ART-MICRON-NAND-FLASH-GUIDE`；不能替代具体 NAND part datasheet |
| Micron NAND Flash 101 | https://user.eng.umd.edu/~blj/CS-590.26/micron-tn2919.pdf | 厂商技术说明镜像 | NAND 基础、接口、可靠性、ECC | 版本较旧，适合基础概念 |
| Kioxia technical resources | https://www.kioxia.com/en-jp/business/memory/technical-resources.html | 厂商技术资料 | NAND flash technology、BiCS FLASH | 多为白皮书级，细节有限 |
| Western Digital ECC/DSP white paper | https://documents.westerndigital.com/content/dam/doc-library/en_us/assets/public/western-digital/collateral/white-paper/white-paper-the-application-of-ecc-dsp-to-flash-memory.pdf | 厂商白皮书 | ECC、DSP、NAND channel、可靠性 | 厂商视角，适合作为工程背景 |
| Western Digital technical documents | https://documents.westerndigital.com/ | 厂商资料库 | SSD、flash、数据中心存储白皮书 | 适合补充 ECC、性能、企业 SSD 背景 |

### 本地 Vendor Intake

| 来源 | 本地文件 | 覆盖主题 | 使用注意 |
|---|---|---|---|
| NAND vendor public materials intake | [sources/vendor-intake/nand-vendor-public-materials.md](sources/vendor-intake/nand-vendor-public-materials.md) | Micron、Kioxia、Samsung、SK hynix、YMTC、Western Digital 公开资料入口和参数抽取模板 | 公开资料多为入口；具体控制器参数必须回到 part number datasheet |
| NAND parameter extraction matrix | [sources/vendor-intake/nand-parameter-extraction-matrix.yml](sources/vendor-intake/nand-parameter-extraction-matrix.yml) | NAND geometry、timing、interface、ECC/read-retry、可靠性和参数可信度分层 | 用于把公开资料/受限 datasheet 转成可复现实验字段 |
| Micron NAND Flash Guide intake | [sources/vendor-intake/micron-nand-flash-guide-intake.md](sources/vendor-intake/micron-nand-flash-guide-intake.md) | 已固定 Micron family-level guide 的可用结论、不可用字段和下游映射 | 只适用于术语/责任边界，不能替代具体 Micron NAND datasheet |
| Controller/IP vendor public materials intake | [sources/vendor-intake/controller-vendor-public-materials.md](sources/vendor-intake/controller-vendor-public-materials.md) | AMD、Microchip、Marvell、Silicon Motion、Phison、Innogrit、Maxio 公开资料入口 | 公开 controller brief 不能替代内部 FTL/RTL 设计资料 |
| Controller/IP vendor extraction matrix | [sources/vendor-intake/controller-vendor-extraction-matrix.yml](sources/vendor-intake/controller-vendor-extraction-matrix.yml) | 控制器厂商公开材料的字段抽取、可信度分层和下游资产映射 | 用于把 vendor brief/guide 转成可追踪入口 |
| Controller/IP vendor sample registry | [sources/vendor-intake/controller-vendor-sample-registry.yml](sources/vendor-intake/controller-vendor-sample-registry.yml) | 记录首批 controller vendor 样本、后续固定步骤和相关资产 | 用于快速查看样本覆盖进度 |
| AMD PG329 NVMe Target Controller intake | [sources/vendor-intake/amd-pg329-nvmetc-intake.md](sources/vendor-intake/amd-pg329-nvmetc-intake.md) | NVMe target IP、queue/register、PRP fetch、work queue 术语 | 只适合作为 NVMe 前端模块参考 |
| Microchip Flashtec NVMe Controller intake | [sources/vendor-intake/microchip-flashtec-nvme-intake.md](sources/vendor-intake/microchip-flashtec-nvme-intake.md) | enterprise / data-center SSD controller、on-chip flash management、security 语言 | 只适合作为产品族和功能边界入口 |
| Marvell SSD Controllers intake | [sources/vendor-intake/marvell-ssd-controllers-intake.md](sources/vendor-intake/marvell-ssd-controllers-intake.md) | data-center SSD controller、LDPC、TLC/QLC/SLC 叙事 | 只适合作为 controller family 入口 |
| Silicon Motion SSD Controller intake | [sources/vendor-intake/silicon-motion-ssd-controller-intake.md](sources/vendor-intake/silicon-motion-ssd-controller-intake.md) | PCIe Gen5 / NVMe 2.0、enterprise 16/8-channel 叙事 | 只适合作为 controller family 入口 |
| Phison SSD Controller intake | [sources/vendor-intake/phison-ssd-controller-intake.md](sources/vendor-intake/phison-ssd-controller-intake.md) | PCIe Gen5、DRAM-less/E28/E31T、SmartCache 叙事 | 只适合作为 controller family 入口 |
| InnoGrit SSD Controller intake | [sources/vendor-intake/innogrit-ssd-controller-intake.md](sources/vendor-intake/innogrit-ssd-controller-intake.md) | IG5222/IG5636 brief、PCIe Gen4/Gen5、data-center 叙事 | 只适合作为 controller family 入口 |
| Maxio SSD Controller intake | [sources/vendor-intake/maxio-ssd-controller-intake.md](sources/vendor-intake/maxio-ssd-controller-intake.md) | PCIe / SATA SSD controllers、DRAM-less、Agile ECC、SmartCache | 只适合作为 controller family 入口 |
| NAND/controller/patent research notes | [sources/research-nand-controller-patent-notes.md](sources/research-nand-controller-patent-notes.md) | NAND vendor public intake、patent search portals、CPC tags、query starters | 调研侧记，后续应拆成正式 intake 或 versioned source 条目 |

## FPGA 与硬件参考设计

| 来源 | URL | 类型 | 覆盖主题 | 使用注意 |
|---|---|---|---|---|
| AMD NVMe Target Controller IP | https://www.amd.com/en/products/adaptive-socs-and-fpgas/intellectual-property/ef-di-nvmetc.html | 厂商 IP 官方页 | FPGA 内实现 NVMe device、QDMA、NVMe target | 商业 IP；用于模块边界参考 |
| AMD PG329 NVMe Target Controller | https://docs.amd.com/r/en-US/pg329-nvme-target-controller | 厂商产品指南 | NVMe target IP、PRP fetch、QDMA、寄存器/接口 | 不覆盖 NAND FTL |
| FPGA Drive AXI-MM PCIe examples | https://github.com/fpgadeveloper/fpga-drive-aximm-pcie | 开源参考设计 | FPGA/MPSoC 连接 M.2 NVMe SSD | 偏主机侧接 SSD，不是 SSD controller 内部 |
| FPGA NVMe hardware driver | https://github.com/mcrl/NVMe | 开源硬件项目 | FPGA-resident NVMe host controller | 需自行审查 license、活跃度和硬件限制 |
| BABOL software-defined NAND controller | https://exascale.info/assets/pdf/2024_micro_flash_controller.pdf | 论文 PDF | 软件定义 NAND controller、Cosmos+ 硬件 | 适合研究 NAND controller 与 FPGA 原型 |

## 后续搜集队列

- NAND vendor datasheet：Micron、Kioxia、Samsung、SK hynix、YMTC 的公开 datasheet、technical note、application note。
- Controller vendor 文档：Microchip/PMC、Marvell、Silicon Motion、Phison、Innogrit、Maxio 的公开 brief/app note。
- FPGA PCIe endpoint example：AMD/Xilinx、Intel FPGA、LitePCIe、QEMU PCI endpoint target。
- 测试工具：xNVMe、fio、blktests、SPDK perf、nvme-cli plugin。
- Patent 检索：FTL mapping、LDPC soft decoding、power-loss recovery、multi-stream placement、write cliff mitigation。
- 会议论文：FAST、USENIX ATC、OSDI/SOSP、MICRO/ISCA/HPCA、DATE/DAC、MSST。

## 本地研究索引

- [SSD 设计论文与 BibTeX 种子](BIBLIOGRAPHY.md)
- [SSD 专利检索索引](PATENT_INDEX.md)
- [Patent Intake Template](sources/patents/patent-intake-template.md)
