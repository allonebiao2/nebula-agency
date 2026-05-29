@echo off
title NOVA - Setup Wizard NEBULA Prospector
cd /d "%~dp0"
echo.
echo ================================================================
echo   NOVA - Setup Wizard NEBULA Prospector
echo ================================================================
echo.

REM Verifie Python
where python >nul 2>nul
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH.
    echo.
    echo Telecharge Python ici : https://www.python.org/downloads/
    echo IMPORTANT : Pendant l'install, COCHE "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM Lance le wizard
python scripts\setup_wizard.py

echo.
echo ================================================================
pause
