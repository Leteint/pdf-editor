@echo off
setlocal EnableDelayedExpansion

echo ============================================================
echo   PDF Editor - Build + Installer
echo ============================================================
echo.

:: Configuration
set APP_NAME=PDFEditor
set APP_VERSION=1.0.0
set DIST_DIR=dist\%APP_NAME%
set SPEC_FILE=build.spec
set ISS_FILE=installer\PDF_Editor.iss

:: Tesseract (leave empty to skip bundling)
set TESSERACT_DIR=C:\Program Files\Tesseract-OCR

:: Path to iscc.exe (Inno Setup compiler)
set ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
if not exist "%ISCC%" set ISCC=C:\Program Files\Inno Setup 6\ISCC.exe

:: Step 1: check Python and PyInstaller
echo [1/4] Checking prerequisites...

python --version >/dev/null 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH.
    pause
    exit /b 1
)

python -m PyInstaller --version >/dev/null 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: pip install pyinstaller failed.
        pause
        exit /b 1
    )
)

echo    OK - Python and PyInstaller ready.
echo.

:: Step 2: install dependencies
echo [2/4] Installing dependencies from requirements.txt...
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo WARNING: Some dependencies may have failed to install.
)
echo    OK
echo.

:: Step 3: PyInstaller build
echo [3/4] Building application with PyInstaller...
echo        (this may take several minutes)
echo.

if exist "build\%APP_NAME%" rmdir /s /q "build\%APP_NAME%"
if exist "%DIST_DIR%"       rmdir /s /q "%DIST_DIR%"

python -m PyInstaller %SPEC_FILE% --noconfirm --clean
if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed. See output above.
    pause
    exit /b 1
)

echo.
echo    Build succeeded: %DIST_DIR%
echo.

:: Step 4: Inno Setup installer
echo [4/4] Creating installer with Inno Setup...

if not exist "%ISCC%" (
    echo    Inno Setup not found at: %ISCC%
    echo    Download from https://jrsoftware.org/isdl.php
    echo    Portable application ready in: %DIST_DIR%
    goto :done
)

"%ISCC%" "%ISS_FILE%"
if errorlevel 1 (
    echo ERROR: Inno Setup compilation failed.
    pause
    exit /b 1
)

echo.
echo    Installer created: installer\%APP_NAME%-%APP_VERSION%-Setup.exe

:done
echo.
echo ============================================================
echo   Done!
echo.
echo   Portable app : %DIST_DIR%\%APP_NAME%.exe
if exist "installer\%APP_NAME%-%APP_VERSION%-Setup.exe" (
    echo   Installer    : installer\%APP_NAME%-%APP_VERSION%-Setup.exe
)
echo ============================================================
echo.
pause
