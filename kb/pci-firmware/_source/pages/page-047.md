---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 47
headings: ["4.3.2. Resource Description", "4.3.2.1. Resource Setting", "4.3.2.2. Boot Bus Number", "4.3.2.3. PCI Segment Group", "4.4. PCI Interrupt Routing"]
---

# Source page 47

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  47
4.3.2. Resource Description
4.3.2.1. Resource Setting
Host bridges resources programming is communicated to the operating system using ACPI methods
_CRS, _SRS, and _PRS.  _CRS indicates the current resource setting for the host bridge.  This
includes I/O space, memory space, and bus range assigned to the bridge by platform firmware.
A non-configurable device only specifies _CRS.  However, if they are configurable, devices include
_PRS to indicate the possible resource setting and _SRS to allow OSPM to specify a new resource
allocation for the device.
4.3.2.2. Boot Bus Number
In multiple host bridge systems, _BBN method is used to provide PCI_Config Operation Region
access for a specific bus.
4.3.2.3. PCI Segment Group
PCI Segment Group concept enables support for more than 256 buses in a system by allowing the
reuse of the PCI bus numbers.  The _SEG method is used to uniquely identify PCI Segment
Groups.
Complete details are located in the ACPI Specification.
4.4. PCI Interrupt Routing
The routing of PCI INTx interrupts to interrupt controllers cannot be deduced through the PCI
register space. ACPI object, _PRT, is required under all PCI host bridges and is used to indicate the
routing of the PCI INTx interrupts to the interrupt controllers.  If the Root Ports are described in
the ACPI namespace and have an associated _PRT, operating systems must evaluate and use routing
as described in the _PRT.
MSI and MSI-X are standardized by the PCI-X Specification and the PCI Express Base Specification.
ACPI is not involved in the use of MSI or MSI-X.
