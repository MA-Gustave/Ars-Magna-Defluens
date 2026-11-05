# Ars Magna Defluens — Local Console v0.4.0

**Status:** first runnable Windows coordination console. Not the future hosted GitOps orchestration platform. Read-only for RGL and WordBench sources; only WordBench executes GF.

## Launch from the repository root

Double-click `Lancer_Ars_Magna_Defluens.bat` (or its English alias `Launch_Ars_Magna_Defluens.bat`). A normal Python 3 installation is sufficient; no pip/npm/Node dependency is required. A browser opens on `127.0.0.1` with a session token. Keep the BAT terminal open while using the app. Close with **Fermer la console / Close console** or Ctrl+C.

Optional: `pyw -3 Ars_Magna_Defluens.pyw` is a console-free launcher. The regular BAT is recommended for visible diagnostics.

## Available features

* **Dashboard:** reads the latest batch ZIP in `%USERPROFILE%\Downloads\Ars_Magna_Defluens\practical_pilot_runs`; shows actual attempts, technical candidates, failures, and per-language status.
* **Campaigns:** starts the *installed* WordBench Python modules (not copied validators) for `check`, `smoke` (14 languages), `full` (210 scenarios) or `compare`. It captures a live log and allows a user-initiated stop.
* **Languages & evidence:** opens candidate sentences from `pilot_run.json` inside the latest ZIP, including original raw output and a display-only `&+` normalization.
* **Ecosystem:** opens WordBench's `launch_gui.bat`, Observatory's `Launch_Observatory.bat`, or the configured project directories.
* **Settings:** editable absolute paths; saved in `%LOCALAPPDATA%\Ars_Magna_Defluens\settings.json` on Windows.
* **Guided tour:** offline historical demonstration (data from the earlier 210-case campaign), launched in a separate browser tab from the actual console.

## Defaults

The console expects these sibling directories under `C:\mycode\Grammatical-Framework` if Ars Magna Defluens is installed there:

- `GF_Wordbench`
- `GF_Observatory`
- `GF_RGL_AI_Compendium`
- `gf-rgl`
- `gf-3.12-windows\gf.exe`

If paths differ, use **Configuration / Settings**. Report ZIPs stay in Downloads. Local console logs stay under `%LOCALAPPDATA%\Ars_Magna_Defluens\logs`.

## Trust and evidence semantics

`candidate_for_review` **does not** mean linguistic certification. The console never modifies `.gf` RGL code, never changes approved gold files, never claims that all GF languages are supported, and never launches `gf.exe` independently. It delegates WordBench jobs via a fixed argument vector (no user-supplied shell commands) and presents the resulting archives as read-only evidence. The exact raw GF output remains unchanged in the ZIP, including `&+` markers.

The web server binds only to `127.0.0.1`, uses a random per-session access token for every API request, and sends no CORS headers. It needs no Internet connection. It does not include GitHub login, multi-user access, remote queues or deployment automation; those remain target architecture elements.

## Tests

From the Defluens repository root:

```powershell
py -3 -m unittest discover -s tests -p "test_console.py" -v
```

The GUI has also been exercised in Chromium via Playwright. Browser automation is for development validation and is **not required** to run the application.

## Semantic Studio (v0.4.0)

A new **Semantic Studio** tab calls only the public SemantiK Architect CLI:
`validate-request`, `render`, and `capabilities`. Click **Load SA sample** to
load the structured example from the installed Architect repository; no free-
text-to-semantics inference is performed. Its readiness test calls public
SemantiK Runtime Orchestrator `inspect-profile`; declared runtime metadata
without a real PGF must remain `BLOCKED`.

WordBench's `handoff` campaign action creates a candidate-only development
mapping JSON; it never means runtime qualification. Configure the two separate
SemantiK repository roots under Settings; the configured GF executable is
passed to SA only for its official precompiled-PGF CLI backend.
