---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 11
headings: ["2.2.3. Interrupt Support", "2.3. BIOS32 Service Directory", "2.3.1. Determining the Existence of BIOS32 Service Directory"]
---

# Source page 11

TRADITIONAL PCI BIOS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  11
The PCI BIOS provides a 16-bit real and protected mode interface and a 32-bit protected mode
interface.  The 16-bit interface is provided through PC/AT Int 1Ah software interrupt.  The PCI
BIOS Int 1Ah interface operates in either real mode, virtual-86 mode, or 16:16 protected mode.
The BIOS functions may also be accessed through the industry standard entry point for INT 1Ah
(physical address 000F FE6Eh) by simulating an INT instruction.3  The INT 1Ah entry point
supports 16-bit code only.  Protected mode callers of this interface must set the CS selector base to
0 F000h.
The protected mode interface supports 32-bit protected mode callers.  The protected mode PCI
BIOS interface is accessed by calling (not a simulated INT) through a protected mode entry point in
the PCI BIOS.  The entry point and information needed for building the segment descriptors are
provided by the BIOS32 Service Directory (refer to Section 2.3).  32-bit callers invoke the PCI BIOS
routines using CALL FAR.
The PCI BIOS routines (for both 16-bit and 32-bit callers) must be invoked with appropriate
privilege so that interrupts can be enabled/disabled and the routines can access I/O space.
Implementers of the PCI BIOS must assume that CS is execute-only and DS is read-only.
2.2.3. Interrupt Support
To support PC-compatible BIOS, the system must support the INTx routing.  MSI or MSI-X may
be supported for the operating system use after booted from BIOS.
2.3. BIOS32 Service Directory
Detecting the absence or presence of 32-bit BIOS services with 32-bit code can be problematic.
Standard BIOS entry points cannot be called in 32-bit mode on all machines because the platform
BIOS may not support 32-bit callers.  This section describes a mechanism for detecting the presence
of 32-bit BIOS services.  While the mechanism supports the detection of the PCI BIOS, it is
intended to be broader in scope to allow detection of any/all 32-bit BIOS services.  The description
of this mechanism, known as BIOS32 Service Directory, is provided in three parts; the first part
specifies an algorithm for determining if the BIOS32 Service Directory exists on a platform, the
second part specifies the calling interface to the BIOS32 Service Directory, and the third part
describes how the BIOS32 Service Directory supports PCI BIOS detection.
2.3.1. Determining the Existence of BIOS32 Service
Directory
A BIOS which implements the BIOS32 Service Directory must embed a specific, contiguous
16-byte data structure, beginning on a 16-byte boundary somewhere in the physical address range
0E 0000h - 0F FFFFh.  A description of the fields in the data structure are given in Table 2-1.

3 Note that accessing the BIOS functions through the industry standard entry point will bypass any code that may
have “hooked” the INT 1Ah interrupt vector.
