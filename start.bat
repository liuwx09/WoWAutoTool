@echo off
echo ====================================
echo WoW Auto Tool Launcher
echo ====================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking dependencies...
pip install -r requirements.txt > nul 2>&1

REM Run
echo Starting WoW Auto Tool...
python main.py

pause
