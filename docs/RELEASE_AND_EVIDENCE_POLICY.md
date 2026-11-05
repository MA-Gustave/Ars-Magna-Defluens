# Candidate Evidence, Human Review and Runtime Release Policy

Defluens intentionally separates **development evidence** from **linguistic certification** and **production release**.

| State or artifact | Demonstrates | Does not demonstrate |
|---|---|---|
| WordBench 14 × 15 probes | Individual GF development checks in prepared languages | Integration of every probe into SemantiK Architect |
| `STRUCTURAL_PASS_ONLY` | Canonical requests, obligations and FR/EN semantic parity checks | Execution of any PGF |
| `PGF_BUILT_CANDIDATE_ONLY` | A candidate grammar compiled by real GF with source hashes | Conformance or language quality |
| `REAL_GF_CANDIDATE_PASS` | Successful automated SA→GF candidate realizations and technical invariants | Native-speaker approval or `RELEASED` status |
| Reviewed TSV (`human_review`) | External, case-specific human observations | Automatic RuntimeSet admission |
| `RELEASED` RuntimeSet | Explicit admission under SemantiK Runtime Orchestrator's release policy | A state the Defluens console may set itself |

## Mandatory boundaries

- **WordBench** controls compilation, GF exit codes, hashes and build diagnostics.
- **SemantiK Architect** controls canonical semantics, semantic obligations and candidate realization.
- **GF/RGL** controls linguistic forms; **diK** owns provenance-aware lexical inputs.
- **Defluens** coordinates local workflows and displays immutable evidence; it does not invent grammatical outputs, release decisions or synthetic success.
- **SemantiK Runtime Orchestrator** owns final promotion, activation and runtime lifecycle.

## Human linguistic review checklist

For each French and English candidate output, review at least: meaning preservation; negation and polarity; tense/aspect; person/number/gender agreement where applicable; copular and verbal complements; imperative morphology; word order and article/preposition choice; spelling and punctuation; lexical appropriateness and register; complete representation and correct order of statements. Document any defect with its case ID, PGF hash and concrete source where possible.

No number of automated passing cases may be substituted for completed human reviews, additional semantic-contract work or release policy approval. The November 5, 2026 Windows evidence has `human_reviews_completed: 0`.
