@echo off
REM Build script for Windows executable using PyInstaller

echo ==========================================
echo   Podcast Archive - Windows Build Script
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.11
    echo Download: https://www.python.org/downloads/release/python-3119/
    pause
    exit /b 1
)

echo Python found:
python --version

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo Detected: %PYVER%
echo.

REM Warn if Python 3.13
echo %PYVER% | findstr /C:"3.13" >nul
if not errorlevel 1 (
    echo ==========================================
    echo   WARNING: Python 3.13 Detected!
    echo ==========================================
    echo.
    echo Python 3.13 is too new! PyInstaller doesn't support it yet.
    echo.
    echo SOLUTION:
    echo 1. Install Python 3.11 from:
    echo    https://www.python.org/downloads/release/python-3119/
    echo 2. Run: py -3.11 build_windows.bat
    echo.
    echo OR use SIMPLE_INSTALL.bat to run without building exe
    echo.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv-build" (
    echo Creating build environment...
    python -m venv venv-build
    if errorlevel 1 (
        echo Error creating virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating build environment...
call venv-build\Scripts\activate.bat

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

REM Install dependencies
echo Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Try: pip install fastapi uvicorn streamlit sqlalchemy aiosqlite
    pause
    exit /b 1
)

pip install -r requirements-build.txt
if errorlevel 1 (
    echo Warning: Build dependencies failed, installing PyInstaller directly...
    pip install pyinstaller
)

REM Download NLTK data
echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Build executable
echo.
echo Building Windows executable...
echo This may take 5-10 minutes...
echo.

pyinstaller ^
    --name "PodcastArchive" ^
    --onefile ^
    --windowed ^
    --add-data "frontend;frontend" ^
    --add-data ".env.example;." ^
    --hidden-import "streamlit" ^
    --hidden-import "backend" ^
    --hidden-import "sklearn.utils._cython_blas" ^
    --hidden-import "sklearn.neighbors.typedefs" ^
    --hidden-import "sklearn.tree._utils" ^
    --hidden-import "uvicorn.logging" ^
    --hidden-import "uvicorn.loops.auto" ^
    --hidden-import "uvicorn.protocols.http.auto" ^
    --collect-all "streamlit" ^
    --collect-all "nltk" ^
    --collect-all "whisper" ^
    podcast_archive_launcher.py

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo   Build successful!
    echo ==========================================
    echo.
    echo Executable location: dist\PodcastArchive.exe
    echo.
    echo To run:
    echo   Double-click dist\PodcastArchive.exe
    echo.

    REM Create distribution folder
    if not exist "distribution" mkdir distribution
    copy dist\PodcastArchive.exe distribution\
    copy .env.example distribution\
    copy README.md distribution\
    copy QUICKSTART.md distribution\

    echo Distribution package created in: distribution\
    echo.
) else (
    echo.
    echo Build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

pause
