@echo off
REM Install script for Behavioral Authentication System

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  AI-Based Behavioral Authentication System - Setup Wizard      ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python detected
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: pip is not available
    echo Please reinstall Python with pip included
    pause
    exit /b 1
)

echo ✅ pip is available
echo.

REM Install requirements
echo 📦 Installing required packages...
echo This may take 1-2 minutes...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo ✅ Installation completed successfully!
echo.
echo 📚 Next steps:
echo.
echo   1. Run Quick Demo:
echo      python quick_start.py
echo.
echo   2. Launch Main Application:
echo      python main_app.py
echo.
echo   3. View Examples:
echo      python examples.py
echo.
echo   4. Run Tests:
echo      python test_suite.py
echo.
echo.
echo 📖 Documentation:
echo   - README.md: Complete documentation
echo   - API_REFERENCE.md: Full API reference
echo   - QUICKSTART.txt: Getting started guide
echo.
pause
