@echo off
title Terraria Installer Builder
cls

echo ========================================
echo       Terraria Auto-Installer Builder
echo ========================================
echo.

REM 1. Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8+ and add to PATH.
    pause
    exit /b 1
)

REM 2. Install Requirements
echo [1/3] Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b 1
)

REM 3. Check Files
echo.
echo [2/3] Checking files...
if not exist "terraria_installer.spec" (
    echo [ERROR] File 'terraria_installer.spec' not found!
    pause
    exit /b 1
)

if not exist "banner.jpg" (
    echo [ERROR] File 'banner.jpg' not found!
    pause
    exit /b 1
)

REM 4. Build
echo.
echo [3/3] Building EXE...
pyinstaller terraria_installer.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo [ERROR] Build Failed! Check the log above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [SUCCESS] BUILD COMPLETE!
echo ========================================
echo.
echo File location: dist\Calamity_Ultra_Installer.exe
echo.
pause