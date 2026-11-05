# FR/EN GF 3.12 Candidate Validation — Windows Evidence (2026-11-05)

**Evidence type:** user-provided terminal transcript of a real Windows PowerShell execution. This page records observed tool output; it is **not** a substitute for archived GF logs, source artifacts or a signed CI attestation. The resulting candidates were **not published or activated**.

## Command

```powershell
& 'C:\mycode\Grammatical-Framework\ars-magna-defluens\Qualifier_Candidats_FR_EN_v011.bat' --compile-and-real
```

The command delegated PGF candidate builds to **WordBench**, running the installed `gf.exe` version 3.12 against RGL, then invoked the existing SemantiK Architect real-GF candidate qualification workflow.

## Candidate builds — observed successful output

| Item | French | English |
|---|---|---|
| Profile | `defluens-core-fr-1` | `defluens-core-en-1` |
| Concrete | `DefluensCoreFre` | `DefluensCoreEng` |
| WordBench report status | `PGF_BUILT_CANDIDATE_ONLY` | `PGF_BUILT_CANDIDATE_ONLY` |
| GF process | `completed` | `completed` |
| GF exit code | `0` | `0` |
| PGF compiled | `true` | `true` |
| PGF bytes | `509913` | `31478` |
| GF build duration | `4046` ms | `359` ms |
| PGF SHA-256 | `b473eb8e7982fbd708626b9e73677682d12e3b5f6c9ca0abf3e1b2fa1e024a6d` | `c75a793c29d0835e3ac78c82aede9155388d426d1fd59666e8ccf3bdb35380b3` |
| Released / activated | `false / false` | `false / false` |
| Linguistically certified | `false` | `false` |

Source files were read from `C:\mycode\SemantiK_Architect\SemantiK_Architect\profiles\defluens-core-1`; the GF binary from `C:\mycode\Grammatical-Framework\gf-3.12-windows\gf.exe`; the RGL from `C:\mycode\Grammatical-Framework\gf-rgl`.

### Source SHA-256 recorded in the build reports

| Source | SHA-256 |
|---|---|
| `DefluensCore.gf` | `ee04c4425d0f923bc80a7b98b12aa5f25e427ee3cdc6c0ad4e0c8b35caadf1e0` |
| `DefluensCoreFre.gf` | `dfbdbf4f56cb5d3723692853b20f621f052c564247063a70f2c3ac5a74df05ea` |
| `DefluensCoreEng.gf` | `78af1f3269ca4c2b45ea95eb3ea2fe9eb5d95f194071e97b542f1a62c44e3f6b` |

## Qualification results

The subsequent qualification report returned:

```json
{
  "status": "REAL_GF_CANDIDATE_PASS",
  "totals": {
    "authorized": 28,
    "expected_rejections": 8,
    "parity_pairs": 14,
    "structurally_validated": 28,
    "gf_candidates_verified": 28,
    "blocked_pgf": 0,
    "failed": 0,
    "human_reviews_completed": 0
  },
  "released": false,
  "linguistically_certified": false
}
```

Report basename from the transcript:

```text
defluens-v011-real-20261105T182810714481Z.json
defluens-v011-real-20261105T182810714481Z.review.tsv
```

Default directory: `%USERPROFILE%\Downloads\Ars_Magna_Defluens\core_qualification\`.

## What the result proves — and what it does not

**Verified by the reported Windows run:** both FR/EN candidate grammars compiled, PGFs were recorded with exact SHA-256 identifiers, and the automated candidate pipeline verified 28 real-GF-backed results with no blocked cases or failures. The structural cross-language parity checks passed for all 14 pairs.

**Still open:** human linguistic review of **all 28** candidate outputs (agreement, tense, polarity, imperative morphology, lexical idiomaticity, punctuation and ordering), full 15-capability coverage, fourteen-language SA runtime qualification, release authorization, publication and activation. A numerical pass is not a native-speaker or production certification.

The actual TSV rows, PGF binaries and full GF logs were **not supplied** with this documentation update. The evidence above is limited to the terminal transcript and should not be described as an independently reproduced build.

## Failure and fix chronology

1. **Initial Windows compile:** `DefluensCoreFre.gf` failed with GF exit code `1`; the original JSON error field was empty.
2. **v0.11.1 diagnostics:** log inspection exposed five `.s` type mismatches (`CommonRomance.Mood => Str` where `Str` was expected), plus nonblocking `mkAdv` naming warnings.
3. **v0.11.2 fix:** the French concrete uses `mkUtt` before `.s` and qualifies `ParadigmsFre.mkAdv`.
4. **November 5 rerun:** GF exit code `0` for both languages; automated result `REAL_GF_CANDIDATE_PASS`.

Read [GF diagnostics](DEFLUENS_v0.11.1_GF_DIAGNOSTICS.md), [the French fix](DEFLUENS_v0.11.2_GF_FRENCH_FIX.md) and [bilingual qualification](DEFLUENS_v0.11.0_BILINGUAL_QUALIFICATION.md).
