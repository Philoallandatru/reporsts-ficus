---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 114
headings: ["5.2.1.19. Extended BIOS Data Area (EBDA) Usage"]
---

# Source page 114

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  114
5.2.1.19. Extended BIOS Data Area (EBDA) Usage
The Extended BIOS Data Area (EBDA) is a memory buffer allocated in the below 1 MiB address
region of memory.  Historically, this region has been used by Expansion ROM code to create a
permanent memory buffer for its own use.  It is important that the EBDA memory buffer be used
consistently and carefully as it is a shared system resource.
If an Expansion ROM requires memory below the 1 MiB boundary, it should use the PMM
functions to obtain this memory.  The use of EBDA is discouraged due to the complexity of
managing and accessing the EBDA memory.
If an Expansion ROM determines that the PMM services are not available, then it is permissible to
use EBDA with the following guidelines in mind:
1. First the Expansion ROM must determine if the EBDA is present.
Is 40:0Eh non-zero?  Yes, then it is present.  Go to step 2.
Allocate an EBDA.
Read 40:13h size and subtract 1 KiB.
Convert new size to segment and save in 40:0Eh.
Set 40:0E offset 0 to 1 (1 KiB).
2. Make sure EBDA can handle the amount of memory needed.
Obtain current EBDA size in 1 KiB.
Add needed amount of memory (rounded up to nearest KiB).
If the total memory is greater than 64 KiB, then an error has occurred.  The memory request is
too large.
3. Move existing EBDA down in memory.
Disable Interrupts when moving EBDA
Save current EBDA size as size of memory to move.
Move current EBDA down to lower memory.
Zero out old “new” region in upper memory.
Adjust the 40:0Eh pointer to the new EBDA.
Set 40:0Eh offset 0 to new size.
Subtract the size allocated (in KiB) from the value in 40:13h.
After following the above steps, the Expansion ROM may use the new memory (at the highest
offset) in the EBDA buffer.
All code references to the EBDA buffer must be indirect references through the pointer at 40:0Eh.
The Expansion ROM code must always read the pointer at 40:0Eh to determine the beginning
segment of the EBDA buffer.  This value will change as the EBDA buffer is expanded, while the
offset within the buffer will remain constant.
The 8-bit location at 40:13h is the amount of memory installed below 1 MiB.  It is the highest usable
memory address below 1 MiB.  Many BIOSes install the EBDA immediately below the highest
usable memory address but not in all cases.  The variable at 40:13h is not a reliable indicator of
whether an EBDA has been allocated (use 40:0Eh instead), nor is it a reliable indicator of the size of
the EBDA (use 40:0Eh offset 0 instead).  Expansion ROM code should make no inferences about
the EBDA from the value in 40:13h.
