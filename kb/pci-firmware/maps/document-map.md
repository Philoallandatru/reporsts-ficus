# Document map

## Traditional PCI BIOS (PDF pp. 10-31)

Legacy entry points, calling conventions, PCI BIOS functions, configuration-space access, interrupt routing, and return codes.

## UEFI PCI Services (PDF pp. 32-37)

UEFI driver model, root bridge protocol, EFI Byte Code, graphics output, and the firmware-to-operating-system handoff state.

- [UEFI PCI Services](../concepts/uefi-pci-services.md) -> [UEFI PCI Root Bridge Protocol](../concepts/uefi-pci-root-bridge-protocol.md) -> PCI I/O Protocol
- [Firmware/Operating System Handoff](../concepts/firmware-os-handoff.md): `ExitBootServices()` -> firmware-configured Host Bridge/resource state -> operating-system ownership

## PCI Services in ACPI (PDF pp. 38-97)

Enhanced configuration access, root bridge description, interrupt routing, capability/control negotiation via `_OSC`, device-specific methods via `_DSM`, and status reporting.

- [Enhanced Configuration Access Mechanism](../concepts/enhanced-configuration-access.md): `MCFG` for boot-static ranges; `_CBA` for runtime-described ranges
- Boot-static mapping: [MCFG](../concepts/mcfg.md) -> Segment Group plus Start/End Bus -> bus-0-relative base address
- Runtime mapping: [ACPI PCI Host Bridge Description](../concepts/acpi-pci-host-bridge.md) -> `_SEG` plus `_CRS` -> [`_CBA`](../concepts/cba.md)
- Host hierarchy identity: `PNP0A08` (`_HID`) -> extended Configuration Space support; `PNP0A03` (`_CID`) -> legacy compatibility
- Root-bridge resources and routing: `_CRS`/`_PRS`/`_SRS` -> bridge windows; `_BBN`/`_SEG` -> configuration identity; `_PRT` -> INTx routing
- Hierarchy feature ownership: OS support -> [`_OSC`](../concepts/osc.md) Support Field -> Control Field request -> firmware grant/denial
- `_OSC` negotiation lifecycle: side-effect-free query -> dependency-complete request -> monotonic grant retained for the boot
- Device-specific services: [PCI `_DSM`](../concepts/pci-dsm.md) Function 0 revision discovery -> common Revision ID -> supported nonzero functions
- Slot description: [PCI Express Slot Information](../concepts/pci-express-slot-information.md) -> link widths/type/signals; [PCI Express Slot Number Tokens](../concepts/pci-express-slot-number.md) -> source bit ranges -> localized vendor labels
- Root-bus characteristics: PCI root-bus ACPI object -> `_DSM` Function 4 -> [PCI Bus Capabilities Structure](../concepts/pci-bus-capabilities.md)
- Resource handoff: `_DSM` Function 5 -> [PCI Boot Configuration Preservation](../concepts/pci-boot-configuration-preservation.md) -> preserve or rebalance device/hierarchy assignments
- Latency policy: `_DSM` Function 6 -> [Latency Tolerance Reporting](../concepts/latency-tolerance-reporting.md); Functions 8-9 -> [PCI Device Readiness Timing](../concepts/pci-device-readiness-timing.md)
- Device labels: `_DSM` Function 7 -> [PCI Device Naming Hint](../concepts/pci-device-naming-hint.md) -> instance ordering plus optional chassis name
- D3cold platform policy: `_DSM` Function `0Ah` -> [D3cold Auxiliary Power Limit](../concepts/d3cold-aux-power-limit.md); Function `0Bh` -> [PERST# Assertion Delay](../concepts/perst-assertion-delay.md)
- Containment coordination: `_OSC` DPC ownership -> `_DSM` Function `0Ch` -> [DPC and Hot-Plug Surprise Control](../concepts/dpc-hot-plug-surprise-control.md) -> Error Disconnect Recovery and `_OST`
- Containment event identity: Error Disconnect Recovery target -> `_DSM` Function `0Dh` -> [DPC Containment Port Location](../concepts/dpc-containment-port-location.md)
- Vendor-specific TPH setup: Endpoint Device Specific Mode -> `_DSM` Function `0Eh` -> [Vendor-Specific TPH Steering Tag](../concepts/vendor-specific-tph-steering-tag.md)
- SSD indicators: PCIe device or slot -> [PCIe SSD Status LED Interface](../concepts/pcie-ssd-status-led.md) -> supported, current, and requested state bitmaps
- Slot namespace: [Generic ACPI PCI Slot Description](../concepts/generic-acpi-pci-slot-description.md) -> eight `_ADR` function objects sharing one `_SUN`
- Legacy SHPC ownership: firmware-controlled SHPC -> [`OSHP`](../concepts/oshp.md) -> native operating-system control; `_OSC` is preferred when understood
- Hot-plug policy: [`_HPP`/`_HPX`](../concepts/pci-hot-plug-parameters.md) -> inherited bus settings; `_PS3`/`_PS0` -> device D-state transition; `_EJ0` -> removal isolation

## PCI Expansion ROMs (PDF pp. 98-122)

ROM image chaining, headers and PCI data structures, POST/INIT behavior, runtime images, configuration utilities, and SM CLP entry points.

- [PCI Expansion ROM](../concepts/pci-expansion-rom.md) -> 512-byte-aligned image header (`55h AAh`) -> [`PCIR` PCI Data Structure](../concepts/pci-data-structure.md)
- Image traversal: Image Length -> next image; Last Image Indicator bit 7 -> chain termination
- Multi-device image: PCI Data Structure Device ID or nonzero pointer -> [PCI Expansion ROM Device List](../concepts/pci-expansion-rom-device-list.md) -> `0000h` terminator
- POST selection: Expansion ROM Base Address -> `AA55h` signature -> `PCIR`/Code Type traversal -> [POST Expansion ROM Processing](../concepts/post-expansion-rom-processing.md)
- Code Type 0 lifecycle: selected image -> [PC-Compatible Expansion ROM Initialization](../concepts/pc-compatible-expansion-rom-initialization.md) -> INIT relocation/resizing -> corrected run-time checksum
- INIT memory: PMM entry point -> [POST Memory Manager Allocation](../concepts/post-memory-manager-allocation.md) -> temporary allocation or firmware-reserved permanent allocation
- Low-memory fallback: PMM unavailable -> [Extended BIOS Data Area Usage](../concepts/extended-bios-data-area.md) -> movable shared EBDA buffer
- Run-time placement: Maximum Run-Time Image Length -> [Expansion ROM Run-Time Placement](../concepts/expansion-rom-runtime-placement.md) -> final relocation, protection, VGA policy, and alignment
- Shared IRQ path: ROM ISR -> [Expansion ROM Interrupt Chaining](../concepts/expansion-rom-interrupt-chaining.md) -> previous ISR -> default BIOS handler/EOI
- Managed setup: configuration-code pointer -> [Expansion ROM Configuration Utility](../concepts/expansion-rom-configuration-utility.md) -> temporary copy -> optional later POST execution
- Redirected managed setup: Console Redirection flag -> firmware interrupt-only input/output -> utility status/reset request
- Remote pre-boot setup: PCI Data Structure pointer -> [Expansion ROM SM CLP Entry Point](../concepts/expansion-rom-sm-clp-entry-point.md) -> persistent device settings -> INIT
- UEFI image path: Code Type 3 -> [UEFI Expansion ROM](../concepts/uefi-expansion-rom.md) -> UEFI-defined storage and execution model

## Cross-cutting paths

- Addressing: Segment Group -> Bus -> Device -> Function -> Register
- Legacy discovery: BIOS32 Service Directory -> PCI BIOS Present -> indexed device/class search
- Legacy configuration access: PCI BIOS Present -> width-specific read/write call -> conventional or extended register mechanism
- Legacy interrupt routing: routing table -> IRQ bitmap and link topology -> optional immediate assignment
- Ownership: Firmware initialization -> capability negotiation -> operating-system control
- Boot artifacts: [PCI Expansion ROM](../concepts/pci-expansion-rom.md) -> image header -> [PCI Data Structure](../concepts/pci-data-structure.md) -> code image
- Error/status: firmware capability -> OS control -> notification/recovery status
- Legacy status: PCI BIOS function -> [Traditional PCI BIOS Return Codes](../concepts/pci-bios-return-codes.md)
