---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 106
headings: ["5.2.1.1. Expansion ROM Header Extensions", "5.2.1.2. POST Firmware Extensions"]
---

# Source page 106

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  106
5.2.1.1. Expansion ROM Header Extensions
The standard header for PCI Expansion ROM images is expanded slightly for PC-compatibility
(Code Type 0).  Code Type 0 headers use offset 03h as the entry point for the Expansion ROM
INIT function.
Offset Length Value Description
0h 1 55h ROM Signature byte 1
1h 1 AAh ROM Signature byte 2
2h 1 xx Current Image Size in units of 512 bytes
3h 3 xx Entry point for INIT function.  POST does a
FAR CALL to this location.
6h-17h 12h xx Reserved (application unique data)
18h-19h 2 xx Pointer to PCI Data Structure

5.2.1.2. POST Firmware Extensions
The POST firmware copies the entire Expansion ROM image into a RAM address, as described
above.  The RAM address can vary depending on whether the Expansion ROM identifies itself as
being compliant to this specification version 3.0 or later.  (A value of 03h in the PCI Data Structure
Revision field indicates compliance.)
If the Expansion ROM is compliant, then the following steps will be followed by the POST
Firmware:
1. POST Firmware will place the Expansion ROM in RAM at an address that may not be the final
run-time execution address.  This address will be below the 1 MiB address boundary.
2. The POST firmware will then call the INIT function entry point and supply the six arguments
described in Table 5-2.
3. As part of the INIT function, the Expansion ROM code must place the final run-time
Expansion ROM image into the run-time address provided by the POST firmware.
Note that the Expansion ROM code must ensure that the device is quiescent until the interrupt
service routine is in place at the final run-time location.  Caution must be taken in chaining the
interrupt service routine.  It is possible that an interrupt may arrive while the interrupt service
routine is being installed.
4. The POST Firmware will not write-protect the RAM containing the run-time Expansion ROM
code at this step.  In a system compliant to this specification version 3.0 or later, the write-
protection step will be delayed until the Setup portion of the Expansion ROM code, if any, has
been executed.
5. The POST firmware will erase the old image from the temporary RAM location.
