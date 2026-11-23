---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 36
headings: []
---

# Source page 36

UEFI PCI SERVICES
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  36
❑ If applicable7, disable Discard SERR# Enable.  The Discard Timer SERR# Enable bit in the
Bridge Control Register controls whether the timer waiting for the completion of a delayed
transaction generates an SERR (value=1) or simply discards the transaction (value=0) on a time-
out.  The value of 1 is generally required when peer-to-peer transactions are allowed to and from
cards under that bridge.  Allowing peer-to-peer transactions is operating system policy and may
not be supported on all platforms.  Therefore, the bit should be set to 0 when firmware hands
off to the operating system, and any changes to the setting to support peer-to-peer under the
PCI-to-PCI Bridges should be made by the operating system.
The operating system may provide software to configure PCI-to-PCI bridges for optimum
performance.
All slots with an open MRL must be disabled and their Power Indicators must be turned off.  All
occupied slots with MRL closed must be enabled and their Power Indicators must be turned on.
The slot power state for unoccupied slots with MRL closed is implementation dependent and their
Power Indicators must reflect the slot power state.
Firmware must deassert RST# for all occupied PCI slots below the Host Bridge.  Firmware must
observe required wait times such as Trhfa (RST# High to First configuration Access) after taking a
bus out of reset.  Firmware only needs to delay once for all PCI bus controllers before handing
control to the operating system.  This allows the operating system to successively walk PCI buses
without having to successively delay (post reset quiesce period, 1 second) for each bus.
PCI-to-PCI Bridges have RST# asserted by default for the secondary bus.  Firmware is not required
to deassert RST# on secondary buses that are not used for boot and console devices.
UEFI drivers and applications must not change BAR assignments.  The PCI BARs  and the
configuration of any PCI-to-PCI bridge controllers belong to the firmware component that
configured the PCI Bus prior to the execution of the device driver.
The operating system must not assume that all devices have been configured.  Per Section 2.5.6 of
UEFI (Revision.2.8):  ”The presence of a UEFI driver in the system firmware or in an option ROM
does not guarantee that the UEFI driver will be loaded, executed, or allowed to manage any devices
in a platform.”  In addition, UEFI drivers are not involved during PCI hot plug.
Note:  The operating system does not have to walk all buses during boot.  The kernel can
automatically configure devices on request; i.e., an event can cause a scan of I/O on demand.
The operating system can determine if the device’s BARs have been configured by firmware by
checking the I/O Enable, and Memory Enable bits in the device’s command register, and
Expansion ROM BAR enable bit.  If the enable bit is set, then the corresponding resource has been
configured.  If the enable bit is not set, the operating system cannot assume that the associated BAR
register contains valid information.
The address that a processor uses to access a device is not necessarily the same as the address stored
in the device’s BAR.  The translation (_TRA, _TTP, and _TRS) information is not available to the
operating system until after the operating system brings up the ACPI interpreter.  The operating
system must wait until after the ACPI interpreter is up to determine the address at the processor
side associated with the BAR registers configured by firmware.  Before re-enabling a resource, the
operating system must reprogram the BAR register using a value that falls within the range reported

7 For example, does not apply to PCI Express.
