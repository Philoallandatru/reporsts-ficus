---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 20
headings: []
---

# Source page 20

TRADITIONAL PCI BIOS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  20
This routine requires one parameter, RouteBuffer, which is a far pointer to the data structure shown
below.
typedef struct
 {
WORD            BufferSize;
BYTE   FAR * DataBuffer;
 }  IRQRoutingExpansionsBuffer;
 where
BufferSize:  A word size value providing the size of the data buffer.  If the buffer is
too small, the routine will return with status of BUFFER_TOO_SMALL, and this
field will be updated with the required size.  To indicate that the running PCI system
does not have any PCI devices, this function will update the BufferSize field to zero.
On successful completion, this field is updated with the size (in bytes) of the data
returned.
DataBuffer:  Far pointer to the buffer containing PCI interrupt routing information
for all motherboard devices and slots.

IMPLEMENTATION NOTE
Defining the DataBuffer in C
The code example above is syntactically correct for C language in all processor modes.  But the
storage size of the BYTE FAR * offset varies for each mode as follows:
● Real Mode: 2 WORD (Segment:Offset)
● PM16: 2 WORD (Selector:Offset)
● PM32: 3 WORD (Selector:32bitOffset)

This routine also returns information about which IRQs are currently dedicated for PCI usage.  This
information is returned as a bit map where a set bit indicates that the IRQ is dedicated to PCI and
not available for use by devices on other buses.  Note that if an IRQ is routed such that it can be
used by PCI devices and other devices the corresponding bit in the bit map should not be set.  The
function returns this information in the [BX] register where bit 0 corresponds to IRQ0, bit 1 -
IRQ1, etc.  The caller must initialize [BX] to zero before calling this routine.
