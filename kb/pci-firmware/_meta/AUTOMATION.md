# Automation runbook

Each run processes the next unprocessed range in `_meta/progress.json` (normally eight pages).

## Per-run contract

1. Verify the source SHA-256 in `_meta/document.json` still matches `progress.json`.
2. Read the bookmark entries and extracted page files for the batch, including one neighboring page on each side when available.
3. Create or update canonical pages under `concepts/`.
4. Preserve exact identifiers (`_OSC`, `PCIR`, `55h AAh`, field names, bit positions) while paraphrasing prose.
5. Add a local PDF-page citation to every substantive claim.
6. Update `CONCEPT_INDEX.md` and the relevant map.
7. Add tables, diagrams, cross-page structures, ambiguous terms, and apparent contradictions to `review_queue`.
8. Advance `next_page` only after all writes succeed; append the completed range to `processed_ranges`.
9. When `next_page` exceeds `last_page`, run a consistency pass, set `status` to `complete`, and report completion without rewriting settled pages gratuitously.

## Concept page shape

```markdown
# Canonical term

One or two sentence definition.

## Why it matters
## Structure or behavior
## Constraints and edge cases
## Relationships
## Evidence
```

Use aliases only for genuine synonyms or acronyms. Do not treat every heading, field name, or return code as a standalone concept: nest low-level facts under the concept that gives them meaning.
