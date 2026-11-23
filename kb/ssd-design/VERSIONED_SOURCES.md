# 版本化来源清单

`SOURCES.md` 记录资料入口；本文件记录需要固定版本、文件名、hash 或访问条件的资料。当前多数条目仍是待采集状态。

## 状态约定

- `pinned`：已固定版本和本地文件/hash。
- `identified`：已找到官方入口，但还未固定版本文件。
- `todo`：知道需要采集，但尚未找到稳定入口。
- `restricted`：需要会员、账户、购买或厂商授权。

## 规范

| ID | 标题 | 状态 | 固定版本目标 | 官方入口 | 本地文件/hash |
|---|---|---|---|---|---|
| SRC-NVME-BASE | NVM Express Base Specification | pinned | NVMe Base 2.4; local PDF/hash verified | https://nvmexpress.org/wp-content/uploads/NVM-Express-Base-Specification-Revision-2.4-Ratified-2026.07.31.pdf | sources/artifacts/nvmexpress/NVM-Express-Base-Specification-Revision-2.4-Ratified-2026.07.31.pdf; sha256 fe7647532c06859f2952d9db1f90165aa3e9375343d588d5444253f7dbb2c9bd |
| SRC-NVME-NVM | NVM Command Set Specification | pinned | NVM Command Set 1.3; local PDF/hash verified | https://nvmexpress.org/wp-content/uploads/NVM-Express-NVM-Command-Set-Specification-Revision-1.3-Ratified-2026.07.31.pdf | sources/artifacts/nvmexpress/NVM-Express-NVM-Command-Set-Specification-Revision-1.3-Ratified-2026.07.31.pdf; sha256 a5c192fe239777c3c7a70417c16317fcfc24445a8cd72832286651ce76cefc4b |
| SRC-NVME-MI | NVMe Management Interface | pinned | NVMe-MI 2.2; local PDF/hash verified | https://nvmexpress.org/wp-content/uploads/NVM-Express-Management-Interface-Specification-Revision-2.2-Ratified-2026.07.31.pdf | sources/artifacts/nvmexpress/NVM-Express-Management-Interface-Specification-Revision-2.2-Ratified-2026.07.31.pdf; sha256 1aad98ccb9daf9a23b0dcca2c12fde7c99b5bd1bb542cf928af740cd53261817 |
| SRC-NVME-ZNS | Zoned Namespace Command Set Specification | pinned | ZNS 1.5; local PDF/hash verified | https://nvmexpress.org/wp-content/uploads/NVM-Express-Zoned-Namespace-Command-Set-Specification-Revision-1.5-Ratified-2026.07.31.pdf | sources/artifacts/nvmexpress/NVM-Express-Zoned-Namespace-Command-Set-Specification-Revision-1.5-Ratified-2026.07.31.pdf; sha256 9301812b6da1228658d4975d9f6b8fa25f258e9d6e4def011bf2fe4c9812ff16 |
| SRC-NVME-FDP | Flexible Data Placement capability in NVMe Base/NVM Command Set | pinned | Covered by NVMe Base 2.4 and NVM Command Set 1.3; PDF/hash pending | https://nvmexpress.org/specification/nvm-command-set-specification/ | sources/standards-version-pins.yml; sources/standards-public-audit-2026-08-12.yml |
| SRC-NVME-BOOT | NVMe Boot Specification | pinned | NVMe Boot 1.4; official PDF link parsed; scripted download returned HTTP 525 | https://nvmexpress.org/wp-content/uploads/NVM-Express-Boot-Specification-Revision-1.4-Ratified-2026.07.31.pdf | sources/standards-version-pins.yml; sources/source-artifact-manifest.yml |
| SRC-ONFI | ONFI Specification | pinned | ONFI 5.2; PDF/hash pending | https://onfi.org/specs.html | sources/standards-version-pins.yml |
| SRC-JESD218 | JESD218 SSD Endurance | identified | JESD218B.02; manual verification/hash pending | https://www.jedec.org/standards-documents/docs/jesd218b02 | sources/standards-version-pins.yml |
| SRC-JESD219 | JESD219 SSD Workloads | identified | JESD219A; manual verification/hash pending | https://www.jedec.org/standards-documents/docs/jesd219a | sources/standards-version-pins.yml |
| SRC-JESD230 | NAND Flash Interface Interoperability | identified | JESD230G; manual verification/hash pending | https://www.jedec.org/ | sources/standards-version-pins.yml |
| SRC-PCIE-BASE | PCI Express Base Specification | restricted | PCIe Base 7.0; access restricted/hash pending | https://pcisig.com/specifications | sources/standards-version-pins.yml |
| SRC-PCIE-CEM | PCI Express Card Electromechanical Specification | restricted | CEM 6.0; access restricted/hash pending | https://pcisig.com/specifications | sources/standards-version-pins.yml |
| SRC-PCIE-M2 | PCI Express M.2 Specification | restricted | M.2 5.0; access restricted/hash pending | https://pcisig.com/specifications | sources/standards-version-pins.yml |
| SRC-OCP-NVME | OCP Data Center NVMe SSD Specification | pinned | Datacenter NVMe SSD Specification v2.6 (09252024); PDF/hash pending; v2.7 needs manual re-check | https://www.opencompute.org/documents/datacenter-nvme-ssd-specification-v2-6-2-pdf | sources/standards-version-pins.yml; sources/standards-public-audit-2026-08-12.yml |
| SRC-SNIA-PTS | SNIA Solid State Storage Performance Test Specification | pinned | SSS PTS v2.0.2; PDF/hash pending | https://www.snia.org/tech_activities/standards/curr_standards/pts | sources/standards-version-pins.yml; sources/standards-public-audit-2026-08-12.yml |

Artifact 下载和 sha256 状态见 [Source artifact manifest](sources/source-artifact-manifest.yml)。PDF 页数、主题路由和后续抽取任务见 [PDF artifact index](sources/pdf-artifact-index.yml)。主题候选页见 [PDF topic locator](sources/pdf-topic-locator.yml)。本清单中的 `PDF/hash pending` 只有在 manifest 条目变为 `downloaded_hash_verified` 后才算完成；当前 NVMe Base 2.4、NVM Command Set 1.3、ZNS 1.5 与 NVMe-MI 2.2 已完成本地 hash 固定。

## 开源实现

| ID | 标题 | 状态 | 固定版本目标 | 官方入口 | 本地文件/hash |
|---|---|---|---|---|---|
| SRC-COSMOS | Cosmos+ OpenSSD | pinned | HEAD on master queried 2026-08-12 | https://github.com/Cosmos-OpenSSD/Cosmos-plus-OpenSSD | 78601486bb5581e40628ec7e841dea8e97eff034; sources/open-source-implementation-pins.yml |
| SRC-FEMU | FEMU | pinned | HEAD on master queried 2026-08-12 | https://github.com/MoatLab/FEMU | 46e4261f997e39a6184febe8148a6c3449719119; sources/open-source-implementation-pins.yml |
| SRC-SIMPLESSD | SimpleSSD | pinned | HEAD on 2.0 queried 2026-08-12 | https://github.com/SimpleSSD/SimpleSSD | 2be371619a6533821741540ee2d8ce742c2dad2d; sources/open-source-implementation-pins.yml |
| SRC-MQSIM | MQSim | pinned | HEAD on master queried 2026-08-12 | https://github.com/CMU-SAFARI/MQSim | 51f0f2d3fed92d88ef4a0fa61a38024b07bf9d16; sources/open-source-implementation-pins.yml |
| SRC-SPDK | SPDK | pinned | HEAD on master queried 2026-08-12 | https://github.com/spdk/spdk | 804a8090b158cbaef613431711afbaefbc76e2ee; sources/open-source-implementation-pins.yml |
| SRC-LINUX-NVME | Linux NVMe | pinned | HEAD on torvalds/linux master queried 2026-08-12 | https://github.com/torvalds/linux/tree/master/drivers/nvme | f5bbbfec59b4e2fb7520a91de3df8a6174325d6a; sources/open-source-implementation-pins.yml |
| SRC-NVME-CLI | nvme-cli | pinned | HEAD on master queried 2026-08-12 | https://github.com/linux-nvme/nvme-cli | 0a77a7d326e509ad1464bcf49ed130df82312871; sources/open-source-implementation-pins.yml |
| SRC-LIBNVME | libnvme | pinned | HEAD on master queried 2026-08-12 | https://github.com/linux-nvme/libnvme | ad61ac8a319ad0823c1c9861eecbf66125f8b9a1; sources/open-source-implementation-pins.yml |
| SRC-OPENCHANNEL-QEMU | OpenChannelSSD qemu-nvme | pinned | HEAD on master queried 2026-08-12 | https://github.com/OpenChannelSSD/qemu-nvme | b6fb7eb1e9d708b920f24b559c503e68d0eb0329; sources/open-source-implementation-pins.yml |
| SRC-FLASHSIM-FORK | FlashSim accessible fork | pinned | HEAD on master queried 2026-08-12; original flashsim/flashsim unavailable | https://github.com/MatiasBjorling/flashsim | 53098b017a4dbbe27665a755000738ed70862141; sources/open-source-implementation-pins.yml |

Smoke-test 复现口径见 [Open-source implementation smoke-test matrix](sources/implementation-smoke-test-matrix.yml)。当前只定义最小验收信号，尚未完成本地 clone/build。

## NAND Vendor Datasheet 队列

| ID | Vendor | 状态 | 目标资料 | 入口 | 本地文件/hash |
|---|---|---|---|---|---|
| SRC-NAND-MICRON | Micron | pinned | Micron NOR and NAND Flash Guide; public guide, not part datasheet | https://assets.micron.com/adobe/assets/urn%3Aaaid%3Aaem%3Ae98bc653-e42d-45a7-9b8c-03cb3d488f05/renditions/original/as/nor-nand-flash-guide.pdf | sources/artifacts/vendors/micron/nor-nand-flash-guide.pdf; sha256 791d5f24f9d5fa4fcf780dd82cd330d0cd388cccaae3dbf0b17101e5bc3c788f |
| SRC-NAND-KIOXIA | Kioxia | todo | BiCS FLASH datasheet/app note | https://www.kioxia.com/ |  |
| SRC-NAND-SAMSUNG | Samsung | todo | V-NAND datasheet/white paper/app note | https://semiconductor.samsung.com/ |  |
| SRC-NAND-SKHYNIX | SK hynix | todo | NAND datasheet/app note | https://www.skhynix.com/ |  |
| SRC-NAND-YMTC | YMTC | todo | Xtacking NAND public material | https://www.ymtc.com/ |  |
| SRC-NAND-WDC | Western Digital / SanDisk | identified | ECC/DSP white paper、SSD technical documents | https://documents.westerndigital.com/ | sources/vendor-intake/nand-vendor-public-materials.md |
| SRC-NAND-PARAM-MATRIX | NAND parameter extraction matrix | identified | 用于固定每个 vendor/part 的 geometry、timing、ECC/read-retry 和可靠性字段 | sources/vendor-intake/nand-parameter-extraction-matrix.yml | sources/vendor-intake/nand-parameter-extraction-matrix.yml |

## Controller / FPGA / IP

| ID | 标题 | 状态 | 固定版本目标 | 官方入口 | 本地文件/hash |
|---|---|---|---|---|---|
| SRC-AMD-PG329 | AMD PG329 NVMe Target Controller | identified | 文档版本号 | https://docs.amd.com/r/en-US/pg329-nvme-target-controller |  |
| SRC-AMD-NVMETC | AMD NVMe Target Controller IP | identified | IP version | https://www.amd.com/en/products/adaptive-socs-and-fpgas/intellectual-property/ef-di-nvmetc.html |  |
| SRC-FPGA-NVME | FPGA NVMe hardware driver | identified | commit hash | https://github.com/mcrl/NVMe |  |
| SRC-BABOL | BABOL NAND controller paper | identified | paper version | https://exascale.info/assets/pdf/2024_micro_flash_controller.pdf |  |
| SRC-CTRL-VENDOR-MATRIX | Controller/IP vendor extraction matrix | identified | 控制器厂商公开材料字段抽取矩阵版本 | sources/vendor-intake/controller-vendor-extraction-matrix.yml | sources/vendor-intake/controller-vendor-extraction-matrix.yml |
| SRC-CTRL-VENDOR-SAMPLE-REGISTRY | Controller/IP vendor sample registry | identified | controller vendor sample registry version | sources/vendor-intake/controller-vendor-sample-registry.yml | sources/vendor-intake/controller-vendor-sample-registry.yml |
| SRC-CTRL-AMD-PG329-INTAKE | AMD PG329 NVMe Target Controller intake | identified | controller intake sample record | sources/vendor-intake/amd-pg329-nvmetc-intake.md | sources/vendor-intake/amd-pg329-nvmetc-intake.md |
| SRC-CTRL-MICROCHIP-FLASHTEC-INTAKE | Microchip Flashtec NVMe Controller intake | identified | controller intake sample record | sources/vendor-intake/microchip-flashtec-nvme-intake.md | sources/vendor-intake/microchip-flashtec-nvme-intake.md |
| SRC-CTRL-MARVELL-SSD-INTAKE | Marvell SSD Controllers intake | identified | controller intake sample record | sources/vendor-intake/marvell-ssd-controllers-intake.md | sources/vendor-intake/marvell-ssd-controllers-intake.md |
| SRC-CTRL-SILICONMOTION-INTAKE | Silicon Motion SSD Controller intake | identified | controller intake sample record | sources/vendor-intake/silicon-motion-ssd-controller-intake.md | sources/vendor-intake/silicon-motion-ssd-controller-intake.md |
| SRC-CTRL-PHISON-INTAKE | Phison SSD Controller intake | identified | controller intake sample record | sources/vendor-intake/phison-ssd-controller-intake.md | sources/vendor-intake/phison-ssd-controller-intake.md |
| SRC-CTRL-INNOGRIT-INTAKE | InnoGrit SSD Controller intake | identified | controller intake sample record | sources/vendor-intake/innogrit-ssd-controller-intake.md | sources/vendor-intake/innogrit-ssd-controller-intake.md |
| SRC-CTRL-MAXIO-INTAKE | Maxio SSD Controllers intake | identified | controller intake sample record | sources/vendor-intake/maxio-ssd-controller-intake.md | sources/vendor-intake/maxio-ssd-controller-intake.md |

## 论文和专利

| ID | 标题 | 状态 | 固定版本目标 | 官方入口 | 本地文件/hash |
|---|---|---|---|---|---|
| SRC-BIBLIOGRAPHY | SSD 设计论文与 BibTeX 种子 | identified | 固定每篇论文 DOI/PDF/会议页 | BIBLIOGRAPHY.md | BIBLIOGRAPHY.md |
| SRC-PATENT-INDEX | SSD 专利检索索引 | identified | 每个方向至少 5 个 patent family intake | PATENT_INDEX.md | PATENT_INDEX.md |
| SRC-RESEARCH-NAND-PATENT | NAND/controller/patent research notes | identified | 拆分为正式 vendor/patent intake | sources/research-nand-controller-patent-notes.md | sources/research-nand-controller-patent-notes.md |

## 采集要求

1. 每个 `identified` 条目在用于设计结论前，应固定具体版本或 commit。
2. 每个下载的 PDF 应记录文件名、来源 URL、访问日期和 sha256。
3. 受限资料不得直接复制进公开仓库；记录入口和访问条件即可。
4. 源码引用必须记录 commit hash，避免主分支漂移。
