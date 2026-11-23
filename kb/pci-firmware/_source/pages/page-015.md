---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 15
headings: []
---

# Source page 15

TRADITIONAL PCI BIOS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  15
The value returned in [AL] identifies what specific hardware characteristics the platform supports in
relation to accessing configuration space and generating PCI Special Cycles (see Figure 2-1).  The
PCI Specification defines two hardware mechanisms for accessing configuration space.  Bits 0 and 1
of the value returned in [AL] specify which mechanism is supported by this platform.  Bit 0 will be
Set (1) if Mechanism #1 is supported, and Clear (0) otherwise.  Bit 1 will be Set (1) if Mechanism #2
is supported, and Clear (0) otherwise.  Bits 2, 3, 6, and 7 are reserved and returned as zeros.
The PCI Specification also defines hardware mechanisms for generating Special Cycles.  Bits 4 and 5
of the value return in [AL] specify which mechanism is supported (if any).  Bit 4 will be Set (1) if the
platform supports Special Cycle generation based on Config Mechanism #1, and Clear (0)
otherwise.  Bit 5 will be Set (1) if the platform supports Special Cycle generation based on Config
Mechanism #2, and Clear (0) otherwise.

Figure 2-1:  Layout of Value Returned in [AL]
The value returned in [CL] specifies the number of the last PCI bus in the system.  PCI buses are
numbered starting at zero and running up to the value specified in CL.
If the [BX] register indicates that the BIOS is compliant with version 3.0 (or later), then the [CH]
register will have the following meaning:
CH = Level of BIOS support:
bit 0 set = Functions 06h through 0Dh inclusively are implemented for register
      access below 256.
bit 1 set = Functions 06h through 0Dh inclusively are implemented for register
      access in the range 256 - 4096 for POST only.
bit 2 set = Function 0Eh has been implemented.
bit 3 set = Function 0Fh has been implemented.
bit 4 set = Function 02h has been implemented.
bit 5 set = Function 03h has been implemented.
bit 6 set = BIOS supports Option ROM Configuration Code execution.
bit 7 set = BIOS supports calling the Option ROM with DMTF CLP style
      configuration data.
Note that version 3.0 and 3.1 of this specification requires that bit 0 and bit 1 be Set.  This may not
be the case in future versions of the specification.
