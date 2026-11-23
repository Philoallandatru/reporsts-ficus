# Context Map

## Contexts

- [PCI Firmware 3.3](CONTEXT.md) - PCI BIOS, UEFI, ACPI, and Expansion ROM firmware concepts.
- [NVMe Base 2.1](nvme-wiki/CONTEXT.md) - NVMe system, transport, queue, command, storage-resource, and lifecycle concepts.

## Relationships

- PCIe is one transport environment through which NVMe controllers may be exposed, but NVMe architecture is not limited to PCIe.
- PCI firmware establishes platform/device discovery and handoff concerns; NVMe defines the storage protocol and controller behavior above the applicable transport.
- NVMe Key Per I/O selects externally provisioned encryption keys on namespace I/O; key injection and tag association remain owned by the selected external security mechanism.
- NVMe sanitize completion policy is subsystem-scoped: `AUSE` selects restricted or unrestricted processing/failure recovery while the erase itself remains a persistent background operation.
- Underlying-subsystem sanitize state propagates I/O restrictions to associated Exported Namespaces; export does not isolate the underlying user data from sanitize.
- PCIe exposes CMB and PMR through both external BAR and controller-address views; NVMe defines address/ordering/persistence contracts while PCIe supplies the transaction model.
- Power Loss Signaling splits responsibility: the transport drives PLN/PLA connectivity details, while NVMe Base defines Domain configuration, controller state transitions, command fate, and recovery semantics.
- Centralized Discovery composes registration and access control: CDC records come from push or pull registration, while Fabric Zoning selects which subsystem ports appear in each host's Discovery log.
- Fabric Zoning separates logical membership from enforcement granularity: Zone member type selects the usable NQN/IP/protocol/port dimensions, while activation resolves ZoneAliases and may request packet-level network enforcement.
