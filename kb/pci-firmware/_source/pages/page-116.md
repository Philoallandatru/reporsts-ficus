---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 116
headings: ["5.2.1.22. Option ROM and IRET Handling", "5.2.1.23. Stack Size Requirement by Expansion ROM", "5.2.1.24. Configuration Code for Expansion ROMs"]
---

# Source page 116

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  116
5.2.1.22. Option ROM and IRET Handling
The Option ROMs must be capable of handling the level triggered PCI interrupt model where an
interrupt can be shared between multiple devices.  The Option ROMs must implement appropriate
interrupt chaining mechanism and pass control to the next ISR (if present).  There should be a
default System BIOS interrupt handler for all hardware interrupts that executes the IRET and EOI
(acknowledge). Typically, most of the System BIOSes already have a default interrupt handler
installed for handling spurious interrupts.
Note:  The Option ROM always copies the current address (original Interrupt Vector Address) into
its local buffer and proceeds to install its own Interrupt Vector address.  On an ISR invocation, if an
interrupt vector address has been registered by the Option ROM, it is supposed to invoke the
original Interrupt Vector address.  The Option ROM that is the first to install in the interrupt ISR
chain will be the last Option ROM invoked during an ISR execution prior to the control being
passed to the default System BIOS handler.
The interrupt can be left masked in the “Interrupt controller” prior to an Option ROM hooking an
interrupt.  Option ROM can unmask the interrupt once the ISR is installed.  The default System
BIOS interrupt handler must not mask the interrupt once it has been unmasked by the Option
ROM.  Option ROMs in the ISR chain should not mask the level triggered shared interrupt in the
“Interrupt controller”.  System BIOS default interrupt handler should be capable of handling regular
and spurious interrupts by appropriately issuing an EOI to Master/Slave Interrupt controller if IRQ
is greater than or equal to 8.
In order to maintain backward compatibility with current system ROM implementations, the PCI
option ROMs should check for 3.0 (or later) compliant system BIOS via the PCI BIOS Present
function.  If a 3.0 (or later) compliant BIOS is detected, then the option ROM’s interrupt handler
should chain to the next interrupt handler as stated in this section and not perform an EOI.  If a 3.0
(or later) compatible system BIOS is not present, then the option ROM should just EOI and IRET.
5.2.1.23. Stack Size Requirement by Expansion ROM
The system firmware will provide a minimum 4-KiB size of stack to POST Expansion ROM.  It is
recommended that system firmware, operating system, and applications provide a minimum 4-KiB
stack when calling to Expansion ROM at run time.
5.2.1.24. Configuration Code for Expansion ROMs
Certain Expansion ROMs contain configuration code or utility code that may be executed by the
end user during Expansion ROM initialization.  Since prior versions of this specification did not
provide any mechanism for executing this code, the Expansion ROMs code writers implemented a
wide variety of methods to invoke this configuration code.
In many cases the Expansion ROM code would place a prompt on the screen, such as “Press F2 to
enter the XXXX Configuration utility”, and snoop the keystrokes looking for an invocation. This
caused issues to arise in many cases.  There was no guarantee that the invocation keystroke was not
already assigned to another purpose by the system firmware.
