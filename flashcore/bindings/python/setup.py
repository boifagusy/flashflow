from setuptools import setup, Extension
import pybind11

# Define the extension module
flashcore_module = Extension(
    'flashcore',
    sources=[
        '../../src/vector_search.cpp',
        '../../src/inference_engine.cpp',
        '../../src/vault_security.cpp',
        'pybind11_bindings.cpp'
    ],
    include_dirs=[
        '../../include',
        pybind11.get_include(),
        pybind11.get_include(user=True)
    ],
    language='c++',
    cxx_std=17,
)

# Setup configuration
setup(
    name='flashcore',
    version='1.0.0',
    author='FlashFlow Team',
    description='Python bindings for FlashCore C++ library',
    ext_modules=[flashcore_module],
    setup_requires=['pybind11>=2.5.0'],
    zip_safe=False,
)