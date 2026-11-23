---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 122
headings: ["5.2.2. UEFI Expansion ROM (Type 3)"]
---

# Source page 122

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  122
Similarly an Expansion ROM is not required to have a DMTF SM CLP entry point.  If the entry
point is not present, the “Pointer to the DMTF SM CLP entry point” field in the PCI Data
Structure (see Section 5.2.1) should be null.
The normal power-up sequence concerning SM CLP is as follows:
1. An SM CLP configuration session is started via a remote console.
2. The system ROM facilitates the configuration of the PCI device(s) by passing SM CLP
commands via the SM CLP Entry Point interface.
3. The Expansion ROM SM CLP code stores the configuration settings in a non-volatile location
associated with the targeted PCI device so that the configuration information is available to the
PCI device’s option ROM Init code on current and subsequent boots.
4. The system ROM initializes the PCI device(s) by calling the PCI Expansion ROM Init entry
point.
Note: SM CLP configuration sessions that occur after the PCI Expansion ROM Init code has
executed may require the system to be rebooted so that the new configuration changes can take
effect.
5.2.2. UEFI Expansion ROM (Type 3)
Section 13.4.2 “PCI Option ROMs” of the Unified Extensible Firmware Interface Specification, Version 2.4
(http://www.uefi.org) describes ways to store UEFI images (e.g., UEFI drivers) in PCI Expansion
ROMs.  The description in Section 5.2.1 of this document does not apply to UEFI Expansion
ROMs.
