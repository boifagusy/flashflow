#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "../../include/flashcore_api.h"

namespace py = pybind11;

// Helper function to convert numpy array to float vector
std::vector<float> numpy_to_float_vector(py::array_t<float> input) {
    py::buffer_info buf_info = input.request();
    float *ptr = (float *) buf_info.ptr;
    return std::vector<float>(ptr, ptr + buf_info.size);
}

// Wrapper for HNSW Index
class PyHNSWIndex {
private:
    hnsw_index_t* index;

public:
    PyHNSWIndex(int dimensions, int max_elements) {
        index = create_hnsw_index(dimensions, max_elements);
    }

    ~PyHNSWIndex() {
        if (index) {
            destroy_hnsw_index(index);
        }
    }

    void add_vector(py::array_t<float> vector, int id) {
        std::vector<float> vec = numpy_to_float_vector(vector);
        add_vector_to_index(index, vec.data(), id);
    }

    py::list search(py::array_t<float> query, int k) {
        std::vector<float> query_vec = numpy_to_float_vector(query);
        std::vector<int> result_ids(k);
        std::vector<float> result_distances(k);

        int count = search_vector_in_index(index, query_vec.data(), k, result_ids.data(), result_distances.data());

        py::list results;
        for (int i = 0; i < count; ++i) {
            py::dict result;
            result["id"] = result_ids[i];
            result["distance"] = result_distances[i];
            results.append(result);
        }

        return results;
    }
};

// Wrapper for ONNX Runtime
class PyONNXRuntime {
private:
    onnx_runtime_t* runtime;

public:
    PyONNXRuntime(const std::string& model_path) {
        runtime = create_onnx_runtime(model_path.c_str());
    }

    ~PyONNXRuntime() {
        if (runtime) {
            destroy_onnx_runtime(runtime);
        }
    }

    py::array_t<float> run_inference(py::array_t<float> input, int output_size) {
        std::vector<float> input_vec = numpy_to_float_vector(input);
        std::vector<float> output_vec(output_size);

        run_inference(runtime, input_vec.data(), input_vec.size(), output_vec.data(), output_size);

        return py::cast(output_vec);
    }
};

// Wrapper for AES Vault
class PyAESVault {
private:
    aes_vault_t* vault;

public:
    PyAESVault(const std::string& key) {
        vault = create_aes_vault(key.c_str());
    }

    ~PyAESVault() {
        if (vault) {
            destroy_aes_vault(vault);
        }
    }

    py::bytes encrypt(const py::bytes& plaintext) {
        std::string plain_str = plaintext.cast<std::string>();
        std::vector<unsigned char> ciphertext(plain_str.size());

        int length = encrypt_data(vault, 
                                  reinterpret_cast<const unsigned char*>(plain_str.c_str()), 
                                  plain_str.size(), 
                                  ciphertext.data());

        return py::bytes(reinterpret_cast<char*>(ciphertext.data()), length);
    }

    py::bytes decrypt(const py::bytes& ciphertext) {
        std::string cipher_str = ciphertext.cast<std::string>();
        std::vector<unsigned char> plaintext(cipher_str.size());

        int length = decrypt_data(vault, 
                                  reinterpret_cast<const unsigned char*>(cipher_str.c_str()), 
                                  cipher_str.size(), 
                                  plaintext.data());

        return py::bytes(reinterpret_cast<char*>(plaintext.data()), length);
    }
};

PYBIND11_MODULE(flashcore, m) {
    m.doc() = "Python bindings for FlashCore C++ library";

    py::class_<PyHNSWIndex>(m, "HNSWIndex")
        .def(py::init<int, int>(), "Initialize HNSW index with dimensions and max elements")
        .def("add_vector", &PyHNSWIndex::add_vector, "Add a vector to the index")
        .def("search", &PyHNSWIndex::search, "Search for nearest neighbors");

    py::class_<PyONNXRuntime>(m, "ONNXRuntime")
        .def(py::init<const std::string&>(), "Initialize ONNX runtime with model path")
        .def("run_inference", &PyONNXRuntime::run_inference, "Run inference on input data");

    py::class_<PyAESVault>(m, "AESVault")
        .def(py::init<const std::string&>(), "Initialize AES vault with key")
        .def("encrypt", &PyAESVault::encrypt, "Encrypt data")
        .def("decrypt", &PyAESVault::decrypt, "Decrypt data");
}