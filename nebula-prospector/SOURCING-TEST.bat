@echo off
title NOVA - Sourcing test
cd /d "%~dp0"

cls
echo.
echo  ================================================================
echo                NOVA Sourcing Test (OpenStreetMap)
echo  ================================================================
echo.
echo  Lance un sourcing test : salons de beaute a Cotonou.
echo  Tu verras NOVA s'animer dans le dashboard !
echo.
echo  Assure-toi que DASHBOARD.bat tourne dans une autre fenetre.
echo.
echo  -----------------------------------------------------------
echo.

python -m sourcing.openstreetmap search --city Cotonou --category beauty

echo.
echo  ================================================================
echo   Sourcing termine. Va voir le dashboard !
echo  ================================================================
pause
