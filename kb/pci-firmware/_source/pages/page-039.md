---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 39
headings: ["4.1.1. Background"]
---

# Source page 39

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  39
4.1.1. Background
The PCI Express and PCI-X Specifications define the Enhanced Configuration Access Mechanism
for the PC-compatible systems, which allows access to the configuration registers via memory
mapped address space.  The base address of this memory mapped configuration space is platform
specific and is communicated to the operating system via system firmware.
In a hierarchy that supports the enhanced configuration access mechanism, the first 256 bytes
(offsets 0-255) of PCI 2.3 compatible configuration space can be accessed by either the PCI 2.3
configuration mechanism (CF8/CFC) or using the enhanced configuration mechanism.  The
extended register configuration space (region from offset 256-4095) can be accessed only via the
enhanced configuration mechanism for PCI Express devices and Mode 2 PCI-X devices on the PC-
compatible systems.
Table 4-1:  Memory Address PCI Express Configuration Space
Memory Address PCI PCI-X Mode 1 PCI-X Mode 2 PCI Express
A[(20+n):20] Bus[n:0],
where n=0 to 7
Applies Applies Applies Applies
A[19:15] Device[4:0] Applies Applies Applies Applies
A[14:12] Function[2:0] Applies Applies Applies Applies
A[11:8] Extended
Register[3:0]
N/A N/A Applies Applies
A[7:0] Register[7:0] Applies Applies Applies Applies

The 256-MiB window of memory mapped configuration space (assuming maximum addressable
4 KiB per function, eight functions per device, 32 devices per bus) defined by PCI-X and PCI
Express is capable of describing the entire 256 bus PCI Segment Group as shown in Figure 4-1.

Figure 4-1:  256-MiB Region for Enhanced Configuration Space Access Mechanism
The Enhanced Configuration Access Mechanism can be applied to access heterogeneous hierarchies
consisting of PCI/PCI-X/PCI Express.  In this case, the extended configuration space up to a limit
of 4 KiB per device-function is accessible for PCI Express devices and PCI-X Mode 2 devices.
