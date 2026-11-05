# Ars Magna Defluens v0.8.0 — Composed Communication Studio

> **Historical milestone: development candidates only.** At v0.8 packaging time, compilation on the target Windows GF 3.12 installation was unverified. The later November 5, 2026 run confirmed both core candidate PGFs and 28/28 automated realizations; see [Windows validation](WINDOWS_GF_VALIDATION_2026_11_05.md). Human review and RuntimeSet release remain pending.

## Delivered

The **Semantic Studio → C / Composed Communications** editor can combine between **one and eight ordered statements** while preserving independent semantic obligations. It uses six existing SemantiK Architect operation families:

- `clause.copular_attribute`
- `clause.copular_classification`
- `clause.intransitive_event`
- `clause.transitive_event`
- `clause.locative`
- `directive.action`

Both languages use the same abstract grammar `DefluensCore.gf` and separate candidates `DefluensCoreFre` and `DefluensCoreEng`, backed by `SyntaxFre` / `SyntaxEng` and `ParadigmsFre` / `ParadigmsEng`. The controlled lexicon includes Mira, Léa and Noa; qualities, categories, events, objects, places and directives; and polarity or tense where supported.

Defluens obtains its canonical `CommunicationRequest` from the **public SA CLI**, not by assembling free-form prose in JavaScript. WordBench builds and hashes the candidates. SA performs planning, binding and preview; its production-language comparison remains distinct from this development comparison. Neither WordBench nor Defluens decides truth or publishes RuntimeSets.

## Windows workflow

1. Back up local edits; install into `C:\mycode` with the correct repository roots.
2. Confirm `gf-rgl` and `gf-3.12-windows\gf.exe` are installed.
3. Start `Lancer_Ars_Magna_Defluens.bat` from the Defluens repository root.
4. Open **Semantic Studio → C / Composed Communications**. Add up to eight statements, choose French or English, and click **Build CommunicationRequest**.
5. Compile either candidate through WordBench, or use `Compiler_Candidats_FR_EN_GF312.bat` for both languages.
6. Use **Realize request** or **Compare FR + EN** to invoke the real SA candidate pipeline.

The labels in the current local UI may appear in French, such as *Atelier sémantique*, *Construire CommunicationRequest*, *Réaliser la demande*, and *Comparer FR + EN*.

## Local API and contract

The token-protected routes are `GET /api/semantik/core-catalog`, `GET /api/semantik/core-status`, `POST /api/semantik/core-request`, `POST /api/semantik/core-build`, `POST /api/semantik/core-preview`, and `POST /api/semantik/core-preview-many`.

Canonical requests have a deterministic identity, typed graph, ordered obligations, target profile and candidate runtime identity. SA's bridge refuses unmapped lexical items and unsupported features. No obligation is silently dropped.

## Limitations

- The 15-intent × 14-language WordBench lab is a separate set of **210 candidate probes**, not six fully qualified operations in fourteen languages.
- Conditional sentences, source attribution, long-document structures and unrestricted lexicons are out of scope.
- Candidate compilation and automated structural conformance are not equivalent to human-reviewed tense, agreement, register or punctuation.
- No release or activation occurs here; promotion must use SemantiK Runtime Orchestrator.

## Original test boundary

At release construction time, tests covered typed operation mapping, lexical slots, ordered composition, rejecting unknown inputs, public CLI transport and WordBench staging against a **test compiler**. The GUI was exercised with Playwright using explicitly simulated responses. These results must not be confused with the later verified Windows compilation.
