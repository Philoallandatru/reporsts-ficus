---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 97
headings: ["4.10.2. _HPX", "4.10.3. Device State During Hot Plug", "4.10.4. Slot Power State After Device Removal"]
---

# Source page 97

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  97
configuration of PCI devices not configured by the BIOS at system boot.  The object is placed
under a PCI bus where this behavior is desired, such as a bus with hot-plug slots.  _HPP provided
settings apply to all child buses until another _HPP object is encountered.
4.10.2. _HPX
This optional object provides settings that apply to all child buses until another such object is
encountered.  The _HPX method supersedes the _HPP method; operating systems will
preferentially call _HPX over _HPP if both objects exist.
4.10.3. Device State During Hot Plug
PCI Hot Plug support is done through ACPI mechanism or native support.  In the case of using
ACPI, _PS3 method brings the device to its D3 state.  It is device dependent as to whether this is
D3hot or D3cold.  The PCI Express Base Specification defines the context preserved by hardware upon
resume from the D3 state, either D3hot or D3cold.  After the operating system has brought the device
out of the D3 state by using the _PS0 method, firmware with knowledge of the PCI Bus Power
Management support in the device can determine what context was preserved upon resume from
D3.
4.10.4. Slot Power State After Device Removal
PCI Hot Plug support is done through ACPI mechanism or native support.  In the case using ACPI,
_EJ0 is used to online remove a PCI device.  At _EJ0 completion, the PCI device must be isolated
for physical removal.  _EJ0 is recommended to remove the power from the slot if the platform
supports.
