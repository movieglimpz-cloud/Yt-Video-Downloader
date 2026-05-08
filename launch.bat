@echo off
setlocal EnableDelayedExpansion

title YT Downloader Launcher
echo Killing old processes...
taskkill /F /IM python.exe /T >nul 2>&1
echo.

set "PYTHON_EXE=python"
!PYTHON_EXE! --version >nul 2>&1
if %errorlevel% neq 0 (
    set "PYTHON_EXE=%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe"
    !PYTHON_EXE! --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python not found. Please run install.bat first.
        pause
        exit /b 1
    )
)

echo Starting YT Downloader...
start http://localhost:5050
"!PYTHON_EXE!" server.py
pause
