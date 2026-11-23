---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 98
headings: ["5. PCI Expansion ROMs", "5.1. PCI Expansion ROM Contents"]
---

# Source page 98

PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021 98




5.PCI Expansion ROMs
The conventional PCI Local Bus Specification provides a mechanism where devices can provide
Expansion ROM code that can be executed for device-specific initialization and possibly a system
boot function.
This section describes the format, contents, and code entry points for these Expansion ROMs.  In
addition, this section also describes the services and execution environment provided to those
Expansion ROMs by system firmware compliant to this specification, version 3.0 or later.
The information in the Expansion ROMs is laid out to be compatible with existing Intel x86
Expansion ROM headers for ISA add-in cards, but it will also support other machine architectures.
PCI Expansion ROM code is never executed in place.  It is always copied from the ROM device to
RAM and executed (initialized) from RAM.  After initialization the code is moved, by the Expansion
ROM, to its final execution location in RAM, assuming the Expansion ROM code is compliant to
this specification, version 3.0 or later.  This enables dynamic sizing of the code (for initialization and
run time) and provides speed improvements when executing run-time code.
5.1. PCI Expansion ROM Contents
PCI device Expansion ROMs may contain code (executable or interpretive) for multiple processor
architectures.  This may be implemented in a single physical ROM which can contain as many code
images as desired for different system and processor architectures (see Figure 5-1).  Each image
must start on a 512-byte boundary and must contain the PCI Expansion ROM header.  The starting
point of each image depends on the size of previous images.  The last image in a ROM has a special
encoding in the header to identify it as the last image.
5
