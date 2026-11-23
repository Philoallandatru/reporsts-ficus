---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 21
headings: ["2.6.3. Set PCI Hardware Interrupt"]
---

# Source page 21

TRADITIONAL PCI BIOS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  21
ENTRY:
[AH] PCI_FUNCTION_ID
[AL] GET_IRQ_ROUTING_EXPANSIONS
[BX] Must be initialized to 0000h.
[DS] Segment or Selector for BIOS data.
For 16-bit code, the real-mode segment or PM
selector must resolve to physical address
0F 0000h and have a limit of 64 KiB.
For information on 32-bit code, refer to
Section 2.4.
[ES] Segment or Selector for RouteBuffer
parameter.
[DI] for 16-bit
code
[EDI] for 32-bit
code
Offset for RouteBuffer parameter.
EXIT:
[AH] Return Code:
SUCCESSFUL
BUFFER_TOO_SMALL
FUNC_NOT_SUPPORTED
[BX] IRQ bitmap indicating which IRQs are
exclusively dedicated to PCI devices.
[CF] Completion Status, set = error, cleared =
success.
2.6.3. Set PCI Hardware Interrupt
Description:
This function is intended to be used by a system-wide configuration utility or a PNP operating
system.  This function should never be called by device drivers or Expansion ROM code.
This function is optional in this version of the specification.  The caller is responsible for checking
the return code to determine if the call is supported.
Logical input parameters:
BusDev Bus number and device number
IntPin PCI Interrupt Pin (INTA ..
INTD)
IRQNum IRQ Number (0-15)
