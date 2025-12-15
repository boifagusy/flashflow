@echo off

REM Install dependencies
pip install -r requirements.txt

REM Build the Python bindings
python setup.py build_ext --inplace

REM Run tests
python test_flashcore.py

echo FlashCore Python bindings build and test completed!