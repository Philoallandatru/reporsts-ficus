---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 109
headings: ["5.2.1.5. Memory Usage", "1.1.1.1.", "1.1.1.1.", "1.1.1.1.", "1.1.1.1.", "1.1.1.1.", "1.1.1.1.", "1.1.1.1.", "5.2.1.6. Verification of BIOS Support"]
---

# Source page 109

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  109
5.2.1.5. Memory Usage
In PCI Firmware Specifications version 2.1 and earlier, the Expansion ROM code had no method for
reliably sharing the system resources with the BIOS, particularly memory.  PCI Expansion ROMs
attempted to allocate memory from the Extended BIOS Data Area (EBDA) or search for erased
areas of low memory for temporary use. Many PCI Expansion ROMs fail to implement robust
algorithms for sharing memory, and unpredictable behavior may occur.
The Expansion ROM code must make a call to the POST Memory Manager (PMM) to reserve
memory, either for temporary usage or for permanent usage.  This BIOS function call may only be
called during the Expansion ROM initialization phase (INIT phase).


IMPLEMENTATION NOTE
PMM Failure
The Expansion ROM code must be prepared to handle several PMM failure scenarios such as:
● The absence of PMM support in the BIOS
● The absence of PMM “Get Permanent Memory” support in the BIOS
● The PMM denying the request for the memory
In all cases, the 3.0 (or later) compliant Expansion ROM code must be prepared to gracefully
handle these conditions.

5.2.1.6. Verification of BIOS Support
The Expansion ROM code must first verify that the system BIOS is compliant with version 3.0 (or
later) of this specification.  If the BIOS is compliant, the Expansion ROM code can call the PMM
function REQUEST_SYSTEM_MEMORY  to obtain memory for its own use.  The Expansion
ROM code also provides an argument to the PMM function to request either permanent memory or
temporary memory from the BIOS.  Refer to Section 5.2.1.20 for more details on the PMM
functions.
Note that a 3.0 (or later) compliant Expansion ROM is not required to have backward compatibility
and operate successfully with a BIOS compliant with this specification version 2.1 in a system.  It is
a design choice whether the 3.0 (or later) Expansion ROM includes support for 3.0 BIOSes only, or
both the 3.0 and 2.1 BIOSes.
