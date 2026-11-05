# Six-repository integration status — 2026-11-04

## Verified locally in this update

- The latest WordBench full GF report ZIP has 210 candidate probe records in
  14 languages. New `gf_wordbench.practical.semantik_handoff` exports those
  candidates into `semantik_handoff.json` with reported source/script hashes.
- SemantiK's existing operation registry recognizes several suggested matches;
  exactly **42 language-scenario rows** (three semantic constructs across
  14 languages) require a new contract/feature decision: `condition-real`,
  `source-attribution`, `conditional-instruction`. The other operations still
  require lexical-slot and feature-level candidate conformance.
- `SemantiK Architect validate-request` accepted its own Orgo sample.
- A real `render` correctly returned `SA-RUN-001` (no released RuntimeSet for
  the sample's `fr + orgo-operational-1`). No text was synthesized.
- Public Runtime Orchestrator `inspect-profile` correctly returned `BLOCKED`
  for the example French profile with missing `grammar.pgf`.
- The Defluens Semantic Studio uses these public CLIs and preserves failures.
  Browser interaction has been exercised with a mocked HTTP transport and
  real local CLI calls tested separately.

## Not yet delivered / not claimed

- No admitted immutable PGF bundle for the complete 15-intent practical profile.
- No complete SA↔GF concrete bridge for the remaining conditional/source
  attribution semantics, and no complete conformance suite for all 14 languages.
- No qualified 14-language `RELEASED` RuntimeSets or real multi-language SA
  `CommunicationRequest → CommunicationResult` acceptance run.
- No confirmation of native Windows installation or real GF execution of a
  new SA bridge. The existing 210 WordBench probe results remain valid
  *development evidence*, not production release proof.

## Next engineering sequence

1. One fully conformed pilot runtime (e.g. `Fre`) with PGF+bridge+lexicon.
2. Extend the versioned SA↔GF bridge semantics and assert full lexical/feature
   consumption for all 15 fixed intents; no new tense inventory.
3. Run candidate-matrix conformance in SemantiK and structured multi-phrase
   metamorphic tests (5 variants per capability recommended).
4. Promote/activate qualifying runtimes through the existing orchestrator.
5. Display actual released profile coverage in Defluens/Observatory; then
   expand to the remaining 13 target languages.

## Subsequent milestone (2026-11-05; not part of the original 2026-11-04 audit)

The v0.11.2 FR/EN `defluens-core-1` candidate grammars were compiled by
GF 3.12 on the user's Windows workstation. The reported WordBench builds
returned `PGF_BUILT_CANDIDATE_ONLY` and the SemantiK candidate qualifier
returned `REAL_GF_CANDIDATE_PASS`, with 28/28 candidate outputs and 14/14
semantic parity pairs verified. This **supersedes** the earlier statement that
there was no Windows confirmation for these two *core candidate* grammars,
but it **does not** establish any 14-language release or 15-intent conformance.
Human reviews completed: 0. No RuntimeSet was released or activated.
See [Windows GF validation](WINDOWS_GF_VALIDATION_2026_11_05.md).
