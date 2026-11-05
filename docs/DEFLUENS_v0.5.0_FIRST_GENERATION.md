# Ars Magna Defluens v0.5.0 — First Semantic Generation Studio

> **Historical release note.** This page describes the v0.5 scope and evidence available when it was developed. The later FR/EN core candidate compilation was confirmed on Windows on November 5, 2026; see [Windows GF validation](WINDOWS_GF_VALIDATION_2026_11_05.md). That result does not retroactively qualify the distinct v0.5 five-case profile.

## Delivered in v0.5

- The **Semantic Studio** exposes a real GF development candidate for five structured assertions of SemantiK Architect's `konstellation-explorer-3` profile. It delegates PGF compilation to GF WordBench, then calls SA's public `preview-candidate` command. SA executes its existing pipeline through GF rather than using a demonstration sentence or a fallback.
- A **multilingual development view** sends the same structured request to the public `render` command for each selected language (up to fourteen). Only admissible and deployed SA RuntimeSets can answer; an unavailable runtime produces an explicit error.
- Explicit JSON, Markdown and TXT exports plus in-memory-only session history.
- The existing Mécanismes Abstraits ivory, Prussian blue and vermilion UI identity is preserved.

## Original Windows procedure

1. Back up changed files and apply the release archive under `C:\mycode` without an additional top-level directory.
2. Launch `C:\mycode\Grammatical-Framework\ars-magna-defluens\Lancer_Ars_Magna_Defluens.bat`.
3. In **Semantic Studio**, select `A001-core` and **Load case into JSON**.
4. Use **Compile with GF 3.12**. This calls **WordBench** and requires a configured GF binary. If the build fails, inspect the exit code and logs rather than treating the candidate as present.
5. If a PGF candidate is available, use **Preview through actual GF**. The result is a SemantiK `communication_result` labeled `CANDIDATE_PREVIEW`, not a released response.
6. The **Generate selected languages** production control only renders through already admitted RuntimeSets. `SA-RUN-001` or a refusal is expected if a target runtime does not exist.

## Interfaces introduced

| Owner | Interface | Purpose |
|---|---|---|
| WordBench | `python tools/build_semantik_profile3_candidate.py --semantik-root ... --gf-exe ... --force` | Candidate PGF builder, locks and source hashes |
| SemantiK Architect | `preview-candidate --candidate-dir ... --runtime-set-id konstellation-fr-3 request.json` | Existing candidate-only conformance and realization |
| Defluens | `/api/semantik/pilot`, `/candidate`, `/build`, `/preview`, `/render-many` | Session-protected local orchestration |

## Scope and constraints

The five-case profile is a deliberately restricted early slice, **not** an arbitrary-sentence or 15-capability multilingual engine. The GF grammar sources belong to SemantiK Architect; WordBench stages and compiles them, and Defluens never creates its own planner. Candidate output is not equivalent to approved linguistic gold output or a released RuntimeSet. A failed build cannot be substituted with a prewritten phrase.

## Next capabilities identified at the time

Expand structured request/lexical coverage using the RGL, add conditional semantics and source attribution through SA contracts, and develop publication and longer-document workflows separately. The subsequent v0.7–v0.11 milestones address parts of this work; consult the [documentation index](INDEX.md) for current status.
