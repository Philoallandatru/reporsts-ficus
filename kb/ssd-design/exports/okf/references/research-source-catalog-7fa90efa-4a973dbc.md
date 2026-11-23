---
title: research source catalog
source: .\sources\research-source-catalog.md
ingestedAt: "2026-08-12T09:02:08.975Z"
sourceType: file
---

# SSD firmware and hardware design research source catalog

Research date: 2026-08-12.

This file is a detailed ingestion queue for `llmwiki`. Prefer official specifications, official source repositories, official project documentation, vendor technical documents, and paper DOI/conference pages. Use standards for interface claims, source code for implementation structure, papers for design-space reasoning, and vendor documents for product constraints.

## Architecture and standards

| Title | URL | Type | Topics | Notes |
|---|---|---|---|---|
| NVM Express Specifications | https://nvmexpress.org/specifications/ | Official specification index | NVMe Base, Command Sets, transports, NVMe-MI | Highest authority for host-visible NVMe behavior. |
| NVM Express Base Specification | https://nvmexpress.org/specification/nvm-express-base-specification/ | Official specification | Controller model, queues, namespaces, Admin/NVM commands | As of 2026-08-12, official materials indicate NVMe 2.4 was released on 2026-08-04. Pin a specific PDF version before citing fields. |
| PCI-SIG Specifications | https://pcisig.com/specifications | Official specification index | PCIe Base, configuration, transaction/link/physical layers | Some documents require membership or purchase. |
| PCI Express Base Specification overview | https://pcisig.com/specification-overview/pci-express-base | Official overview | PCIe architecture and compatibility | Overview only; use full spec for implementation. |
| ONFI Specifications | https://onfi.org/specs.html | Official specification index | NAND command set, timing, NV-DDR/NV-LPDDR, parameter page | Download PDFs manually if automated fetch is blocked. |
| ONFI Home | https://www.onfi.org/ | Official organization site | ONFI scope and ecosystem | Confirms ONFI is a raw NAND interface, not a host SSD protocol. |
| JEDEC JESD230G | https://www.jedec.org/ | Official standards organization | NAND interface interoperability | Search for `JESD230G` on JEDEC. |
| JEDEC JESD218/JESD219 | https://www.jedec.org/ | Official standards organization | SSD endurance and workload methodology | Use for TBW, UBER, endurance testing, and workload definitions. |

## NAND media and reliability background

| Title | URL | Type | Topics | Notes |
|---|---|---|---|---|
| Micron NOR NAND Flash Guide | https://assets.micron.com/adobe/assets/urn%3Aaaid%3Aaem%3Ae98bc653-e42d-45a7-9b8c-03cb3d488f05/renditions/original/as/nor-nand-flash-guide.pdf | Vendor guide | Raw NAND vs managed NAND, ECC, bad blocks, wear leveling | Good system constraints overview; not a device datasheet. |
| Micron TN-29-19 NAND Flash 101 | https://user.eng.umd.edu/~blj/CS-590.26/micron-tn2919.pdf | Vendor technical note mirror | NAND basics, interface, reliability, ECC | Older but useful for fundamentals. |
| KIOXIA BiCS FLASH | https://europe.kioxia.com/en-mea/business/memory/bics.html | Vendor technical page | 3D NAND generations and direction | Technical marketing, not controller algorithm detail. |
| Samsung 2bit 3D V-NAND White Paper | https://s7d2.scene7.com/is/content/SamsungUS/samsungbusiness/products/computing/ssd/ssds-for-enterprise-storage/20170815/2bit_V-NAND_White_Paper.pdf | Vendor white paper | 3D V-NAND, CTF, cell interference | Older, Samsung-specific framing. |
| KIOXIA Wear Leveling Brief | https://americas.kioxia.com/content/dam/kioxia/en-us/business/memory/mlc-nand/asset/KIOXIA_Managed_Flash_BOS_P3_Understanding_Wear_Leveling_Tech_Brief.pdf | Vendor technical brief | Wear leveling and managed flash background | Conceptual, not product firmware detail. |
| Western Digital firmware updates support | https://support-en.wd.com/app/answers/detailweb/a_id/50745/~/firmware-download-and-updates-for-western-digital-internal-and-external-drives | Vendor support doc | Firmware versions and update practice | Useful for production firmware management reality. |

## FTL, mapping, GC, wear leveling

| Title | URL | Type | Topics | Notes |
|---|---|---|---|---|
| DFTL: A Flash Translation Layer Employing Demand-Based Selective Caching | https://dl.acm.org/doi/10.1145/1508244.1508271 | Paper DOI | Page-level mapping, mapping cache, address translation | Classic FTL paper. |
| DFTL PDF | https://www.cse.psu.edu/~buu1/papers/ps/dftl-asplos09.pdf | Author/school PDF | DFTL algorithm and FlashSim | Use with DOI. |
| FAST | https://link.springer.com/chapter/10.1007/11807964_88 | Paper DOI | Log block and fully associative sector translation | Classic hybrid mapping design. |
| Log Buffer-Based FTL | https://dl.acm.org/doi/10.1145/1275986.1275990 | Paper DOI | FAST extension, merge cost, log block utilization | Classic FTL source. |
| Garbage Collection Techniques for Flash-Resident Page-Mapping FTLs | https://arxiv.org/abs/1504.01666 | Paper preprint | Page-mapping FTL and GC metadata | Verify publication before formal citation. |
| LightNVM FAST'17 | https://www.usenix.org/conference/fast17/technical-sessions/presentation/bjorling | USENIX paper page | Host-managed FTL and PPA interface | Important host/device boundary paper. |
| Open-Channel SSD: What Is It Good For? | https://vldb.org/cidrdb/papers/2020/p17-picoli-cidr20.pdf | CIDR paper PDF | Open-channel SSD and database co-design | System co-design, not NAND timing. |

## ECC, LDPC, reliability

| Title | URL | Type | Topics | Notes |
|---|---|---|---|---|
| LDPC-in-SSD | https://www.usenix.org/conference/fast13/technical-sessions/presentation/zhao | USENIX paper page | LDPC, soft decoding, read latency, ECC pipeline | Classic SSD LDPC paper. |
| LDPC-in-SSD ACM record | https://dl.acm.org/doi/10.5555/2591272.2591298 | Paper DOI | LDPC latency optimization | Use with USENIX page. |
| Western Digital ECC/DSP white paper | https://documents.westerndigital.com/content/dam/doc-library/en_us/assets/public/western-digital/collateral/white-paper/white-paper-the-application-of-ecc-dsp-to-flash-memory.pdf | Vendor white paper | ECC, DSP, NAND channel reliability | Vendor perspective. |
| Errors in Flash-Memory-Based SSDs | https://arxiv.org/abs/1711.11427 | Paper/survey | NAND error characterization, read disturb, retention | Verify formal publication when citing. |
| Error Characterization, Mitigation, and Recovery in Flash Memory Based SSDs | https://arxiv.org/abs/1706.08642 | Paper/survey | Error sources, mitigation, recovery | Useful reliability framework. |
| ONFI 2.3 ECC offload announcement | https://investors.micron.com/news-releases/news-release-details/onfi-introduces-new-23-specification-ecc-offload-functionality | Official/member announcement | ECC offload and EZ-NAND | Announcement only; fields belong in the ONFI spec. |

## OpenSSD and Cosmos+

| Title | URL | Type | Topics | Notes |
|---|---|---|---|---|
| The OpenSSD Project | https://www.openssd-project.org/ | Official project site | OpenSSD project entry | Some links are old; source repos are authoritative. |
| OpenSSD Platforms | https://www.openssd-project.org/platforms/ | Official project docs | Jasmine, Cosmos, Cosmos+ platforms | Good platform selection page. |
| Cosmos+ overview | https://www.openssd-project.org/cosmospl/overview/ | Official project docs | Software, firmware, RTL package | Read before source. |
| Cosmos+ technical resources | https://www.openssd-project.org/cosmospl/resources/ | Official project docs | Tutorial, boot guide, papers, firmware notes | Official learning path. |
| Cosmos-plus-OpenSSD | https://github.com/Cosmos-OpenSSD/Cosmos-plus-OpenSSD | Official source repo | Firmware, RTL, Vivado/Xilinx project, GreedyFTL | Highest authority for this platform. |
| Cosmos+ tutorial PDF | https://raw.githubusercontent.com/Cosmos-OpenSSD/Cosmos-plus-OpenSSD/master/doc/Cosmos%2B%20OpenSSD%202017%20Tutorial.pdf | Official tutorial | Board setup, firmware build, NVMe, FTL, debug | Toolchain is old; pin environment. |
| Cosmos+ rapid prototype paper | https://repository.hanyang.ac.kr/handle/20.500.11754/169320 | Paper page | FPGA prototype, PCIe/NVMe controller, flash controller | Key design-intent paper. |
| Cosmos+ ToS PDF | https://www.openssd-project.org/002590842914/002473402402/cosmospl/tos20.pdf | Project/paper PDF | Single-thread firmware, NVMe manager, FTL, scheduler | Useful source-code map. |
| OCSSD-plus | https://github.com/Cosmos-OpenSSD/OCSSD-plus | Related source repo | Open-channel SSD on Cosmos+ | Host FTL and minimal device firmware. |

## Simulation and experimentation

| Title | URL | Type | Topics | Notes |
|---|---|---|---|---|
| FEMU | https://github.com/MoatLab/FEMU | Official source repo | QEMU/KVM NVMe SSD emulator, blackbox, OCSSD, ZNS | Fast experimentation, not cycle-accurate NAND. |
| FEMU FAST'18 paper | https://www.usenix.org/system/files/conference/fast18/fast18-li.pdf | USENIX paper PDF | FEMU design, accuracy, extensibility | Explains accuracy boundaries. |
| SimpleSSD | https://simplessd.org/ | Official docs | Full-system SSD simulator | Good architecture/system evaluation platform. |
| SimpleSSD-FullSystem | https://github.com/SimpleSSD/SimpleSSD-FullSystem | Official source repo | gem5-integrated SimpleSSD | Match docs and branch. |
| SimpleSSD-Standalone | https://github.com/SimpleSSD/SimpleSSD-Standalone | Official source repo | Standalone SSD simulator | Easier experiments without full gem5. |
| MQSim | https://github.com/CMU-SAFARI/MQSim | Official source repo | NVMe/SATA SSD simulator, multi-queue, latency | Read with FAST'18 paper. |
| MQSim FAST'18 paper | https://www.usenix.org/conference/fast18/presentation/tavakkol | USENIX paper page | Modern multi-queue SSD modeling | Pair with parameter files. |
| FlashSim paper | https://dl.acm.org/doi/10.1109/SIMUL.2009.17 | Paper DOI | NAND SSD simulator and FTL comparisons | Older but historically useful. |
| Extended FlashSim | https://github.com/MatiasBjorling/flashsim | Source repo | BAST, FAST, DFTL prototypes | Not the original main repo; inspect before reuse. |

## Linux, nvme-cli, libnvme, SPDK

| Title | URL | Type | Topics | Notes |
|---|---|---|---|---|
| Linux NVMe documentation | https://docs.kernel.org/nvme/index.html | Official kernel docs | NVMe subsystem, feature/quirk policy, target | Highest authority for mainline Linux behavior. |
| Linux NVMe feature and quirk policy | https://docs.kernel.org/nvme/feature-and-quirk-policy.html | Official kernel docs | Supported features, quirks, vendor extension policy | Required for upstream behavior questions. |
| Linux NVMe driver information | https://nvmexpress.org/drivers/linux-driver-information/ | NVMe official info | Linux driver location and support | Entry point; source is the kernel tree. |
| Linux NVMe host PCI source | https://github.com/torvalds/linux/blob/master/drivers/nvme/host/pci.c | Official source mirror | PCI-attached NVMe host driver | Pin commit for experiments. |
| Linux NVMe core source | https://github.com/torvalds/linux/blob/master/drivers/nvme/host/core.c | Official source mirror | Controller lifecycle, namespaces, admin/I/O path | Read with block layer. |
| nvme-cli | https://github.com/linux-nvme/nvme-cli | Official/community source | Identify, logs, firmware, format, sanitize | Useful command generator. |
| libnvme | https://github.com/linux-nvme/libnvme | Official/community source | NVMe C library and spec structures | Useful for test tools. |
| SPDK docs | https://spdk.io/doc/ | Official docs | Userspace drivers, bdev, NVMe, NVMe-oF | Highest authority for SPDK behavior. |
| SPDK NVMe driver | https://spdk.io/doc/nvme.html | Official docs | Userspace NVMe driver, MMIO, zero-copy, polling | Requires hugepages and device binding in practice. |
| SPDK FTL | https://spdk.io/doc/ftl.html | Official docs | FTL bdev, L2P, cache bdev, recovery | Host-side/block-device FTL, not product SSD firmware. |
| SPDK lib/nvme | https://github.com/spdk/spdk/tree/master/lib/nvme | Official source | Userspace NVMe driver | Good queue pair and transport reference. |
| SPDK lib/ftl | https://github.com/spdk/spdk/tree/master/lib/ftl | Official source | FTL, L2P, relocation, metadata | Public engineering FTL reference. |

## FPGA, hardware references, and NVMe IP

| Title | URL | Type | Topics | Notes |
|---|---|---|---|---|
| AMD NVMe Target Controller IP | https://www.amd.com/en/products/adaptive-socs-and-fpgas/intellectual-property/ef-di-nvmetc.html | Vendor IP page | FPGA NVMe device target, QDMA | Commercial IP; useful module boundary reference. |
| AMD PG329 NVMe Target Controller | https://docs.amd.com/r/en-US/pg329-nvme-target-controller | Vendor product guide | NVMe target IP, registers, WQE, PRP fetch, QDMA | Does not cover NAND FTL. |
| FPGA Drive AXI-MM PCIe examples | https://github.com/fpgadeveloper/fpga-drive-aximm-pcie | Open reference design | FPGA/MPSoC/ACAP to M.2 NVMe SSD | Host-side, not internal SSD controller. |
| FPGA Drive | https://www.fpgadrive.com/ | Project/product site | FPGA to NVMe SSD reference designs | Bring-up and adapter context. |
| FPGA NVMe hardware driver | https://github.com/mcrl/NVMe | Open hardware project | FPGA-resident NVMe host controller | Inspect license, activity, and hardware limits. |
| Design Gateway NVMe-IP | https://dgway.com/NVMe-IP_X_E.html | Vendor IP page | FPGA NVMe host controller | Commercial IP overview only. |
| Missing Link NVMe Streamer | https://devzone.missinglinkelectronics.com/application-notes/nvme-streaming/ | Vendor application note | FPGA high-speed streaming to NVMe SSD | Application design, not SSD firmware. |
| BABOL software-defined NAND controller | https://exascale.info/assets/pdf/2024_micro_flash_controller.pdf | Paper PDF | NAND controller design on Cosmos+ hardware | Good NAND-controller research reference. |
| FSSD | https://github.com/UIUC-ChenLab/FSSD | Research source repo | FPGA SSD research using AMD/Xilinx NVMe target | Depends on restricted/commercial Xilinx material. |

