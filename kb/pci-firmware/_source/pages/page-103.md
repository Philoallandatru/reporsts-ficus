---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 103
headings: ["5.2. Firmware Power-on Self Test (POST) Firmware"]
---

# Source page 103

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  103
5.2. Firmware Power-on Self Test (POST) Firmware
The description of the POST firmware (BIOS) in this section is only pertinent to the management
of PCI Expansion ROMs.  The POST Firmware goes through several steps to configure a PCI
Expansion ROM.  These steps are described below:
1. The POST Firmware examines the PCI bus topology to individually examine each PCI device.
If the device has implemented an Expansion ROM Base Address register in Configuration
Space, then the POST firmware proceeds to the next step.
Note that individual functions on a multi-function PCI Device may each have an Expansion
ROM Base register implementation.
Note that the order in which PCI Devices are examined and initialized is not defined.
2. The POST firmware enables the Expansion ROM at an unused memory address.
3. The POST firmware checks the first two bytes in the Expansion ROM for the AA55h signature.
If that signature is found, then there is a ROM present.  Otherwise, no ROM is attached to the
device, and the POST firmware proceeds to step 10.
4. If a ROM is attached, the POST firmware must search the ROM for an image that has the
proper Code Type.  The following steps can be used to search multiple images.
• If the pointer is valid (non-zero), examine the target location of the pointer.  If the pointer is
invalid, no further images can be located.
• The target location must contain the signature string “PCIR”.  If a valid signature is not
present, no further images can be located.
• If the signature string is valid, examine the Code Type field to determine if it is correct for the
expected type of execution environment.  (Refer to the Code Type field entry for more
information).
• If the Code Type field is not appropriate, then the BIOS needs to continue searching for
Images as described in the next step.  If the Code Type field is appropriate, the BIOS
proceeds to step 5 below.
• The BIOS should then examine the “Last Image” field to determine if more images are
present.  If no further images are present, the BIOS should proceed to step 9.
• If more images are present, the Image Length field should be examined to determine the
starting location of the next image.  The Image Length is added to the starting address of the
current image (not Image 0).  Note that Image Length is in units of 512 bytes.
• The BIOS proceeds to step 3 above.
5. After the correct image has been selected, POST Firmware will verify that the Vendor ID and
Device ID fields match the corresponding fields in the device.
