---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 112
headings: ["5.2.1.14. Relocation of Expansion ROM Run-time Code", "5.2.1.15. Expansion ROM Placement Address"]
---

# Source page 112

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  112
5.2.1.14. Relocation of Expansion ROM Run-time Code
Prior revisions of the PCI Specification described the three arguments that are passed to the
Expansion ROM initialization code.  An Expansion ROM compliant to this specification version 3.0
or later will accept a fourth argument which describes the final run-time address of the Expansion
ROM code.
Expansion ROM code compliant to this specification version 3.0 or later must call the BIOS
Function (Section 2.5.2) to determine if the BIOS is compliant to this specification version 3.0 or
later and will provide this fourth argument.
This new argument permits the BIOS firmware to execute the Expansion ROM initialization code in
a memory space other than its final run-time location.  This is useful when there is insufficient space
remaining in the compatibility region for the BIOS to copy the Expansion ROM initialization code,
but there is sufficient space remaining for the run-time code to be placed correctly.  The BIOS may
initialize the Expansion ROM code in a region other than where the final run-time code will reside.
In all cases, this region will be below the 1 MiB address boundary.
A 3.0 (or later) compliant BIOS will not provide a run-time address that partially overlaps the
temporary INIT address.  The two addresses (if different) will be entirely separate ranges of
memory.  However a 3.0 (or later) compliant BIOS may provide the same address for run-time as
for the INIT address, similar to how a 2.1 compliant BIOS functions now.  In either case, the
Expansion ROM can examine the CS register and the fourth argument (run-time address) to
determine if they are the same region.
Prior to returning control to the BIOS, the Expansion ROM code moves the run-time code, as
described in the earlier section of the document. If the Expansion ROM code updates interrupt
vectors to point to the run-time Expansion ROM code, those interrupt vectors must point to the
final run-time location, not the temporary location where the BIOS may have temporarily placed the
Expansion ROM code for initialization.
For example, if there are 16 KiB of available space remaining to place Expansion ROMs, and a
64 KiB Expansion ROM indicates (via the run-time size field) that its run-time size is 16 KiB then
there is sufficient space for the run-time code to fit.  However, the 64 KiB Expansion ROM
initialization code must be executed first, but the 64 KiB of code cannot be placed in memory (there
is only 16 KiB remaining), so it will fail to be initialized.  However an Expansion ROM compliant to
this specification version 3.0 or later can be initialized in another location and the run-time code
then moved by the Expansion ROM code into its final address.
5.2.1.15. Expansion ROM Placement Address
Prior versions of the PCI Specifications have described the address where Expansion ROMs will be
placed as typically being from 0C 0000h up to 0E 0000h.  This version of the specification now
expands that region to be from A 0000h to F FFFFh inclusively.  System firmware compliant to this
specification version 3.0 or later will place the Expansion ROM code that is compliant to this
specification version 3.0 or later at any aligned address within this expanded range.
If an Expansion ROM not identified as being 3.0 (or later) compliant, the system firmware will place
the Expansion ROM within the legacy address range (0C 0000h up to 0E 0000h).
