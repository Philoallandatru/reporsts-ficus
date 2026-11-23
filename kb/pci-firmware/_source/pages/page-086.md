---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 86
headings: []
---

# Source page 86

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  86
Also note that in this flow chart, certain events (such as DPC trigger) may generate an interrupt to the firmware
(e.g., an ERR_COR message may be sent when DPC is triggered which may be used to generate a SMI to
invoke firmware) and other events may generate interrupts to the operating system (e.g., MSI or MSI-X for Data
Link Layer State Changed and Presence Detect State Changed hot-plug interrupts).
The PCI Express Base Specification requires that the events be signaled in a specific order. For example, on a
DPC trigger event the ERR_COR for the DPC event is required to be generated prior to the MSI or MSI-X for
the Data Link Layer State Changed event. However, many processors cannot guarantee the order of execution
of these events. In some cases, the interrupt handler for firmware may be executed first and in other cases the
operating system interrupt handler may be executed first. In other cases, the operating system interrupt handler
may partially run, then get interrupted by the firmware which runs to completion, and then returns to the
operating system interrupt handler to finish executing.
Sample ASL Code
Scope(\_SB){
Device(PCI0) {   //
   Name (_HID, EISAID("PNP0A03"))
   Name (_UID, 0)
   //..
   Method(_OSC,4, Serialized) {
    // Extended to support DPC specific extensions
   }

   Device(RP0) { // Root port 0, supports DPC
     Name (_ADR , 0)  // Device 0, function 0

     OperationRegion (DPC0, PCI_Config, 0x160, 0x20)
     Field (DPC0, AnyAcc, NoLock, Preserve)
     {
       Hdr, 32 // Start of DPC register block
       // define rest of the DPC registers so that FW can access these from ASL
     }

   Method (_DSM, 4, Serialized)
   {
     // check for GUID and revision match
     Switch(Arg2) {
       Case(0xC) {
         // Enable/disable DPC request, replace x with the spec assigned value
         If (LEqual(Arg3, 0)) {
         // Enable HPS if supported/applicable, disable DPC by modifying
         //  registers in DPC0 op region
         }
         If (LEqual(Arg3, 1)) {
         // Enable DPC by modifying registers in DPC0 op region
         }
       } // End Arg2=0xC
       Case (0xD) {
         // return BDF of port that experienced containment
       } // End Arg2=0xD
     } // End Switch
   } // End DSM

   Method(_OST, 3, Serialized) {
     // OSPM calls this method after processing ErrorDisconnectRecover
     //  notification from firmware
     Switch(And(Arg0,0xFF)) // Mask to retain low byte
     {
       Case(0x0F) { // Error Disconnect Recover request
