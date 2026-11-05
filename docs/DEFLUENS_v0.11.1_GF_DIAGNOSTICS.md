# Ars Magna Defluens v0.11.1 — GF 3.12 Compilation Diagnostics

## Observed trigger

On **November 5, 2026**, the first Windows invocation of `Qualifier_Candidats_FR_EN_v011.bat --compile-and-real` found `gf.exe` and executed `-make` for `DefluensCoreFre.gf`. GF exited with code `1`: `gf_process_state=completed`, `capture_complete=true`, `status=BLOCKED_Gf_COMPILATION`. The report's `error` field was empty because the WordBench builder read only `process.launch_error_message`. That field is normally empty when the executable starts successfully but compilation itself fails.

**The initial JSON report did not include the GF error.** The complete logs existed in `diagnostics_dir` as `gf-stderr.log`, `gf-stdout.log`, and `build-report.json`. In the subsequent log inspection, GF reported five `CommonRomance.Mood => Str` typing errors in the French concrete. See [the v0.11.2 fix](DEFLUENS_v0.11.2_GF_FRENCH_FIX.md) and the [successful Windows rerun](WINDOWS_GF_VALIDATION_2026_11_05.md).

## v0.11.1 changes

- WordBench retains its compilation and candidate-preservation logic, but unsuccessful builds now expose `failure_reason`, `gf_stdout_log`, `gf_stderr_log`, `gf_stdout_tail`, `gf_stderr_tail`, a nonempty `error`, and `diagnostics_dir` in `build-report.json`.
- The read-only tool `GF_Wordbench/tools/inspect_semantik_gf_failure.py` also understands **older v0.11 reports**, even without diagnostic tails in JSON. It selects the latest failure for a chosen profile and displays the final 100 lines of each GF log.
- `Compiler_Candidats_FR_EN_GF312.bat` surfaces logs for French or English build failures; the qualification launcher no longer conflates a GF compilation rejection with a missing executable.
- `Diagnostiquer_Echec_GF_v0111.bat` inspects stored evidence **without compiling GF again**.

## Windows commands

```powershell
& 'C:\mycode\Grammatical-Framework\ars-magna-defluens\Diagnostiquer_Echec_GF_v0111.bat'
```

Or inspect a chosen profile directly:

```powershell
python 'C:\mycode\Grammatical-Framework\GF_Wordbench\tools\inspect_semantik_gf_failure.py' `
  --root "$env:USERPROFILE\Downloads\Ars_Magna_Defluens\semantik_candidates" `
  --profile defluens-core-fr-1
```

After interpreting the *actual* diagnostics and applying the targeted source fix, rerun:

```powershell
& 'C:\mycode\Grammatical-Framework\ars-magna-defluens\Qualifier_Candidats_FR_EN_v011.bat' --compile-and-real
```

## Verification boundaries

The diagnostic patch was tested with intentionally failing fake GF processes on both stdout and stderr. Those tests confirmed log visibility, persistent reports, compatibility with previous build reports, bounded tail output and preservation of old PGF candidates. **They did not themselves prove a valid grammar.** Real GF compilation was confirmed later in the separate November 5 Windows run. No RuntimeSet was released or activated.
