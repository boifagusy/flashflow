#!/usr/bin/env python3
"""
Test script for FlashCore integration with FlashFlow
"""

import sys
import os
import numpy as np

# Add the FlashCore bindings to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'flashcore', 'bindings', 'python'))

def test_flashcore_import():
    """Test importing FlashCore"""
    try:
        import flashcore
        print("✓ FlashCore Python bindings imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import FlashCore: {e}")
        return False

def test_vector_search():
    """Test FlashCore vector search functionality"""
    try:
        import flashcore
        
        # Create HNSW index
        index = flashcore.HNSWIndex(4, 100)
        print("✓ HNSW index created")
        
        # Add vectors
        vec1 = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
        vec2 = np.array([2.0, 3.0, 4.0, 5.0], dtype=np.float32)
        
        index.add_vector(vec1, 1)
        index.add_vector(vec2, 2)
        print("✓ Vectors added to index")
        
        # Search
        query = np.array([1.5, 2.5, 3.5, 4.5], dtype=np.float32)
        results = index.search(query, 2)
        print(f"✓ Vector search completed, found {len(results)} results")
        
        return True
    except Exception as e:
        print(f"✗ Vector search test failed: {e}")
        return False

def test_inference_engine():
    """Test FlashCore inference engine"""
    try:
        import flashcore
        
        # Create ONNX runtime
        runtime = flashcore.ONNXRuntime("test_model.onnx")
        print("✓ ONNX runtime created")
        
        # Run inference
        input_data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
        output_data = runtime.run_inference(input_data, 4)
        print("✓ Inference completed")
        
        return True
    except Exception as e:
        print(f"✗ Inference engine test failed: {e}")
        return False

def test_encryption():
    """Test FlashCore encryption"""
    try:
        import flashcore
        
        # Create AES vault
        vault = flashcore.AESVault("test_key_12345")
        print("✓ AES vault created")
        
        # Encrypt/decrypt
        plaintext = b"Hello, FlashCore!"
        ciphertext = vault.encrypt(plaintext)
        decrypted = vault.decrypt(ciphertext)
        
        if plaintext == decrypted:
            print("✓ Encryption/decryption successful")
            return True
        else:
            print("✗ Encryption/decryption failed: data mismatch")
            return False
    except Exception as e:
        print(f"✗ Encryption test failed: {e}")
        return False

def main():
    """Main test function"""
    print("========================================")
    print("Testing FlashCore Integration")
    print("========================================")
    
    tests = [
        ("Import Test", test_flashcore_import),
        ("Vector Search Test", test_vector_search),
        ("Inference Engine Test", test_inference_engine),
        ("Encryption Test", test_encryption)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n{name}:")
        if test_func():
            passed += 1
    
    print("\n========================================")
    print(f"Test Results: {passed}/{total} tests passed")
    if passed == total:
        print("All tests passed! FlashCore integration is working correctly.")
    else:
        print("Some tests failed. Please check the errors above.")
    print("========================================")

if __name__ == "__main__":
    main()