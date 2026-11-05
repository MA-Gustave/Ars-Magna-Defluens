# Defluens v0.9.0 — diK lexical integration laboratory

> **Evidence boundary:** this is a lexical candidate handoff, not GF runtime qualification. The 2026-11-05 FR/EN PGF milestone pertains to the separate `defluens-core-1` candidate. See [Windows validation](WINDOWS_GF_VALIDATION_2026_11_05.md).

The new panel **Semantic Studio → F / Lexical Handoff** (shown as **Atelier sémantique → F / Transfert lexical** in the French UI) invokes only public
process-level CLIs. No diK, WordBench or SemantiK internals are imported into
Defluens, and no arbitrary grammar/semantic mapping is generated.

## Before running

- Install `diK` in `C:\mycode\diK` (its code lives in `diK\src\dik`), or
  configure the exact diK source subfolder in Settings.
- Produce immutable L/S/F observations via diK's existing `lexemes-import`.
- Choose an explicit locale (e.g. fr/en).

## Workflow

1. Enter the diK observation directory and click **Préparer le transfert diK**.
   The server calls `diK world gf-handoff`, then `diK world semantik-knowledge`.
2. Copy the provided mapping-review template to a **separate JSON file** and
   explicitly review the GF function/category, semantic owner, provenance and
   licensing. A blank template yields zero binding candidates.
3. Enter this separately edited review path and click **Construire le candidat
   WordBench**. Existing candidate outputs are never overwritten.
4. Click **Inspecter avec SemantiK**. It validates candidate integrity and
   refuses any claim of publication or PGF verification.

Outputs are placed in `Downloads/Ars_Magna_Defluens/lexical_integration`.
The local UI is authenticated by a session token and delegates via `subprocess`
argv, not shell commands. Errors are surfaced without grammar fallback.

Defluens does not perform diK sense curation, WordBench GF compilation,
SemantiK articulation, Spek document composition or RuntimeSet promotion.
A passing lexical inspector is **not** an executable language runtime.
