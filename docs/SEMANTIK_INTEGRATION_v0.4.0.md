# Defluens 0.4.0 — real SemantiK integration, no duplicate grammar

The new **Semantic Studio** is a local UI client for the existing, public
SemantiK Architect Python CLI (`render`, `validate-request`, `capabilities`).
It accepts **structured JSON** only and never interprets free-form text,
implements a replacement planner, makes up a grammatical sentence, or marks
unreleased candidates as conformant.

An additional read-only `inspect-profile` control delegates to the public
SemantiK Runtime Orchestrator. A `BLOCKED` result is shown as blocked. A
RELEASED declaration in a capability manifest is *not* proof of a present
compiled grammar; a real render remains subject to SemantiK's gates.

The WordBench Campaigns section adds `handoff`, which delegates to
`gf_wordbench.practical.semantik_handoff` and writes
`%USERPROFILE%\Downloads\Ars_Magna_Defluens\alignment14\semantik_handoff.json`.
The handoff is **development evidence**, not READY release evidence.

Local paths in Settings:

* `C:\mycode\SemantiK_Architect\SemantiK_Architect`
* `C:\mycode\SemantiK_Architect\SemantiK_Runtime_Orchestrator`

SA is invoked with the running Python interpreter, `PYTHONPATH` pointing to
its `src` and optional `SEMANTIK_GF_EXECUTABLE` for its official GF CLI
fallback. No private SA module is imported into Defluens. The same-origin UI
is token-protected and bound to loopback; user JSON stays local.

## Windows acceptance test

1. Install all six patches at the exact repository roots.
2. Start `Lancer_Ars_Magna_Defluens.bat`.
3. Open **Semantic Studio**, choose **Load SA sample** and **Validate request**.
4. Choose **Inspect readiness** (`fr`, `konstellation-explorer-3`). A missing
   compiled `grammar.pgf` must be reported as `BLOCKED`, not as a success.
5. Optionally choose **Render with SA**; success requires a real admitted
   RuntimeSet and remains a SemantiK response, not a Defluens substitute.
6. Under **GF Campaigns**, run **Create handoff** after a full WordBench ZIP;
   inspect the JSON and its explicit missing contract/conformance gates.

To reach 14-language production, compile real PGFs and create immutable SA
candidate bundles, qualify every intended operation/feature per language,
then use the existing SemantiK Runtime Orchestrator to publish artifacts.
This integration patch is a **vertical-slice preparation**, not that release.
