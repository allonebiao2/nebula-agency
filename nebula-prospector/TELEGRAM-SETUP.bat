@echo off
title NOVA - Setup Telegram
cd /d "%~dp0"

cls
echo.
echo  ================================================================
echo                NOVA Setup Telegram
echo  ================================================================
echo.
echo  Etapes :
echo   1) Telegram - @BotFather - /newbot - recupere le TOKEN
echo   2) Telegram - @userinfobot - recupere ton CHAT ID
echo   3) Colle les 2 valeurs ci-dessous
echo   4) Verifie que tu as bien envoye /start a ton bot
echo.
echo  ================================================================
echo.

python scripts\setup_telegram.py

echo.
echo  ================================================================
pause
