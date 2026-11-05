# Ars Magna Defluens v0.11.0 — Structured Bilingual Qualification

> **Development candidate; no PGF included in the documentation release and no RuntimeSet published.** This document describes the v0.11 implementation and its reproducible commands. A later run on **November 5, 2026** successfully compiled and tested both candidates on Windows; see [observed results](WINDOWS_GF_VALIDATION_2026_11_05.md).

## New in v0.11

- Retains the **36 reference vectors** from v0.10: **28 authorized** requests and **eight expected rejections**, constructed/validated exclusively by the public SemantiK Architect CLI. Adds **14 FR/EN semantic parity pairs**: typed graph, obligations, supporting context and constraints must agree independently of the requested language.
- For real GF acceptance, Defluens sends **two batches of 14 canonical requests** to the new public SA command `preview-candidate-batch`. SA constructs a language-specific `CandidateConformance`, verifies the `pipeline.lock.json` and hashes, and executes each request with its existing planner, lexical binder and actual GF adapter. Individual failures remain visible.
- Defluens checks PGF/lock hashes on both sides of the process boundary, language, profile, exact text reconstruction from output blocks, statement order, mandatory-obligation coverage and deterministic result identifiers. These are **technical/structural checks**; they do not determine grammatical accuracy or style.
- Every run writes **new JSON and UTF-8 TSV review artifacts**. Real candidate lines start as `PENDING` for human linguistic review. Missing PGFs produce `BLOCKED_PGF` without fabricated text. No automatic approval is possible.
- The **C3 / Bilingual qualification** UI panel executes **structural checks only**. Its web button cannot invoke the real GF mode.

## Windows: structural checks

After backing up changes and installing the correct files beneath `C:\mycode`, run:

```powershell
& 'C:\mycode\Grammatical-Framework\ars-magna-defluens\Qualifier_Candidats_FR_EN_v011.bat'
```

Or open **Semantic Studio → C3 / Bilingual qualification**. This mode neither compiles nor executes GF.

## Windows: real GF mode

Use the installed GF 3.12 binary, RGL source and WordBench builder at the locations configured by `Compiler_Candidats_FR_EN_GF312.bat`.

To compile **both** candidates under WordBench and then realize the 28 cases:

```powershell
& 'C:\mycode\Grammatical-Framework\ars-magna-defluens\Qualifier_Candidats_FR_EN_v011.bat' --compile-and-real
```

To reuse previously built candidates:

```powershell
& 'C:\mycode\Grammatical-Framework\ars-magna-defluens\Qualifier_Candidats_FR_EN_v011.bat' --real
```

WordBench remains the **exclusive candidate compilation boundary**. SemantiK Architect owns candidate realization. Defluens does not generate or patch grammar code. The batch size and local runtime depend on the installed GF/RGL and machine.

## Reports, fields and verdicts

Default directory:

```text
%USERPROFILE%\Downloads\Ars_Magna_Defluens\core_qualification\
```

Each run produces `defluens-v011-*.json` and a matching `defluens-v011-*.review.tsv`. Existing reports are preserved.

| Verdict | Meaning |
|---|---|
| `STRUCTURAL_PASS_ONLY` | Structural vectors and FR/EN parity succeeded; **no GF executed** |
| `BLOCKED_PGF` | Candidate PGF missing/invalid; no sentence invented |
| `FAILED` | Unexpected SA refusal, lock/language inconsistency, obligations, blocks or GF result mismatch |
| `REAL_GF_CANDIDATE_PASS` | All 28 real GF-backed candidate outputs passed the technical checks; **human linguistic review still pending** |

The TSV includes `candidate_text`, `pgf_sha256`, `deterministic_result_id`, `human_review` (initially `PENDING`) and `reviewer_notes`. A reviewed TSV is **external human evidence**; the qualification code neither auto-imports it as approval nor promotes any runtime.

## Unsupported capabilities

The integrated SA operations are attribute, classification, event, transitive action, location and directive. **Real conditions** and **conditional instructions** remain `CONTRACT_EXTENSION_REQUIRED` among the 15 intent mappings. They must receive typed semantic contracts, GF realization and conformance before becoming authoring options. Mere clause concatenation is not an acceptable substitute. Source attribution is also a separate contract gap.

## Original development test boundary

During the v0.11 build, unit tests and structural CLI integration were exercised without the Windows GF binary. Batch adapter tests used doubles; real-GF attempts without PGFs correctly returned `BLOCKED_PGF`. **Later evidence:** the end-user's November 5 Windows run actually compiled both candidates and achieved `REAL_GF_CANDIDATE_PASS`. This newer evidence is recorded separately rather than changing the historic test claims.

## Unchanged responsibilities

SemantiK Architect owns semantic fidelity and realization. WordBench builds PGFs and captures compilation evidence. GF/RGL owns grammar. diK manages lexical identities and provenance. Spek handles document composition. Defluens coordinates workflows and displays evidence. No source synchronization, RGL modification, RuntimeSet publication or activation is performed by this version.
