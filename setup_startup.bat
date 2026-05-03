@echo off
set "SCRIPT_PATH=%~dp0run_background.vbs"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_NAME=YTDownloader.lnk"

echo Setting up Auto-Startup for YT Downloader...
echo Script Path: %SCRIPT_PATH%

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTUP_DIR%\%SHORTCUT_NAME%'); $Shortcut.TargetPath = 'wscript.exe'; $Shortcut.Arguments = '\"%SCRIPT_PATH%\"'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save()"

echo Done! The downloader will now run automatically in the background when you log in.
echo.
echo Running it now for the first time...
wscript.exe "%SCRIPT_PATH%"
echo Successfully started in background.
pause
