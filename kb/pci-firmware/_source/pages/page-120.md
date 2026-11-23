---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 120
headings: ["5.2.1.25. DMTF Server Management Command Line Protocol  (SM CLP) Support"]
---

# Source page 120

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  120
The Configuration Code header and associated code is included in the Image Length field for the
PCI Data Structure ROM size.
5.2.1.25. DMTF Server Management Command Line Protocol
(SM CLP) Support
The Option ROM may optionally provide an entry point that will support device configuration via
the DMTF SM CLP standard.12  This interface will follow an API defined in the DMTF SM CLP
Specification 1.0.2 Final Standard.  This interface is accessed with a FAR CALL in Big Real Mode
where the system ROM will pass in a DMTF SM CLP compatible configuration message that will
target the device or a child of that device.  This interface may be called multiple times in order to
completely configure a device during pre-boot.  It is the responsibility of the System ROM to
perform any discovery, enumeration, and subsequent translation of the SM CLP UFiTs for any
given Container in an implementation.  The option ROM code should assume that the system
firmware will call the entry point in Big Real Mode and with a minimum of 4 KiB for the stack and a
least 128 KiB of extended memory available via PMM.
Input parameters are described below:
Table 5-5:  Input Arguments for SM CLP Entry Point
Argument Number Register Meaning
1 [AH] Bus number
2 [AL] Upper 5 bits are the Device number
3 [AL] The lower 3 bits are the Function number
4 [ES:EDI] Pointer to NULL-terminated SM CLP Command Line string
buffer
5 [DS:ESI] Pointer to SM CLP Command Response string buffer

AX contains the Bus/Device/Function of the source of the PCI option ROM, same as the PCI
option ROM INIT and Configuration entry points described earlier in this specification.  This
provides an indicator of which PCI device is being targeted to the SM CLP code.  If a PCI option
ROM’s SM CLP entry point supports more than one device as an SM CLP target, the Command
Line Protocol string buffer must also be examined for target information, according to the SM ME
Addressing Specification. ES:EDI points to a Command Line string as defined in the SM CLP
Specification (see Section 5.1.9, “Input Data”).  DS:ESI points to a buffer of at least 4 KiB in size.
Strings are always NULL-terminated.
Note:  The scope of the target in the SM CLP Command Line string buffer is limited to the Address
Space of the PCI device and is not expected to be scoped to the overall containing Computer
System.  SM CLP implementations in PCI option ROMs are expected to adhere to the SM ME
Addressing Specification with the exception that Collections, Logical Devices, Computer Systems, and
other Managed Elements are allowed to be in the root of the Address Space.

12 This document references v1.0.2 of the DMTF SM CLP Specification which is available from the DMTF group at
http://www.dmtf.org/sites/default/files/standards/documents/DSP0214.pdf.
