---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 87
headings: ["4.6.13. _DSM for Locating the Port that Experienced the Containment Event"]
---

# Source page 87

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  87
         Switch(AND(Arg1, 0xFF))  {
           Case (0x80) {// Success
           // Extract BDF of the port with containment event from upper
           //  word of Arg1.
           // Read AER status register from the endpoint below this port.
           } // End Case(0x80)

           Default {
           // IO recovery failed or unrecognized status code
           // Optionally, attempt FW specific recovery.  OK to do nothing
           } // End Default
         } // End Switch
       } // End Case(0xF)
     } // End Switch
   } // End _OST
  } // End RP0
} // End PCI0
} // End \_SB


4.6.13. _DSM for Locating the Port that Experienced the
Containment Event
Firmware may wish to issue Error Disconnect Recover notification on a port that is parent of the
port that experienced the containment event. This can be facilitated by implementing this DSM
under the parent port scope. This method, if present, must be evaluated by the DPC aware OS after
Error Disconnect Recover  notification. This method returns the bus, device and function number
of the child port where the containment event occurred. If the parent is a root port, the return value
may represent the bus, device and function number of a switch downstream port that entered
containment mode. The segment number of the child port is assumed to be identical to the parent
port.
If this DSM is not implemented under the port that is the target of  Error Disconnect Recover, the
OS assumes that the target of the notify event is the port that experienced the containment event.
Location:
This object can be placed under any object representing a DPC capable PCI Express Root Port or
Switch Downstream Port. If a port implements this DSM, its child devices cannot instantiate this
DSM function.
Arguments:
Arg0: UUID: E5C937D0-3553-4d7a-9117-EA4D19C3434D
Arg1: Revision ID: lowest valid Revision ID value: 5
Arg2: Function Index: 0Dh
Arg3:  Empty Package
