---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 8
headings: ["1.3. Terms and Acronyms"]
---

# Source page 8

INTRODUCTION
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021 8
PCI-X Addendum to the PCI Local Bus Specification, Revision 2.0
PCI Hot-Plug Specification, Revision 1.1
PCI Standard Hot-Plug Controller and Subsystem Specification, Revision 1.0 (SHPC 1.0)
DMTF Server Management Command Line Protocol (SM CLP) Specification, v1.0.2, Document Number
DSP0214, March 7, 2007, http://www.dmtf.org/standards/published_documents/DSP0214.pdf
SMBIOS Reference Specification, v3.4.0a, Document Number DSP0134, December 7, 2019,
https://www.dmtf.org/standards/smbios
1.3. Terms and Acronyms
Term Definition
Active State Power Management (ASPM) An autonomous hardware based active state
mechanism, Active State Power Management defined in
PCI Express.
Advanced Error Reporting (AER) A capability for advanced error control and reporting
defined in PCI Express.
Bus Number A number in the range 0…255 that uniquely selects a
PCI bus.
Configuration Space A separate address space on PCI buses.  Used for
device identification and configuring devices into
Memory and I/O spaces.
Device ID A predefined field in configuration space that (along with
Vendor ID) uniquely identifies the device.
Device Number A number in the range 0…31 that uniquely selects a
device on a PCI bus.
Function Number A number in the range 0…7 that uniquely selects a
function within a multi-function PCI device.
Message Signaled Interrupt (MSI) An optional feature that enables a device to request
service by writing a system-specified DW of data to a
system-specified address using a Memory Write
semantic Request.
Multi-function PCI device A PCI device that contains multiple functions.  For
instance, a single device that provides both LAN and
SCSI functions and has a separate configuration space
for each function is a multi-function device.
Operating System Hot Plug (OSHP) An ACPI control method to transfer control of Hot-Plug
to the operating system.  On some systems, this
method is defined for Ports that are Hot-Plug capable
and being controlled by ACPI firmware.
PCI An acronym for Peripheral Component Interconnect.
