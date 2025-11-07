@echo off
REM One-click installer for Windows

echo ==========================================
echo   Podcast Archive - Windows Installer
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not installed!
    echo.
    echo Please install Python 3.10+ from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH"
    pause
    exit /b 1
)

echo [1/4] Python found
python --version

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing pip...
    python -m ensurepip --upgrade
)

echo [2/4] Installing dependencies...
pip install -q --upgrade pip
pip install -r requirements.txt

echo [3/4] Downloading NLTK data...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"

echo [4/4] Initializing database...
python scripts\init_db.py

echo.
echo ==========================================
echo   Installation Complete!
echo ==========================================
echo.
echo To start the application, run:
echo   python run_gui.py
echo.
echo Or double-click: run_gui.py
echo.
pause
