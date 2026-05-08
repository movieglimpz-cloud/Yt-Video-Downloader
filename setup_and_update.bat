@echo off
echo ==============================================
echo  YT Downloader Setup and Update Script
echo ==============================================
echo.

:: Check for Git repository
if exist ".git" (
    echo [INFO] GitHub repository detected.
    echo [INFO] Pulling the latest updates from GitHub...
    git pull
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to pull latest updates. Please check your internet connection or git configuration.
    ) else (
        echo [SUCCESS] Successfully pulled latest updates.
    )
) else (
    echo [INFO] This folder was not downloaded via Git (no .git folder found).
    echo [INFO] Skipping git pull.
)
echo.

:: Install dependencies
echo [INFO] Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install flask flask-cors pytubefix yt-dlp

echo.
echo [INFO] Note: Please ensure 'ffmpeg' is installed on your system for downloading high-quality merged formats.
echo [SUCCESS] Setup and update process complete!
pause
