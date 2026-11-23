---
type: concept
title: Single-root input/output virtualization
description: In virtualization, single root input/output virtualization (SR-IOV) is
  a specification that allows the isolation of PCI Express resources for manageability
  and performance reasons.
tags:
- wikipedia
- wikipedia-en
timestamp: '2024-12-27T23:36:19Z'
x-wikipedia:
  site: en.wikipedia.org
  lang: en
  pageid: 46996238
  revisionId: 1265644962
  parentRevisionId: 1183302780
  wikidataId: Q16625626
  canonicalUrl: https://en.wikipedia.org/wiki/Single-root_input/output_virtualization
  license: CC BY-SA; see licenseUrl and Wikimedia Terms of Use
  licenseUrl: https://creativecommons.org/licenses/by-sa/4.0/
  sourceApi: MediaWiki Action API
  fetchedAt: '2026-08-25T15:32:13Z'
  crawlDepth: 0
  sourceSeed: Single-root input/output virtualization
  relevanceScore: 19
  requiredKeywords:
  - pci express
  - peripheral component interconnect
  - single-root input/output virtualization
  - sr-iov
  matchedKeywords:
  - i/o
  - io
  - pci express
  - peripheral component interconnect
  - sr-iov
  excludedKeywords: []
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# [Single-root input/output virtualization](https://en.wikipedia.org/wiki/Single-root_input/output_virtualization)

In virtualization, single root input/output virtualization (SR-IOV) is a specification that allows the isolation of PCI Express resources for manageability and performance reasons.


Details
A single physical PCI Express bus can be shared in a virtual environment using the SR-IOV specification. The SR-IOV offers different virtual functions to different virtual components (e.g. network adapter) on a physical server machine. SR-IOV uses physical and virtual functions to control or configure PCIe devices. Physical functions have the ability to move data in and out of the device while virtual functions are lightweight PCIe functions that support data flowing but also have a restricted set of configuration resources. The virtual or physical functions available to the hypervisor or guest operating system depend on the PCIe device.
The SR-IOV allows different virtual machines (VMs) in a virtual environment to share a single PCI Express hardware interface. In contrast, MR-IOV allows I/O PCI Express to share resources among different VMs on different physical machines.


InfiniBand
A major field of application for SR-IOV is within high-performance computing (HPC). The use of high-performance...

## Wikipedia Links in This Bundle

- [PCI Express](pci-express.md)

## Wikipedia Links Not Included

- Hypervisor
- I/O virtualization
- InfiniBand
- LWN.net
- MSDN
- Network adapter
- Supercomputer
- Virtual machines
- Virtualization
- Vmware
- Xen

## Categories

- All articles needing additional references
- All articles that are too technical
- Articles needing additional references from June 2015
- Articles with multiple maintenance issues
- Articles with short description
- Computer networking
- Hardware virtualization
- Peripheral Component Interconnect
- Short description matches Wikidata
- Wikipedia articles that are too technical from June 2015

## Source

- [Single-root input/output virtualization](https://en.wikipedia.org/wiki/Single-root_input/output_virtualization)
- Revision: 1265644962
- License: CC BY-SA; see the page footer and Wikimedia Terms of Use.
