---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 108
headings: ["5.2.1.3.1. Calculating a New Checksum at the End of INIT", "5.2.1.4. Image Structure and Length"]
---

# Source page 108

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  108
When the INIT function completes, the POST firmware sees that the run-time size is 8 KiB in this
example and can copy the next Expansion firmware to the optimum location.
If the INIT function wants to completely remove itself from the Expansion ROM area, it does so by
writing a zero to the Initialization Size field (the byte at offset 02h).  In this case, no checksum has to
be generated (since there is no length to checksum across).
5.2.1.3.1. Calculating a New Checksum at the End of INIT
The INIT function is responsible for guaranteeing that the checksum across the size of the image is
correct.  If the INIT function modifies the RAM area in any way, a new checksum must be
calculated and stored in the image.
The checksum is validated by performing a byte-sum of the Expansion ROM across the entire
address.  The address range is calculated from the Current Image Size field in the ROM Header.
The resulting byte-sum must be zero.
5.2.1.4. Image Structure and Length
A PC-compatible image has three lengths associated with it:  a run-time length, an initialization
length, and an image length.  The image length is the total length of the image, and it must be greater
than or equal to the initialization length. The image length is contained in the Image Length field in
the PCI Data structure.
Once the image has been copied into RAM by the POST firmware, the Image Length field is no
longer referenced by POST firmware and is no longer relevant. It does not need to be adjusted
when the Expansion ROM size changes.
The initialization length specifies the amount of the image that contains both the initialization and
run-time code.  This is the amount of data that POST firmware will copy into RAM before
executing the initialization routine.  This length is calculated from the Current Image Size at offset
2h in the ROM header. Initialization length must be greater than or equal to run-time length.
The run-time length specifies the amount of the image that contains the run-time code.  This is the
amount of data the POST firmware will leave in RAM while the system is operating.  Again this is
calculated from the Current Image Size at offset 2h in the ROM header.  The Current Image Size
must be updated if the size of the Expansion ROM is changed during the INIT phase.
The PCI Data structure must be contained within the run-time portion of the image (if there is any),
otherwise, it must be contained within the initialization portion.
It is critical that the checksum be maintained at all times.  When the POST firmware is examining
the images in the Expansion ROM the checksum for the Image Length must be zero or the image
will not be used.  Later when the Expansion ROM is initialized and the Current Image Size is
updated, the checksum must again be updated to maintain a valid image.
