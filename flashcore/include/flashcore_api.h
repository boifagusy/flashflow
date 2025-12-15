#ifndef FLASHCORE_API_H
#define FLASHCORE_API_H

#ifdef __cplusplus
extern "C" {
#endif

// Vector Search (HNSW Index) Functions
typedef struct hnsw_index hnsw_index_t;

hnsw_index_t* create_hnsw_index(int dimensions, int max_elements);
void destroy_hnsw_index(hnsw_index_t* index);
int add_vector_to_index(hnsw_index_t* index, float* vector, int id);
int search_vector_in_index(hnsw_index_t* index, float* query_vector, int k, int* result_ids, float* result_distances);

// Native Inference Engine (ONNX Runtime) Functions
typedef struct onnx_runtime onnx_runtime_t;

onnx_runtime_t* create_onnx_runtime(const char* model_path);
void destroy_onnx_runtime(onnx_runtime_t* runtime);
int run_inference(onnx_runtime_t* runtime, float* input_data, int input_size, float* output_data, int output_size);

// Vault Security (AES-256) Functions
typedef struct aes_vault aes_vault_t;

aes_vault_t* create_aes_vault(const char* key);
void destroy_aes_vault(aes_vault_t* vault);
int encrypt_data(aes_vault_t* vault, const unsigned char* plaintext, int plaintext_len, unsigned char* ciphertext);
int decrypt_data(aes_vault_t* vault, const unsigned char* ciphertext, int ciphertext_len, unsigned char* plaintext);

#ifdef __cplusplus
}
#endif

#endif // FLASHCORE_API_H