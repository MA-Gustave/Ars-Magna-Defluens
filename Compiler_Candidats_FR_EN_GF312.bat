@echo off
setlocal EnableExtensions
chcp 65001 >nul
set "DEFLUENS=%~dp0"
set "WB=%DEFLUENS%..\GF_Wordbench"
set "RGL=%DEFLUENS%..\gf-rgl"
set "SA=%DEFLUENS%..\..\SemantiK_Architect\SemantiK_Architect"
set "GF=%DEFLUENS%..\gf-3.12-windows\gf.exe"
set "OUT=%USERPROFILE%\Downloads\Ars_Magna_Defluens\semantik_candidates"
echo.
echo Ars Magna Defluens v0.8 - PGF candidat FR + EN
 echo WordBench : %WB%
 echo SemantiK  : %SA%
 echo GF        : %GF%
echo.
if not exist "%GF%" (echo ERREUR - gf.exe est introuvable.&exit /b 2)
if not exist "%WB%\tools\build_semantik_profile3_candidate.py" (echo ERREUR - WordBench est introuvable.&exit /b 2)
if not exist "%SA%\profiles\defluens-core-1\DefluensCore.gf" (echo ERREUR - Sources SemantiK v0.8 introuvables.&exit /b 2)
if not exist "%RGL%\src\api\SyntaxFre.gf" (echo ERREUR - RGL officielle introuvable.&exit /b 2)
set "PYTHONIOENCODING=utf-8"
python "%WB%\tools\build_semantik_profile3_candidate.py" --semantik-root "%SA%" --gf-exe "%GF%" --rgl-root "%RGL%" --profile defluens-core-fr-1 --output "%OUT%\defluens-core-fr-1" --timeout 420 --force
if errorlevel 1 (
  echo ERREUR - compilation du PGF francais. Les anciens candidats sont conserves.
  python "%WB%\tools\inspect_semantik_gf_failure.py" --root "%OUT%" --profile defluens-core-fr-1
  exit /b 3
)
python "%WB%\tools\build_semantik_profile3_candidate.py" --semantik-root "%SA%" --gf-exe "%GF%" --rgl-root "%RGL%" --profile defluens-core-en-1 --output "%OUT%\defluens-core-en-1" --timeout 420 --force
if errorlevel 1 (
  echo ERREUR - compilation du PGF anglais. Les anciens candidats sont conserves.
  python "%WB%\tools\inspect_semantik_gf_failure.py" --root "%OUT%" --profile defluens-core-en-1
  exit /b 4
)
echo.
echo PGF candidats construits (NON PUBLIES). Ouvrir l'atelier Defluens pour tester.
exit /b 0
