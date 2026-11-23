---
type: concept
title: 64b/66b encoding
description: In data networking and transmission, 64b/66b is a line code that transforms
  64-bit data to 66-bit line code to provide enough state changes to allow reasonable
  clock recovery and alignment of the data stream at the rece...
tags:
- wikipedia
- wikipedia-en
timestamp: '2026-06-05T06:36:12Z'
x-wikipedia:
  site: en.wikipedia.org
  lang: en
  pageid: 7287059
  revisionId: 1357881940
  parentRevisionId: 1342777994
  wikidataId: Q2631891
  canonicalUrl: https://en.wikipedia.org/wiki/64b/66b_encoding
  license: CC BY-SA; see licenseUrl and Wikimedia Terms of Use
  licenseUrl: https://creativecommons.org/licenses/by-sa/4.0/
  sourceApi: MediaWiki Action API
  fetchedAt: '2026-08-25T15:01:05Z'
  crawlDepth: 1
  sourceSeed: PCI Express
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# [64b/66b encoding](https://en.wikipedia.org/wiki/64b/66b_encoding)

In data networking and transmission, 64b/66b is a line code that transforms 64-bit data to 66-bit line code to provide enough state changes to allow reasonable clock recovery and alignment of the data stream at the receiver. It was defined by the IEEE 802.3 working group as part of the IEEE 802.3ae-2002 amendment which introduced 10 Gbit/s Ethernet. At the time 64b/66b was deployed, it allowed 10 Gb Ethernet to be transmitted over fiber optic with the same lasers used by SONET OC-192, rather than requiring the 12.5 Gbit/s lasers that were not expected to be available for several years.
The protocol overhead of a coding scheme is the ratio of the number of raw payload bits to the number of raw payload bits plus the number of added coding bits. The overhead of 64b/66b encoding is 2 coding bits for every 64 payload bits or 3.125%. This is a considerable improvement on the 25% overhead of the previously used 8b/10b encoding scheme, which added 2 coding bits to every 8 payload bits.
The overhead can be reduced further by doubling the payload size to produce the 128b/130b encoding used by PCIe 3.0.


Function
As its scheme name suggests, 64 payload bits are encoded as a 66-bit entity...

## Wikipedia Links in This Bundle

- [10 Gigabit Ethernet](10-gigabit-ethernet.md)

## Wikipedia Links Not Included

- 100 Gigabit Ethernet
- 10G-EPON
- 2B1Q
- 4B3T
- 4B5B
- 6b/8b encoding
- 8b/10b encoding
- AC-coupled
- Alternate-Phase Return-to-Zero
- Aurora (protocol)
- Baseband

## Categories

- All Wikipedia articles written in American English
- All articles lacking in-text citations
- All articles needing additional references
- All articles with vague or ambiguous time
- Articles lacking in-text citations from January 2017
- Articles needing additional references from June 2026
- Articles with short description
- Encodings
- Line codes
- Short description matches Wikidata
- Telecommunications standards
- Use American English from March 2019
- Use mdy dates from September 2021
- Vague or ambiguous time from April 2021

## Source

- [64b/66b encoding](https://en.wikipedia.org/wiki/64b/66b_encoding)
- Revision: 1357881940
- License: CC BY-SA; see the page footer and Wikimedia Terms of Use.
