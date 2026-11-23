---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 113
headings: ["5.2.1.16. VGA Expansion ROM", "5.2.1.17. Expansion ROM Placement Alignment", "5.2.1.18. BIOS Boot Specification"]
---

# Source page 113

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  113
The system firmware must write-protect the region where the PCI Expansion ROM run-time code
resides in the new range.  System firmware must have a clear understanding of the systems capability
to write-protect the various regions of RAM.  The system firmware must write-protect the region
where the PCI Expansion ROM run-time code resides in the new range.  It is possible that a 3.0 (or
later) compliant Expansion ROM cannot be placed in the A 0000h address region; for example,
because the system does not support write-protecting this region.
The region from A 0000h-B FFFFh is also the legacy frame buffer location for VGA device.  The
system firmware should exclude this range from the available Expansion ROMs space as long as
VGA device is supported.  For the system without supporting VGA device, the system firmware is
responsible for determining if there are unacceptable risks in placing the Expansion ROMs in the
region from A 0000h-B FFFFh.
5.2.1.16. VGA Expansion ROM
Prior versions of this specification have stated that VGA Expansion ROMs must be initialized into
the 0C 0000h address space.  That requirement is lifted in this version of the specification.  A 3.0 (or
later) compliant VGA Expansion ROM can be initialized at any location in the Expansion ROM
placement address range.
Diagnostic firmware and POST firmware should not assume that if a valid PCI Expansion ROM
exists at the 0C 0000h address that it is a VGA Expansion ROM.  Firmware should look at the Class
Code field in the PCI Data structure to determine if the Expansion ROM belongs to a PCI VGA
device.
The 3.0 (or later) compliant BIOS may elect to always place the VGA Expansion ROM at the legacy
0C 0000h address.  The BIOS is responsible for determining if there are unacceptable risks to
placing the VGA Expansion ROM at non-legacy addresses.
5.2.1.17. Expansion ROM Placement Alignment
Traditional ISA legacy Expansion ROMs were placed in memory at addresses aligned on a 2-KiB
boundary.  This tradition has carried through into PCI and it results in an average 1-KiB gap
between Expansion ROMs.
3.0 (or later) compliant Expansion ROMs may be placed at addresses evenly aligned on a 512-byte
boundary.  However, the BIOS must be aware of legacy operating systems and legacy applications
that will continue to search for Expansion ROMs on the traditional 2-KiB boundaries.  The BIOS is
responsible for determining if there are unacceptable risks in placing the Option ROMs at non-
legacy addresses.
5.2.1.18. BIOS Boot Specification
All 3.0 (or later) compliant Expansion ROMs must support the BIOS Boot Specification found at
http://www.acpica.org/sites/acpica/files/specsbbs101.pdf.  However this specification supersedes
the BIOS Boot Specification for the definitions of the Expansion ROM placement address, the VGA
Expansion ROM placement, and the Expansion ROM placement alignment.
