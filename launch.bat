@echo off
title YT Downloader Launcher
echo Killing old processes...
taskkill /F /IM python.exe /T >nul 2>&1
echo.
echo Starting YT Downloader...
start http://localhost:5050
python server.py
pause
