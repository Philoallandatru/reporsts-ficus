---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 82
headings: ["4.6.12. _DSM for Downstream Port Containment and Hot-Plug Surprise Control"]
---

# Source page 82

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  82
4.6.12. _DSM for Downstream Port Containment and Hot-
Plug Surprise Control
If the System Firmware Intermediary (SFI) capability structure is implemented, then this section
assumes that system firmware has ownership of SFI. Use cases where system firmware does not
own SFI are outside the scope of this specification.
When firmware controls Downstream Port Containment (DPC), this section describes how the
operating system can request the firmware to enable DPC and suppress Hot-Plug Surprise for a
given DPC capable root port or a switch port. When the operating system controls DPC, this
section describes how the operating system can request the firmware to suppress Hot-Plug Surprise
for a given DPC capable root port or a switch port. The request is communicated through the
_DSM ACPI method. This _DSM function is mandatory for firmware to implement on a port if the
firmware supports the Error Disconnect Recovery mechanism (defined in the ACPI Specification) on
that port. This _DSM function must be evaluated by the operating system if the operating system
supports the Error Disconnect Recovery notification regardless of whether the operating system or
firmware owns DPC. This _DSM function, if present, must be evaluated by the Error Disconnect
Recovery aware OS at least once after the _OSC handshake. As a result of plug and play operations,
this _DSM function may be evaluated multiple times during the OS operation with differing inputs.
The OS is not permitted to evaluate _DSM while the port is in DPC triggered state. It is
recommended that the OS quiesce all traffic below the port while evaluating this _DSM function.
Note that PCI Express Base Specification recommends suppressing the Hot-Plug Surprise bit in the Slot
Capabilities register when DPC is enabled and so it is recommended that firmware suppress or
enable Hot-Plug Surprise when it enables or disables DPC, respectively. Note that if HPS is
suppressed while DPC is disabled, then there is window where HPS is not suppressed and DPC is
disabled. A Surprise Down error that happens during this window may be reported as an
uncorrectable error even though DPC has not yet been enabled to handle it and therefore the
system may crash. It is therefore recommended that firmware never have Hot-Plug Surprise
suppressed while DPC is disabled.
Also note that when the firmware hands control to the operating system, it may have already
enabled DPC and may have already cleared the Hot-Plug Surprise bit. This model is to handle legacy
hardware that does not provide a way to clear the Hot-Plug Surprise bit at runtime. The details of
what the firmware does are outside the scope of this specification. However, the operating system
behavior remains same. The operating system must still evaluate this _DSM function to enable or
disable DPC and follow the flow in the implementation note below titled “DPC Event Handling”.
The operating system must evaluate this _DSM function when enabling or disabling DPC regardless
of whether the operating system or system firmware owns DPC. If the operating system owns DPC
then evaluating this _DSM function lets the system firmware know when the operating system is
ready to handle DPC events and gives the system firmware an opportunity to clear the Hot-Plug
Surprise bit, if applicable.
Location:
This object can be placed under any object representing a DPC capable PCI Express Root Port or
Switch Downstream Port. Firmware is permitted to apply the settings of this _DSM function to any
ports downstream from the port where this _DSM function is located that do not include an
instance of this _DSM function.
