cmake_minimum_required(VERSION 3.10)
project(FlashCore VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Compiler flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -Wall -Wextra")

# Include directories
include_directories(include)

# Source files
set(SOURCES
    src/vector_search.cpp
    src/inference_engine.cpp
    src/vault_security.cpp
)

# Create shared library
add_library(flashcore SHARED ${SOURCES})

# Link required libraries (these would need to be installed)
# find_package(ONNXRuntime REQUIRED)
# target_link_libraries(flashcore PRIVATE onnxruntime)

# Create static library
add_library(flashcore_static STATIC ${SOURCES})

# Tests
enable_testing()
add_subdirectory(tests)

# Installation
install(TARGETS flashcore flashcore_static
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

install(DIRECTORY include/
    DESTINATION include
    FILES_MATCHING PATTERN "*.h"
)