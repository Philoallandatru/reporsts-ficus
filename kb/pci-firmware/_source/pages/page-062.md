---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 62
headings: ["4.6. _DSM Definitions for PCI"]
---

# Source page 62

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  62
     }

     If(LNotEqual(CDW3,CTRL))
     { // Capabilities bits were masked
      Or(CDW1,0x10,CDW1)
     }
     // Update DWORD3 in the buffer
     Store(CTRL,CDW3)
     Return(Arg3)
    } Else {
     Or(CDW1,4,CDW1)  // Unrecognized UUID
     Return(Arg3)
    }
   } // End _OSC

            // End PCI0
4.6. _DSM Definitions for PCI
Device Specific Method (_DSM ) is defined in the ACPI Specification. This object is a control method
that enables devices to provide device specific control functions that are consumed by the device
driver. Table 4-7 below lists the UUID, Revision, and Function definitions.
The valid values of the Revision ID argument for an individual _DSM Function range from the
Initial Revision ID value (lowest value) as shown in Table 4-7 to the Current Revision ID value
(highest value).
The Current Revision ID value for this revision of this specification is 6. For example: a valid
Revision ID value for Function 8 is 3 through the Current Revision ID value inclusive; a value of 0,
1 or 2 is not valid for Function 8. Any value passed in as the Revision ID argument greater than the
Current Revision ID is invalid.
The Current Revision ID value for all Functions of this _DSM is incremented whenever a new
Function is added, or when the definition of an existing Function definition is modified in a way that
affects its operation.


Note: It is possible that the functionality of a given _DSM Function may change between
Revision ID values, in a backwards-compatible manner. System firmware may wish to support
all valid values of the Revision ID, but in doing so must process the _DSM Function invocation
in a manner expected by the Revision ID value passed in by OSPM. If system firmware
chooses to support only a subset of the valid Revision IDs, it uses the return value of _DSM
Function 0 to convey the supported Functions based on the Revision ID value to OSPM.

System firmware must support the same Revision ID value for all implemented functions. If OSPM
invokes a Function with an invalid Revision ID, system firmware must not take any action on
inputs, and any returned data may be invalid.
