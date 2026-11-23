---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 92
headings: []
---

# Source page 92

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  92

Table 4-15: PCIe SSD Device Status Bitmap Description
Bit State Description
Bit [2] OK OK state may mean the drive is functioning normally. This state may
implicitly mean that a PCIe SSD is present, powered on, and working
normally as seen by the software. A more granular indication of the
drive not physically present or present but not powered up are both
outside the scope of this specification.
Bit [3] Locate Locate state may mean the specific drive is being identified by an
OSPM.
Bit [4]  Fail Fail state may mean the drive is not functioning properly.
Bit [5] Rebuild Rebuild state may mean this drive is part of a multi-drive storage
volume/array that is rebuilding or reconstructing data from redundancy
on to this specific drive.
Bit [6] PFA PFA stands for Predicted Failure Analysis. This state may mean the
drive is still functioning normally but predicted to fail soon.
Bit [7] Hot Spare Hot Spare state may mean this drive is marked to be automatically
used as a replacement for a failed drive and contents of the failed drive
may be rebuilt on this drive.
Bit [8]  In a Critial Array In A Critical Array state may mean the drive is part of a multidrive
storage array and that array is degraded.
Bit [9] In a Failed Array In A Failed Array state may mean the drive is part of a multidrive
storage array and that array is failed.
Bit [10] Invalid Device Type Invalid Device Type state may mean the drive is not the right type for
the connector (e.g., An enclosure supports SAS and NVMe drives and
this drive state indicates that a SAS drive is plugged into an NVMe
Slot).
Bit [11] Disabled Disabled state mean slot is disabled. The power from this slot may be
removed.
