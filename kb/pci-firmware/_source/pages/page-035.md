---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 35
headings: []
---

# Source page 35

UEFI PCI SERVICES
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  35
Firmware must configure all Host Bridges in the systems, even if they are not connected to a
console or boot device.  Firmware must configure Host Bridges in order to allow operating systems
to use the devices below the Host Bridges.  This is because the Host Bridges programming model is
not defined by the PCI Specifications.  “Configured” in this context means that:
❑ Memory and I/O resources are assigned and configured.
❑ Includes both the resources consumed by the Host Bridge and the resources passed through to
the secondary bus.
❑ The bridge is enabled to receive and forward transactions.
❑ The bridge is operating in “safe” mode.  Safe mode includes:
● Enabling resources such as: I/O Port, Memory addresses, VGA routing, bus number, etc.
● Enabling detection of parity and system errors.
● Programming cacheline, latency timer, and other registers as required by the PCI
Specifications.
Firmware must report Host Bridges in the ACPI namespace.  Each Host Bridge object must contain
the following objects:
❑ _HID and _CID
❑ _CRS to determine all resources consumed and produced (passed through to the secondary bus)
by the host bridge. Firmware allocates resources (Memory Addresses, I/O Port, etc.) to Host
Bridges.  The _CRS descriptor informs the operating system of the resources it may use for
configuring devices below the Host Bridge:
● _TRA, _TTP, and _TRS translation offsets to inform the operating system of the mapping
between the primary bus and the secondary bus.
❑ _PRT and the interrupt descriptor to determine interrupt routing.
❑ _BBN to obtain a bus number.
❑ _UID to match with UEFI device path.
❑ _SEG if it has a non-zero PCI Segment Group number.
❑ _STA if hot plug is supported.
❑ _MAT if hot plug is supported.
Firmware is required to configure all PCI-to-PCI Bridges in the hierarchy leading to boot and
console devices. Firmware may optionally configure all PCI-to-PCI Bridges in the system.  When
configuring a PCI-to-PCI Bridge, Firmware must set it to safe mode.  This includes:
❑ Programming and enabling resources such as: I/O Port, Memory addresses, VGA routing, bus
number, etc.
❑ Enabling detection of parity and system errors.
❑ If applicable, program cache_line, latency timer, and other registers as required by the PCI
Specifications.
