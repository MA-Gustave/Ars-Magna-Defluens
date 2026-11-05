@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"
title Ars Magna Defluens - Console locale
set "PYTHONCMD="
where py.exe >nul 2>nul
if not errorlevel 1 set "PYTHONCMD=py -3"
if not defined PYTHONCMD (
    where python.exe >nul 2>nul
    if not errorlevel 1 set "PYTHONCMD=python"
)
if not defined PYTHONCMD (
    echo.
    echo Python 3 est requis pour lancer Ars Magna Defluens.
    echo Installez Python 3, puis relancez ce fichier.
    pause
    exit /b 1
)
echo.
echo ============================================================
echo  ARS MAGNA DEFLUENS - CONSOLE DE PILOTAGE
echo  MECANISMES ABSTRAITS - par Gustave
echo ============================================================
echo.
echo Ouverture de l'interface dans votre navigateur...
echo Ne fermez pas cette fenetre pendant l'utilisation.
echo La console fonctionne localement, sans serveur externe.
echo.
%PYTHONCMD% -m console.server
if errorlevel 1 (
  echo.
  echo La console a rencontre une erreur.
  pause
  exit /b 1
)
exit /b 0
