@echo off
setlocal EnableDelayedExpansion

title YT Downloader - Full Setup

echo ==============================================
echo   YT Video Downloader - FULL A-Z SETUP
echo ==============================================
echo.
echo This script will install Python, FFmpeg, and all required packages.
echo Please ensure you have an active internet connection.
echo.

:: 1. Check for Python
echo [1/3] Checking for Python...
set "PYTHON_EXE=python"
!PYTHON_EXE! --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Python not found in PATH. Checking common installation paths...
    set "PYTHON_EXE=%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe"
    if not exist "!PYTHON_EXE!" (
        echo [INFO] Python is not installed. Downloading Python 3.11...
        curl -L -o python_installer.exe https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
        if %errorlevel% neq 0 (
            echo [ERROR] Failed to download Python. Please check your internet connection.
            pause
            exit /b 1
        )
        echo [INFO] Installing Python silently (this may take a minute)...
        start /wait python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
        echo [SUCCESS] Python installed.
        del python_installer.exe
    )
)

:: Re-verify Python
!PYTHON_EXE! --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python installation could not be verified. 
    echo Please close this window, open a new one, and try again, or install Python manually.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%a in ('!PYTHON_EXE! --version') do set PY_VER=%%a
    echo [SUCCESS] Found !PY_VER!
)
echo.

:: 2. Check for FFmpeg
echo [2/3] Checking for FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    if exist "ffmpeg.exe" (
        echo [SUCCESS] FFmpeg found in current directory.
    ) else (
        echo [INFO] FFmpeg not found in PATH. Downloading FFmpeg...
        curl -L -o ffmpeg.zip https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
        if %errorlevel% neq 0 (
            echo [ERROR] Failed to download FFmpeg.
            pause
            exit /b 1
        )
        echo [INFO] Extracting FFmpeg (this might take a moment)...
        powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath 'ffmpeg_temp' -Force"
        echo [INFO] Moving FFmpeg binaries...
        move /Y "ffmpeg_temp\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe" . >nul
        move /Y "ffmpeg_temp\ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe" . >nul
        echo [INFO] Cleaning up...
        rmdir /S /Q "ffmpeg_temp"
        del /Q "ffmpeg.zip"
        echo [SUCCESS] FFmpeg installed locally.
    )
) else (
    echo [SUCCESS] FFmpeg is already installed in PATH.
)
echo.

:: 3. Install Python Dependencies
echo [3/3] Installing Python dependencies...
!PYTHON_EXE! -m pip install --upgrade pip --quiet
!PYTHON_EXE! -m pip install flask flask-cors pytubefix yt-dlp --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install some Python packages.
    pause
    exit /b 1
)
echo [SUCCESS] Python dependencies installed successfully!
echo.

:: 4. Create Directories
echo [SETUP] Creating required directories...
if not exist "YTDownloader" mkdir YTDownloader
if not exist "Downloads" mkdir Downloads

echo.
echo ==============================================
echo   Setup Complete!
echo ==============================================
echo You can now run 'launch.bat' to start the application.
echo.
pause
