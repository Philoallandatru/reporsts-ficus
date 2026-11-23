---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 119
headings: ["5.2.1.24.2. Configuration Utility Behavior Under Console Redirection", "5.2.1.24.3. Configuration Utility Code Header"]
---

# Source page 119

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  119
However, the exact method for selecting and executing the individual Option ROM configuration
code is not defined by this specification.
5.2.1.24.2. Configuration Utility Behavior Under Console Redirection
When the system firmware is running Console Redirection, it will set bit 0 of the BL register prior
when calling the configuration utility code.  This places additional restrictions on the configuration
utility code, as described below:
❑ The configuration code must not change the video mode at any point during its execution.
Attempts to enter any graphical video mode, in particular, are destructive to Console Redirection
session.  The BIOS will already be in the preferred text mode when it calls the configuration
utility code, and the it must not be changed.
❑ The only permitted input device is keyboard via Int 16h.  Mouse and other types of input
devices that cannot be easily redirected over the Console Redirection will not function.
❑ The configuration code must perform all output via Int 10h services.  Writing output directly to
a video buffer may cause data to not be redirected correctly in the Console Redirection session.
Preferrably, the configuration code would use the Int 10h Write-TTY function for screen output
and would minimize the use of cursor repositioning, color dependencies, and “screen-scraping”
(screen clearing)  features, which perform poorly under Console Redirection.
5.2.1.24.3. Configuration Utility Code Header
The configuration utility code must be separated from the standard Expansion ROM code and be in
a contiguous, self-contained block of code that can be independently executed by system firmware.
The configuration utility code header resides at the very beginning of this code block and has the
following format:
Offset  Length  Description
0     1  Configuration Code Length
1     40  Configuration Code Identifier string
41     1  Revision of this header structure

Configuration Code Length  This byte indicates size of the Configuration code in units of
     512 bytes.
Configuration Code Identifier string The Configuration Code Identifier string is a null-terminated
     ASCII text string giving the name of the vendor’s
     configuration utility.  For example, it may contain “ABC SCSI
     configuration utility”.  This text will be displayed to the end
     user by the System Firmware.  Note that the system firmware
     will display the text until a null is encountered or until
     40 bytes have been displayed.
Header Revision    This field is the version of the structure of the Configuration
     Code Header.  This version of the header have a revision
     field value of 1.
