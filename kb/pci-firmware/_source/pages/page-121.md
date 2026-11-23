---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 121
headings: []
---

# Source page 121

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  121
The output parameters are described in :

Table 5-6:  Output Arguments for SM CLP Entry Point
Argument Number Register Meaning
1 [AH] If [AL] = 2 (COMMAND_PROCESSING_FAILED) the contents
of [AH] are derived from the SM CLP Processing Error Value
(refer to SM CLP Specification – Table 6: Processing Error
Values and Tags).
If [AL] = 3 (COMMAND_EXECUTION_FAILED) the contents
of [AH] are derived from the SM CLP CIM Status Code Values
(refer to SM CLP Specification – Table 9: CIM Status Code
Values and Descriptions)
2 [AL] SM CLP Command Status (refer to SM CLP Specification –
Table 4: Command Status Values and Tags)
3 [EAX] Bit 31: OEM Code Flag
0 = Execution Code is an SM CLP Probable Cause Value
(refer to SM CLP Specification Table 11 – Probable Cause
Values and Descriptions)
1 = Execution Code is an OEM Specific value
4 [EAX] Bits 30-16: Execution Code
5 [ES:EDI] Pointer to NULL-terminated SM CLP Command Line string
buffer
6 [DS:ESI] Pointer to NULL-terminated SM CLP Command Response
string buffer

AL contains 0 for a successful command completion status.  If AL is returned with a value of 2, a
command processing error is signified and AH will contain a code signifying the cause of the
processing error.  If AL is returned with a value of 3, an execution error has occurred and the upper
16-bits of EAX will contain an execution error code.  Bit 31 of EAX specifies whether the
Execution Code is an SM CLP defined code or an OEM-specific code.  The string buffer pointers
(ES:EDI and DS:ESI) and the contents of the SM CLP Command Line string buffer are preserved.
The SM CLP Command Response string buffer is filled in by the option ROM in the
“keyword=value” format described in the SM CLP Specification (refer to Section 5.1.10, “Output
Data”), unless otherwise requested via the SM CLP –output option in the Command Line string
buffer.  Option ROM support for this default “keyword=value” output format is required, while
support for other SM CLP output formats is optional (the SM CLP option ROM should return an
OPTION NOT SUPPORTED error in AH if the SM CLP – output option requested by the caller
is not supported by the option ROM).
All other x86 registers are preserved.
Note that not all 3.0 (or later) system firmware will support calling the DMTF SM CLP entry point.
The support for this function can be determined by examining the results of the “PCI BIOS
Present” call described in Section 2.5.2.  This is useful for diagnostics and validation in determining
if the DMTF SM CLP interface will be used.  In addition an Expansion ROM may change its
configuration behavior if it determines that the 3.0 (or later) system firmware will not call the DMTF
SM CLP API.
