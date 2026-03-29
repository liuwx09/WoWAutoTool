@echo off
setlocal enabledelayedexpansion

echo ====================================
echo WoW Auto Tool - One-File Build
echo ====================================
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Install dependencies if needed
echo Checking dependencies...
pip install opencv-python numpy mss pydirectinput PyQt5 Pillow pywin32 pyinstaller --quiet 2>nul

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Create directories that need to be included
if not exist "images" mkdir images
if not exist "scripts" mkdir scripts
if not exist "logs" mkdir logs

REM Build one-file executable
echo.
echo Building one-file executable...
echo This may take several minutes...
echo.

pyinstaller --onefile --console=false --name WoWAutoTool --add-data "images;images" --add-data "scripts;scripts" --add-data "config.json;." main.py

echo.
echo ====================================
if exist "dist\WoWAutoTool.exe" (
    echo Build SUCCESSFUL!
    echo.
    echo Executable location:
    echo %SCRIPT_DIR%dist\WoWAutoTool.exe
    echo.
    echo NOTE: This is a single executable but requires
    echo the images/ and scripts/ folders to be present!
    echo.
    echo Would you like to open the output folder?
    choice /c YN /n /t 5 /d Y
    if !errorlevel! == 1 (
        explorer "dist"
    )
) else (
    echo Build FAILED!
    echo Check the output above for errors.
)
echo ====================================

pause
