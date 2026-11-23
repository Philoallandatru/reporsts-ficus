# Source profile

## Document

- Title: PCI Firmware Specification
- Revision: 3.3
- Date printed in the document: January 20, 2021
- Length: 122 pages
- Producer: Microsoft Word for Office 365
- PDF structure: unencrypted, native text layer, 143 bookmarks
- Layout inventory: four listed figures and 25 listed tables

## Extraction implications

OCR is unnecessary and would reduce quality. The bookmark tree is the primary section boundary signal; PDF page numbers are stable evidence anchors.

The text layer is strong for prose and headings but not sufficient by itself for:

- multi-page tables and bit-field layouts;
- diagrams such as the 256-MiB enhanced configuration-space region;
- binary structures with offsets, lengths, signatures, and alignment constraints;
- normative keywords whose scope may span adjacent paragraphs;
- ACPI methods (`_OSC`, `_DSM`, `_OST`) whose arguments and return buffers are defined across several pages.

Those items go into `review_queue` and require comparison with a rendered page before being marked reviewed.

## Natural bounded contexts

1. Traditional PCI BIOS
2. UEFI PCI Services
3. PCI Services in ACPI
4. PCI Expansion ROMs

Shared concepts - configuration space, PCI address identity, host bridges, firmware/OS ownership, and error/status reporting - should be linked across these contexts rather than duplicated.
