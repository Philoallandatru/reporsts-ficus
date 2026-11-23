# PCI Firmware 3.3 Knowledge Context

Canonical domain language for the concept wiki derived from PCI Firmware Specification Revision 3.3.

## Language

**PCI Address**:
The hierarchical identity of a PCI function: Segment Group Number, Bus Number, Device Number, and Function Number. A register offset identifies data within that function's Configuration Space.
_Avoid_: BDF when the segment group is relevant

**Configuration Space**:
The separate PCI address space used to identify and configure devices, distinct from Memory Space and I/O Space.

**PCI Segment Group**:
A firmware-managed logical collection of PCI buses that permits bus numbers to be reused across groups; it is not a physical entity.
_Avoid_: Segment when the full specification term removes ambiguity

**Firmware/Operating System Handoff**:
The boundary at which firmware leaves PCI devices in a specified state and the operating system assumes applicable ownership or control.

**UEFI PCI Root Bridge Protocol**:
The UEFI host-side I/O abstraction used by a PCI Bus Driver for PCI Memory, I/O, Configuration, and DMA operations across a Root Bridge.

**Enhanced Configuration Access Mechanism**:
The memory-mapped PCI configuration access mechanism whose base addresses are described to an operating system through ACPI `MCFG` or `_CBA`.

**MCFG**:
The ACPI table that reports boot-time, non-hot-removable Enhanced Configuration Access Mechanism mappings by PCI Segment Group and bus range.

**_CBA**:
The optional ACPI host-bridge control method that returns a processor-relative Enhanced Configuration Access Mechanism base address for runtime-described or hot-plug-capable mappings.

**_OSC**:
The ACPI capability and control negotiation method through which OSPM reports support and requests ownership of features for a PCI host-bridge hierarchy.

**PCI Device Specific Method (`_DSM`)**:
The UUID-scoped ACPI method family through which PCI devices expose versioned, device-specific functions; Function 0 negotiates the supported function set for a common Revision ID.

**PCI Express Slot Number Tokens**:
Bit ranges that decompose `_SUN`, PCI-to-PCI Bridge Chassis ID, or PCI Express Physical Slot Number values into named topology elements; vendor-specific token kinds use IDs `80h`–`FFh`.

**PCI Bus Capabilities Structure**:
The aligned, bus-type-specific record returned by PCI `_DSM` Function 4 to describe a PCI root bus's capabilities and operating mode.

**PCI Boot Configuration Preservation**:
The PCI `_DSM` Function 5 policy that determines whether firmware-assigned PCI resources must be retained or may be rebalanced by the operating system.

**PCI Device Readiness Timing**:
The PCI `_DSM` Functions 8 and 9 model separating hierarchy-wide post-reset delay responsibility from per-device readiness-duration overrides.

**D3cold Auxiliary Power Limit**:
The PCI `_DSM` Function `0Ah` negotiation through which a driver requests a D3cold auxiliary-power budget and firmware grants, denies, defers, or keeps main power present.

**PERST# Assertion Delay**:
The PCI `_DSM` Function `0Bh` delay between `PME_TO_Ack` receipt and `PERST#` assertion for an add-in device entering D3cold in S0.

**DPC and Hot-Plug Surprise Control**:
The PCI `_DSM` Function `0Ch` protocol that orders DPC state changes and Hot-Plug Surprise suppression according to firmware or operating-system DPC ownership.

**DPC Containment Port Location**:
The PCI `_DSM` Function `0Dh` mechanism that identifies the child port that entered containment when Error Disconnect Recovery notification targets its parent.

**PCIe SSD Status LED Interface**:
The UUID-scoped `_DSM` interface through which OSPM discovers, reads, and requests platform-controlled PCIe SSD status indications.

**Generic ACPI PCI Slot Description**:
The eight-object namespace representation of one physical PCI slot, using a common `_SUN` and `_ADR` values for Functions 0 through 7.

**Operating System Hot Plug (`OSHP`)**:
The legacy ACPI control method that transfers an SHPC from firmware management to native operating-system control; `_OSC` is preferred when supported.

**PCI Hot-Plug Parameters**:
Inherited ACPI bus settings supplied by `_HPP` or its preferred successor `_HPX` for devices configured during hot plug or after firmware boot configuration.

**PCI Expansion ROM**:
A device-associated ROM containing one or more chained images, each described by an image header and a PCI Data Structure.
_Avoid_: Option ROM when referring specifically to the complete multi-image structure

**PCI Data Structure**:
The `PCIR`-identified structure within a ROM image that describes the image's device identity, class, size, code type, revision, and chaining state.

**PCI Expansion ROM Device List**:
A `0000h`-terminated array of Device IDs referenced from a non-UEFI Revision 3.0-or-later PCI Data Structure when one ROM image supports multiple devices.

**POST Expansion ROM Processing**:
The firmware sequence that discovers a PCI Expansion ROM, traverses images, selects by Code Type and device identity, validates the checksum, copies the image to RAM, and disables ROM decoding.

**PC-Compatible Expansion ROM Initialization**:
The Code Type 0 POST/INIT contract covering the x86 entry point, firmware arguments, relocation, run-time resizing, and checksum maintenance.

**POST Memory Manager (PMM) Allocation**:
The BIOS-coordinated temporary or permanent memory allocation service available to Expansion ROM code during INIT.

**Expansion ROM Run-Time Placement**:
The Revision 3.0-or-later contract that separates an Expansion ROM's temporary INIT address from its protected final run-time address below 1 MiB.

**Expansion ROM Configuration Utility**:
An optional self-contained ROM code block that firmware preserves during INIT and can execute later in POST at the user's request.

**Expansion ROM SM CLP Entry Point**:
The optional Code Type 0 far-call interface through which system firmware sends DMTF SM CLP commands to a PCI device or its children during pre-boot configuration.

**UEFI Expansion ROM**:
A Code Type 3 PCI Expansion ROM whose UEFI image storage and execution model are defined by the UEFI specification rather than the Code Type 0 rules.
