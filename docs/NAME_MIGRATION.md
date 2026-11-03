# Ars Magna Defluens — naming and compatibility

**Effective:** 2026-11-03  
**Canonical public name:** **Ars Magna Defluens**  
**Preferred repository/folder slug:** `ars-magna-defluens`  
**Former public name:** Ars Magna Lulli  
**Former repository/folder slug:** `ars-magna-lulli`

## Scope of this change

- Rename product references, documentation titles and ecosystem labels.
- Keep the responsibilities: **Defluens orchestrates**, **WordBench proves**,
  **Observatory explains**, **Compendium governs**, and **GF executes**.
- Keep existing immutable WordBench reports, source locks, evidence hashes,
  language IDs, and historical Git links unchanged.
- Keep the legacy machine field value **`lulli`** where an existing `v1`
  schema enumerates it. A change to `defluens` must be a separate, explicitly
  versioned schema migration with a reader compatible with both tokens.
- This ZIP uses `ars-magna-defluens/` as its extracted source folder.
  Observatory detects either `ars-magna-defluens/` or `ars-magna-lulli/`.

## Publishing changes to GitHub

Renaming a folder on disk or in a ZIP **does not rename** the remote GitHub
repository, its URL, package name, Python imports or CI workflows. GitHub
repository rename and local `git remote` updates must be performed separately
when the actual remote is available; do not rewrite links without verification.
The old snapshot's `SMARTDUMP_INDEX.txt` remains historical provenance.

## Current implementation boundary

This repository currently documents a target GitOps orchestrator. The
coordination engine has not been implemented merely by renaming this repo.
