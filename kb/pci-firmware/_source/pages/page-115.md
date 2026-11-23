---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 115
headings: ["5.2.1.20. POST Memory Manager (PMM) Functions", "5.2.1.21. Backward Compatibility of Option ROMs"]
---

# Source page 115

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  115
5.2.1.20. POST Memory Manager (PMM) Functions
This description of the new PMM functions is based on the existing PMM 1.01 Specification.11
Section 3.3.3 of that specification describes the input arguments for the various PMM calls.  The
flags field is now expanded to include a definition for bit 3 as shown in Table 5-4.
Table 5-4:  Fields and Values for PMM Functions
Bits Field Value Description
1:0 Memory Type 1..3 0 = Invalid
1 = Requesting convention memory block
(0 MiB to 1 MiB)
2 = Requesting extended memory block (1 MiB
to 4 GiB)
3 = Requesting either conventional or extended
memory
2 Alignment 0..1 0 = No alignment
1 = Use alignment from length parameter
3 Attribute 0...1 0 = Temporary memory use during POST
1 = Permanent memory use
4:15 Reserved 0 Reserved for future use

5.2.1.21. Backward Compatibility of Option ROMs
It is intended that 3.0 (or later) definitions of Option ROMs be compatible with the earlier 2.1
definitions.  It is possible for a single 3.0 (or later) Option ROM image to function with 3.0 (or later)
compliant System Firmware and with 2.1 compliant System Firmware.  The 3.0 fields and functions
in the Option ROM will be ignored by 2.1 compliant System Firmware.  Any 2.1 compliant System
Firmware should have no difficulty locating the 3.0 (or later) Option ROM and initializing it in a
manner consistent with this specification version 2.1.
It is also possible to have two separate ROM images for the same PCI device: one for 2.1-compliant
System Firmware and one for 3.0 (or later) compliant System Firmware.  In this case, the 2.1 Option
ROM image must appear first in the sequence of images. 3.0 (or later) compliant System Firmware
will first search for a 3.0 (or later) Option ROM image and only use the 2.1 Option ROM image if
no 3.0 (or later) Option ROM image is found.

11 The POST Memory Manager (PMM) Specification, Version 1.01, can be found at
http://www.pcisig.com/specifications/conventional/pci_firmware/.
