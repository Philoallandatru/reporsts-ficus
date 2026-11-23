---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 32
headings: ["3. UEFI PCI Services", "3.1. UEFI Driver Model", "3.1.1. PCI Root Bridge Protocol"]
---

# Source page 32

PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021 32




3.UEFI PCI Services
UEFI stands for Unified Extensible Firmware Interface.  The UEFI Specification, Version 2.4 or later
(http://www.uefi.org) describes an interface between the operating system and the platform
firmware.  The interface is in the form of data tables that contain platform-related information and
boot and run-time services calls that are available to the operating system and its loader.  Together,
these provide a standard environment for booting an operating system.
The following sections provide an overview of the UEFI Services relevant to PCI (including
Conventional PCI, PCI-X, and PCI Express).  For details, refer to the UEFI Specification.  UEFI is
processor-agnostic.
3.1. UEFI Driver Model
The UEFI Driver Model is designed to support the execution of drivers that run in the pre-boot
environment present on systems that implement the UEFI firmware.  These drivers may manage
and control hardware buses and devices on the platform, or they may provide some software
derived platform specific services.
The UEFI Driver Model is designed to extend the UEFI Specification in a way that supports device
drivers and bus drivers.  It contains information required by UEFI driver writers to design and
implement any combination of bus drivers and device drivers that a platform may need to boot an
UEFI-compliant operating system.
Applying the UEFI Driver Model to PCI, the UEFI Specification defines the PCI Root Bridge
Protocol and the PCI Driver Model and describes how to write PCI bus drivers and PCI devices
drivers in the UEFI environment.  For details, refer to the UEFI Specification.
3.1.1. PCI Root Bridge Protocol
A PCI Root Bridge is represented in UEFI as a device handle that contains a Device Path Protocol
instance and a PCI Root Bridge Protocol instance.
PCI Root Bridge Protocol provides an I/O abstraction for a PCI Root Bridge that the host bus can
perform.  This protocol is used by a PCI Bus Driver to perform PCI Memory, PCI I/O, and PCI
Configuration cycles on a PCI Bus.  It also provides services to perform different types of bus
mastering DMA on a PCI bus.
PCI Root Bridge Protocol abstracts device specific code from the system memory map.  This allows
system designers to make changes to the system memory map without impacting platform
independent code that is consuming basic system resources.  An example of such system memory
map changes is a system that provides non-identity memory mapped I/O (MMIO) mapping
between the host processor view and the PCI device view.
3
