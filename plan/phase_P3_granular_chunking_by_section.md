# Phase P3 — Granular Chunking by Section
**Outcome:** Leaf sections → one chunk each; parents aggregate children; previews shown.

## Tasks
1. Compute section spans over `ParsedObject[]` regardless of engine used (engine-agnostic).
2. Leaf rule: 1:1 section-to-chunk; parent = ordered union of descendant chunks.
3. `POST /chunks/{file_id}` computes/persists mapping; UI previews first N chars.
4. Handle empty sections and overlaps robustly.

## Acceptance
- Random audits match expected region boundaries on both native and mineru fixtures.
