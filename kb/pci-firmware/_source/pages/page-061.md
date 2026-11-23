---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 61
headings: ["4.5.3. ASL Example"]
---

# Source page 61

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  61
4.5.3. ASL Example
A sample _OSC implementation for a mobile system incorporating a PCI Express hierarchy is
shown below:
  Device(PCI0) // Root PCI bus
  {
   Name(_HID,EISAID("PNP0A08")) // PCI Express Root Bridge
   Name(_CID,EISAID("PNP0A03")) // Compatible PCI Root Bridge

   Name(SUPP,0) // PCI _OSC Support Field value
   Name(CTRL,0) // PCI _OSC Control Field value

   Method(_OSC,4)
   { // Check for proper UUID
    If(LEqual(Arg0,ToUUID("33DB4D5B-1FF7-401C-9657-7441C03DD766")))
    {
     // Create DWORD-addressable fields from the Capabilities Buffer
     CreateDWordField(Arg3,0,CDW1)
     CreateDWordField(Arg3,4,CDW2)
     CreateDWordField(Arg3,8,CDW3)

     // Save Capabilities DWORD2 & 3
     Store(CDW2,SUPP)
     Store(CDW3,CTRL)

     // Only allow native hot plug control if the OS supports:
     // * ASPM
     // * Clock PM
     // * MSI/MSI-X
     If(LNotEqual(And(SUPP, 0x16), 0x16))
     {
      And(CTRL,0x1E,CTRL) // Mask bit 0 (and undefined bits)
     }

     // Always allow native PME, AER (no dependencies)

     // Never allow SHPC (no SHPC controller in this system)
     And(CTRL,0x1D,CTRL)

     If(Not(And(CDW1,1))) // Query flag clear?
     { // Disable GPEs for features granted native control.
      If(And(CTRL,0x01)) // Hot plug control granted?
      {
       Store(0,HPCE) // clear the hot plug SCI enable bit
       Store(1,HPCS) // clear the hot plug SCI status bit
      }
      If(And(CTRL,0x04)) // PME control granted?
      {
       Store(0,PMCE) // clear the PME SCI enable bit
       Store(1,PMCS) // clear the PME SCI status bit
      }
      If(And(CTRL,0x10)) // OS restoring PCI Express cap structure?
      { // Set status to not restore PCI Express cap structure
       // upon resume from S3
       Store(1,S3CR)
      }
     }

     If(LNotEqual(Arg1,One))
     { // Unknown revision
      Or(CDW1,0x08,CDW1)
