@echo off
REM Simple installer that works with any Python version (including 3.13)
REM This won't create an exe, but will let you run the app

echo ==========================================
echo   Podcast Archive - Simple Installer
echo   (Works with Python 3.13)
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not installed!
    echo.
    echo Please install Python from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/5] Python found
python --version

REM Create venv
echo [2/5] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists, using existing one
) else (
    python -m venv venv
    if errorlevel 1 (
        echo Error creating virtual environment
        pause
        exit /b 1
    )
)

REM Activate venv
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

REM Install core dependencies (skip problematic ones for Python 3.13)
echo [5/5] Installing dependencies (this may take a few minutes)...
echo.

echo Installing FastAPI and Streamlit...
pip install fastapi uvicorn[standard] streamlit pydantic pydantic-settings python-multipart

echo Installing database...
pip install sqlalchemy aiosqlite

echo Installing audio processing...
pip install pydub soundfile

echo Installing NLP (this may take a while)...
pip install nltk scikit-learn

echo Installing utilities...
pip install python-dotenv httpx tqdm click watchdog fpdf2

echo Installing AI models (optional, can skip if issues)...
pip install openai-whisper transformers torch --index-url https://download.pytorch.org/whl/cpu

echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)" 2>nul

echo Initializing database...
python scripts\init_db.py 2>nul

echo.
echo ==========================================
echo   Installation Complete!
echo ==========================================
echo.
echo To run the app:
echo   1. Run: START.bat
echo   2. Or: python run_gui.py
echo.
echo Your browser will open at: http://localhost:8501
echo.
pause
