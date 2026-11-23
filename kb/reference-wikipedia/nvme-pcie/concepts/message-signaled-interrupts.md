---
type: concept
title: Message Signaled Interrupts
description: Message Signaled Interrupts (MSI) are a method of signaling interrupts,
  using special in-band messages to replace traditional out-of-band signals on dedicated
  interrupt lines.
tags:
- wikipedia
- wikipedia-en
timestamp: '2026-04-03T15:53:09Z'
x-wikipedia:
  site: en.wikipedia.org
  lang: en
  pageid: 4266780
  revisionId: 1346906830
  parentRevisionId: 1314441657
  wikidataId: Q476098
  canonicalUrl: https://en.wikipedia.org/wiki/Message_Signaled_Interrupts
  license: CC BY-SA; see licenseUrl and Wikimedia Terms of Use
  licenseUrl: https://creativecommons.org/licenses/by-sa/4.0/
  sourceApi: MediaWiki Action API
  fetchedAt: '2026-08-25T15:32:13Z'
  crawlDepth: 0
  sourceSeed: Message Signaled Interrupts
  relevanceScore: 25
  requiredKeywords:
  - direct memory access
  - interrupt
  - memory-mapped i/o
  - message signaled interrupt
  - msi
  - pci express
  - peripheral component interconnect
  matchedKeywords:
  - bus
  - controller
  - direct memory access
  - i/o
  - interrupt
  - io
  - memory
  - msi
  - pci express
  - peripheral component interconnect
  excludedKeywords: []
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# [Message Signaled Interrupts](https://en.wikipedia.org/wiki/Message_Signaled_Interrupts)

Message Signaled Interrupts (MSI) are a method of signaling interrupts, using special in-band messages to replace traditional out-of-band signals on dedicated interrupt lines. While message signaled interrupts are more complex to implement in a device, they have some significant advantages over pin-based out-of-band interrupt signalling, such as improved interrupt handling performance. This is in contrast to traditional interrupt mechanisms, such as the legacy interrupt request (IRQ) system.
Message signaled interrupts are supported in PCI bus since its version 2.2, and in later available PCI Express bus. Some non-PCI architectures also use message signaled interrupts.


Overview
Traditionally, a device has an interrupt line (pin) which it asserts when it wants to signal an interrupt to the host processing environment. This traditional form of interrupt signalling is an out-of-band form of control signalling since it uses a dedicated path to send such control information, separately from the main data path. MSI replaces those dedicated interrupt lines with in-band signalling, by exchanging special messages that indicate interrupts through the main data path. In particular, MSI allows...

## Wikipedia Links in This Bundle

- [Advanced Programmable Interrupt Controller](advanced-programmable-interrupt-controller.md)
- [Direct memory access](direct-memory-access.md)
- [Interrupt](interrupt.md)
- [PCI Express](pci-express.md)

## Wikipedia Links Not Included

- Control register
- Device driver
- FreeBSD
- GSC bus
- Haiku (operating system)
- Hewlett-Packard
- HyperTransport
- ISBN (identifier)
- In-band
- Interrupt controller
- Interrupt handler
- Interrupt request
- Linux
- Linux kernel
- List of Microsoft codenames
- Memory-mapped I/O
- Memory controller
- NetBSD
- OpenBSD
- Out-of-band data
- PCI-SIG

## Categories

- All articles with unsourced statements
- Articles with short description
- Articles with unsourced statements from January 2014
- CS1 errors: periodical ignored
- Digital electronics
- Interrupts
- Peripheral Component Interconnect
- Short description matches Wikidata

## Source

- [Message Signaled Interrupts](https://en.wikipedia.org/wiki/Message_Signaled_Interrupts)
- Revision: 1346906830
- License: CC BY-SA; see the page footer and Wikimedia Terms of Use.
