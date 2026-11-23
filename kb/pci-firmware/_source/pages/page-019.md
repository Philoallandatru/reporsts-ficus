---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 19
headings: []
---

# Source page 19

TRADITIONAL PCI BIOS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  19
Table 2-2:  Layout of IRQ Routing Table Entry
Offset Size Description
0 byte PCI Bus number
1 byte PCI Device number (in upper 5 bits)
2 byte Link value for INTA#
3 word IRQ bit-map for INTA#
5 byte Link value for INTB#
6 word IRQ bit-map for INTB#
8 byte Link value for INTC#
9 word IRQ bit-map for INTC#
11 byte Link value for INTD#
12 word IRQ bit-map for INTD#
14 byte Slot Number
15 byte Reserved (for OEM use)

Two values are provided for each PCI interrupt pin in every slot.  One of these values is a bit-map
that shows which of the standard AT IRQs this PCI interrupt can be routed to.  This provides the
routing Expansions for one particular PCI interrupt pin.  In this bit-map, bit 0 corresponds to
IRQ0, bit 1 to IRQ1, etc.  A “1” bit in this bit-map indicates a routing is possible:  a “0” bit indicates
no routing is possible.  The second value is a “link” value that provides a way of specifying which
PCI interrupt pins are wire-OR'ed together on the motherboard.  Interrupt pins that are wired
together must have the same “link” value in their table entries.  Values for the “link” field are
arbitrary except that the value zero indicates that the PCI interrupt pin has no connection to the
interrupt controller.5
The Slot Number value at the end of the structure is used to communicate whether the table entry is
for a motherboard device or an add-in slot.  For motherboard devices, Slot Number should be set to
zero.  For add-in slots, Slot Number should be set to a value that corresponds with the physical
placement of the slot on the motherboard.  This provides a way to correlate physical slots with PCI
Device numbers.  Values (with the exception of 00h) are OEM specific.6  For end user ease-of-use,
slots in the system should be clearly labeled (e.g., solder mask, back panel, etc.).

5This is typically used for motherboard devices that have only an IRQA# line and not IRQB#, IRQC#, or IRQD#.
6For example, a system with 4 ISA slots and 3 PCI slots arranged as 3-ISA, 3-PCI, and 1-ISA may choose to start
numbering the slots at the 3-ISA end in which case the PCI slot numbers would be 4, 5, and 6.  If slot numbering
started at the 1-ISA end, PCI slot numbers would be 2, 3, and 4.
