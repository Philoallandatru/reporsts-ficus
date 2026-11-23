---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 67
headings: ["4.6.3. _DSM for Vendor-specific Token ID Strings"]
---

# Source page 67

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  67
4.6.3. _DSM for Vendor-specific Token ID Strings
For vendor-specific token IDs, the tokens themselves do not provide enough information to display
slot number information to the user.  This section provides a method for the BIOS to return a
human readable description in multiple languages of the hardware element represented by a vendor-
specific token ID.  In the example usage of the _DSM for PCI Express Slot Number in
Section 4.6.2, if a vendor-specific token ID is used, the resulting string displayed to the user would
contain a string returned from this method instead of a standard string like “Cabinet” or “Slot”.
This method returns a package of packages.  Each sub-package consists of a Language identifier and
corresponding Unicode string for a given locale.  Specifying a language identifier allows OSPM to
easily determine if support for displaying the Unicode string is available.  OSPM can use this
information to determine whether or not to display the device string, or which string is appropriate
for a user’s preferred locale.  It is assumed that OSPM will always support the primary English locale
to accommodate English embedded in a non-English string, such as a brand name.  If OSPM does
not support the specific sub-language ID, it may choose to use the primary language ID for
displaying device text.
The language IDs returned by this method indicate that the corresponding string follows the format
specified in RFC 3066.  Strings are returned in Unicode (UTF-16).
In addition to supporting the existing strings in RFC 3066, the following aliases are also supported:
RFC String Supported Alias String
zh-Hans zh-chs
zh-Hant zh-cht
Location:
This method must exist in the same context as the _DSM for PCI Express Slot Number.
.

Arguments:
Arg0: UUID: E5C937D0-3553-4d7a-9117-EA4D19C3434D
Arg1: Revision ID: lowest valid Revision ID value: 1
Arg2: Function Index: 3
Arg3: A package containing one element.  The element is the Token ID to return the string
for.  The Token ID must be an integer in the range 80h-FFh.

Return:
A package of packages.
Each sub-package contains two elements:
The language ID of the string
The Unicode string representing the token ID
