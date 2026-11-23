---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 37
headings: []
---

# Source page 37

UEFI PCI SERVICES
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  37
in the _CRS descriptor of the parent Host Bridge.  The operating system must ensure that the
address range is not used by any other device below that Host Bridge.
Operating systems must not configure devices with resources outside what is reported by the Host
Bridge _CRS.  Firmware reports the address ranges that are routed to that particular Host Bridge.
There is no guarantee that devices under that bridge will respond to other address ranges.
The Expansion ROM BAR (at 30h) is normally not enabled at the firmware handoff to the
operating system and the operating system must assume that the BAR content is invalid.  For some
devices, when the Expansion ROM BARs are enabled, the device’s other BARs are disabled.  PCI
specifies that a device may share decoders between the Expansion ROM BAR and other BARs, and
that device independent software must not access the other BARs when the Expansion ROM BAR
is enabled.  Firmware may leave the Expansion ROM BARs enabled if it happens to know that the
device does not share address decoders.  This could be firmware based on the Device ID or
firmware that is shipped in the card itself.  The device independent operating system software must
disable the Expansion ROM when accessing the device via the other BARs.  If the operating system
wants to use the Expansion ROM, it must “take turns” enabling the Expansion ROM BAR, using
the ROM, then disabling the BAR again before resuming access to the card via its other BARs.  In
other words, the operating system must not assume that the card has dual decoders.  The operating
system is not prohibited from accessing all the card’s resources if it knows that the card has dual
decoders and that the Expansion ROM BAR content is correct.
