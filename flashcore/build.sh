#!/bin/bash

# Create build directory
mkdir -p build
cd build

# Configure with CMake
cmake ..

# Build the project
make

# Run tests
ctest --verbose

echo "FlashCore build and test completed!"