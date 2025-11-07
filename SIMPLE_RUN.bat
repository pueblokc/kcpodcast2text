@echo off
REM Simple runner - works with Python 3.13

echo ==========================================
echo   Starting Podcast Archive...
echo ==========================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo.
    echo Please run SIMPLE_INSTALL.bat first
    echo.
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Error: Dependencies not installed!
    echo.
    echo Please run SIMPLE_INSTALL.bat first
    echo.
    pause
    exit /b 1
)

REM Run the app
echo Starting Podcast Archive GUI...
echo.
echo Your browser will open automatically at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

python podcast_archive_launcher.py

pause
