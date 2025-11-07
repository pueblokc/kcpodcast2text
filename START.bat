@echo off
REM Quick launcher for Windows

echo Starting Podcast Archive...

REM Check if venv exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

python podcast_archive_launcher.py

pause
