# Ars Magna Defluens

**Local-first orchestration for structured multilingual communication with Grammatical Framework (GF).**

> **Current implementation: v0.11.2, Windows development candidate.** The local Defluens console, SemantiK Architect bridge, WordBench candidate compiler, and FR/EN qualification workflow are implemented. On **November 5, 2026**, both French and English candidate PGFs compiled successfully with GF 3.12 on Windows and the **28/28 automated candidate realizations** passed. **Human linguistic reviews: 0; no RuntimeSet has been released or activated.** A hosted GitOps platform and 300-language orchestration remain architectural goals, not delivered features.

[Documentation](docs/INDEX.md) · [GitHub Wiki](https://github.com/MA-Gustave/Ars-Magna-Defluens/wiki) · [Windows GF evidence](docs/WINDOWS_GF_VALIDATION_2026_11_05.md) · [Architecture](docs/ARCHITECTURE.md)

## What works today

- **Local Windows console:** start `Lancer_Ars_Magna_Defluens.bat`; access the dashboard, WordBench campaigns, evidence explorer, Semantic Studio, lexical handoff and configuration from a loopback-only browser interface.
- **Structured semantic authoring:** produce a canonical `CommunicationRequest` using the public SemantiK Architect CLI, not a parallel parser or a phrase-template generator.
- **Composed communications:** up to **eight ordered statements** using **six** supported operation families: copular attribute, copular classification, intransitive event, transitive event, location and directive.
- **Candidate FR/EN GF grammars:** `DefluensCore.gf` with `DefluensCoreFre` and `DefluensCoreEng`, compiled by **GF WordBench**, realized through **SemantiK Architect** and GF/RGL.
- **Automated candidate qualification:** 28 authorized requests, eight expected rejections, 14 FR/EN semantic parity pairs, and a review TSV. Candidate results are never automatically certified or published.
- **diK lexical handoff:** exchange provenance-aware lexical candidates for separately reviewed mappings, without inventing semantic or grammatical authority.

## Verified Windows milestone — November 5, 2026

The user-run command was:

```powershell
& 'C:\mycode\Grammatical-Framework\ars-magna-defluens\Qualifier_Candidats_FR_EN_v011.bat' --compile-and-real
```

| Validation item | Observed result |
|---|---|
| French `DefluensCoreFre` PGF | Compiled, GF exit code `0`, 509,913 bytes |
| English `DefluensCoreEng` PGF | Compiled, GF exit code `0`, 31,478 bytes |
| Authorized requests | 28 |
| Expected rejections | 8 |
| Structural validations | 28/28 |
| FR/EN semantic parity pairs | 14/14 |
| Real-GF candidate results verified | 28/28 |
| Blocked PGFs / failed cases | 0 / 0 |
| Final automated verdict | `REAL_GF_CANDIDATE_PASS` |
| Human linguistic reviews completed | **0** |
| Released / activated RuntimeSets | **No / no** |

This is an **automated technical pass**, not proof of grammatical elegance, universal coverage, or production readiness. The compiled PGFs and original qualification reports remain on the Windows workstation; they are **not included** in this repository documentation. See [the validation record](docs/WINDOWS_GF_VALIDATION_2026_11_05.md), [the bilingual qualification procedure](docs/DEFLUENS_v0.11.0_BILINGUAL_QUALIFICATION.md) and [the v0.11.2 GF fix](docs/DEFLUENS_v0.11.2_GF_FRENCH_FIX.md).

## Quick start on Windows

**Requirements:** Python 3; the local Defluens, WordBench and SemantiK Architect repositories; GF 3.12 (`gf.exe`); and the GF RGL source tree. The default paths assumed by the bundled launchers are:

```text
C:\mycode\
├── Grammatical-Framework\
│   ├── ars-magna-defluens\
│   ├── GF_Wordbench\
│   ├── gf-rgl\
│   └── gf-3.12-windows\gf.exe
└── SemantiK_Architect\SemantiK_Architect
```

Launch the local console:

```powershell
& 'C:\mycode\Grammatical-Framework\ars-magna-defluens\Lancer_Ars_Magna_Defluens.bat'
```

In **Semantic Studio → C3 / Bilingual qualification**, run the **structural-only** checks, or use the command line to compile with WordBench and verify candidate GF output:

```powershell
# Compile both FR/EN candidates, then run the real GF-backed candidate checks.
& 'C:\mycode\Grammatical-Framework\ars-magna-defluens\Qualifier_Candidats_FR_EN_v011.bat' --compile-and-real

# Reuse already built candidates without recompiling.
& 'C:\mycode\Grammatical-Framework\ars-magna-defluens\Qualifier_Candidats_FR_EN_v011.bat' --real
```

The launchers may show French UI or diagnostic labels; this is not a different API. They retain the original filenames for compatibility. You can find JSON reports and a human-review TSV in:

```text
%USERPROFILE%\Downloads\Ars_Magna_Defluens\core_qualification\
```

See [Getting started](docs/GETTING_STARTED.md) for setup, reporting, and troubleshooting.

## System boundaries

| Component | Responsibility |
|---|---|
| **Ars Magna Defluens** | Local UI, orchestration, report presentation and candidate workflow coordination |
| **SemantiK Architect** | Canonical communication requests, planning, lexical/bridge conformance and GF-backed realization |
| **GF WordBench** | Build/test invocation, diagnostics, PGF candidates, evidence and source locks |
| **GF / Resource Grammar Library (RGL)** | Grammar types, language-specific syntax and morphology |
| **diK** | Lexical observations, identities, sources and provenance |
| **GF RGL AI Compendium** | Engineering guidance and normative RGL development constraints |
| **GF Observatory** | Aggregated read-only evidence and status display |
| **Spek** | Document composition and semantic publishing, separate from language realization |

**No second semantic planner, no text-only fallback, no automatic promotion.** A `PGF_BUILT_CANDIDATE_ONLY` or `REAL_GF_CANDIDATE_PASS` verdict is not a `RELEASED` RuntimeSet. Release and activation remain under the existing SemantiK Runtime Orchestrator policy.

## Coverage and current limitations

The current FR/EN candidate profile covers **six operation families**, not the whole 15-intent practical-generation portfolio. The broader WordBench lab contains **15 intended capabilities × 14 prepared languages (210 candidate probes)**, which must not be presented as 210 SemantiK-qualified realizations or production runtimes. Real conditional constructs, conditional instructions and source attribution still require explicit semantic contracts and GF conformance. Vocabulary is controlled; arbitrary free text is not an accepted semantic interface.

The local console is **not** a hosted multi-tenant application: GitHub OAuth, contributor editing through a web IDE, serverless compilation via GitHub Actions, a 300-language global observatory and zero-infrastructure GitOps are planned architectural directions. They are not implemented here.

## Documentation and project history

Start with the [documentation index](docs/INDEX.md), [architecture](docs/ARCHITECTURE.md), [console guide](docs/CONSOLE_LOCALE.md), [bilingual qualification](docs/DEFLUENS_v0.11.0_BILINGUAL_QUALIFICATION.md), [GF diagnostics](docs/DEFLUENS_v0.11.1_GF_DIAGNOSTICS.md) and [Windows proof](docs/WINDOWS_GF_VALIDATION_2026_11_05.md). The GitHub wiki offers task-oriented navigation.

**Naming:** Ars Magna Defluens is the canonical product name. *Ars Magna Lulli* and `ars-magna-lulli` are historical identifiers; persisted machine tokens must only be changed through versioned migrations. See [name migration](docs/NAME_MIGRATION.md).

**Status policy:** we distinguish documentation, automated structural evidence, compiled PGF evidence, human linguistic review and approved runtime release. Historical version notes retain their original testing context; the November 5 validation record supersedes older statements that FR/EN candidate compilation was still pending.
