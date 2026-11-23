---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 40
headings: ["4.1.2. MCFG Table Description"]
---

# Source page 40

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  40
For non-Mode 2 PCI-X and all PCI devices, only the first 256 bytes of configuration space are
accessible.
Note that a given chipset implementation may choose to implement less than 256 MiB for the
memory mapped configuration space.  Further, implementations with multiple host bridges or
mixed hierarchies (for example, a multi-chip implementation with PCI Express as well as PCI-X at
the root level) are allowed to implement the memory mapped configuration space in a discontinuous
fashion; that is, the 256 PCI buses could be distributed across multiple host bridges in a non-
overlapping fashion.
Note that in a multiple host bridge hierarchy, there is no requirement for the host bridges to
program the buses within a PCI Segment Group or Groups in a contiguous fashion.
4.1.2. MCFG Table Description
The MCFG table is an ACPI table that is used to communicate the base addresses corresponding to
the non-hot removable PCI Segment Groups range within a PCI Segment Group available to the
operating system at boot. This is required for the PC-compatible systems.
The MCFG table is only used to communicate the base addresses corresponding to the PCI
Segment Groups available to the system at boot.  This table directly refers to PCI Segment Groups
defined in the system via the _SEG object in the ACPI namespace for the applicable host bridge
device.  For systems containing only a single PCI Segment Group, the default PCI Segment Group
number, namely, PCI Segment Group 0, is implied.  In such a case, the default PCI Segment Group
need not be represented in the ACPI namespace (i.e., no _SEG method is required in such a
hierarchy).
The size of the memory mapped configuration region is indicated by the start and end bus number
fields in the Memory mapped Enhanced configuration space base address allocation structure as
shown in Table 4-3.  0-255 is the range of allowed bus numbers supported for a given PCI Segment
Group.
Table 4-2 provides a description of the MCFG table.
