#include "../include/flashcore_api.h"
#include <iostream>
#include <cassert>
#include <cstring>

int main() {
    std::cout << "Testing Vault Security Module..." << std::endl;
    
    // Create AES vault
    aes_vault_t* vault = create_aes_vault("test_key_12345");
    assert(vault != nullptr);
    std::cout << "✓ Created AES vault" << std::endl;
    
    // Encrypt data
    const char* plaintext = "Hello, FlashCore!";
    unsigned char ciphertext[100];
    
    int ciphertext_len = encrypt_data(vault, (const unsigned char*)plaintext, strlen(plaintext), ciphertext);
    assert(ciphertext_len == strlen(plaintext));
    std::cout << "✓ Encrypted data" << std::endl;
    
    // Decrypt data
    unsigned char decrypted[100];
    
    int decrypted_len = decrypt_data(vault, ciphertext, ciphertext_len, decrypted);
    assert(decrypted_len == ciphertext_len);
    std::cout << "✓ Decrypted data" << std::endl;
    
    // Check results (plaintext should match decrypted text in our mock implementation)
    assert(memcmp(plaintext, decrypted, decrypted_len) == 0);
    std::cout << "✓ Encryption/Decryption returned correct results" << std::endl;
    
    // Clean up
    destroy_aes_vault(vault);
    std::cout << "✓ Destroyed AES vault" << std::endl;
    
    std::cout << "All Vault Security tests passed!" << std::endl;
    return 0;
}