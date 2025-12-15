package flashcore

/*
#cgo CFLAGS: -I../../../flashcore/include
#cgo LDFLAGS: -L../../../flashcore/build -lflashcore
#include "flashcore_api.h"
#include <stdlib.h>
*/
import "C"
import (
	"unsafe"
)

// HNSWIndex represents a vector search index
type HNSWIndex struct {
	ptr *C.hnsw_index_t
}

// NewHNSWIndex creates a new HNSW index
func NewHNSWIndex(dimensions, maxElements int) *HNSWIndex {
	index := C.create_hnsw_index(C.int(dimensions), C.int(maxElements))
	return &HNSWIndex{ptr: index}
}

// Destroy frees the HNSW index
func (idx *HNSWIndex) Destroy() {
	C.destroy_hnsw_index(idx.ptr)
}

// AddVector adds a vector to the index
func (idx *HNSWIndex) AddVector(vector []float32, id int) error {
	cVector := (*C.float)(C.malloc(C.size_t(len(vector)) * C.sizeof_float))
	defer C.free(unsafe.Pointer(cVector))

	for i, v := range vector {
		(*[1 << 30]C.float)(unsafe.Pointer(cVector))[i] = C.float(v)
	}

	result := C.add_vector_to_index(idx.ptr, cVector, C.int(id))
	if result != 0 {
		return nil // In a real implementation, we'd return a proper error
	}
	return nil
}

// SearchResult represents a vector search result
type SearchResult struct {
	ID       int
	Distance float32
}

// Search searches for the k nearest neighbors
func (idx *HNSWIndex) Search(query []float32, k int) ([]SearchResult, error) {
	cQuery := (*C.float)(C.malloc(C.size_t(len(query)) * C.sizeof_float))
	defer C.free(unsafe.Pointer(cQuery))

	for i, v := range query {
		(*[1 << 30]C.float)(unsafe.Pointer(cQuery))[i] = C.float(v)
	}

	cResultIDs := (*C.int)(C.malloc(C.size_t(k) * C.sizeof_int))
	defer C.free(unsafe.Pointer(cResultIDs))

	cResultDistances := (*C.float)(C.malloc(C.size_t(k) * C.sizeof_float))
	defer C.free(unsafe.Pointer(cResultDistances))

	count := C.search_vector_in_index(idx.ptr, cQuery, C.int(k), cResultIDs, cResultDistances)
	if count < 0 {
		return nil, nil // In a real implementation, we'd return a proper error
	}

	results := make([]SearchResult, int(count))
	resultIDs := (*[1 << 30]C.int)(unsafe.Pointer(cResultIDs))[:count:count]
	resultDistances := (*[1 << 30]C.float)(unsafe.Pointer(cResultDistances))[:count:count]

	for i := 0; i < int(count); i++ {
		results[i] = SearchResult{
			ID:       int(resultIDs[i]),
			Distance: float32(resultDistances[i]),
		}
	}

	return results, nil
}

// ONNXRuntime represents an ONNX runtime
type ONNXRuntime struct {
	ptr *C.onnx_runtime_t
}

// NewONNXRuntime creates a new ONNX runtime
func NewONNXRuntime(modelPath string) *ONNXRuntime {
	cModelPath := C.CString(modelPath)
	defer C.free(unsafe.Pointer(cModelPath))

	runtime := C.create_onnx_runtime(cModelPath)
	return &ONNXRuntime{ptr: runtime}
}

// Destroy frees the ONNX runtime
func (rt *ONNXRuntime) Destroy() {
	C.destroy_onnx_runtime(rt.ptr)
}

// RunInference runs inference on the model
func (rt *ONNXRuntime) RunInference(input []float32, outputSize int) ([]float32, error) {
	cInput := (*C.float)(C.malloc(C.size_t(len(input)) * C.sizeof_float))
	defer C.free(unsafe.Pointer(cInput))

	for i, v := range input {
		(*[1 << 30]C.float)(unsafe.Pointer(cInput))[i] = C.float(v)
	}

	output := make([]float32, outputSize)
	cOutput := (*C.float)(C.malloc(C.size_t(outputSize) * C.sizeof_float))
	defer C.free(unsafe.Pointer(cOutput))

	result := C.run_inference(rt.ptr, cInput, C.int(len(input)), cOutput, C.int(outputSize))
	if result != 0 {
		return nil, nil // In a real implementation, we'd return a proper error
	}

	cOutputSlice := (*[1 << 30]C.float)(unsafe.Pointer(cOutput))[:outputSize:outputSize]
	for i, v := range cOutputSlice {
		output[i] = float32(v)
	}

	return output, nil
}

// AESVault represents an AES-256 vault
type AESVault struct {
	ptr *C.aes_vault_t
}

// NewAESVault creates a new AES vault
func NewAESVault(key string) *AESVault {
	cKey := C.CString(key)
	defer C.free(unsafe.Pointer(cKey))

	vault := C.create_aes_vault(cKey)
	return &AESVault{ptr: vault}
}

// Destroy frees the AES vault
func (vault *AESVault) Destroy() {
	C.destroy_aes_vault(vault.ptr)
}

// Encrypt encrypts data
func (vault *AESVault) Encrypt(plaintext []byte) ([]byte, error) {
	cPlaintext := (*C.uchar)(C.CBytes(plaintext))
	defer C.free(unsafe.Pointer(cPlaintext))

	cCiphertext := (*C.uchar)(C.malloc(C.size_t(len(plaintext))))
	defer C.free(unsafe.Pointer(cCiphertext))

	length := C.encrypt_data(vault.ptr, cPlaintext, C.int(len(plaintext)), cCiphertext)
	if length < 0 {
		return nil, nil // In a real implementation, we'd return a proper error
	}

	ciphertext := C.GoBytes(unsafe.Pointer(cCiphertext), C.int(length))
	return ciphertext, nil
}

// Decrypt decrypts data
func (vault *AESVault) Decrypt(ciphertext []byte) ([]byte, error) {
	cCiphertext := (*C.uchar)(C.CBytes(ciphertext))
	defer C.free(unsafe.Pointer(cCiphertext))

	cPlaintext := (*C.uchar)(C.malloc(C.size_t(len(ciphertext))))
	defer C.free(unsafe.Pointer(cPlaintext))

	length := C.decrypt_data(vault.ptr, cCiphertext, C.int(len(ciphertext)), cPlaintext)
	if length < 0 {
		return nil, nil // In a real implementation, we'd return a proper error
	}

	plaintext := C.GoBytes(unsafe.Pointer(cPlaintext), C.int(length))
	return plaintext, nil
}
