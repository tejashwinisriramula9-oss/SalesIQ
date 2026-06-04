@echo off
REM SalesIQ - Quick Start Guide for Windows
REM Run this script to get SalesIQ up and running

cls
echo.
echo ============================================================
echo           SalesIQ - Quick Start Setup Script
echo      Enterprise Business Intelligence Platform v1.0.0
echo ============================================================
echo.

REM Step 1: Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python not found. Please install Python 3.9+
    pause
    exit /b 1
)
python --version
echo * Python found
echo.

REM Step 2: Create Virtual Environment
echo [2/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo * Virtual environment created
) else (
    echo * Virtual environment already exists
)
echo.

REM Step 3: Activate Virtual Environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo * Virtual environment activated
echo.

REM Step 4: Install Dependencies
echo [4/5] Installing dependencies...
pip install -r requirements.txt
echo * Dependencies installed
echo.

REM Step 5: Verify Setup
echo [5/5] Verifying setup...
python verify_setup.py
echo.

echo ============================================================
echo           SUCCESS - SalesIQ is ready to run!
echo.
echo   Run the following command to start:
echo.
echo   streamlit run app.py
echo.
echo   The app will open at: http://localhost:8501
echo ============================================================
echo.
pause
