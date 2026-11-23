# PCI Firmware 3.3 Wiki

This is a source-traceable concept wiki for the PCI Firmware Specification, Revision 3.3. It is organized around concepts and relationships rather than mirroring the PDF chapter-by-chapter.

## Start here

- [Concept index](CONCEPT_INDEX.md)
- [Document map](maps/document-map.md)
- [Source profile](_meta/SOURCE_PROFILE.md)
- [Automation runbook](_meta/AUTOMATION.md)
- [Extraction progress](_meta/progress.json)

## Evidence convention

Every factual concept statement should link to at least one local source page, for example `[PDF p. 39](_source/pages/page-039.md)`. External sources are supplementary and must not silently replace the meaning of Revision 3.3.

## Wiki layers

- `_source/pages/`: mechanically extracted, page-addressable evidence.
- `concepts/`: one canonical concept per Markdown file.
- `maps/`: navigation and relationship maps.
- `_meta/`: extraction manifest, progress state, review queue, and operating rules.

The PDF is authoritative. Wiki prose is an explanatory index into it, not a substitute for conformance work.
