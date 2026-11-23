---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 23
headings: ["2.7. Accessing Configuration Space", "2.7.1. Access Rules for PCI Express I/O and Memory Mapped Accesses"]
---

# Source page 23

TRADITIONAL PCI BIOS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  23
EXIT:
[AH] Return Code:
SUCCESSFUL
SET_FAILED
FUNC_NOT_SUPPORTED
[CF] Completion Status, set = error, cleared
= success.
2.7. Accessing Configuration Space
The 32-bit PCI BIOS functions must be accessed using CALL FAR.  The CS and DS descriptors
must be setup to encompass the physical addresses specified by the Base and Length parameters
returned by the BIOS32 Service Directory.  The CS and DS descriptors must have the same base.
The ES descriptors must be setup to encompass the physical address reported by the PCI Express
Base Address Register (BAR) region.  The ES descriptor must have a base of zero with the limit of
4 GiB to encompass the 256-MiB PCI Express BAR region.  The calling environment must allow
access to I/O space and provide at least 1 KiB of stack space.  Platform BIOS writers must assume
that CS is execute-only, DS is read-only, and ES is read/write.
The underlying assumptions being made are the following:
❑ If PCI BIOS functions support access to extended configuration registers, the PCI Express
memory mapped configuration base address must be programmed with an address region that
exists below 4 GiB of memory.
❑ The caller has the responsibility to appropriately parse the data returned from accessing non-
existing registers of a PCI Device.  The caller has to ensure that Register accesses beyond
256 bytes be invoked only on devices that have the support for extended configuration space.
For example:  if the caller accesses DWORD Register 0FFCh (4092) of a regular PCI device, the
data returned cannot be predicted.
❑ PCI BIOS functions do not comprehend the concept of PCI Segment Groups (for definition,
refer to Section 4.3.2.3) and, hence, can only support access to the devices in the default PCI
Segment Group, namely, PCI Segment Group 0.
2.7.1. Access Rules for PCI Express I/O and Memory
Mapped Accesses
Firmware should use the PCI I/O Index/Data mechanism to access configuration space registers
0-255.  Only accesses to configuration space registers 256 and beyond should use the PCI Express
memory-mapped access mechanism.
