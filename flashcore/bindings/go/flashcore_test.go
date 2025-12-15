package flashcore

import (
	"testing"
)

func TestHNSWIndex(t *testing.T) {
	index := NewHNSWIndex(4, 100)
	defer index.Destroy()

	vector := []float32{1.0, 2.0, 3.0, 4.0}
	err := index.AddVector(vector, 1)
	if err != nil {
		t.Errorf("Failed to add vector to index: %v", err)
	}

	query := []float32{1.5, 2.5, 3.5, 4.5}
	results, err := index.Search(query, 1)
	if err != nil {
		t.Errorf("Failed to search index: %v", err)
	}

	if len(results) != 1 {
		t.Errorf("Expected 1 result, got %d", len(results))
	}

	if results[0].ID != 1 {
		t.Errorf("Expected ID 1, got %d", results[0].ID)
	}
}

func TestONNXRuntime(t *testing.T) {
	runtime := NewONNXRuntime("test_model.onnx")
	defer runtime.Destroy()

	input := []float32{1.0, 2.0, 3.0, 4.0}
	output, err := runtime.RunInference(input, 4)
	if err != nil {
		t.Errorf("Failed to run inference: %v", err)
	}

	if len(output) != 4 {
		t.Errorf("Expected output length 4, got %d", len(output))
	}

	// In our mock implementation, output should equal input
	for i, v := range input {
		if output[i] != v {
			t.Errorf("Expected output[%d] = %f, got %f", i, v, output[i])
		}
	}
}

func TestAESVault(t *testing.T) {
	vault := NewAESVault("test_key_12345")
	defer vault.Destroy()

	plaintext := []byte("Hello, FlashCore!")
	ciphertext, err := vault.Encrypt(plaintext)
	if err != nil {
		t.Errorf("Failed to encrypt data: %v", err)
	}

	decrypted, err := vault.Decrypt(ciphertext)
	if err != nil {
		t.Errorf("Failed to decrypt data: %v", err)
	}

	if string(decrypted) != string(plaintext) {
		t.Errorf("Decrypted text doesn't match original: got %s, want %s", string(decrypted), string(plaintext))
	}
}
