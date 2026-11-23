---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 14
headings: ["2.5. Host Interface", "2.5.1. Identifying PCI Resources", "2.5.2. PCI BIOS Present"]
---

# Source page 14

TRADITIONAL PCI BIOS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  14
2.5. Host Interface
2.5.1. Identifying PCI Resources
The following group of functions allow the caller to determine first, if the PCI BIOS support is
installed, and second, if specific PCI devices are present in the system.
2.5.2. PCI BIOS Present
This function allows the caller to determine whether the PCI BIOS interface function set is present,
and what the current interface version level is.  It also provides information about what hardware
mechanism for accessing configuration space is supported, and whether or not the hardware
supports generation of PCI Special Cycles.
ENTRY:
[AH] PCI_FUNCTION_ID
[AL] PCI_BIOS_PRESENT
EXIT:
[EDX] “PCI”, “P” in [DL], “C” in [DH], etc.  There is a
“space” character in the upper byte.
[AH] Present Status, 00h = BIOS Present if and only if
EDX set properly.
[AL] Hardware mechanism.
[BH] Interface Level Major Version.
[BL] Interface Level Minor Version.
[CL] Number of last PCI bus in the system.
[CF] Present Status, set = No BIOS Present,
reset = BIOS Present if and only if EDX set
properly.
If the CARRY FLAG [CF] is cleared and AH is set to 00h, it is still necessary to examine the
contents of [EDX] for the presence of the string “PCI” + (trailing space) to fully validate the
presence of the PCI function set.  [BX] will further indicate the version level, with enough
granularity to allow for incremental changes in the code that do not affect the function interface.
Version numbers are stored as Binary Coded Decimal (BCD) values.  For example, Version 2.10
would be returned as a 02h in the [BH] registers and 10h in the [BL] registers.
A BIOS  that complies with Version 3.1 of the specification will return with 0310h in the [BX]
register.
