# Ars Magna Defluens v0.7.0 — Parametric French attributes

> **Historical scope note:** compilation was not performed in the original authoring environment. A later 2026-11-05 Windows run successfully compiled the separate `defluens-core-1` FR/EN candidates. It does not by itself certify every v0.7 attribute combination. See [Windows validation](WINDOWS_GF_VALIDATION_2026_11_05.md).

## Goal

Turn the v0.6 GF probe into a genuinely typed **canonical SemantiK Architect request**, using the existing `clause.copular_attribute` operation. **No text templates** in Defluens or SemantiK. RGL French owns tense, negation, agreement and copular syntax.

## What is actually implemented

1. The `SemantiK Architect` public CLI `defluens-attribute-request` turns explicit user selections into one `CommunicationRequest` with typed entity/concept refs, statement polarity, and `qualifier:tense`. It refuses unknown IDs.
2. `profiles/defluens-attribute-fr-1` contains the GF abstract and French concrete grammar, lexical bindings, SA↔GF bridge and candidate suite.
3. The WordBench public `build_semantik_profile3_candidate.py` builder now also accepts `--profile defluens-attribute-fr-1 --rgl-root <RGL>` and compiles the GF grammar under the WordBench process boundary into a **separate hashed candidate**, without changing the old five-case profile.
4. Defluens calls only those public CLI/build commands; the preview is still `SemantiK Architect preview-candidate` (original `CandidateConformance` pipeline). It exposes an editable canonical JSON request and refuses absent PGF.
5. 3 named subjects × 4 attributes × 2 polarities × 3 tenses = 72 possible typed combinations. The controlled vocabulary is deliberate; arbitrary prose and arbitrary GF expressions are **not** accepted as lexical inputs.

## Windows steps (French labels are retained for UI compatibility)

Extract the v0.7 ZIP into `C:\mycode` over v0.6 (back up local edits first). Launch `C:\mycode\Grammatical-Framework\ars-magna-defluens\Lancer_Ars_Magna_Defluens.bat`.

In **Atelier sémantique → B / Attributs sémantiques variables**:

1. Select `Mira` + `prêt(e)` + `Négative` + `Présent`.
2. Click **Créer la demande JSON**, inspect `CommunicationRequest`.
3. Click **Compiler le PGF RGL** (needs installed `gf.exe` and `gf-rgl`). WordBench will back up an existing candidate.
4. Click **Réaliser avec SemantiK + GF**. The response must come from the real candidate pipeline; there is no canned fallback.
5. Change any of the four selections and rebuild the JSON (no need to recompile). Try `Léa` + `absente` + `Positive` + `Futur`.

Or run WordBench directly:

```powershell
cd C:\mycode\Grammatical-Framework\GF_Wordbench
python tools\build_semantik_profile3_candidate.py `
  --semantik-root C:\mycode\SemantiK_Architect\SemantiK_Architect `
  --gf-exe C:\mycode\Grammatical-Framework\gf-3.12-windows\gf.exe `
  --rgl-root C:\mycode\Grammatical-Framework\gf-rgl `
  --profile defluens-attribute-fr-1 `
  --timeout 420 `
  --output "$env:USERPROFILE\Downloads\Ars_Magna_Defluens\semantik_candidates\defluens-attribute-fr-1" --force
```

The CLI mapper can be tested without any PGF:

```powershell
cd C:\mycode\SemantiK_Architect\SemantiK_Architect
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
python -m semantik_architect.adapters.inbound.cli.main defluens-attribute-request `
  --subject mira --attribute ready --polarity negative --tense present
```

## What is NOT claimed

- The authoring environment did not contain `gf.exe` and did not compile or test the real French PGF. Python tests verify SA planning + lexical/bridge expression selection using a **test double**; WordBench builder tests use a non-GF executable stub. Windows GF 3.12 is the next required acceptance check.
- A working PGF is a development candidate, not a released SA RuntimeSet or a linguistically certified French profile.
- This profile handles **one predicate family only** (`clause.copular_attribute`) and four attributes; it does not realize arbitrary encyclopedia paragraphs, the other 14 practical capacities, or any of the other 13 languages yet.
- No new grammatical strategy was implemented in the SA core, no RGL upstream code was modified, and Runtime Orchestrator is unchanged.

## Contract and provenance

`CommunicationRequest → CommunicationPlanner → LanguagePlanner → lexical binding → versioned SA↔GF bridge → PGF realizer → coverage-checked CommunicationResult`.

No hidden fallback. A failed build or absent candidate must yield an error, not a French sentence.
