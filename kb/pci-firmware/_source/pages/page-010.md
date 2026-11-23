---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 10
headings: ["2. Traditional PCI BIOS", "2.1. Functional Description", "2.2. Assumptions and Constraints", "2.2.1. ROM BIOS Location", "2.2.2. Calling Conventions"]
---

# Source page 10

PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021 10




2.Traditional PCI BIOS
2.1. Functional Description
PCI BIOS functions provide a software interface to the hardware used to implement a PCI based
system.  Its primary usage is for generating operations in PCI specific address spaces (configuration
space and Special Cycles).
PCI BIOS functions are specified to operate in the following modes of the X86 architecture.  The
modes are:  real-mode, 16:16 protected mode (also known as 286 protected mode), 16:32 protected
mode (introduced with the 386), and 0:32 protected mode (also known as “flat” mode, wherein all
segments start at linear address 0 and span the entire 4 GiB address space).
Access to the PCI BIOS functions for 16-bit callers is provided through Interrupt 1Ah.  32-bit (i.e.,
protected mode) access is provided by calling through a 32-bit protected mode entry point.  The
PCI BIOS function code is B1h.  Specific BIOS functions are invoked using a sub-function code.  A
user simply sets the host processors registers for the function and sub-function desired and calls the
PCI BIOS software.  Status is returned using the CARRY FLAG ([CF]) and registers specific to the
function invoked.
2.2. Assumptions and Constraints
2.2.1. ROM BIOS Location
The PCI BIOS functions are intended to be located within an IBM-PC compatible ROM BIOS.
2.2.2. Calling Conventions
The PCI BIOS functions use the X86 CPU’s registers to pass arguments and return status.    The
caller must use the appropriate sub-function code.
These routines preserve all registers and flags except those used for return parameters.  The CARRY
FLAG [CF] will be altered as shown to indicate completion status.  The calling routine will be
returned with the interrupt flag unmodified and interrupts will not be enabled during function
execution.  These routines are re-entrant.  These routines require 1024 bytes of stack space and the
stack segment must have the same size (i.e., 16-bit or 32-bit) as the code segment.
2
