---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 43
headings: ["4.1.3. The _CBA Method"]
---

# Source page 43

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  43
4.1.3. The _CBA Method
Some systems may support hot plug of host bridges that introduce either a range of buses within an
existing PCI Segment Group or introduce a new PCI Segment Group.  For example, each I/O chip
in a multi-chip PCI Express root complex implementation could start a new PCI Segment Group.
The base address of the memory mapped configuration space for such a hot pluggable PCI Segment
Group or a range of buses within a PCI Segment Group is described using an ACPI control
method, _CBA, that is under the host bridge devices that are part of the PCI Segment Group.  This
applies to PC-compatible systems only.
The _CBA (Memory mapped Configuration Base Address) control method is an optional ACPI
object that returns the 64-bit memory mapped configuration base address for the hot plug capable
host bridge.  The base address returned by _CBA is processor-relative address.  The _CBA control
method evaluates to an Integer.
This control method appears under a host bridge object.  When the _CBA method appears under an
active host bridge object, the operating system evaluates this structure to identify the memory
mapped configuration base address corresponding to the bus number range specified in _CRS
method. Within the same PCI Segment Group, different host bridges, each with its associated bus
number range, may have a different configuration base address. An ACPI namespace object that
contains the _CBA method must also contain a corresponding _SEG method.
For a host bridge that includes _CBA, the _CBA and _BBN control methods have to be executed
first to enable PCI_Config_OpRegion access for devices below the bridge.  As a result, the _CBA
and _BBN methods must not include PCI_Config opregions that refer to devices below the host
bridge.
A set of hot pluggable host bridges could have _CBA under each of the host bridge devices, where
each host bridge device is typically described in the ACPI namespace with PNP0A08 for _HID and
PNP0A03 for _CID.  In this case, the memory mapped configuration base address (always
corresponds to bus number 0 of a given bus number range) is provided by _CBA and the bus
number range covered by the base address is indicated by the corresponding bus number range
specified in _CRS.
If rebalancing of resources on a host bridge is supported via _PRS, _SRS, it is the responsibility of
the operating system to reevaluate _CBA every time _CRS is evaluated.
Memory mapped configuration base addresses for non-hot pluggable host bridges must be described
using MCFG table.

_CBA Control Method
Arguments:
None
Result Code:
Memory mapped configuration base address for the PCI-compatible host bridge returned as an
integer
Note:  Starting with ACPI 2.0, integers are 64-bit entities.
