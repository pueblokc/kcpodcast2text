@echo off
REM Check Python version compatibility

echo ==========================================
echo   Python Version Checker
echo ==========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found!
    echo.
    echo Please install Python from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Checking Python version...
python --version

REM Get version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo.
echo Detected version: %PYVER%
echo.

REM Check if 3.13
echo %PYVER% | findstr /C:"3.13" >nul
if not errorlevel 1 (
    echo ==========================================
    echo   Python 3.13 Detected
    echo ==========================================
    echo.
    echo [!] Python 3.13 is TOO NEW for building executables
    echo.
    echo What works:
    echo   [OK] Running the app directly: python run_gui.py
    echo   [OK] Using SIMPLE_INSTALL.bat and SIMPLE_RUN.bat
    echo.
    echo What doesn't work:
    echo   [X] Building .exe file with PyInstaller
    echo   [X] Some packages may have issues
    echo.
    echo RECOMMENDATION:
    echo   For building exe: Install Python 3.11
    echo   Download: https://www.python.org/downloads/release/python-3119/
    echo.
    echo   For just running: Use SIMPLE_INSTALL.bat
    echo.
    goto end
)

REM Check if 3.11
echo %PYVER% | findstr /C:"3.11" >nul
if not errorlevel 1 (
    echo ==========================================
    echo   Perfect! Python 3.11 - RECOMMENDED
    echo ==========================================
    echo.
    echo [OK] This version is perfect!
    echo [OK] Can run the app directly
    echo [OK] Can build .exe files
    echo [OK] All packages supported
    echo.
    echo You can use:
    echo   - build_windows.bat (to create exe)
    echo   - SIMPLE_INSTALL.bat then SIMPLE_RUN.bat
    echo   - python run_gui.py
    echo.
    goto end
)

REM Check if 3.10 or 3.12
echo %PYVER% | findstr /C:"3.10 3.12" >nul
if not errorlevel 1 (
    echo ==========================================
    echo   Good! Python 3.10/3.12 - Compatible
    echo ==========================================
    echo.
    echo [OK] This version should work fine
    echo [OK] Can run the app
    echo [OK] Can probably build .exe
    echo.
    echo You can use:
    echo   - build_windows.bat (to create exe)
    echo   - SIMPLE_INSTALL.bat then SIMPLE_RUN.bat
    echo   - python run_gui.py
    echo.
    goto end
)

REM Other version
echo ==========================================
echo   Unknown Version
echo ==========================================
echo.
echo [?] This Python version may work, but is untested
echo.
echo Recommended: Python 3.11
echo Download: https://www.python.org/downloads/release/python-3119/
echo.

:end
pause
