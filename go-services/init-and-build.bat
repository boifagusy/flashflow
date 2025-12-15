@echo off
echo Initializing and building all FlashFlow Go services...

REM Initialize and build build-service
echo.
echo === Building build-service ===
cd build-service
go mod tidy
if %ERRORLEVEL% EQU 0 (
    go build -o build-service.exe
    if %ERRORLEVEL% EQU 0 (
        echo Successfully built build-service
    ) else (
        echo Failed to build build-service
    )
) else (
    echo Failed to initialize build-service dependencies
)
cd ..

REM Initialize and build dev-server
echo.
echo === Building dev-server ===
cd dev-server
go mod tidy
if %ERRORLEVEL% EQU 0 (
    go build -o dev-server.exe
    if %ERRORLEVEL% EQU 0 (
        echo Successfully built dev-server
    ) else (
        echo Failed to build dev-server
    )
) else (
    echo Failed to initialize dev-server dependencies
)
cd ..

REM Initialize and build file-watcher
echo.
echo === Building file-watcher ===
cd file-watcher
go mod tidy
if %ERRORLEVEL% EQU 0 (
    go build -o file-watcher.exe
    if %ERRORLEVEL% EQU 0 (
        echo Successfully built file-watcher
    ) else (
        echo Failed to build file-watcher
    )
) else (
    echo Failed to initialize file-watcher dependencies
)
cd ..

REM Initialize and build cli-wrapper
echo.
echo === Building cli-wrapper ===
cd cli-wrapper
go mod tidy
if %ERRORLEVEL% EQU 0 (
    go build -o flashflow-go.exe
    if %ERRORLEVEL% EQU 0 (
        echo Successfully built cli-wrapper
    ) else (
        echo Failed to build cli-wrapper
    )
) else (
    echo Failed to initialize cli-wrapper dependencies
)
cd ..

echo.
echo All services processed!
pause