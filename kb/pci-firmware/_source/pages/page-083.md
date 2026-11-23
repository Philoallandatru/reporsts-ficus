---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 83
headings: []
---

# Source page 83

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  83
Arguments:
Arg0: UUID: E5C937D0-3553-4d7a-9117-EA4D19C3434D
Arg1: Revision ID: lowest valid Revision ID value: 5 (Refer to the Downstream Port Containment
Related Enhancements ECN for details on Revision 5 of this function.  The current
definition of this function was introduced with a Revision ID of 6.)
Arg2: Function Index: 0Ch
Arg3:  Downstream Port Containment and Hot-Plug Surprise Control
Type: Package
Description: A package of one integer
Integer 1:
0: Disable DPC. If this _DSM function is implemented, then support for disabling
DPC is optional. If disabling DPC is not supported, then the return value from this
_DSM function will be set to 1 to indicate DPC is enabled. If disabling DPC is
supported, then the following steps are required:
1. First, firmware should set the Hot-Plug Surprise bit if the port is Hot-Plug
Surprise capable and the port provides a way to set to the Hot-Plug Surprise bit.
If SFI HPS Suppress bit is implemented, then firmware should clear it to 0.
Proprietary mechanisms are permitted to be used to set the Hot-Plug Surprise
to 1 if the SFI HPS Suppress bit is not implemented. This step is skipped if the
port does not provide a way to set the Hot-Plug Surprise bit.
2. If firmware owns DPC:
- Firmware disables DPC
Else if the operating system owns DPC:
- The operating system disables DPC after evaluating this _DSM function.
It is recommended that disabling DPC be performed as soon as possible after enabling
Hot-Plug Surprise in order to minimize the window where DPC is enabled but HPS is
not suppressed.

1:  Enable DPC. If this _DSM function is implemented, then support for enabling
DPC is mandatory; however, firmware may choose not to enable DPC in certain cases.
If firmware chooses not to enable DPC, then the return value from this _DSM
function will be cleared to 0 to indicate DPC is disabled. The following steps are
required if firmware chooses to enable DPC:
1.  If firmware owns DPC:
- Firmware enables DPC
Else if the operating system owns DPC:
- The operating system enables DPC prior to evaluating this _DSM function.
2.  Second, firmware should clear the Hot-Plug Surprise bit if the port is Hot-Plug
Surprise capable and the port provides a way to clear to the Hot-Plug Surprise
bit. If SFI HPS Suppress bit is implemented, then firmware should set it to 1.
Proprietary mechanisms are permitted to be used to clear the Hot-Plug Surprise
to 0 if the SFI HPS Suppress bit is not implemented.
It is recommended that suppressing Hot-Plug Surprise be performed as soon as
possible after enabling DPC in order to minimize the window where DPC is enabled
but HPS is not suppressed.
