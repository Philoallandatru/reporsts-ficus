---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 33
headings: ["3.1.2. PCI Driver Model", "3.2. PCI-X Mode 2 and PCI Express", "3.3. EFI Byte Code", "3.4. Graphics Output Protocol"]
---

# Source page 33

UEFI PCI SERVICES
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  33
3.1.2. PCI Driver Model
The PCI Driver Model is designed to extend the UEFI Driver Model in a way that supports PCI
Bus Drivers and PCI Device Drivers.  This applies to Conventional PCI, PCI-X, and PCI Express.
PCI Bus Drivers manage PCI buses present in a system.  The PCI Bus Driver creates child device
handles that must contain a Device Path Protocol instance and a PCI I/O Protocol instance.  The
PCI I/O Protocol is used by the PCI Device Driver to access memory and I/O on a PCI controller.
PCI Device Drivers manage PCI controllers present on PCI buses.  The PCI Device Drivers
produce an I/O abstraction that may be used to boot an UEFI compliant operating system.
3.2. PCI-X Mode 2 and PCI Express
The PCI-X Mode 2 and PCI Express provide a software programming model that is software
compatible with the Conventional PCI.
UEFI PCI I/O Protocol supports up to 4 GiB of configuration space; therefore, it covers the PCI-
X Mode 2 and PCI Express Extended Configuration space of 4 KiB in size.
UEFI uses a single timer interrupt in pre-boot, UEFI device drivers are polled so INTx, MSI, or
MSI-X is not used by UEFI.
To identify a function (e.g., Conventional PCI, PCI-X vs. PCI Express), the UEFI driver uses
Device ID, Vendor ID, and Capability Pointer in the compatibility configuration space.
3.3. EFI Byte Code
The UEFI Specification defines a virtual machine that provides a platform and CPU independent
mechanism for loading and executing UEFI device drivers.  The instruction set of the virtual
machine is called EFI Byte Code, or EBC.
For details of the EBC Virtual Machine, refer to the UEFI Specification.
3.4. Graphics Output Protocol
Graphics Output Protocol (GOP) is defined in the UEFI Specification to remove the hardware
requirement to support legacy VGA and INT 10h BIOS.  GOP provides a software abstraction to
draw on the video screen.
Note:  A graphics adapter will still require a performance driver for high speed operation in the
operating system.
Note:  VGA hardware can support GOP.
