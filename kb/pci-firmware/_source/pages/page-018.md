---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 18
headings: ["2.6. PCI Support Functions", "2.6.1. Generate Special Cycle", "2.6.2. Get PCI Interrupt Routing Expansions"]
---

# Source page 18

TRADITIONAL PCI BIOS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  18
2.6. PCI Support Functions
The following functions provide support for several PCI specific operations.
2.6.1. Generate Special Cycle
This function allows for generation of PCI special cycles.  The generated special cycle will be
broadcast on a specific PCI bus in the system.
ENTRY:
 [AH]   PCI_FUNCTION_ID
 [AL]  GENERATE_SPECIAL_CYCLE
 [BH]  Bus Number (0...255)
 [EDX]  Special Cycle Data
EXIT:
 [AH]  Return Code:
    SUCCESSFUL
    FUNC_NOT_SUPPORTED
 [CF]  Completion Status, set = error, reset = success.
2.6.2. Get PCI Interrupt Routing Expansions
Description:
Logical input parameters:
RouteBuffer Pointer to buffer data structure
This routine returns the PCI interrupt routing Expansions available on the system motherboard and
also the current state of what interrupts are currently exclusively assigned to PCI.  Routing
information is returned in a data buffer that contains an IRQ Routing for each PCI device or slot.
The format of an entry in the IRQ routing table is shown in Table 2-2.
