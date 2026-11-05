# Ars Magna Defluens v0.10.0 — Reproducible FR/EN Candidate Acceptance

> **Development candidate only.** This is a historical account of the v0.10 gates. The real FR/EN GF milestone was subsequently confirmed on Windows on November 5, 2026; see [validation evidence](WINDOWS_GF_VALIDATION_2026_11_05.md).

## Purpose

The v0.8–v0.9 releases already provided six FR/EN semantic operation families and a diK lexical handoff. Unit tests alone could not prove real candidate PGF execution. Version 0.10 introduced a **two-tier, auditable acceptance workflow**.

## Tier 1 — Structural acceptance without GF

A reference catalog includes **28 authorized requests** (24 single-statement cases: six operation families × two languages × two variants, plus four three- or eight-statement compositions) and **eight intentionally rejected requests**. The actual **SemantiK Architect public CLI** (`defluens-core-batch`) constructs and validates the cases. Defluens checks language/profile identity, statement count/order, polarity and obligations. A structural pass executes **no GF**.

## Tier 2 — Real GF candidate acceptance

The same 28 authorized requests pass through the SA `preview-candidate` CLI, using WordBench candidates with a compiled PGF and intact `pipeline.lock.json`. Missing PGFs produce `BLOCKED_PGF`, not a synthetic phrase. Candidate results must match the selected runtime, produce non-empty text and cover all mandatory obligations.

`REAL_GF_CANDIDATE_PASS` remains a **technical candidate outcome**: not human linguistic certification, not a `RELEASED` RuntimeSet, and not activation.

## Windows usage

Open **Semantic Studio → C2 / FR + EN candidate acceptance** for the structural-only check. Each run creates its own JSON report in `Downloads\Ars_Magna_Defluens\core_acceptance`.

```bat
Verifier_Candidats_FR_EN_v010.bat
```

For real GF execution, first compile the PGF candidates with WordBench, then run:

```bat
Verifier_Candidats_FR_EN_v010.bat --real
```

The batch command returns a nonzero code for missing candidates or failed checks. Logs and reports are never silently overwritten. The browser button cannot trigger the real GF mode.

## Boundaries

- diK still owns lexical sources and human review of candidate mappings.
- These gates cover **six semantic operation families in two languages**, not all 15 intended capabilities in 14 languages.
- Agreement, morphology, tense, punctuation, style and lexical choice still require human linguistic review.
- Spek, the SA Runtime Orchestrator and RGL source are unchanged.
- The SA batch CLI reuses the official planner; it does not publish RuntimeSets.
