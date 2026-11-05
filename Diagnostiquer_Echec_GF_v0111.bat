@echo off
setlocal EnableExtensions
chcp 65001 >nul
set "DEFLUENS=%~dp0"
set "WB=%DEFLUENS%..\GF_Wordbench"
set "OUT=%USERPROFILE%\Downloads\Ars_Magna_Defluens\semantik_candidates"
set "PROFILE=defluens-core-fr-1"
if /i "%~1"=="--en" set "PROFILE=defluens-core-en-1"
if not exist "%WB%\tools\inspect_semantik_gf_failure.py" (
  echo ERREUR : outil de diagnostic WordBench v0.11.1 introuvable.
  exit /b 2
)
echo === Diagnostic du dernier echec GF %PROFILE% - SANS recompilation ===
python "%WB%\tools\inspect_semantik_gf_failure.py" --root "%OUT%" --profile "%PROFILE%"
exit /b %ERRORLEVEL%
