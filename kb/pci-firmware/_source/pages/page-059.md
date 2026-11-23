---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 59
headings: ["4.5.2. Rules for Evaluating _OSC", "4.5.2.1. Query Flag", "4.5.2.2. Evaluation Conditions", "4.5.2.3. Sequence of _OSC Calls"]
---

# Source page 59

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  59
4.5.2. Rules for Evaluating _OSC
This section defines when and how the operating system must evaluate _OSC as well as restrictions
on firmware implementations.
4.5.2.1. Query Flag
If the Query Support Flag (Capabilities DWORD 1, bit 0) is set by the operating system when
evaluating _OSC, no hardware settings are permitted to be changed by firmware in the context of
the _OSC call.  It is strongly recommended that the operating system evaluate _OSC with the Query
Support Flag set until _OSC returns the Capabilities Masked bit clear, to negotiate the set of features
to be granted to the operating system for native support.  A platform may require a specific
combination of features to be supported natively by an operating system before granting native
control of a given feature.
4.5.2.2. Evaluation Conditions
The operating system must evaluate _OSC under the following conditions:
❑ During initialization of any driver that provides native support for features described in the
section above.  These features may be supported by one or many drivers, but should only be
evaluated by the main bus driver for that hierarchy.  Secondary drivers must coordinate with the
bus driver to install support for these features.  Drivers may not relinquish control of features
previously obtained; i.e., bits set in Capabilities DWORD3 after the negotiation process must be
set on all subsequent negotiation attempts.
❑ When a Notify(<device>, 8) is delivered to the PCI Host Bridge device.
❑ Upon resume from S4.  Platform firmware will handle context restoration when resuming from
S1-S3.
4.5.2.3. Sequence of _OSC Calls
The following rules govern sequences of calls to _OSC that are issued to the same host bridge and
occur within the same boot:
❑ The operating system is permitted to evaluate _OSC an arbitrary number of times.
❑ If the operating system declares support of a feature in the Status Field in one call to _OSC,
then it must preserve the set state of that bit (declaring support for that feature) in all subsequent
calls.
❑ If the operating system is granted control of a feature in the Control Field in one call to _OSC,
then it must preserve the set state of that bit (requesting that feature) in all subsequent calls.
❑ Firmware may not reject control of any feature it has previously granted control to.
There is no mechanism for the operating system to relinquish control of a feature previously
requested and granted.
