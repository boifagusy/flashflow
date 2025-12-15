#!/bin/bash

# Create WASM build directory
mkdir -p wasm_build
cd wasm_build

# Compile to WASM using Emscripten
emcc ../src/vector_search.cpp ../src/inference_engine.cpp ../src/vault_security.cpp \
  -I../include \
  -o flashcore.js \
  -s EXPORTED_FUNCTIONS='["_create_hnsw_index", "_destroy_hnsw_index", "_add_vector_to_index", "_search_vector_in_index", "_create_onnx_runtime", "_destroy_onnx_runtime", "_run_inference", "_create_aes_vault", "_destroy_aes_vault", "_encrypt_data", "_decrypt_data"]' \
  -s EXPORTED_RUNTIME_METHODS='["ccall", "cwrap"]' \
  -s MODULARIZE=1 \
  -s EXPORT_NAME="FlashCore" \
  -s ALLOW_MEMORY_GROWTH=1 \
  -s WASM=1 \
  -O3

echo "FlashCore WASM build completed!"