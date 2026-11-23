---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 22
headings: []
---

# Source page 22

TRADITIONAL PCI BIOS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  22
This routine causes the specified hardware interrupt (IRQ) to be connected to the specified interrupt
pin of a PCI device.  It makes the following assumptions:
1. The caller  is responsible for all error checking to ensure no resource conflict exits between the
specific hardware interrupt assigned to the PCI device and any other hardware interrupt resource
in the system.
2. The caller is responsible for ensuring that the specified interrupt is configured properly (level
triggered) in the interrupt controller.  If the system contains hardware outside of the interrupt
controller that controls interrupt triggering (edge/level), then the callee (i.e., the BIOS) is
responsible for setting that hardware to level triggered for the specified interrupt.
3. The caller is responsible for updating PCI configuration space (i.e., Interrupt Line registers) for
all effected devices.
4. The caller must be aware that changing IRQ routing for one device will also change the IRQ
routing for other devices whose INTx# pins are WIRE-ORed together (i.e., they have the same
link field in the Get Routing Expansions call).
If the requested interrupt cannot be assigned to the specified PCI device, then SET_FAILED status
is returned.  This routine immediately effects the interrupt routing and does nothing to remember
the routing for the next system boot.
The BusDev parameter specifies the PCI bus and device numbers for the PCI device/slot being
modified.  The high-order byte of BusDev contains the PCI bus number.  The device number is
provided in the top five bits of the low-order byte of BusDev.  For example, to specify device 6 on
PCI bus 2 the BusDev parameter would be 0230h.
The IntPin parameter specifies which interrupt pin (INTA#,..,INTD#) of the specified PCI device/slot
is effected by this call.  A value of 0Ah corresponds to INTA#, 0Bh to INTB#, etc.
The IRQNum parameter specifies which IRQ input is to be connected to the PCI interrupt pin.
This parameter can have values of 0..15 specifying IRQ0 thru IRQ15 respectively.
ENTRY:
[AH] PCI_FUNCTION_ID
[AL] SET_PCI_HW_INT
[CL] IntPin parameter.  Valid values 0Ah..0Dh.
[CH] IRQNum parameter.  Valid values 0..0Fh.
[BX] BusDev parameter.  [BH] holds bus number,
[BL] holds Device (upper 5 bits), and
Function (lower 3 bits) numbers.
[DS] Segment or Selector for BIOS data.
For 16-bit code, the real-mode segment or
the Protected Mode selector must resolve to
physical address 0F 0000h and have a limit
of 64 KiB.
For 32-bit code, see Section 2.4.
