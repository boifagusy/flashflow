@echo off
echo Building Direct Renderer...
go build -o direct-renderer.exe main.go
if %errorlevel% == 0 (
    echo Build successful!
    dir direct-renderer.exe
) else (
    echo Build failed with error level %errorlevel%
)