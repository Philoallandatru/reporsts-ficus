## [2026-08-12T00:58:41Z] ingest | source catalog
- Source: ./sources/source-catalog.md
- Saved: sources\source-catalog-a4e27b56.md
- Chars: 3,958
## 2026-08-12

- Added Mermaid architecture, read/write path, and recovery flow maps under `maps/`.
- Added `TEST_PLAN.md` and `tools/check_ssd_wiki.py`.
- Validation passed with `python tools/check_ssd_wiki.py`: 18 concept pages, 14 requirements, 29 tests.
- Added `mkdocs.yml`, `llms.txt`, source/page/test templates, `VERSIONED_SOURCES.md`, and `BACKLOG.md`.
- Extended `tools/check_ssd_wiki.py` to require maintenance files and templates.
- Added executable test assets under `tests/`, including fio workload profiles, nvme-cli command probes,
  machine-readable requirements coverage, and a fault-injection scenario catalog.
- Extended `tools/check_ssd_wiki.py` to validate test asset references against `TEST_PLAN.md` and
  `TRACEABILITY_MATRIX.md`.
- Validation passed with `python tools/check_ssd_wiki.py`: 18 concept pages, 14 requirements, 29 tests.
- `llmwiki status --json` shows 3 pending source files and no compiled state yet; compilation still requires
  provider access.
- Added `COVERAGE_GAPS.md` to answer which SSD firmware, hardware, source and verification areas still need
  expansion, and linked it from README, Wiki, knowledge map and MkDocs navigation.
- Marked completed backlog items for fio/nvme-cli profiles and machine-readable test requirements.
- Added `BIBLIOGRAPHY.md` with SSD/FTL/LDPC/emulation paper entries and BibTeX seeds.
- Added `PATENT_INDEX.md` with SSD patent search directions for FTL metadata, PLP, LDPC, SLC cache,
  placement hints and controller acceleration.
- Added NAND and controller vendor intake files under `sources/vendor-intake/`, plus a patent intake template
  under `sources/patents/`.
- Linked the new source-traceability material from README, Wiki, knowledge map, MkDocs navigation,
  `SOURCES.md`, `VERSIONED_SOURCES.md`, `COVERAGE_GAPS.md`, `BACKLOG.md`, and the local checker.
- Added research side note `sources/research-nand-controller-patent-notes.md` to the source indexes and checker.
- Added three FTL mapping concept pages: page mapping, hybrid/log-block mapping, and DFTL/demand-based mapping.
- Linked the FTL mapping pages from the FTL overview pages, README, Wiki index, knowledge map, MkDocs navigation,
  coverage gaps, backlog, and local checker coverage.
- Added `tests/faults/power-loss-state-table.yml` with 10 `PLP-WIN-*` recovery windows covering host DMA,
  NAND program, journal replay, checkpoint generation and GC relocation/erase boundaries.
- Linked the PLP state table from the power-loss recovery page, recovery flow map, README, Wiki index,
  knowledge map, MkDocs navigation, backlog and coverage gaps.
- Extended `tools/check_ssd_wiki.py` to validate PLP state windows against fault injection references and
  planned `T4-*` tests.
- Added [GC Victim Selection 与 Wear Leveling 策略](wiki/concepts/gc-wear-leveling-policy.md) covering
  greedy, cost-benefit, hot/cold-aware, QoS-aware, emergency GC, dynamic wear leveling and static wear leveling.
- Added `tests/requirements/gc-policy-matrix.yml` with machine-readable `GC-POL-*` policy entries, watermarks,
  metrics, risks, requirements and test bindings.
- Linked the GC policy assets from README, Wiki index, knowledge map, MkDocs navigation, requirements YAML,
  backlog, coverage gaps and the local checker.
- Added [SLC Cache、Write Cliff 与 Destage 策略](wiki/concepts/slc-cache-write-cliff-destage.md), covering
  cache modes, admission, write cliff states, destage, metadata recovery, QoS scheduling and metrics.
- Added `tests/requirements/slc-cache-policy-matrix.yml` with `SLC-POL-*` policy entries, states, metrics,
  risks, requirements and test bindings.
- Added `tests/profiles/fio/slc-cache-write-cliff.fio` for T5-003-style cache full / write cliff experiments.
- Linked SLC cache assets from README, Wiki index, knowledge map, MkDocs navigation, TEST_PLAN, requirements YAML,
  backlog, coverage gaps and the local checker.
- Added [FDP、Streams、Placement Hint 与内部 FTL](wiki/concepts/fdp-streams-placement-hints.md), separating
  NVMe host-visible semantics, internal FTL placement policy and patent/vendor terminology.
- Added `tests/requirements/placement-policy-matrix.yml` with `PLC-POL-*` policy entries for no-hint baseline,
  stream placement, FDP reclaim unit mapping, SLC admission, fallback and placement metadata recovery.
- Linked placement assets from README, Wiki index, knowledge map, MkDocs navigation, TEST_PLAN, requirements YAML,
  backlog, coverage gaps and the local checker.
- Added [Firmware Update、Metadata Compatibility 与 Rollback](wiki/concepts/firmware-update-rollback.md), covering
  image staging, slot table, activation, metadata compatibility, migration, anti-rollback and observability.
- Added `tests/requirements/firmware-update-policy-matrix.yml` with `FW-POL-*` policy entries for signed staging,
  atomic slot commit, metadata compatibility, migration journal, rollback, security version and telemetry.
- Added `tests/faults/firmware-update-state-table.yml` with `FWUP-WIN-*` power-loss/update windows and linked
  them from `fault-injection.yml`.
- Linked firmware update assets from README, Wiki index, knowledge map, MkDocs navigation, TEST_PLAN,
  requirements YAML, backlog, coverage gaps and the local checker.
- Added [DRAM-less SSD 与 Host Memory Buffer](wiki/concepts/dram-less-hmb-ssd.md), covering clean mapping cache,
  dirty metadata hazards, descriptor validation, DMA fault fallback, reset invalidation, miss-storm QoS and isolation.
- Added `tests/requirements/hmb-policy-matrix.yml` with `HMB-POL-*` policy entries and HMB lifecycle states.
- Added `tests/profiles/fio/hmb-mapping-miss-storm.fio` for random read/mixed workloads that stress mapping-cache miss paths.
- Linked HMB assets from README, Wiki index, knowledge map, MkDocs navigation, TEST_PLAN, requirements YAML,
  backlog, coverage gaps and the local checker.
- Added [Flash Scheduler、Channel/Die/Plane Arbitration 与 Read Priority](wiki/concepts/flash-scheduler-arbitration.md), covering
  request classes, channel/die/plane resources, arbitration, read priority, program/erase suspend, multi-plane constraints,
  error paths and telemetry.
- Added `tests/requirements/flash-scheduler-policy-matrix.yml` with `FSCH-POL-*` policy entries and scheduler states.
- Linked flash scheduler assets from README, Wiki index, knowledge map, MkDocs navigation, TEST_PLAN, requirements YAML,
  backlog, coverage gaps and the local checker.
- Expanded [ECC、LDPC 与可靠性管理](wiki/concepts/ecc-ldpc-reliability.md) with an LDPC pipeline state machine,
  read-retry ladder, soft-decode QoS budget, metadata ECC priority and reliability telemetry fields.
- Added `tests/requirements/ldpc-pipeline-policy-matrix.yml` with `LDPC-POL-*` policy entries for hard decode,
  read retry, soft-decision decode, retry-storm QoS guard, scrub/refresh, metadata priority and uncorrectable telemetry.
- Linked LDPC pipeline assets from README, Wiki index, knowledge map, MkDocs navigation, TEST_PLAN, requirements YAML,
  backlog, coverage gaps and the local checker.
- Added `sources/vendor-intake/nand-parameter-extraction-matrix.yml` to turn NAND vendor materials into repeatable
  geometry, timing, interface, ECC/read-retry and reliability extraction fields with confidence levels.
- Expanded [NAND 介质参数手册](wiki/concepts/nand-media-parameter-guide.md) and
  [NAND Vendor 公开资料 Intake](sources/vendor-intake/nand-vendor-public-materials.md) with parameter confidence
  levels, subsystem mappings and read-retry handling rules.
- Linked NAND parameter extraction assets from README, Wiki index, knowledge map, MkDocs navigation, SOURCES,
  VERSIONED_SOURCES, backlog, coverage gaps and the local checker.
- Added `sources/open-source-implementation-pins.yml` with `git ls-remote` commit pins for Cosmos+ OpenSSD, FEMU,
  SimpleSSD, MQSim, SPDK, Linux NVMe, nvme-cli, libnvme, OpenChannelSSD qemu-nvme and an accessible FlashSim fork.
- Updated [开源实现索引](wiki/concepts/opensource-implementation-index.md), [源码导读](wiki/concepts/source-code-reading-guide.md),
  README, Wiki index, knowledge map, MkDocs navigation, SOURCES, VERSIONED_SOURCES, backlog, coverage gaps and the
  local checker to point at the pinned implementation list.
- Added `sources/standards-version-pins.yml` with version/access-condition pins for NVMe Base/NVM/ZNS/FDP/MI,
  ONFI, JEDEC endurance/interface standards, PCI-SIG Base/CEM/M.2, OCP NVMe SSD and SNIA supporting material.
- Updated README, Wiki index, knowledge map, MkDocs navigation, SOURCES, VERSIONED_SOURCES, backlog, coverage gaps
  and the local checker to point at the standards version pins.
- Added `tests/requirements/emulator-hook-matrix.yml` binding PLP, LDPC, flash scheduler, HMB and firmware update
  verification assets to FEMU/SimpleSSD/MQSim/Cosmos+ and host-side source-code hook targets.
- Linked the emulator hook matrix from README, Wiki index, knowledge map, MkDocs navigation, TEST_PLAN,
  tests README, requirements YAML, backlog, coverage gaps and the local checker.
- Added `tests/requirements/verification-evidence-schema.yml` defining run headers, hook events, fault injection
  events and pass/fail decision evidence for emulator-backed tests.
- Added `templates/verification-report-template.md` and linked the evidence assets from README, Wiki index,
  knowledge map, MkDocs navigation, TEST_PLAN, tests README, backlog, coverage gaps and the local checker.
- Added `tests/evidence/sample-plp-pass.jsonl` as a minimal PLP evidence log that exercises the verification schema.
- Added `tools/validate_evidence_log.py` and extended `tools/check_ssd_wiki.py` to validate the sample evidence log
  as part of the normal knowledge-base check.
- Added `tests/evidence/sample-ldpc-pass.jsonl` as a minimal LDPC/read-retry evidence log that exercises the
  verification schema.
- Extended `tools/check_ssd_wiki.py` to validate every `tests/evidence/*.jsonl` sample as part of the normal
  knowledge-base check.
- Added `sources/standards-public-audit-2026-08-12.yml` to record official public-version audit results for
  NVMe Base/NVM/ZNS/MI/Boot, OCP Datacenter NVMe SSD, SNIA SSS PTS, ONFI and JEDEC entries.
- Updated standards pins from the public audit: NVM Command Set 1.3, ZNS 1.5, NVMe-MI 2.2, NVMe Boot 1.4,
  and FDP coverage through NVMe Base/NVM Command Set rather than a standalone TP-only entry.
- Extended `tools/check_ssd_wiki.py` to require the public standards audit and verify that each audited `SRC-*`
  record is represented in both `VERSIONED_SOURCES.md` and `standards-version-pins.yml`.
- Added `sources/implementation-smoke-test-matrix.yml` to define local clone/build/smoke-test acceptance criteria
  for Cosmos+, FEMU, SimpleSSD, MQSim, SPDK, Linux NVMe, nvme-cli, libnvme, OpenChannel qemu-nvme and FlashSim fork.
- Linked the smoke-test matrix from README, Wiki index, knowledge map, MkDocs navigation, source-code guide,
  open-source implementation index, sources, versioned sources, backlog and coverage gaps.
- Extended `tools/check_ssd_wiki.py` to verify that every pinned open-source implementation has a matching
  smoke-test matrix entry and that the matrix does not reference unknown projects.
- Added `sources/source-artifact-manifest.yml` to track planned/manual/restricted/downloaded source artifacts,
  local filenames and sha256 requirements for standards and public PDFs.
- Added `tools/validate_source_artifacts.py` to validate artifact manifest status, source-id references,
  local-file containment and sha256 matches when an artifact is marked `downloaded_hash_verified`.
- Linked the source artifact manifest from README, Wiki index, knowledge map, MkDocs navigation, SOURCES,
  VERSIONED_SOURCES, backlog and coverage gaps.
- Extended `tools/check_ssd_wiki.py` to require and run the source artifact manifest validator as part of the
  normal knowledge-base check.
- Downloaded official NVM Express Base Specification Revision 2.4 and NVM Command Set Specification Revision 1.3
  PDFs into `sources/artifacts/nvmexpress/`.
- Recorded local filenames, file sizes and sha256 hashes for those two NVM Express PDFs in
  `sources/source-artifact-manifest.yml`, `sources/standards-version-pins.yml` and `VERSIONED_SOURCES.md`.
- Extended `tools/check_ssd_wiki.py` to require downloaded artifact sha256 values to be reflected in the standards
  pins or versioned source list.
- Parsed current official NVM Express PDF links for ZNS Revision 1.5, NVMe-MI Revision 2.2 and NVMe Boot Revision 1.4.
- Downloaded official ZNS 1.5 and NVMe-MI 2.2 PDFs into `sources/artifacts/nvmexpress/` and recorded local filenames,
  file sizes and sha256 hashes in the artifact manifest, standards pins and versioned source list.
- Recorded the official NVMe Boot 1.4 PDF URL, but kept it as `manual_download_required` because scripted download
  returned HTTP 525 in this environment.
- Added `sources/pdf-artifact-index.yml` to record page counts, topic routes, primary pages and next extraction tasks
  for downloaded PDF artifacts.
- Extended `tools/validate_source_artifacts.py` to validate the PDF artifact index against the source artifact manifest,
  local sha256 values, PDF file magic and parsed page counts.
- Linked the PDF artifact index from README, Wiki index, SOURCES, VERSIONED_SOURCES, KNOWLEDGE_MAP, MkDocs navigation,
  backlog and coverage gaps.
- Added `tools/locate_pdf_topics.py` to locate common SSD/NVMe topic terms in verified PDF artifacts.
- Added `sources/pdf-topic-locator.yml` with candidate pages for Identify Controller, Firmware Commit, Sanitize,
  Flexible Data Placement, Telemetry, Zone Management, Zone Descriptor, Namespace Management and Management Interface.
- Extended `tools/validate_source_artifacts.py` to validate topic-locator artifact ids and page ranges.
- Added `tests/requirements/nvme-command-spec-map.yml` to connect nvme-cli command templates, test IDs, requirement IDs,
  safety classes, verified PDF artifacts and PDF topic-locator entries.
- Extended `tools/check_ssd_wiki.py` to validate NVMe command map references to tests, requirements, topic IDs,
  indexed artifacts and safety classes.
- Extended `tests/requirements/verification-evidence-schema.yml` and `tools/validate_evidence_log.py` with
  `host_command_event` records for host-side nvme-cli evidence.
- Added `tests/evidence/sample-nvme-cli-readonly-pass.jsonl` as a read-only id-ctrl / smart-log evidence sample
  bound to `NVME-CMD-*` command map entries, tests, requirements and verified PDF artifacts.
- Added raw stdout/stderr sample files under `tests/evidence/raw/` for the nvme-cli evidence sample.
- Extended `tools/validate_evidence_log.py` to validate host command raw stdout/stderr paths, ensure they stay under
  `tests/evidence/`, require files to exist and require stdout to be non-empty.
- Added `tests/requirements/nvme-cli-output-field-map.yml` to register parsed nvme-cli output fields used by
  host command evidence.
- Extended `tools/validate_evidence_log.py` to require each `host_command_event.observed_fields` key to be registered
  in the nvme-cli output field map and bound to the corresponding `NVME-CMD-*` command.
- Extended `tools/check_ssd_wiki.py` to validate output field map references to commands, topics, artifacts, tests
  and requirements.
- Extended `tools/validate_evidence_log.py` to parse nvme-cli raw stdout key-value lines and verify each
  `host_command_event.observed_fields` value against the preserved raw output.
- Downloaded Micron's public NOR and NAND Flash Guide into `sources/artifacts/vendors/micron/`, recorded its sha256
  and page count, and linked it from the NAND vendor intake plus parameter extraction matrix as an official-family
  source.
- Extended `tools/check_ssd_wiki.py` to validate fixed NAND parameter-matrix artifacts against the source artifact
  manifest and PDF artifact index, including artifact id, local file and sha256 consistency.
- Added `sources/vendor-intake/micron-nand-flash-guide-intake.md` to capture the usable family-level conclusions,
  blocked fields and downstream mapping for Micron's public NOR/NAND guide, then linked it from README, wiki index,
  knowledge map, MkDocs navigation and SOURCES.
- Verified that `llmwiki ingest` works against the four `sources/*.md` input files, producing hashed ingest copies;
  updated llmwiki documentation to reflect that the remaining blocker is successful compile/provider state rather than
  missing source-file paths.
- Re-ran `llmwiki compile --review --lang zh-CN` on 2026-08-12 and captured a current reproducible blocker:
  compile reaches the extracting stage for 8 pending inputs, then fails with `403 No active subscription found for this group`.
- Re-tested `llmwiki compile` against the MiniMax Anthropic-compatible endpoint on 2026-08-12; the provider-group
  `403` changed to a reproducible `401 invalid api key`, confirming the gateway path is reachable and the remaining
  blocker is authentication.
- Re-tested `llmwiki compile` against llmwiki's native `minimax` provider on 2026-08-12; it also reaches the extract
  phase and then fails with `401 invalid api key (2049)`, confirming the blocker is credential/permission rather than
  the Anthropic-compatible adapter path.
- Extended `tools/check_ssd_wiki.py` to validate the four canonical llmwiki source inputs and ensure each one has at
  most one hashed ingest variant under `sources/`.
- Extended `tools/check_ssd_wiki.py` to validate llmwiki canonical source files and ensure each canonical source has at
  most one hashed ingest variant under `sources/`.
- Added `tools/check_llmwiki_setup.py` as a focused local diagnostic for `.llmwiki` config presence, canonical source
  files, ingest variants, provider env visibility, and raw `llmwiki status --json` output.
- Extended `tools/check_llmwiki_setup.py` with a static provider preflight summary so the local diagnostic reports the
  effective provider, default model, missing credential variables, and custom endpoint hints before any network call.
- Added `tools/check_llmwiki_setup.py --self-test` so the provider preflight branches can be regression-tested locally
  without touching external APIs.
- Added `tests/requirements/llmwiki-provider-matrix.yml` to record llmwiki provider defaults, auth markers and local
  preflight coverage in a machine-readable form, then linked it from the main README.
- Extended `tools/check_llmwiki_setup.py` to surface the provider matrix snapshot in both JSON and human-readable
  output so the diagnostics show their own source-of-truth file.
## [2026-08-12T09:02:08Z] ingest | source catalog
- Source: .\sources\source-catalog.md
- Saved: sources\source-catalog-3e9312b0.md
- Chars: 4,128

## [2026-08-12T09:02:08Z] ingest | seed
- Source: .\sources\seed.md
- Saved: sources\seed-2f87dbcb.md
- Chars: 2,773

## [2026-08-12T09:02:08Z] ingest | research nand controller patent notes
- Source: .\sources\research-nand-controller-patent-notes.md
- Saved: sources\research-nand-controller-patent-notes-53079fdd.md
- Chars: 25,270

## [2026-08-12T09:02:08Z] ingest | research source catalog
- Source: .\sources\research-source-catalog.md
- Saved: sources\research-source-catalog-7fa90efa.md
- Chars: 13,865
## [2026-08-16T06:07:44Z] query | SSD firmware 中 FTL、GC、wear leveling 和 NVMe command processing 的边界是什么？
- Pages: [[concepts/host-ftl-与-open-channel-ssd]], [[concepts/spdk-ftl-库与主机侧闪存管理]], [[concepts/nvme-规范体系]], [[concepts/linux-nvme-内核驱动架构]], [[concepts/ssd-子系统设计文档模板]]

## [2026-08-16T06:09:07Z] query | NAND channel/die/plane 结构如何影响 SSD 并行度？
- Pages: [[concepts/onfi-闪存接口规范]], [[concepts/主流-nand-技术路线图]], [[concepts/ymtc-xtacking-架构]]

