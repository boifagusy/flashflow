#include "../include/flashcore_api.h"
#include <iostream>
#include <cassert>
#include <cmath>

int main() {
    std::cout << "Testing Inference Engine Module..." << std::endl;
    
    // Create ONNX runtime
    onnx_runtime_t* runtime = create_onnx_runtime("test_model.onnx");
    assert(runtime != nullptr);
    std::cout << "✓ Created ONNX runtime" << std::endl;
    
    // Run inference
    float input[] = {1.0f, 2.0f, 3.0f, 4.0f};
    float output[4];
    
    int result = run_inference(runtime, input, 4, output, 4);
    assert(result == 0);
    std::cout << "✓ Ran inference" << std::endl;
    
    // Check results (input should be copied to output in our mock implementation)
    for (int i = 0; i < 4; ++i) {
        assert(std::abs(output[i] - input[i]) < 1e-6);
    }
    std::cout << "✓ Inference returned correct results" << std::endl;
    
    // Clean up
    destroy_onnx_runtime(runtime);
    std::cout << "✓ Destroyed ONNX runtime" << std::endl;
    
    std::cout << "All Inference Engine tests passed!" << std::endl;
    return 0;
}