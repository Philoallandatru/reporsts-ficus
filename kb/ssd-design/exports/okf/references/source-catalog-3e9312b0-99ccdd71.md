---
title: source catalog
source: .\sources\source-catalog.md
ingestedAt: "2026-08-12T09:02:08.303Z"
sourceType: file
---

# SSD design source catalog for llmwiki

This seed catalog records high-trust sources to ingest for an SSD firmware and hardware design wiki.

## Standards

- NVM Express Specifications: https://nvmexpress.org/specifications/
  - Owns the host-visible NVMe protocol, command sets, transports, controller properties, queues, reset behavior, firmware download/commit behavior, logs, telemetry, sanitize, and power management.
- NVM Express Base Specification: https://nvmexpress.org/specification/nvm-express-base-specification/
  - Use a fixed version PDF when citing fields. As of 2026-08-12, official materials indicate NVMe 2.4 was released on 2026-08-04.
- ONFI Specifications: https://onfi.org/specs.html
  - Owns the Open NAND Flash Interface command, address, data, electrical, and timing model for NAND devices that implement ONFI.
- JEDEC JESD218: https://www.jedec.org/standards-documents/docs/jesd218b02
  - Defines SSD endurance rating methodology.
- JEDEC JESD219: https://www.jedec.org/standards-documents/docs/jesd219a
  - Defines endurance workloads for SSD rating.
- JEDEC JESD230G: https://www.jedec.org/
  - Search the JEDEC standards library for NAND Flash Interface Interoperability.
- PCI-SIG Specifications: https://pcisig.com/specifications
  - Owns PCIe base and form-factor related interface requirements.
- OCP Documents: https://www.opencompute.org/documents
  - Contains OCP Data Center NVMe SSD specifications and related data-center SSD requirements.

## Host software

- Linux NVMe documentation: https://docs.kernel.org/nvme/index.html
- Linux NVMe source: https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/nvme
- SPDK NVMe documentation: https://spdk.io/doc/nvme.html
- SPDK FTL documentation: https://spdk.io/doc/ftl.html
- SPDK source: https://github.com/spdk/spdk
- nvme-cli: https://github.com/linux-nvme/nvme-cli
- libnvme: https://github.com/linux-nvme/libnvme
- xNVMe: https://xnvme.io/
- fio: https://github.com/axboe/fio

## SSD implementation and simulation

- Cosmos+ OpenSSD docs: https://cosmos-plus-openssd-doc.readthedocs.io/
- Cosmos+ OpenSSD source: https://github.com/Cosmos-OpenSSD/Cosmos-plus-OpenSSD
- OpenSSD Project: https://www.openssd-project.org/
- FEMU: https://github.com/MoatLab/FEMU
- SimpleSSD: https://github.com/SimpleSSD/SimpleSSD
- MQSim: https://github.com/CMU-SAFARI/MQSim
- Open-Channel SSD docs: https://openchannelssd.readthedocs.io/

## Classic papers

- DFTL DOI: https://dl.acm.org/doi/10.1145/1508244.1508271
- DFTL PDF: https://www.cse.psu.edu/~buu1/papers/ps/dftl-asplos09.pdf
- FAST: https://link.springer.com/chapter/10.1007/11807964_88
- LDPC-in-SSD: https://www.usenix.org/conference/fast13/technical-sessions/presentation/zhao
- LightNVM FAST'17: https://www.usenix.org/conference/fast17/technical-sessions/presentation/bjorling
- FEMU FAST'18: https://www.usenix.org/system/files/conference/fast18/fast18-li.pdf
- MQSim FAST'18: https://www.usenix.org/conference/fast18/presentation/tavakkol

## Vendor and research resources

- Micron technical notes: https://www.micron.com/support/technical-notes
- Kioxia technical resources: https://www.kioxia.com/en-jp/business/memory/technical-resources.html
- ETH/SAFARI projects: https://safari.ethz.ch/projects_and_seminars/
- Western Digital technical documents: https://documents.westerndigital.com/
- SNIA: https://www.snia.org/

## FPGA and hardware references

- AMD NVMe Target Controller IP: https://www.amd.com/en/products/adaptive-socs-and-fpgas/intellectual-property/ef-di-nvmetc.html
- AMD PG329 NVMe Target Controller: https://docs.amd.com/r/en-US/pg329-nvme-target-controller
- FPGA Drive AXI-MM PCIe examples: https://github.com/fpgadeveloper/fpga-drive-aximm-pcie
- FPGA NVMe hardware driver: https://github.com/mcrl/NVMe
- BABOL software-defined NAND controller: https://exascale.info/assets/pdf/2024_micro_flash_controller.pdf

Use standards as the authority for interface claims. Use open-source projects as examples of implementation structure. Use papers and vendor notes for design-space intuition, reliability phenomena, and workload assumptions.

