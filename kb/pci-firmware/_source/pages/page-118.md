---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 118
headings: ["5.2.1.24.1. Executing the Expansion ROM Configuration Code"]
---

# Source page 118

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  118
Support for Configuration Utility Code management is optional for the system firmware.  The
Expansion ROM must call the “PCI BIOS Present” function, as described in Section 2.5.2, to
determine whether the system firmware has implemented the support for Expansion ROM
Configuration Code.
5.2.1.24.1. Executing the Expansion ROM Configuration Code
The configuration code remains in temporary memory so long as it is possible that an end user may
need to use the configuration code.  The system firmware will make a far call into the configuration
utility code, and the configuration utility will perform a far return to pass control back to system
firmware when it has completed.  The configuration code need not preserve any registers, and is
expected to update the BH register as defined below.  The system firmware will call the
configuration code in “Big Real Mode”, as defined in the footnote to Section 5.2.1.9.  In addition,
the Bus/Device/Function number and the far pointer to the PMM entry point will be provided as
argument as shown below.
Arg. Register Meaning
1 [AH]  Bus number
2 [AL]  Upper 5 bits are the Device number
3 [AL]  Lower 3 bits are the Function number
4 [BL]  System Firmware state:
   Bit 0 set = BIOS is performing Console Redirection.
   Bit 1:7 = Reserved.
5 [BH]   Configuration utility status.  Cleared to zero by system firmware prior to call.
6  [CX]  Segment of the PMM Services Entry Point.
7 [DX]  Offset of the PMM Services Entry Point.
8 [SI]  Segment of the run-time Expansion ROM code.
9 [DI]  Offset of the run-time Expansion ROM code.
Prior to returning control to the system firmware via a far return, the configuration code will update
the BH register as follows:
 Bit 0 set = Configuration utility is requesting a system reset
 Bits 1 to 7 = Reserved
The system firmware provides the far pointer to the PMM Services Entry point.  The PMM Services
Entry pointer is described in Section 3.1.1 “PMM Structure”, (offset 7) of the POST Memory Manager
Specification, Version 1.01.  By providing the PMM Services Entry pointer, it is no longer necessary for
the Expansion ROM code to search for the PMM Structure, validate the PMM signature, and
validate the PMM checksum.
The configuration utility code can assume that all basic devices have been initialized and the system
firmware is providing input and output services.  The configuration utility code must use the system
firmware Interrupt services for input and output functions.
System firmware will have a list of all the configuration code from the various Expansion ROMs.
System firmware will be responsible for creating a method for the end user to selectively execute the
configuration code.  This may be done within a specific page of the ROM based Setup program.
