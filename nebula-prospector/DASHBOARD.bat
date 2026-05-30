@echo off
title NOVA Dashboard - NEBULA Prospector
cd /d "%~dp0"

cls
echo.
echo  ================================================================
echo                NOVA Dashboard - NEBULA Prospector
echo  ================================================================
echo.

REM Detecte l'IP locale (Wi-Fi ou Ethernet)
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do (
    set "IP=%%a"
    goto :foundip
)
:foundip
set IP=%IP: =%

echo  Le dashboard demarre dans une seconde...
echo.
echo  -----------------------------------------------------------
echo   Sur ce PC          :  http://localhost:8001
if defined IP echo   Sur ton portable   :  http://%IP%:8001    (meme Wi-Fi requis)
echo  -----------------------------------------------------------
echo.
echo   ASTUCE : sur ton portable, ouvre le navigateur et tape
echo            l'adresse ci-dessus. Ton PC et ton portable
echo            doivent etre sur le MEME Wi-Fi.
echo.
echo   Pour arreter le dashboard : appuie sur Ctrl+C
echo  -----------------------------------------------------------
echo.

REM Lance uvicorn accessible sur tout le reseau local (0.0.0.0)
python -m uvicorn dashboard.server:app --host 0.0.0.0 --port 8001

echo.
echo Dashboard arrete.
pause
