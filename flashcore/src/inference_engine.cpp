#include "../include/flashcore_api.h"
#include <iostream>
#include <cstring>

// Simple implementation of ONNX runtime for demonstration purposes
struct onnx_runtime {
    char model_path[256];
};

extern "C" {

onnx_runtime_t* create_onnx_runtime(const char* model_path) {
    onnx_runtime_t* runtime = new onnx_runtime();
    strncpy(runtime->model_path, model_path, sizeof(runtime->model_path) - 1);
    runtime->model_path[sizeof(runtime->model_path) - 1] = '\0';
    std::cout << "Created ONNX runtime with model: " << runtime->model_path << std::endl;
    return runtime;
}

void destroy_onnx_runtime(onnx_runtime_t* runtime) {
    std::cout << "Destroyed ONNX runtime" << std::endl;
    delete runtime;
}

int run_inference(onnx_runtime_t* runtime, float* input_data, int input_size, float* output_data, int output_size) {
    std::cout << "Running inference on model: " << runtime->model_path << std::endl;
    
    // Simple mock inference - just copy input to output for demonstration
    int copy_size = std::min(input_size, output_size);
    for (int i = 0; i < copy_size; ++i) {
        output_data[i] = input_data[i];
    }
    
    // Fill remaining output with zeros
    for (int i = copy_size; i < output_size; ++i) {
        output_data[i] = 0.0f;
    }
    
    return 0; // Success
}

} // extern "C"