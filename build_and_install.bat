@echo off
rem Rebuild MastersTracker.exe from source and reinstall it (Start Menu + Desktop shortcut).
cd /d "%~dp0"
".venv\Scripts\pyinstaller.exe" --noconfirm --clean --windowed --name MastersTracker --icon app.ico ^
  --add-data "tracker/static;tracker/static" --add-data "tracker/ocr.ps1;tracker" --collect-all webview --hidden-import winotify --hidden-import pystray._win32 --hidden-import segno main.py
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
pause
