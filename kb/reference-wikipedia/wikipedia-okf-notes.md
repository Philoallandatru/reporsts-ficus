---
type: Concept
title: Wikipedia to OKF research note
description: 'Date: 2026-08-25'
tags:
- docs
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Wikipedia to OKF research note

Date: 2026-08-25

## Goal

Build a standalone Open Knowledge Format (OKF) bundle from Wikipedia without using LLM compilation. The bundle should be usable as a separate knowledge base now, and importable into an `llmwiki` project later.

## Local OKF contract

The local `llm-wiki-compiler` implementation treats OKF as a directory bundle:

- `index.md` is reserved and carries `okf_version: "0.1"` in frontmatter.
- `log.md` is reserved for bundle history.
- Other Markdown files with non-empty frontmatter `type` are importable documents.
- Native exports group ordinary pages under `concepts/` and `queries/`.
- `llmwiki import --okf <dir>` stages OKF docs by default; `--trusted` writes them directly.

Source: local implementation in `tmp/llm-wiki-compiler/src/commands/import.ts`, `tmp/llm-wiki-compiler/src/import/okf-read.ts`, `tmp/llm-wiki-compiler/src/import/okf-map.ts`, and `tmp/llm-wiki-compiler/src/export/okf/index-log.ts`.

## Wikimedia source options

### Action API

The MediaWiki Action API is a web API available at each wiki's `/w/api.php` endpoint. MediaWiki's own documentation lists English Wikipedia's endpoint as `https://en.wikipedia.org/w/api.php` and describes `action=query` as the API surface for fetching data from and about pages.

Useful query properties for this project:

- `prop=extracts` from TextExtracts returns plain-text or limited HTML page extracts.
- `prop=links` returns page links, which is enough to preserve a local graph edge list.
- `prop=categories` returns category membership.
- `prop=revisions` can return revision ids and timestamps for traceability.
- `prop=pageprops` can expose `wikibase_item`, connecting a page to Wikidata.
- `redirects=1` resolves redirects to canonical titles.

Primary sources:

- MediaWiki Action API overview: https://www.mediawiki.org/wiki/API:Main_page
- TextExtracts API: https://www.mediawiki.org/wiki/Extension:TextExtracts
- Links API: https://www.mediawiki.org/wiki/API:Links
- Categories API: https://www.mediawiki.org/wiki/API:Categories
- Revisions API: https://www.mediawiki.org/wiki/API:Revisions

### Dumps

For full Wikipedia-scale builds, dumps are the better source than live API crawling. Wikimedia's dump index publishes completed wiki dumps, including `enwiki` and `zhwiki`, and notes that files are available in formats including compressed XML and JSON.

Primary source: https://dumps.wikimedia.org/backup-index.html

## Usage constraints

Wikimedia API usage guidance requires callers to identify themselves with a meaningful User-Agent, follow throttling notifications, comply with content licenses when republishing cached data, and avoid high-rate or concurrent traffic that degrades service. MediaWiki's API etiquette page recommends serial requests, the `maxlag` parameter for non-interactive work, JSON for new API users, caching where possible, and exponential backoff when rate limited.

Primary sources:

- Wikimedia Foundation API Usage Guidelines: https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_API_Usage_Guidelines
- MediaWiki API etiquette: https://www.mediawiki.org/wiki/API:Etiquette

## Decision

Use two tracks:

1. Seeded API builder for small or topic-focused standalone OKF bundles.
2. Dump-based builder later for full Wikipedia-scale conversion.

The seeded API builder is deliberately non-LLM and low-token: it writes page extracts, metadata, categories, and links directly into OKF Markdown. Integration with the existing NVMe/PCIe/SSD knowledge bases should happen later as a separate review or merge step.

## Current implementation

`tools/build_wikipedia_okf.py` implements the seeded API track.

The generated bundle includes:

- `index.md`
- `log.md`
- `concepts/*.md`
- `wikipedia-pages.jsonl`
- `wikipedia-candidates.jsonl`

Each concept page carries `x-wikipedia` metadata with page id, revision id, Wikidata id when available, canonical URL, license note, fetch timestamp, crawl depth, and source seed.

The builder also supports a topic-filtered crawl for focused bundles:

- `--topic-filter` enables scoring for non-seed pages.
- `--include-keywords` / `--include-keywords-file` define relevance scoring terms.
- `--required-keywords` / `--required-keywords-file` require at least one strong anchor for non-seed pages.
- `--exclude-keywords` / `--exclude-keywords-file` subtract score for drift-prone pages.
- `--candidate-report` writes accepted and rejected crawl candidates as JSONL for tuning.

Current NVMe/PCIe focused files:

- `wikipedia-nvme-pcie-seeds.txt`
- `wikipedia-nvme-pcie-required-keywords.txt`
- `wikipedia-nvme-pcie-exclude-keywords.txt`
- `wikipedia-nvme-pcie-okf/`
