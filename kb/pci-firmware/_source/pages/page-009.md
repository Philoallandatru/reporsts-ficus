---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 9
headings: []
---

# Source page 9

INTRODUCTION
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021 9
Term Definition
Segment Group Number A number in the range 0…65535 that uniquely selects a
PCI Segment Group.
PCI Segment Group is purely a software concept
managed by system firmware and used by the operating
system.  It is a logical collection of PCI buses (or bus
segments).  There is no tie to any physical entities.  It is
a way to logically group the PCI bus segments and PCI
Express Hierarchies.
PCI Segment Group concept enables support for more
than 256 buses in a system by allowing the reuse of the
PCI bus numbers.  Within each PCI Segment Group,
the bus numbers for the PCI buses must be unique.
PCI buses in different PCI Segment Group are
permitted to have the same bus number.
A PCI Segment Group contains one or more PCI host
bridges.
There is at least one PCI Segment Group, PCI Segment
Group 0, in a system.
Standard Hot-Plug Controller (SHPC) A PCI Hot-Plug Controller compliant with SHPC 1.0.
Vendor ID A predefined field in configuration space that (along with
Device ID) uniquely identifies the device.
