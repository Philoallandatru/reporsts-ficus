---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 110
headings: ["5.2.1.7. Permanent Memory", "5.2.1.8. Temporary Memory", "5.2.1.9. Memory Locations"]
---

# Source page 110

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  110
5.2.1.7. Permanent Memory
Permanent memory will continue to be assigned to the Expansion ROM even after the operating
system has booted.  This is accomplished by the BIOS updating the data for the Interrupt 15h,
E820h function (“Get Memory Map”), to show that this memory allocated to the Expansion ROM
is reserved, private, and unmovable.
In addition, the BIOS must support the ACPI memory tables that describe reserved regions of
memory.  Interrupt 15h, E820h function (“Get Memory Map”), and the ACPI memory tables must
both contain entries for the memory reserved by Expansion ROMs.
The operating system must make the “Get Memory Map” call to the BIOS to understand the usage
of this reserved area of memory.  If the operating system fails to understand that this memory is
reserved, then unpredictable behavior may occur.
5.2.1.8. Temporary Memory
If the Expansion ROM initialization code requests temporary memory via PMM, the BIOS will
allocate memory that is usable only during the time of Expansion ROM code initialization.  This is
useful as a buffer for the Expansion ROM code to decompress the ROM for example.  When the
Expansion ROM initialization code finishes execution, and returns control to the BIOS, the memory
will no longer be usable by the Expansion ROM.  Any data left in this region may be erased or over-
written.
5.2.1.9. Memory Locations
When the Expansion ROM initialization code requests memory, it can specify whether the memory
should be located above or below the 1 MiB (F FFFFh) boundary.  Memory below the 1 MiB
boundary is very limited and Expansion ROMs should be frugal with this valuable system resource.
When the Expansion ROM initialization code requests permanent memory above 1 MiB, it is
assumed that the code is capable of accessing this space at a later time when the operating system
may be running in protected mode.
Note that the Expansion ROM initialization code will be called from the BIOS in “big real mode,”10
and the code will have data access to the full 32-bit address range of memory.  This will permit
access to any memory buffers allocated above the 1 MiB address boundary.


10 In “Big Real Mode” (aka 32-bit Flat model) is an x86 CPU state where normal Real Mode has been enhanced to
have all the segment limits set to 4 GiB.  The BIOS will accomplish this mode by entering Protected Mode, setting the
segment limits to 4 GiB, and returning to Real Mode (now “Big Real Mode”).  In this mode, the processor will honor
the segment register limits and they are unaffected by segment register loads.  Refer to
http://www.phoenix.com/resources/specs-pmm101.pdf for more information.
