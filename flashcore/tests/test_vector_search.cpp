#include "../include/flashcore_api.h"
#include <iostream>
#include <cassert>
#include <cmath>

int main() {
    std::cout << "Testing Vector Search Module..." << std::endl;
    
    // Create HNSW index
    hnsw_index_t* index = create_hnsw_index(4, 100);
    assert(index != nullptr);
    std::cout << "✓ Created HNSW index" << std::endl;
    
    // Add vectors to index
    float vec1[] = {1.0f, 2.0f, 3.0f, 4.0f};
    float vec2[] = {2.0f, 3.0f, 4.0f, 5.0f};
    float vec3[] = {3.0f, 4.0f, 5.0f, 6.0f};
    
    assert(add_vector_to_index(index, vec1, 1) == 0);
    assert(add_vector_to_index(index, vec2, 2) == 0);
    assert(add_vector_to_index(index, vec3, 3) == 0);
    std::cout << "✓ Added vectors to index" << std::endl;
    
    // Search for nearest neighbors
    float query[] = {1.5f, 2.5f, 3.5f, 4.5f};
    int result_ids[3];
    float result_distances[3];
    
    int result_count = search_vector_in_index(index, query, 3, result_ids, result_distances);
    assert(result_count == 3);
    std::cout << "✓ Performed vector search" << std::endl;
    
    // Check results (vec2 should be closest to query)
    assert(result_ids[0] == 2); // vec2 should be closest
    std::cout << "✓ Vector search returned correct results" << std::endl;
    
    // Clean up
    destroy_hnsw_index(index);
    std::cout << "✓ Destroyed HNSW index" << std::endl;
    
    std::cout << "All Vector Search tests passed!" << std::endl;
    return 0;
}