---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 49
headings: []
---

# Source page 49

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  49
Since _OSC applies to the entire hierarchy originated by a PCI Host Bridge, and system firmware
cannot generally comprehend the features and capabilities of all devices that may be hot-plugged
into a system, lack of explicit support of a feature in the system firmware is not a reason to mask a
Control Field bit to zero. For example, unless system firmware has knowledge that the system
contains hardware that does not work properly with Standard Hot-Plug Controller (SHPC) or PCI
Express Native Hot Plug software, it must grant operating system requests for PCI Express Native
Hot Plug control and SHPC Native Hot Plug control bits, even if the system does not explicitly
support hot plug.  It is the operating system’s responsibility to determine whether a slot in the
hierarchy is hot pluggable by examining the status of the slots based on the PCI Express Base
Specification and the PCI SHPC Specification.
For the above reason, system firmware must always assume that PCI-X features are supported
beneath a PCI Express hierarchy unless it has explicit knowledge to the contrary, and must not mask
_OSC Control Field bits that apply only to PCI/PCI-X to zero in PCI Express hierarchies.
However, if a bit in the _OSC Control Field applies to PCI Express, system firmware must mask
this bit to zero in a PCI/PCI-X hierarchy.
If the _OSC control method is absent from the scope of a host bridge device, then the operating
system must not enable or attempt to use any features defined in this section for the hierarchy
originated by the host bridge.  Doing so could contend with platform firmware operations or
produce undesired results.
It is recommended that a machine with multiple host bridge devices should report the same
capabilities for all host bridges of the same type and also negotiate control of the features described
in the Control Field in the same way for all host bridges of the same type.  That is, for a machine
with multiple host bridge devices supporting both PCI/PCI-X and PCI Express hierarchies, this
recommendation applies to each host bridge type separately. PCI/PCI-X host bridge devices can
have one capabilities setting and PCI Express hot bridge devices can have another.
Table 4-4:  Interpretation of the _OSC Support Field
Support Field
Bit Offset
Interpretation
0 Extended PCI Config operation regions supported
The operating system sets this bit to 1 if it supports ASL accesses through PCI
Config operation regions to extended configuration space (offsets greater than
FFh).  Otherwise, the operating system sets this bit to 0.
1 Active State Power Management supported
The operating system sets this bit to 1 if it natively supports configuration of Active
State Power Management registers in PCI Express devices.  Otherwise, the
operating system sets this bit to 0.
2 Clock Power Management supported
The operating system sets this bit to 1 if it supports Clock Power Management and
will enable this feature during a native hot plug insertion event if supported by the
newly added device.  Otherwise, the operating system sets this bit to 0.
