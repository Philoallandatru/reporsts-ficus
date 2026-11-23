---
title: seed
source: .\sources\seed.md
ingestedAt: "2026-08-12T09:02:08.571Z"
sourceType: file
---

# SSD firmware and hardware design seed notes

An SSD controller turns host block I/O into NAND operations. The host-visible side is governed by NVMe over PCIe or another NVMe transport; the internal side is governed by NAND behavior and controller firmware policy.

The front end of an NVMe SSD includes PCIe endpoint logic, NVMe controller registers, queue fetch and completion logic, DMA, interrupt generation, and command dispatch. The existing `nvme-wiki` and `pcie-wiki` in this workspace should remain the primary local references for those protocol layers.

The back end includes flash channels, chip-enable selection, die/LUN/plane parallelism, command/address/data phase handling, ECC or LDPC encode/decode, data scrambling, bad-block handling, and read-retry support. ONFI is the primary public interface specification for many NAND devices, while vendor datasheets provide the device-specific timing and command details.

SSD firmware is dominated by the Flash Translation Layer. The FTL maps host LBAs to physical flash locations, chooses write placement, keeps mapping metadata durable, performs garbage collection, balances wear, refreshes vulnerable data, handles errors, and coordinates background work with host QoS. FTL design is the place where product goals such as latency, write amplification, endurance, DRAM cost, and recovery time collide.

Power-loss handling is a cross-cutting design concern. Firmware needs an ordering model for data and metadata, hardware needs power-loss detection and enough hold-up energy for emergency commits, and verification needs fault injection across queue, DMA, cache, metadata, and NAND program states.

Open implementations and simulators cover different layers. Cosmos+ OpenSSD is useful for reading firmware and FPGA-oriented controller structure. FEMU is useful for host-system experiments with emulated NVMe SSDs. SimpleSSD and MQSim are useful for architecture and FTL experiments. SPDK and Linux are useful host-side references for queueing, commands, reset, and interoperability.

The next engineering pages should cover concrete FTL data structures, power-loss recovery, ECC/LDPC reliability management, hardware module boundaries, verification matrices, source-code reading guides, minimal controller implementation stages, NAND media parameters, performance/QoS/write amplification, production compliance, glossary terms, requirement-to-verification traceability, NVMe command lifecycle, metadata format and recovery conventions, fault injection catalogs, architecture diagrams, read/write flow diagrams, recovery flow diagrams, and test plan templates. A useful implementation-oriented wiki page should identify design goals, durable state, volatile state, main state machine, failure cases, and verification points.
