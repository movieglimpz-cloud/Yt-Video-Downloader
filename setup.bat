@echo off
echo ==============================================
echo   YT Video Downloader - Full Setup
echo ==============================================
echo.

:: Check if running as administrator (not required, but helpful info)
net session >nul 2>&1
if %errorlevel% == 0 (
    echo [INFO] Running with administrator privileges.
) else (
    echo [INFO] Running without administrator privileges (normal mode).
)
echo.

:: Check if Python is installed
echo [CHECK] Checking for Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo [INFO] Please download and install Python from https://python.org
    echo [INFO] Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
for /f "tokens=*" %%a in ('python --version') do set PYTHON_VERSION=%%a
echo [SUCCESS] Found %PYTHON_VERSION%
echo.

:: Check if pip is available
echo [CHECK] Checking for pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not installed.
    echo [INFO] Please reinstall Python and make sure pip is included.
    pause
    exit /b 1
)
echo [SUCCESS] pip is available
echo.

:: Upgrade pip first
echo [STEP 1/5] Upgrading pip...
python -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Could not upgrade pip, continuing with current version...
) else (
    echo [SUCCESS] pip upgraded successfully
echo.

:: Install Flask
echo [STEP 2/5] Installing Flask...
python -m pip install flask --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Flask.
    pause
    exit /b 1
)
echo [SUCCESS] Flask installed
echo.

:: Install Flask-CORS
echo [STEP 3/5] Installing Flask-CORS...
python -m pip install flask-cors --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Flask-CORS.
    pause
    exit /b 1
)
echo [SUCCESS] Flask-CORS installed
echo.

:: Install pytubefix
echo [STEP 4/5] Installing pytubefix...
python -m pip install pytubefix --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install pytubefix.
    pause
    exit /b 1
)
echo [SUCCESS] pytubefix installed
echo.

:: Install yt-dlp
echo [STEP 5/5] Installing yt-dlp...
python -m pip install yt-dlp --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install yt-dlp.
    pause
    exit /b 1
)
echo [SUCCESS] yt-dlp installed
echo.

:: Create necessary directories
echo [SETUP] Creating necessary directories...
if not exist "YTDownloader" mkdir YTDownloader
if not exist "Downloads" mkdir Downloads
echo [SUCCESS] Directories created
echo.

:: Check for ffmpeg (optional but recommended)
echo [CHECK] Checking for ffmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] ffmpeg is not found in PATH.
    echo [INFO] ffmpeg is recommended for high-quality video downloads.
    echo [INFO] You can download it from: https://ffmpeg.org/download.html
) else (
    echo [SUCCESS] ffmpeg is available
echo.

:: Summary
echo ==============================================
echo   Setup Complete!
echo ==============================================
echo.
echo All dependencies have been installed successfully:
echo   - Flask
echo   - Flask-CORS
echo   - pytubefix
echo   - yt-dlp
echo.
echo To start the application:
echo   1. Run: launch.bat
echo   2. Or run: python server.py
echo.
echo The server will start at: http://localhost:5000
echo.
pause
