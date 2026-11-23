---
type: concept
title: Memory-mapped I/O and port-mapped I/O
description: Memory-mapped I/O (MMIO) and port-mapped I/O (PMIO) are two complementary
  methods of performing input/output (I/O) between the central processing unit (CPU)
  and peripheral devices in a computer (often mediating access v...
tags:
- wikipedia
- wikipedia-en
timestamp: '2026-03-30T20:50:39Z'
x-wikipedia:
  site: en.wikipedia.org
  lang: en
  pageid: 335157
  revisionId: 1346254845
  parentRevisionId: 1316160924
  wikidataId: Q891094
  canonicalUrl: https://en.wikipedia.org/wiki/Memory-mapped_I/O_and_port-mapped_I/O
  license: CC BY-SA; see licenseUrl and Wikimedia Terms of Use
  licenseUrl: https://creativecommons.org/licenses/by-sa/4.0/
  sourceApi: MediaWiki Action API
  fetchedAt: '2026-08-25T15:32:13Z'
  crawlDepth: 0
  sourceSeed: Memory-mapped I/O
  relevanceScore: 17
  requiredKeywords:
  - memory-mapped i/o
  - mmio
  matchedKeywords:
  - i/o
  - io
  - memory
  excludedKeywords: []
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# [Memory-mapped I/O and port-mapped I/O](https://en.wikipedia.org/wiki/Memory-mapped_I/O_and_port-mapped_I/O)

Memory-mapped I/O (MMIO) and port-mapped I/O (PMIO) are two complementary methods of performing input/output (I/O) between the central processing unit (CPU) and peripheral devices in a computer (often mediating access via chipset). An alternative approach is using dedicated I/O processors, commonly known as channels on mainframe computers, which execute their own instructions.
Memory-mapped I/O uses the same address space to address both main memory and I/O devices. The memory and registers of the I/O devices are mapped to (associated with) address values, so a memory address may refer to either a portion of physical RAM or to memory and registers of the I/O device. Thus, the CPU instructions used to access the memory (e.g. MOV ...) can also be used for accessing devices. Each I/O device either monitors the CPU's address bus and responds to any CPU access of an address assigned to that device, connecting the system bus to the desired device's hardware register, or uses a dedicated bus.
To accommodate the I/O devices, some areas of the address bus used by the CPU must be reserved for I/O and must not be available for normal physical memory; the range of addresses used for I/O devices...

## Wikipedia Links in This Bundle

- None

## Wikipedia Links Not Included

- 1-bit computing
- 12-bit computing
- 128-bit computing
- 16-bit
- 16-bit computing
- 24-bit computing
- 256-bit computing
- 32-bit
- 32-bit computing
- 3 GB barrier
- 4-bit computing
- 48-bit computing
- 512-bit computing
- 64-bit
- 64-bit computing
- 640 KB barrier
- 8-bit
- 8-bit computing
- ACPI
- AI accelerator
- AMD
- ARM architecture family
- Abstract machine
- Adapteva
- Adder (electronics)

## Categories

- All articles needing additional references
- Articles needing additional references from August 2010
- Articles with short description
- Input/output
- Short description is different from Wikidata
- Use dmy dates from December 2023
- Use list-defined references from December 2023

## Source

- [Memory-mapped I/O and port-mapped I/O](https://en.wikipedia.org/wiki/Memory-mapped_I/O_and_port-mapped_I/O)
- Revision: 1346254845
- License: CC BY-SA; see the page footer and Wikimedia Terms of Use.
