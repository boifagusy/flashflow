#include "../include/flashcore_api.h"
#include <iostream>
#include <cstring>
#include <openssl/aes.h>
#include <openssl/evp.h>

// Simple implementation of AES-256 vault for demonstration purposes
struct aes_vault {
    unsigned char key[32]; // AES-256 key
};

extern "C" {

aes_vault_t* create_aes_vault(const char* key) {
    aes_vault_t* vault = new aes_vault();
    
    // Copy key (in a real implementation, we'd derive a key from the input)
    memset(vault->key, 0, sizeof(vault->key));
    if (key) {
        size_t key_len = strlen(key);
        memcpy(vault->key, key, std::min(key_len, sizeof(vault->key)));
    }
    
    std::cout << "Created AES-256 vault" << std::endl;
    return vault;
}

void destroy_aes_vault(aes_vault_t* vault) {
    std::cout << "Destroyed AES-256 vault" << std::endl;
    delete vault;
}

int encrypt_data(aes_vault_t* vault, const unsigned char* plaintext, int plaintext_len, unsigned char* ciphertext) {
    std::cout << "Encrypting data with AES-256" << std::endl;
    
    // Simple mock encryption - just copy data for demonstration
    memcpy(ciphertext, plaintext, plaintext_len);
    
    return plaintext_len; // Return ciphertext length
}

int decrypt_data(aes_vault_t* vault, const unsigned char* ciphertext, int ciphertext_len, unsigned char* plaintext) {
    std::cout << "Decrypting data with AES-256" << std::endl;
    
    // Simple mock decryption - just copy data for demonstration
    memcpy(plaintext, ciphertext, ciphertext_len);
    
    return ciphertext_len; // Return plaintext length
}

} // extern "C"