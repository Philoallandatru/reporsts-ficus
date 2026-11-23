---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 71
headings: ["4.6.4.1.3. _DSM for Bus Capabilities"]
---

# Source page 71

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  71
4.6.4.1.3. _DSM for Bus Capabilities
This section describes how the Bus Capabilities structure is exposed through the _DSM ACPI
method.
The _DSM method must appear in the context of a PCI root bus, identified by a _HID or _CID of
PNP0A03.  The UUID for reporting a Bus Capabilities structure in a _DSM in this context is
{E5C937D0-3553-4D7A-9117-EA4D19C3434D}, the revision is 1, and the function is 4.
Note:  Function 0 is a generic Query function that is supported by _DSMs with any UUID and
Revision ID.
Location:
This object will be placed under the object representing the PCI or PCI-X root bus in the ACPI
namespace.  This object should have a _HID or _CID of PNP0A03.
Arguments:
Arg0: UUID: E5C937D0-3553-4d7a-9117-EA4D19C3434D
Arg1: Revision ID: lowest valid Revision ID value: 1
Arg2: Function Index: 4
Arg3: Empty Package
Return:
ACPI Buffer type; the definition of the return a package of two items and the description is as
follows.
Package item 1:
Type: Integer
Purpose: status of operation
Description: 0: Failure
 1: Success

Package item 2:
Type: Buffer
Purpose: Capabilities structure
Description: The buffer layout will be as follows:

Field Byte Length Byte Offset Value Description
Version 2 0 1 Version of the return buffer
Status 2 2 Zero or
Ones
Status return of this method: Zero
indicates success, Ones indicate
failure.
Length 4 4 Computed The length of the entire buffer, in
bytes, including the version,
starting from offset 0.  This field is
used to record the size of the
entire buffer.
Bus
Capabilities
Structure
Dependent on capability
type and size of structure
8 Computed The bus capabilities as defined in
the Bus Capabilities Structure
Definitions
