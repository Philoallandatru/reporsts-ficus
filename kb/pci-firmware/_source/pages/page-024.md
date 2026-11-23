---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 24
headings: ["2.7.2. INT1Ah Access Calls in Real Mode", "2.7.3. Read Configuration Byte"]
---

# Source page 24

TRADITIONAL PCI BIOS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  24
2.7.2. INT1Ah Access Calls in Real Mode
The real mode invocations of INT 1Ah for reading the PCI Express Extended Configuration space
are intended to be used for handling the internal BIOS/system firmware code calls during POST (if
needed).  After POST, it is recommended that the PCI Express Extended Configuration space be
accessed directly without the use of INT 1Ah.  The ACPI MCFG table describes the location of the
PCI Express configuration space, and this table will be present in a firmware implementation
compliant to this specification version 3.0 (or later).  If INT 1Ah is invoked after POST for reading
the PCI Express extended configuration space, the firmware may return
FUNC_NOT_SUPPORTED.
2.7.3. Read Configuration Byte
This function allows reading individual bytes from the configuration space of a specific device.
ENTRY:
 [AH] PCI_FUNCTION_ID
 [AL] READ_CONFIG_BYTE
 [BH] Bus Number (0...255)
 [BL] Device Number in upper 5 bits,
  Function Number in lower 3 bits.
 [DI] Register Number (0...4095) [bits 11:0]
   To Read Register number greater than 255 [bit15=1]
   To Read Register number less than or equal to 255 [bit15=0]
EXIT:
 [CL] Byte Read
 [AH] Return Code:
   SUCCESSFUL
   BAD_REGISTER_NUMBER
   FUNC_NOT_SUPPORTED
 [CF] Completion Status, set = error, reset = success.
