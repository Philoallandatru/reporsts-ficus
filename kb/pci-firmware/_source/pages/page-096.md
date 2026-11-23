---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 96
headings: ["4.9. The OSHP Control Method", "4.10. Hot Plug Parameters", "4.10.1. _HPP"]
---

# Source page 96

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  96
4.9. The OSHP Control Method
Some systems that include SHPC that are released before ACPI-compliant operating systems with
native SHPC support are available, use ACPI firmware to operate the SHPC.  Firmware control of
the SHPC must be disabled if an operating system with native support is used.  Platforms that
provide ACPI firmware to operate the SHPC must also provide a control method to transfer control
to the operating system.  This method is called OSHP (Operating System Hot Plug) and is provided
for each SHPC that is controlled by ACPI firmware.  Operating systems with native SHPC support
must execute the OSHP method, if present, for each SHPC before accessing the SHPC’s registers
and when returning from a hibernated state.  If an SHPC’s OSHP method is executed multiple
times, and the switch to operating system control has already been achieved, the method must return
successfully without doing anything.  After the OSHP method is executed, the firmware must not
access the SHPC registers.  If any signals such as the System Interrupt or PME# have been redirected
for servicing by the firmware, they must be restored appropriately for operating system control.
The following is an example of a namespace entry for an SHPC that is managed by firmware:
Device(PPB1){
...
Method(OSHP, 0) {
// Disable firmware access to SHPC and restore
// the normal System Interrupt and Wakeup Signal
// connection. (See the Implementation Note below.)
}
...
}


IMPLEMENTATION NOTE
Controlling the SHPC Using ACPI
● When using ACPI to control the SHPC, the following should be considered:  Firmware should
redirect the System Interrupt and the Wakeup signal to a GPE so that ACPI can service the
interrupts instead of the operating system.  An appropriate _Lxx GPE handler should be
provided.  When an operating system with native SHPC support executes the OSHP method,
the firmware restores the normal System Interrupt and Wakeup signal connection so the
interrupts can be serviced by the operating system.  In a PCI-to-PCI bridge implementation,
access to the SHPC registers is recommended to be done through the DWORD Select/DWORD
Data pair in Configuration Space and not the memory Base Address register.  This is because
versions of ACPI prior to 2.0 do not allow memory access through a Base Address register.  In a
Host Bridge implementation, the Host Bridge Register Block can be accessed directly by
declaring a memory space operation region to encompass it.
● A platform may implement both OSHP and _OSC. However, an operating system that
comprehends _OSC will preferentially call _OSC over OSHP.
4.10. Hot Plug Parameters
4.10.1. _HPP
This optional object evaluates to the cache-line size, latency timer, SERR enable, and PERR enable
values to be used when configuring a PCI device inserted into a hot-plug slot or for performing
