@echo off
REM Build script for FlashCore and FlashFlow integration

echo ========================================
echo Building FlashCore and FlashFlow Integration
echo ========================================

REM Build FlashCore C++ library
echo.
echo [1/3] Building FlashCore C++ library...
cd flashcore
if not exist build mkdir build
cd build
cmake ..
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: CMake configuration failed
    exit /b 1
)
cmake --build .
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: C++ build failed
    exit /b 1
)
cd ..\..

REM Build FlashCore Python bindings
echo.
echo [2/3] Building FlashCore Python bindings...
cd flashcore\bindings\python
python setup.py build_ext --inplace
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python bindings build failed
    exit /b 1
)
cd ..\..\..

REM Build FlashCore Go service
echo.
echo [3/3] Building FlashCore Go service...
cd go-services\flashcore-service
go build -o flashcore-service.exe main.go
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Go service build failed
    exit /b 1
)
cd ..\..

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo To run the FlashCore service:
echo   cd go-services\flashcore-service
echo   .\flashcore-service.exe
echo.
echo To run the FlashFlow test project:
echo   cd test-projects\flashcore-test
echo   python ..\..\python-services\flet-direct-renderer\main.py .
echo.