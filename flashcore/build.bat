@echo off

REM Create build directory
mkdir build
cd build

REM Configure with CMake
cmake ..

REM Build the project
cmake --build .

REM Run tests
ctest --verbose

echo FlashCore build and test completed!