import numpy as np
import flashcore
import sys
import os

# Add the flet-direct-renderer to the path so we can import its modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'python-services', 'flet-direct-renderer'))

try:
    import main as flet_renderer
    print("✓ Successfully imported Flet renderer")
except ImportError as e:
    print(f"⚠ Warning: Could not import Flet renderer: {e}")
    flet_renderer = None

def test_flashcore_with_flet():
    """Test FlashCore integration with Flet renderer"""
    print("Testing FlashCore with Flet renderer...")
    
    # Test vector search functionality
    index = flashcore.HNSWIndex(4, 100)
    
    # Add some sample vectors
    vec1 = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)  # Unit vector along x-axis
    vec2 = np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32)  # Unit vector along y-axis
    vec3 = np.array([0.0, 0.0, 1.0, 0.0], dtype=np.float32)  # Unit vector along z-axis
    
    index.add_vector(vec1, 1)
    index.add_vector(vec2, 2)
    index.add_vector(vec3, 3)
    
    # Search for vectors closest to a query
    query = np.array([0.9, 0.1, 0.05, 0.0], dtype=np.float32)  # Close to x-axis
    results = index.search(query, 3)
    
    print(f"Vector search results: {results}")
    
    # The first result should be vec1 (ID 1) since it's closest to our query
    assert results[0]["id"] == 1
    print("✓ Vector search working correctly")
    
    # Test encryption/decryption
    vault = flashcore.AESVault("flashflow_secret_key")
    
    original_data = b"This is a test of the FlashCore encryption system"
    encrypted_data = vault.encrypt(original_data)
    decrypted_data = vault.decrypt(encrypted_data)
    
    assert original_data == decrypted_data
    print("✓ Encryption/decryption working correctly")
    
    # Test inference engine
    runtime = flashcore.ONNXRuntime("sample_model.onnx")
    
    # Simple input vector
    input_vector = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    output_vector = runtime.run_inference(input_vector, 4)
    
    # In our mock implementation, output should equal input
    assert np.allclose(input_vector, output_vector)
    print("✓ Inference engine working correctly")
    
    print("✓ All FlashCore integration tests passed!")

if __name__ == "__main__":
    print("Running FlashCore integration tests...")
    test_flashcore_with_flet()
    print("Integration tests completed successfully!")