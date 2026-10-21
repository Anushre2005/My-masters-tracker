@echo off
rem Start Masters Tracker with a console window (useful for seeing errors).
cd /d "%~dp0"
".venv\Scripts\python.exe" main.py %*
