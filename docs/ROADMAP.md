# Development Roadmap

## Completed candidate milestones

- v0.3–v0.4: local Windows console and SemantiK CLI integration.
- v0.5–v0.7: five-case candidate preview, 15-intent/14-language GF lab and typed variable attributes.
- v0.8–v0.9: six-operation composed communications, FR/EN candidate grammars and diK lexical handoff.
- v0.10–v0.11: 36 structural vectors, 14 semantic parity pairs, batch GF candidate verification and human-review TSV.
- v0.11.1–v0.11.2: readable GF diagnostics and French `S`→`Utt` type correction.
- **November 5, 2026:** both FR/EN PGFs compiled with GF 3.12 on Windows; 28/28 real-GF candidate results passed automated checks.

## Priority 1 — Linguistic qualification

Obtain and review the actual `.review.tsv` candidate text in French and English. Record human decisions case-by-case, preserve PGF/source hashes, and fix genuine linguistic defects in their owning component. Only then consider a candidate for the separate SemantiK release process.

## Priority 2 — Missing semantic operation contracts

Model **real conditions**, **conditional instructions** and **source attribution** as typed semantic constructs. Extend SA↔GF bridges, lexical bindings and conformance suites; do not implement them by concatenating sentences or generating untyped GF strings in Defluens.

## Priority 3 — Coverage expansion

Extend the currently controlled lexicon using provenance-aware diK observations and separately reviewed WordBench mappings. Expand supported operation/feature combinations and target additional languages. The 14-language/15-intent WordBench probe matrix is a development input, not production multilingual coverage.

## Longer-term architecture — proposals, not deployed

A GitHub-backed, multi-tenant editor, GitHub OAuth, Actions-based compilation, a global Observatory read model and up-to-300-language coordination remain design targets. Each requires its own security, cost, quota, provenance and integration acceptance gates.
