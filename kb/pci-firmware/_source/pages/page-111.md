---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 111
headings: ["5.2.1.10. Permanent Memory Size Limits", "5.2.1.11. Multiple Requests for Memory", "5.2.1.12. Protected Mode", "5.2.1.13. Run-Time Expansion ROM Size"]
---

# Source page 111

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  111
5.2.1.10. Permanent Memory Size Limits
An Expansion ROM needs to limit the request for permanent allocation to 64 KiB (total) for above
1 MiB memory requests.  The limit is 40 KiB (total) for below 1 MiB permanent memory requests.
This total upper bound for permanent memory allocation can be tracked by the Firmware (System
BIOS).  The total amount of permanent memory available has to be shared between multiple
Expansion ROMs.  Before requesting memory, an Expansion ROM can query using PMM function
0 (pmmAllocate) call with the length “0” and appropriate flags to obtain the maximum permanent
memory size available for allocation.
5.2.1.11. Multiple Requests for Memory
Expansion ROM initialization code may make multiple calls to the BIOS to request memory.
Expansion ROM initialization code may request temporary memory or permanent memory any
number of times.  However, the total amount of permanent memory requested must not exceed the
limits described in Section 5.2.1.10.
The Expansion ROM code must always check the status code being returned to determine if the
requested memory was actually allocated to the Expansion ROM.
5.2.1.12. Protected Mode
If the Expansion ROM initialization code switches into Protected Mode, it must return control to
the BIOS in Big Real Mode (a 32-bit flat model).  In addition many BIOS services are not available
in Protected Mode during Expansion ROM initialization.  Refer to the 32-bit BIOS Service
Directory (Section 2.3) for further details.
5.2.1.13. Run-Time Expansion ROM Size
The conventional PCI Local Bus Specification requires that the Expansion ROM code resize itself after
initialization to reduce its use of the memory space.  However it is not possible for the BIOS to
know, prior to running the Expansion ROM initialization code, if the Expansion ROM will fit into
the space remaining for Expansion ROM placement.  An Expansion ROM compliant to this
specification version 3.0 or later will have a new field in the PCI Data Structure header (Maximum
Run-Time Image Length) to indicate the run-time space occupied by the Expansion ROM.
It may not be possible for the Expansion ROM code to know the actual run-time size (which is
affected by the presence or absence of other PCI devices in the system).  This run-time size field
describes the maximum run-time size that the Expansion ROM could occupy after the initialization
code has been run.
The BIOS firmware will examine this field prior to calling the Expansion ROM initialization code.
If there is insufficient space remaining to place the run-time Expansion ROM code, the BIOS may
elect to not initialize the Expansion ROM.
