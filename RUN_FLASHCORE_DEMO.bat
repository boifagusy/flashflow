@echo off
REM Script to run the FlashCore demo with FlashFlow

echo ========================================
echo FlashCore Demo with FlashFlow
echo ========================================

REM Check if FlashCore is built
if not exist flashcore\build\flashcore.dll (
    echo FlashCore not built. Building now...
    call build-flashcore.bat
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to build FlashCore
        exit /b 1
    )
)

REM Check if Python bindings are built
if not exist flashcore\bindings\python\flashcore.cp39-win_amd64.pyd (
    echo Python bindings not built. Building now...
    cd flashcore\bindings\python
    python setup.py build_ext --inplace
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to build Python bindings
        exit /b 1
    )
    cd ..\..\..
)

REM Run the test suite
echo.
echo Running FlashCore integration tests...
python test-flashcore.py

echo.
echo Starting FlashFlow test project with FlashCore integration...
cd test-projects\flashcore-test
python ..\..\python-services\flet-direct-renderer\main.py .

echo.
echo To view the demo:
echo 1. Open your browser
echo 2. Navigate to http://localhost:8013
echo 3. Click "View FlashCore Demo" to see FlashCore in action