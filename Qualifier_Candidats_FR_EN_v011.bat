@echo off
setlocal EnableExtensions
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (set "PYTHON=py -3") else (set "PYTHON=python")
echo =============================================================
echo Ars Magna Defluens v0.11 - Qualification candidate FR/EN
 echo Aucune publication - validation linguistique humaine requise.
echo =============================================================
if /i "%~1"=="--compile-and-real" (
  echo Compilation des deux candidats par WordBench...
  call "%~dp0Compiler_Candidats_FR_EN_GF312.bat"
  if errorlevel 1 (echo ECHEC de compilation GF 3.12 - consulter les diagnostics GF affiches ci-dessus.&exit /b 3)
  %PYTHON% tools\qualifier_core_v011.py --real
) else if /i "%~1"=="--real" (
  %PYTHON% tools\qualifier_core_v011.py --real
) else (
  %PYTHON% tools\qualifier_core_v011.py
)
set "RESULT=%ERRORLEVEL%"
echo.
echo Rapports JSON + revue TSV dans Downloads\Ars_Magna_Defluens\core_qualification
if not "%RESULT%"=="0" echo BLOQUE ou ECHEC - aucune realisation GF ne doit etre presume reussie.
pause
exit /b %RESULT%
