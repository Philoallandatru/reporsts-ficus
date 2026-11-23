---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 48
headings: ["4.5. _OSC – A Mechanism for Exposing PCI Express Capabilities Supported by an Operating System", "4.5.1. _OSC Interface for PCI Host Bridge Devices"]
---

# Source page 48

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  48
4.5. _OSC – A Mechanism for Exposing PCI Express
Capabilities Supported by an Operating
System
_OSC is an object that is used by OSPM to query the capabilities of a device (as defined in ACPI)
and to communicate to the platform the feature support or capabilities provided by a device’s driver.
This object is a child object of the device in the ACPI namespace.  Device specific objects are
evaluated after _OSC invocation.  For a complete description of _OSC method, refer to the ACPI
Specification.
4.5.1. _OSC Interface for PCI Host Bridge Devices
The _OSC interface defined in this section applies only to “Host Bridge” ACPI devices that
originate PCI, PCI-X, or PCI Express hierarchies.  These ACPI devices must have a _HID of (or a
_CID including either EISAID(“PNP0A03”) or EISAID(“PNP0A08”).  For a host bridge device
that originates a PCI Express hierarchy, the _OSC interface defined in this section is required. For a
host bridge device that originates a PCI/PCI-X bus hierarchy, inclusion of an _OSC object is
optional.
The _OSC interface for a PCI/PCI-X/PCI Express hierarchy is identified by the Universal Unique
IDentifier (UUID) 33DB4D5B-1FF7-401C-9657-7441C03DD766. A revision ID of 1 encompasses
fields defined in this section of this revision of this specification comprised of three DWORDs,
including the first DWORD described by the generic ACPI definition of _OSC.
The first DWORD in the _OSC Capabilities Buffer contains bits that are generic to _OSC.  These
include status and error information.
The second DWORD in the _OSC Capabilities Buffer is the Support Field.  Bits defined in the
Support Field provide information regarding operating system supported features.  Contents in the
Support Field are passed one way; the operating system will disregard any changes to this field when
returned.
The third DWORD in the _OSC Capabilities Buffer is the Control Field.  Bits defined in the
Control Field are used to submit requests by the operating system for control/handling of the
associated feature, typically (but not limited to) those features that utilize native interrupts or events
handled by an operating system-level driver.  If any bits in the Control Field are returned cleared
(masked to zero) by the _OSC control method, the respective feature is designated unsupported by
the platform and must not be enabled by the operating system.  Some of these features may be
controlled by platform firmware prior to operating system boot or during runtime for a legacy
operating system, while others may be disabled/inoperative until native operating system support is
available. System firmware must only mask a Control Field bit to zero if it has explicit knowledge
that the feature will not work properly under native operating system control, due to platform errata
or other incompatibilities.
