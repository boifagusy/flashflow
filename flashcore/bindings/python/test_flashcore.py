import numpy as np
import flashcore

def test_hnsw_index():
    """Test the HNSW index functionality"""
    print("Testing HNSW Index...")
    
    # Create index
    index = flashcore.HNSWIndex(4, 100)
    
    # Add vectors
    vec1 = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    vec2 = np.array([2.0, 3.0, 4.0, 5.0], dtype=np.float32)
    vec3 = np.array([3.0, 4.0, 5.0, 6.0], dtype=np.float32)
    
    index.add_vector(vec1, 1)
    index.add_vector(vec2, 2)
    index.add_vector(vec3, 3)
    
    # Search
    query = np.array([1.5, 2.5, 3.5, 4.5], dtype=np.float32)
    results = index.search(query, 3)
    
    print(f"Search results: {results}")
    assert len(results) == 3
    assert results[0]["id"] == 2  # vec2 should be closest to query
    
    print("✓ HNSW Index tests passed!")

def test_onnx_runtime():
    """Test the ONNX runtime functionality"""
    print("Testing ONNX Runtime...")
    
    # Create runtime
    runtime = flashcore.ONNXRuntime("test_model.onnx")
    
    # Run inference
    input_data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    output_data = runtime.run_inference(input_data, 4)
    
    print(f"Input: {input_data}")
    print(f"Output: {output_data}")
    
    # In our mock implementation, output should equal input
    assert np.allclose(input_data, output_data)
    
    print("✓ ONNX Runtime tests passed!")

def test_aes_vault():
    """Test the AES vault functionality"""
    print("Testing AES Vault...")
    
    # Create vault
    vault = flashcore.AESVault("test_key_12345")
    
    # Encrypt data
    plaintext = b"Hello, FlashCore!"
    ciphertext = vault.encrypt(plaintext)
    
    # Decrypt data
    decrypted = vault.decrypt(ciphertext)
    
    print(f"Original: {plaintext}")
    print(f"Encrypted: {ciphertext}")
    print(f"Decrypted: {decrypted}")
    
    # In our mock implementation, decrypted should equal original
    assert decrypted == plaintext
    
    print("✓ AES Vault tests passed!")

if __name__ == "__main__":
    print("Running FlashCore Python bindings tests...")
    test_hnsw_index()
    test_onnx_runtime()
    test_aes_vault()
    print("All tests passed!")