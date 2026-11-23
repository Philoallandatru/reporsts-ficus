---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 34
headings: ["3.5. Device State at Firmware/Operating System Handoff"]
---

# Source page 34

UEFI PCI SERVICES
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  34
3.5. Device State at Firmware/Operating System
Handoff
System firmware is only required to configure the boot and console devices.  This section specifies
the state of the PCI subsystem at firmware handoff and provides guidance to the operating system
on how to determine if a particular component was configured by firmware.  PCI subsystem refers
to components that are compliant to the PCI, PCI-X, or PCI-Express Specifications.  In this
section, “PCI Specifications” refers to the PCI, PCI-X, or PCI Express Specification.
Firmware owns the PCI subsystem prior to handing control off to the operating system.  The
handoff point is the return from UEFI ExitBootServices().  After the operating system loader calls
ExitBootServices(), the operating system owns the PCI subsystem.
Firmware may provide pre-boot user interaction to allow the system operator to specify the desired
boot and console devices.
Firmware must configure the entire path to the console (both input and output) and boot devices.
This includes, the chipset, bridges, and multi-function devices.  The device configuration is required
to load the operating system loader, display boot up messages, and allow operator interaction with
the boot process.
Optionally, firmware may configure all devices and bridges in the system.  Firmware is not required
to configure devices other than boot and console devices.
Since not all devices may be configured prior to the operating system handoff, the operating system
needs to know whether a specific BAR register has been configured by firmware.  The operating
system makes the determination by checking the I/O Enable, and Memory Enable bits in the
device's command register, and Expansion ROM BAR enable bits.  If the enable bit is set, then the
corresponding resource register has been configured.
Note:  The operating system does not use the state of the Bus Master Enable bit to determine the
validity of the BARs.  If the BAR ranges are enabled, the device must respond to those addresses.
The device may not be able to master a transaction, but enabled BARs must be configured correctly
by firmware.
The operating system is required to configure PCI subsystems:
❑ During hotplug
❑ For devices that take too long to come out of reset
❑ PCI-to-PCI bridges that are at levels below what firmware is designed to configure
