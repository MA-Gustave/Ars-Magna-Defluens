# Getting Started — Local Windows Development

This guide covers the **implemented local console and FR/EN candidate workflow**, not the proposed hosted GitOps platform.

## Prerequisites

- Windows and Python 3 available as `py -3` or `python`.
- Source trees for Defluens, **GF WordBench** and **SemantiK Architect**.
- A working `gf.exe` 3.12 and a matching local RGL source tree.
- Optional: diK, GF Observatory, GF RGL AI Compendium and Spek, depending on the workflow.

Default paths used by the provided launchers:

```text
C:\mycode\Grammatical-Framework\ars-magna-defluens
C:\mycode\Grammatical-Framework\GF_Wordbench
C:\mycode\Grammatical-Framework\gf-rgl
C:\mycode\Grammatical-Framework\gf-3.12-windows\gf.exe
C:\mycode\SemantiK_Architect\SemantiK_Architect
```

If your local trees use different roots, configure paths in Defluens **Settings**. Back up edited files before extracting any corrective ZIP.

## Start the console

```powershell
& 'C:\mycode\Grammatical-Framework\ars-magna-defluens\Lancer_Ars_Magna_Defluens.bat'
```

The browser UI is bound to `127.0.0.1`, protected by a per-session token. Keep the launcher window open. The legacy English alias `Launch_Ars_Magna_Defluens.bat` is also available.

## Explore the candidate pipeline

1. Open **Semantic Studio → C / Composed Communications** (the UI may show **Atelier sémantique → C / Atelier de communications composées**).
2. Choose up to eight ordered statements from six supported semantic families and build the canonical `CommunicationRequest` using the SA CLI.
3. Compile the FR/EN PGF candidates through WordBench, then perform a candidate preview through SA/GF; do **not** use handwritten GF text as a surrogate.
4. In **C3 / Bilingual qualification**, run structural-only qualification when you only need canonical/obligation checks.
5. For the full real-GF candidate run, invoke the batch command below on Windows.

```powershell
& 'C:\mycode\Grammatical-Framework\ars-magna-defluens\Qualifier_Candidats_FR_EN_v011.bat' --compile-and-real
```

To run the real candidate check without a fresh build:

```powershell
& 'C:\mycode\Grammatical-Framework\ars-magna-defluens\Qualifier_Candidats_FR_EN_v011.bat' --real
```

## Review reports

Look in `%USERPROFILE%\Downloads\Ars_Magna_Defluens\core_qualification\`. Each run emits a JSON report and a matching `.review.tsv`. Open the TSV in a spreadsheet editor to review the exact candidate text while preserving `pgf_sha256` and `deterministic_result_id`. Use `human_review` and `reviewer_notes` for external native-speaker evaluation. **Do not treat `PENDING` as approval**.

Expected technical verdicts: `STRUCTURAL_PASS_ONLY`, `BLOCKED_PGF`, `FAILED`, and `REAL_GF_CANDIDATE_PASS`. See [qualification details](DEFLUENS_v0.11.0_BILINGUAL_QUALIFICATION.md).

## Troubleshooting

If the French/English candidate build fails, read the preserved stdout/stderr logs and run:

```powershell
& 'C:\mycode\Grammatical-Framework\ars-magna-defluens\Diagnostiquer_Echec_GF_v0111.bat'
```

For an earlier French GF 3.12 build, five `Mood => Str` errors were fixed in v0.11.2 by wrapping `mkS` in `mkUtt`. The actual corrected FR/EN Windows run passed on November 5, 2026. See [diagnostic history](DEFLUENS_v0.11.1_GF_DIAGNOSTICS.md) and [the validation record](WINDOWS_GF_VALIDATION_2026_11_05.md).

## Safety boundary

A candidate PGF or accepted automated report is **not** a published/activated RuntimeSet. Do not bypass SemantiK Runtime Orchestrator, replace existing candidates with test fixtures, or infer the missing conditional/source-attribution semantics from plain text.
