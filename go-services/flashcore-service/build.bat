@echo off
REM Build script for FlashCore service

REM Build the FlashCore C++ library first
echo Building FlashCore C++ library...
cd ..\..\flashcore
if not exist build mkdir build
cd build
cmake ..
cmake --build .

REM Return to FlashCore service directory
cd ..\..\go-services\flashcore-service

REM Build the Go service
echo Building FlashCore Go service...
go build -o flashcore-service.exe main.go

echo FlashCore service build completed!