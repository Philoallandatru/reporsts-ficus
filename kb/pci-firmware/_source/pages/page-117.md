---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 117
headings: []
---

# Source page 117

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  117
Assigning multiple functionality to a single keystroke may cause a portion of the system to become
inaccessible during Expansion ROM initialization.  In addition, the Expansion ROM must wait for
some arbitrary period of time to be certain that the user had not pressed the keystroke.  This adds an
unnecessary delay to the Expansion ROM initialization code and to the overall system POST time,
particularly in the cases where no change in configuration is needed by the end user.
Beginning with this version of the specification, the Expansion ROM vendors can isolate the
configuration code and the system firmware will execute the configuration code only when
specifically requested by the user.  The Expansion ROM header (defined in Section 5.1.2) now
contains an optional pointer to the header for the configuration code.  During POST when the
system firmware is preparing the Expansion ROM for the INIT stage, the system firmware will
make a copy of the configuration utility code (if present in the ROM image) and leave it in
temporary memory for later execution.
At the completion of the INIT phase, the Expansion ROM will shrink itself to the final run-time
size (without the configuration utility code), and the configuration code will remain in temporary
memory.  Note that the BIOS will not write-protect the run-time Expansion ROM image until the
very end of POST.  This permits the Expansion ROM Configuration Utility code to update the run-
time Expansion ROM code with configuration parameters or any other data collected by the
Configuration Utility code.  The Expansion ROM run-time size must include the region where
configuration parameters are stored, and the size must not increase when the Configuration Utility
code updates the run-time code with the configuration parameters.  The Configuration Utility code
must also update the checksum for the run-time Expansion ROM code to keep the run-time image
valid.
System firmware will be responsible for managing the location and execution of the configuration
utilities for all the Expansion ROMs.  However, the Expansion ROM can control some of the ways
that the System firmware treats the configuration utility code.  There are three possible scenarios.
❑ Legacy:  In this scenario, the Expansion ROM image does not contain a pointer to the
configuration utility code header.  The Expansion ROM either has no configuration code, or it
prefers to run the configuration code during the INIT phase as 2.1 compliant Expansion ROMs
do today. The system firmware does not manage the configuration utility code in this scenario.
❑ Hybrid:  In this scenario, the Expansion ROM  has a valid configuration utility code header.
However the Expansion ROM runs the configuration utility code during the INIT phase, as
described in the legacy style above.  In addition the system firmware has preserved a copy of the
configuration utility code and may execute it at a later point in POST.  The configuration utility
code must be prepared to be executed twice in this scenario.
❑ Delayed Execution:  In this scenario, the Expansion ROM has a valid configuration utility
code header.  Unlike the previous two scenarios, the configuration utility is not executed (by the
Expansion ROM) during the INIT phase.  The configuration utility code is only executed by the
system firmware at a later point in POST.
The preferred method is the “delayed execution” style described above.  This permits the system
firmware to manage the execution of the Configuration Utility code in a consistent and organized
manner.
