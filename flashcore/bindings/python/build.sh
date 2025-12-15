#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Build the Python bindings
python setup.py build_ext --inplace

# Run tests
python test_flashcore.py

echo "FlashCore Python bindings build and test completed!"