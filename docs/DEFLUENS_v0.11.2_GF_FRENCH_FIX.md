# Ars Magna Defluens v0.11.2 — French GF Sentence-Type Fix

## Root cause confirmed by the actual compiler

GF 3.12 on Windows rejected `DefluensCoreFre.gf` with exit code `1`. Five linearizations projected `(mkS ...).s` directly, but the French RGL sentence field had the type `CommonRomance.Mood => Str`; the candidate's `Output.s` field required a plain `Str`. This was a GF type mismatch, not a missing compiler. The earlier empty JSON `error` field was independently fixed by v0.11.1.

## Source change

In the **SemantiK Architect** source repository, the French concrete grammar now converts each `S` sentence into `Utt` via `mkUtt` before reading `.s` for these operations: `RealizeAttribute`, `RealizeClass`, `RealizeEvent`, `RealizeAction`, `RealizeLocation`. The three potentially ambiguous `mkAdv` calls are explicitly qualified as `ParadigmsFre.mkAdv`. The earlier `DefluensAttributeFre.gf` v0.7 profile received the same preventative `mkUtt` conversion.

Schematic RGL pattern (illustrative, not a standalone grammar definition):

```gf
-- Old: sentence projection was a Mood-indexed table.
{s = (mkS t p (mkCl subject adjective)).s} ;

-- Fixed: Utt.s is a Str.
{s = (mkUtt (mkS t p (mkCl subject adjective))).s} ;
```

The GF abstract grammar, English concrete, SemantiK canonical JSON, bridge contracts, WordBench release rules and RuntimeSet activation policies were not changed by this fix.

## Install and qualify on Windows

Save any local edits before extracting the v0.11.2 corrective archive to the appropriate roots under `C:\mycode`. Then run:

```powershell
& 'C:\mycode\Grammatical-Framework\ars-magna-defluens\Qualifier_Candidats_FR_EN_v011.bat' --compile-and-real
```

If GF reports a different rejection, use `Diagnostiquer_Echec_GF_v0111.bat` to obtain stdout and stderr; do not infer a partial success. The command does not release or activate candidates. Even a completed GF compilation requires review of the human-language TSV.

## Subsequent confirmed result — November 5, 2026

The user reran the full command on Windows after installing v0.11.2. **Both PGFs compiled with GF exit code `0`**, and the batch qualifier returned `REAL_GF_CANDIDATE_PASS`: 28 real-GF candidate outputs verified, 14 FR/EN semantic parity pairs, zero blocked PGFs and zero failures. **Human reviews completed: 0; released: false; linguistically certified: false.** See [the complete milestone record](WINDOWS_GF_VALIDATION_2026_11_05.md).
