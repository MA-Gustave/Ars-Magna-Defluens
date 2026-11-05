# Ars Magna Defluens — Architecture and Data Flow

**Architecture status (November 5, 2026):** the local Windows console and candidate FR/EN pipeline exist. The GitOps/multi-tenant design described at the end of this page remains a future target. This distinction is intentional.

## 1. Current executable architecture

```text
Defluens local console (127.0.0.1, token-protected)
       |
       +-- WordBench CLI ------------------> gf.exe 3.12 + RGL
       |                                     |
       |                                hashed PGF candidates
       |
       +-- SemantiK Architect public CLI --> CommunicationRequest
       |                                     -> semantic planning
       |                                     -> lexical resolution
       |                                     -> SA↔GF bridge
       |                                     -> candidate GF realization
       |                                     -> CommunicationResult
       |
       +-- diK public CLIs ----------------> provenance-aware lexical handoff
       |
       +-- read-only evidence explorer ---> local WordBench/SA JSON/TSV/ZIP
```

**Ownership constraints:** SemantiK owns planning and realization; WordBench owns candidate builds and GF diagnostic evidence; RGL owns morphology and syntax; diK owns lexical knowledge/provenance; Defluens coordinates and displays results; the Runtime Orchestrator alone governs publication and activation. Defluens must not construct sentences by concatenating text or silently substitute simulated GF output.

## 2. Structured request and candidate pipeline

The user chooses a set of controlled semantic statements. Defluens asks the **public SemantiK Architect CLI** to construct a canonical `CommunicationRequest`. The `defluens-core-1` candidate supports up to eight ordered statements from six families: attribute, classification, intransitive event, transitive event, location and directive. SA plans and validates semantic obligations, resolves lexical slots and builds the GF expression. WordBench compiles the abstract `DefluensCore.gf` with `DefluensCoreFre.gf` / `DefluensCoreEng.gf`, using RGL functions. Candidate preview checks both the compiled PGF and its source locks.

## 3. Trust boundaries and failure semantics

- The console binds to `127.0.0.1`, uses a session access token, and invokes known CLI arguments via subprocess, not arbitrary shell fragments.
- Real GF compilation occurs under WordBench. Source hashes, compiler exit status and diagnostics belong in the evidence record.
- `BLOCKED_PGF`, GF errors, unmapped lexemes and unsupported semantic features must remain explicit failures.
- `STRUCTURAL_PASS_ONLY` does not execute GF; `REAL_GF_CANDIDATE_PASS` proves candidate technical execution, **not** human-reviewed language quality.
- A candidate never becomes `RELEASED` merely because compilation succeeded. No RuntimeSet is auto-published or auto-activated.

## 4. Confirmed Windows milestone

On November 5, 2026, an end-user run of GF 3.12 compiled the French and English candidates with exit code `0`. The subsequent qualification reported 28/28 real-GF candidate results, 14/14 FR/EN semantic parity pairs, zero failures, and zero completed human reviews. See [Windows GF validation](WINDOWS_GF_VALIDATION_2026_11_05.md).

## 5. Planned GitOps architecture — not yet implemented

The long-term specification envisages a shared multi-tenant language editor with routing by language code, GitHub OAuth attribution, commits via the contributor's identity, Actions-based GF compilation, and a read-only Observatory consuming aggregates. It targets collaboration across up to 300 languages without a custom compilation-server fleet. These are **design goals**, not current runtime features, operating cost guarantees or deployed infrastructure. GitHub Actions quotas and security policies will need separate operational design.

## 6. Related contracts

- [Local console](CONSOLE_LOCALE.md)
- [SemantiK integration](SEMANTIK_INTEGRATION_v0.4.0.md)
- [Composed Studio (v0.8)](DEFLUENS_v0.8.0_COMPOSED_STUDIO.md)
- [Bilingual qualification (v0.11)](DEFLUENS_v0.11.0_BILINGUAL_QUALIFICATION.md)
- [GF diagnostics and remediation](DEFLUENS_v0.11.1_GF_DIAGNOSTICS.md)
- [Release policy](RELEASE_AND_EVIDENCE_POLICY.md)
