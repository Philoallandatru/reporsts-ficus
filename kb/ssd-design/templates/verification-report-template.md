# SSD Verification Report Template

## Run Header

| Field | Value |
|---|---|
| Run ID |  |
| Timestamp UTC |  |
| DUT kind | FEMU / SimpleSSD / MQSim / Cosmos+ / FPGA / software model |
| DUT build ID |  |
| Source pin IDs |  |
| Host OS |  |
| Kernel / QEMU version |  |
| Tool versions | nvme-cli / fio / xNVMe / SPDK / libnvme |
| Random seed |  |
| Workload ID |  |
| Namespace size |  |
| Device path or backend |  |

## Scope

| Field | Value |
|---|---|
| Requirement IDs | REQ- |
| Test IDs | T |
| Hook IDs | HOOK- |
| Fault IDs | FI- |
| Policy IDs |  |
| State windows | PLP-WIN- / FWUP-WIN- |

## Hook Evidence

| Field | Value |
|---|---|
| Hook ID | HOOK- |
| Trigger ID |  |
| Injection point |  |
| Armed | yes/no |
| Fired | yes/no |
| Deterministic counter value |  |
| Expected outcome |  |
| Observed outcome |  |
| Raw log location |  |
| Parser version |  |

## Required Evidence

List required fields from `tests/requirements/verification-evidence-schema.yml`.

| Field | Present | Value / Location |
|---|---|---|
|  | yes/no |  |

## Forbidden Evidence

| Field | Absent | Notes |
|---|---|---|
|  | yes/no |  |

## Decision

| Field | Value |
|---|---|
| Decision | pass / fail / inconclusive / blocked |
| Decision reason |  |
| Required evidence present | yes/no |
| Forbidden evidence absent | yes/no |
| Reviewer |  |
| Follow-up issue |  |

## Notes

- 
