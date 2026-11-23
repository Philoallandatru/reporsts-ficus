---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 107
headings: ["5.2.1.3. Resizing of Expansion ROMs During INIT"]
---

# Source page 107

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  107
Table 5-2:  Arguments for an Expansion ROM Compliant to this Specification Version 3.0
or Later
Argument Number Register Meaning
1 [AH] Bus number
2 [AL] Upper 5 bits are the Device number
3 [AL] The lower 3 bits are the Function number
4 [BX] Run-time address.  This is the final run-time address where
the ROM image will be located after Initialization.  This
address is in units of 16-bytes.
5 [CX] Segment of the PMM Services Entry Point
6 [DX] Offset of the PMM Services Entry Point

Table 5-3:  Arguments for a Legacy Expansion ROM
Argument Number Register Meaning
1 [AH] Bus number
2 [AL] Upper 5 bits are the Device number
3 [AL] The lower 3 bits are the Function number

If the Expansion ROM is not compliant with this specification version 3.0 or later, then the
following steps will be followed by the POST Firmware:
1. POST Firmware will place the Expansion ROM in RAM within the legacy compatibility address
(usually 0C 0000h to 0E 0000h).
2. The POST firmware will then call the INIT function entry point and supply the three arguments
described in Table 5-3.
3. The POST Firmware will then write-protect the RAM containing the run-time Expansion ROM
code.  The size of the Expansion ROM and amount of RAM to write-protect is determined by
examining the Current Image Size field at offset 2 in the ROM header.
The POST firmware should be prepared to handle any mixture of Revision 3.0 (or later) compliant
and non-complaint Expansion ROMs in the system.
5.2.1.3. Resizing of Expansion ROMs During INIT
When the Expansion ROM INIT function is called, it is possible for the Expansion ROM code to
reduce the amount of space needed for the run-time code and run-time data.  This permits the
Expansion ROM to occupy the minimal amount of RAM at run-time.
For example, a device Expansion ROM may require 24 KiB for its initialization and run-time code
but only 8 KiB for the run-time code.  The image in the ROM will show a size of 24 KiB (in the
Image Length field in the PCI Data structure), so that the POST firmware copies the whole thing
into RAM.  Then when the INIT function is running, it can adjust the size down to 8 KiB.  This is
accomplished by updating the Current Image Size field (at offset 2h) in the ROM Header.
