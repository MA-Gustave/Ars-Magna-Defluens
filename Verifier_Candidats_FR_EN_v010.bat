@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  set "PYTHON=py -3"
) else (
  set "PYTHON=python"
)
echo =============================================================
echo Ars Magna Defluens v0.10 - Recette FR/EN (candidats non publies)
echo =============================================================
if /i "%~1"=="--real" (
  echo Mode PGF reel : requiert les deux PGF compiles via WordBench.
  %PYTHON% tools\recette_core_v010.py --real
) else (
  echo Mode structurel : SemantiK Architect sans compilation GF.
  %PYTHON% tools\recette_core_v010.py
)
set "RESULT=%ERRORLEVEL%"
echo.
if not "%RESULT%"=="0" echo ECHEC ou PGF BLOQUE : aucune publication n'a ete effectuee.
echo Les rapports JSON sont ecrits dans Downloads\Ars_Magna_Defluens\core_acceptance.
pause
exit /b %RESULT%
