# Ars Magna Defluens — Local Console v0.3.0

## New, working code

- Added root launchers: `Lancer_Ars_Magna_Defluens.bat`, `Launch_Ars_Magna_Defluens.bat`, optional `Ars_Magna_Defluens.pyw`.
- Added a localhost-only application written in standard-library Python plus HTML/CSS/JS, using the actual Mécanismes Abstraits brand palette and supplied logo.
- Operational WordBench `check`, `smoke`, `full` and `compare` process delegation (14-language focus), live logs, explicit stop, and failure handling.
- Read-only ingestion of real WordBench batch ZIPs; 14-language evidence explorer with GF raw/display output toggle.
- Direct launchers for WordBench and Observatory; path-based access to Compendium, GF RGL, archives and Defluens itself.
- Persistent absolute-path settings in LocalAppData, FR/EN UI, bundled English guided tour.
- No third-party runtime dependencies and no changes to GF/RGL source files.

## Evidence and verification

- Python unittest suite exercises settings validation, raw/archive preservation, fixed Python invocation arguments, a real stubbed subprocess boundary, and loopback API security.
- Playwright/Chromium user-interface test uses the **real 210-case uploaded archive as fixture**, with browser API responses mocked because local `127.0.0.1` browser navigation is restricted in this verification environment. That test covers the overview, 14-language explorer, raw/display join, locale switch, campaigns page, and mobile viewport. The Python API has been independently tested through real HTTP requests.
- A native Windows launch and actual `gf.exe` run remain to be verified by the user's Windows installation.

## Important distinction

The console reports **candidate generation**, not gold approval or semantic coverage certification. It is a first executable local coordinator, not the full GitOps platform in the original design specification.
