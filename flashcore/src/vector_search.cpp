#include "../include/flashcore_api.h"
#include <vector>
#include <algorithm>
#include <cmath>
#include <cstring>
#include <iostream>

// Simple implementation of HNSW index for demonstration purposes
struct hnsw_index {
    int dimensions;
    int max_elements;
    std::vector<std::pair<int, std::vector<float>>> vectors; // id, vector pairs
};

extern "C" {

hnsw_index_t* create_hnsw_index(int dimensions, int max_elements) {
    hnsw_index_t* index = new hnsw_index();
    index->dimensions = dimensions;
    index->max_elements = max_elements;
    return index;
}

void destroy_hnsw_index(hnsw_index_t* index) {
    delete index;
}

int add_vector_to_index(hnsw_index_t* index, float* vector, int id) {
    if (index->vectors.size() >= index->max_elements) {
        return -1; // Index is full
    }
    
    std::vector<float> vec(vector, vector + index->dimensions);
    index->vectors.push_back(std::make_pair(id, vec));
    return 0; // Success
}

int search_vector_in_index(hnsw_index_t* index, float* query_vector, int k, int* result_ids, float* result_distances) {
    if (k <= 0 || k > index->vectors.size()) {
        return -1; // Invalid k
    }
    
    // Simple brute-force search for demonstration
    std::vector<std::pair<float, int>> distances; // distance, id pairs
    
    for (const auto& vec_pair : index->vectors) {
        int id = vec_pair.first;
        const std::vector<float>& stored_vector = vec_pair.second;
        
        // Calculate Euclidean distance
        float distance = 0.0f;
        for (int i = 0; i < index->dimensions; ++i) {
            float diff = query_vector[i] - stored_vector[i];
            distance += diff * diff;
        }
        distance = std::sqrt(distance);
        
        distances.push_back(std::make_pair(distance, id));
    }
    
    // Sort by distance
    std::sort(distances.begin(), distances.end());
    
    // Return top k results
    int result_count = std::min(k, static_cast<int>(distances.size()));
    for (int i = 0; i < result_count; ++i) {
        result_ids[i] = distances[i].second;
        result_distances[i] = distances[i].first;
    }
    
    return result_count;
}

} // extern "C"