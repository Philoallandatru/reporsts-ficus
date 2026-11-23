---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 85
headings: []
---

# Source page 85

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  85

 IMPLEMENTATION NOTE
DPC Event Handling: The following flow chart documents the behavior when firmware maintains control of
AER and DPC and grants control of PCIe Hot-Plug to the operating system.
Is OS state reliable and did
all drivers unload?
Child Device Config
Space Accessible?
 Notify(Port2, 0xF), where
Port2 may either be a parent of
Port or same as Port4.
Containment Event
Triggers system
interrupt1
System interrupt handler
locates the port that triggered
DPC
Capture error status logged by
port
Hardware
 Firmware
 OS
Cleanup - Notify and unload
child drivers below Port
Clear port error status, bring Port
out of DPC, assign bus numbers to
child devices.
If child device(s) physically present, optionally
attempt recovery using proprietary methods, re -
enable link, assign bus numbers, read and clear
error status4. _OST(0xF,BDF<<16+
0x81,
Stop
Capture error status. Optionally,
validate if device should be
recovered3.
_OST(0xF,BDF<<16+
0x80,
No
No
Yes
Yes
Capture and clear error status.
Re-enumerate child devices,
process _HPX, load drivers. OS
may instead choose to keep the
devices offline3, either via SW
(not load driver) or HW (power
down device, disable Link5,6,7).
Clear error status. OS may choose to offline
devices3, either via SW (not load driver) or
HW (power down device, disable Link5,6,7).
Otherwise process _HPX, complete device
enumeration, load drivers
Return
from _OST
Recovery
Complete
Locate and invoke DSM(0xD) in Port2
Scope and locate Port BDF. If
DSM(0xD) is not present, assume
Port=Port2.
Does Port
implement DPC?
No
 (1)  Containment may be accomplished
purely in HW (e.g., DPC) or may involve
FW assistance (e.g., FW setting the
Disable Link bit).
Surprise hot remove event for hot
plug capable slot?
Should recovery be attempted3?
No
Release DPC
if needed.
Log, Exit2
No
Yes
Cleanup. Log error/
notify user.7
  (2) A surprise hot remove may trigger
containment event if the port s Hot-
Plug Surprise bit = 0. Since surprise hot
remove event is signaled to OS via hot
plug interrupt, FW should not issue
Notify(0xF) to avoid double reporting.
FW should clear other UC errors logged
by port (if any) and bring link out of
DPC if it has entered DPC.
 (4) FW shall not generate APEI/WHEA
error records in response to DPC event
if recovery is desired, otherwise it may
interfere with recovery. In most cases,
OS can capture error status registers
from DPC port and child devices
directly.
Also part of native DPC
handler flow
Continue
Recovery?
No
Yes
Clear error
status. DPC
Software Trigger
or Disable Link5.
Yes
Success?
Yes
No
  (3) FW/OS may rely on past device
history, type of error, etc. to determine
if the recovery should be performed/
continued.
(5) If setting Disable Link and port
supports DPC, DPC should be disabled
prior to setting  Disable Link
(6) OS can call DSM(0xC) to disable DPC.
Has OS called enable
DPC DSM?
Yes
No
Release DPC
if needed,
Treat like UC
error
  (7) Link is disabled. For Hot-Plug
Capable slots, OS is required to re-
enable the link when a device is
removed in order for a subsequent
insertion to work. If link is disabled and
in-band presence detect cannot be
disabled, hot remove will not generate
a hot-plug interrupt to notify the OS. In
this case, OS should enable the link and
offline the device via SW.
Child Device Physically
Removed?
Yes
Yes
DLLSC Enable is 1b? No
Yes
Notify(Port,
DEVICE_CHECK) Return from _OST
Notify(Port,
BUS_CHECK)
Return from
_OST
Child Device
Physically
Removed?
No
Yes
No
Return from _OST
Capture
error
status

For devices with persistent errors, a port may be kept in the DPC triggered state (disabled) to keep those
devices from continuing to generate errors. For hot-plug slots, the errant device may be removed and replaced
with a new device. If the DPC trigger state is not cleared, then the port above the newly inserted device will still
be disabled and will be non-operational. Therefore, operating systems may need to modify their hot-plug
interrupt handling code to clear DPC Trigger Status when a device is removed so that a subsequent insertion
will succeed. Likewise, if the Disable Link bit or Secondary Bus Reset bit is set then the operating system is
required to clear it when a device is removed in order for a subsequent device insertion to work. Refer to note 7
in the flow chart.
