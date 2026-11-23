---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 88
headings: ["4.6.14. _DSM for Quering Platform Vendor Specific TPH Features"]
---

# Source page 88

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  88
Return: Location of the port that experienced containment event
Type: Integer
Description:
Port Bus, Device, and Function number encoded as a 16-bit quantity.
(Bits 2:0 = Function, Bits 7:3 = Device, Bits 15:8 = Bus)
Status of Operation as a 1-bit quantity:
Bit 31 = 0: Success
Bit 31 = 1: Failure
All other bits are reserved.
4.6.14. _DSM for Quering Platform Vendor Specific TPH
Features
The _DSM for Quering Platform Vendor Specific TPH Features function describes how PCI
Express Root Complex support for Vendor Specific decode of Steering Tags is conveyed to the PCI
bus driver. PCIe transactions may be recognized and handled specially by the root complex based on
the Steering Tag field within a TLP Header for upstream memory TLPs.
Operating System Software uses information returned from this Function to convey to a driver
managing an Endpoint to set up the Endpoint hardware to use the correct Steering Tag value as
needed. Endpoints describe their ability to use vendor-specific ST values by setting the Device
Specific Mode Supported bit in their TPH Requester Capability Register in the TPH Extended
Capability Structure.
Location:
Support for this function is only applicable for a _DSM Control Method within the scope of a PCI
Express Root Port or a Root Complex Integrated Endpoint.
Arguments:
Arg0: UUID: E5C937D0-3553-4d7a-9117-EA4D19C3434D
Arg1: Revision ID: lowest valid Revision ID value: 6
Arg2: Function Index: 0x0E
Arg3 (bits 15:0): Integer: Vendor ID
Arg3 (bits 31:16): Feature ID:  Vendor specific feature being inquired
Return:
Integer
Steering Tag value to be used for the Feature ID inquired by Arg3. If the feature is implemented by
the platform, the value must not be Zero.
