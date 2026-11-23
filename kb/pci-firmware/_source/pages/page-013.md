---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 13
headings: ["2.4. PCI BIOS 32-bit Service"]
---

# Source page 13

TRADITIONAL PCI BIOS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  13
ENTRY:
[EAX] Service Identifier.  This is a four character string used to
specifically identify which 32-bit BIOS Service is being sought.
[EBX] The low order byte ([BL]) is the BIOS32 Service Directory
function selector.  Currently only one function is defined (with
the encoding of zero) which returns the values provided
below.
The upper three bytes of [EBX] are reserved and must be zero
on entry.
EXIT:
[AL] Return Code:
00h = Service corresponding to Service Identifier is
present.
80h = Service corresponding to Service Identifier is not
present.
81h = Unimplemented function for BIOS Service
Directory (i.e., BL has an unrecognized value).
[EBX] Physical address of the base of the BIOS service.
[ECX] Length of the BIOS service.
[EDX] Entry point into BIOS service.  This is an offset from the base
provided in EBX.
2.4. PCI BIOS 32-bit Service
The BIOS32 Service Directory may be used to detect the presence of the PCI BIOS.  The Service
Identifier for the PCI BIOS is “$PCI” (4943 5024h).
The 32-bit PCI BIOS functions must be accessed using CALL FAR.  The CS and DS descriptors
must be setup to encompass the physical addresses specified by the Base and Length parameters
returned by the BIOS32 Service Directory.  The CS and DS descriptors must have the same base.
The calling environment must allow access to I/O space and provide at least 1 KiB of stack space.
Platform BIOS writers must assume that CS is execute-only and DS is read-only.
