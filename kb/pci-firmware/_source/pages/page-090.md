---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 90
headings: ["4.7.1. _DSM Method Output", "4.7.2. Query Supported Functions (Function Index 0)"]
---

# Source page 90

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  90

4.7.1. _DSM Method Output
Functions 1, 2, and 3 shall return a buffer of length greater than or equal to 4. The first four bytes of
the output buffer represent status are structured in Table 4-13.
Table 4-13: Status Field
Field Byte Length Byte Offset Description
General Status Code 2 0 0 – Success
1 – Not Supported
2 – Invalid Input Parameters
3 – Communication Error
4 – Function-Specific Error Code
5 – Vendor-Specific Error Code
6 - 0xFFFF – Reserved
Function-specific
Error Code
1 2 This field contains an error code that is specific to
the function. This field only contains valid
information if General Status Code = Function-
Specific Error Code.
Vendor-specific Error
Code
1 3 This field contains vendor-specific status codes. It
only contains valid information if General Status
Code = Vendor-Specific Error Code.
Note:  Any non-zero General Status Code indicates that the function failed.
4.7.2. Query Supported Functions (Function Index 0)
Function 0 of every _DSM is a query function that returns the set of supported function indexes
and is always required. This function returns the functions supported by this interface version
Input (Arg3)
None
Return
This function returns an ACPI Buffer containing the byte values {0x0F}
