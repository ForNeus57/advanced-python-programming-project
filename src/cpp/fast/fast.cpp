#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <cuda_runtime.h>
#include <numpy/arrayobject.h>
#include <nvjpeg.h>

#include <iostream>
#include <sstream>
#include <stdexcept>
#include <vector>

struct FastException : public std::runtime_error {
    explicit FastException(const std::string &error) : runtime_error{error.c_str()} {}
};

struct JPEGHandle {
    nvjpegHandle_t handle = {};
    JPEGHandle() {
        const nvjpegStatus_t jpeg_err = nvjpegCreateSimple(&this->handle);
        if (jpeg_err != NVJPEG_STATUS_SUCCESS) {
            std::stringstream error_stream{};

            error_stream << "Cannot initialize the nvjpeg hangle.\n"
                         << "Error: " << jpeg_err
                         << " (please consult the: "
                            "https://docs.nvidia.com/cuda/archive/12.4.0/nvjpeg/index.html#nvjpeg-api-return-codes )"
                         << "\n";

            throw FastException{error_stream.str()};
        }
    }
    ~JPEGHandle() {
        const nvjpegStatus_t jpeg_err = nvjpegDestroy(handle);
        if (jpeg_err != NVJPEG_STATUS_SUCCESS) {
            std::stringstream error_stream{};

            error_stream << "Cannot destroy the nvjpeg hangle.\n"
                         << "Error: " << jpeg_err
                         << " (please consult the: "
                            "https://docs.nvidia.com/cuda/archive/12.4.0/nvjpeg/index.html#nvjpeg-api-return-codes )"
                         << "\n";

            //            throw FastException{error_stream.str()};
        }
    }
};

static PyObject *FastError = nullptr;

static PyObject *fast_encode_jpeg(PyObject * /*self*/, PyObject *args) {
    PyArrayObject *input_array = nullptr;
    PyArg_ParseTuple(args, "O", &input_array);

    if (PyErr_Occurred() != nullptr) {
        return nullptr;
    }

    if (PyArray_NDIM(input_array) != 3 || PyArray_TYPE(input_array) != NPY_UINT8) {
        PyErr_SetString(PyExc_TypeError, "Input must be a (H, W, C) uint8 array.");
        return nullptr;
    }

    const auto height = static_cast<std::size_t>(PyArray_DIM(input_array, 0));
    const auto width = static_cast<std::size_t>(PyArray_DIM(input_array, 1));
    const auto channels = static_cast<std::size_t>(PyArray_DIM(input_array, 2));
    const std::size_t raw_size = height * width * channels;

    auto *data = reinterpret_cast<unsigned char *>(PyArray_DATA(input_array));

    try {
        const JPEGHandle handle;

        nvjpegEncoderState_t encoder_state;
        auto jpeg_err = nvjpegEncoderStateCreate(handle.handle, &encoder_state, nullptr);
        if (jpeg_err != NVJPEG_STATUS_SUCCESS) {
            std::stringstream error_stream;

            error_stream << "Encoder state creation failed.\n"
                         << "Error: " << jpeg_err
                         << " (please consult the: "
                            "https://docs.nvidia.com/cuda/archive/12.4.0/nvjpeg/index.html#nvjpeg-api-return-codes )"
                         << "\n";

            PyErr_SetString(PyExc_ValueError, error_stream.str().c_str());
            return nullptr;
        }

        nvjpegEncoderParams_t encode_params;
        jpeg_err = nvjpegEncoderParamsCreate(handle.handle, &encode_params, nullptr);
        if (jpeg_err != NVJPEG_STATUS_SUCCESS) {
            nvjpegEncoderStateDestroy(encoder_state);

            std::stringstream error_stream;

            error_stream << "Encoder params creation failed.\n"
                         << "Error: " << jpeg_err
                         << " (please consult the: "
                            "https://docs.nvidia.com/cuda/archive/12.4.0/nvjpeg/index.html#nvjpeg-api-return-codes )"
                         << "\n";

            PyErr_SetString(PyExc_ValueError, error_stream.str().c_str());
            return nullptr;
        }
        nvjpegEncoderParamsSetQuality(encode_params, 90, nullptr);
        nvjpegEncoderParamsSetSamplingFactors(encode_params, NVJPEG_CSS_420, nullptr);

        unsigned char *device_pixels_ptr;
        cudaError_t err = cudaMalloc(reinterpret_cast<void **>(&device_pixels_ptr), raw_size);
        if (err != cudaSuccess) {
            nvjpegEncoderParamsDestroy(encode_params);
            nvjpegEncoderStateDestroy(encoder_state);

            std::stringstream error_stream;

            error_stream << "Cuda Malloc failed.\n"
                         << "Error: " << cudaGetErrorString(err) << "\n";

            PyErr_SetString(PyExc_ValueError, error_stream.str().c_str());
            return nullptr;
        }

        err = cudaMemcpy(device_pixels_ptr,  // Destination (Host)
                         data,               // Source (GPU)
                         raw_size, cudaMemcpyHostToDevice);
        if (err != cudaSuccess) {
            cudaFree(device_pixels_ptr);
            nvjpegEncoderParamsDestroy(encode_params);
            nvjpegEncoderStateDestroy(encoder_state);

            std::stringstream error_stream;

            error_stream << "Cuda Memcopy failed.\n"
                         << "Error: " << cudaGetErrorString(err) << "\n";

            PyErr_SetString(PyExc_ValueError, error_stream.str().c_str());
            return nullptr;
        }

        const nvjpegImage_t img_data = {
            {device_pixels_ptr, nullptr, nullptr, nullptr},
            {width * channels,  0,       0,       0      },
        };

        jpeg_err = nvjpegEncodeImage(handle.handle, encoder_state, encode_params, &img_data, NVJPEG_INPUT_RGBI,
                                     static_cast<int>(width), static_cast<int>(height), nullptr);
        if (jpeg_err != NVJPEG_STATUS_SUCCESS) {
            cudaFree(device_pixels_ptr);
            nvjpegEncoderParamsDestroy(encode_params);
            nvjpegEncoderStateDestroy(encoder_state);

            std::stringstream error_stream;

            error_stream << "Encoder failed.\n"
                         << "Error: " << jpeg_err
                         << " (please consult the: "
                            "https://docs.nvidia.com/cuda/archive/12.4.0/nvjpeg/index.html#nvjpeg-api-return-codes )"
                         << "\n";

            PyErr_SetString(PyExc_ValueError, error_stream.str().c_str());
            return nullptr;
        }

        size_t length;
        jpeg_err = nvjpegEncodeRetrieveBitstream(handle.handle, encoder_state, nullptr, &length, nullptr);
        if (jpeg_err != NVJPEG_STATUS_SUCCESS) {
            cudaFree(device_pixels_ptr);
            nvjpegEncoderParamsDestroy(encode_params);
            nvjpegEncoderStateDestroy(encoder_state);

            std::stringstream error_stream;

            error_stream << "Encoder bitstream retrival failed.\n"
                         << "Error: " << jpeg_err
                         << " (please consult the: "
                            "https://docs.nvidia.com/cuda/archive/12.4.0/nvjpeg/index.html#nvjpeg-api-return-codes )"
                         << "\n";

            PyErr_SetString(PyExc_ValueError, error_stream.str().c_str());
            return nullptr;
        }

        std::vector<unsigned char> jpeg_out(length);
        jpeg_err = nvjpegEncodeRetrieveBitstream(handle.handle, encoder_state, jpeg_out.data(), &length, nullptr);
        if (jpeg_err != NVJPEG_STATUS_SUCCESS) {
            cudaFree(device_pixels_ptr);
            nvjpegEncoderParamsDestroy(encode_params);
            nvjpegEncoderStateDestroy(encoder_state);

            std::stringstream error_stream;

            error_stream << "Encoder bitstream retrival failed.\n"
                         << "Error: " << jpeg_err
                         << " (please consult the: "
                            "https://docs.nvidia.com/cuda/archive/12.4.0/nvjpeg/index.html#nvjpeg-api-return-codes )"
                         << "\n";

            PyErr_SetString(PyExc_ValueError, error_stream.str().c_str());
            return nullptr;
        }

        cudaFree(device_pixels_ptr);
        nvjpegEncoderParamsDestroy(encode_params);
        nvjpegEncoderStateDestroy(encoder_state);

        return PyBytes_FromStringAndSize(reinterpret_cast<char *>(jpeg_out.data()), static_cast<Py_ssize_t>(length));

    } catch (FastException &error) {
        PyErr_SetString(PyExc_ValueError, error.what());
        return nullptr;
    }
}

// Sources:
// -
// https://github.com/NVIDIA/CUDALibrarySamples/blob/ee70ba1f7882f92e325eb8598f61dde7b77a5499/nvJPEG/nvJPEG-Decoder/nvjpegDecoder.h#L161
// - https://docs.nvidia.com/cuda/archive/12.4.0/nvjpeg/index.html#jpeg-transcoding-example
static PyObject *fast_decode_jpeg(PyObject * /*self*/, PyObject *args) {
    PyObject *raw_data_object = nullptr;
    PyArg_ParseTuple(args, "O", &raw_data_object);

    if (PyErr_Occurred() != nullptr) {
        return nullptr;
    }

    if (!static_cast<bool>(PyBytes_Check(raw_data_object))) {
        PyErr_SetString(PyExc_TypeError, "Argument must be a bytes object!");
        return nullptr;
    }

    auto bytes_size = PyBytes_Size(raw_data_object);
    auto *data_read_only = PyBytes_AsString(raw_data_object);
    if (data_read_only == nullptr) {
        std::stringstream error_stream;

        error_stream << "CBytes object provided has value: nullptr.\n";
        PyErr_SetString(PyExc_ValueError, error_stream.str().c_str());
        return nullptr;
    }

    nvjpegHandle_t handle;
    nvjpegStatus_t jpeg_err = nvjpegCreateSimple(&handle);
    if (jpeg_err != NVJPEG_STATUS_SUCCESS) {
        std::stringstream error_stream;

        error_stream << "Cannot initialize the nvjpeg hangle.\n"
                     << "Error: " << jpeg_err
                     << " (please consult the: "
                        "https://docs.nvidia.com/cuda/archive/12.4.0/nvjpeg/index.html#nvjpeg-api-return-codes )"
                     << "\n";

        PyErr_SetString(PyExc_ValueError, error_stream.str().c_str());
        return nullptr;
    }

    nvjpegJpegState_t state;
    jpeg_err = nvjpegJpegStateCreate(handle, &state);
    if (jpeg_err != NVJPEG_STATUS_SUCCESS) {
        nvjpegDestroy(handle);

        std::stringstream error_stream;

        error_stream << "Cannot initialize the nvjpeg jpeg status.\n"
                     << "Error: " << jpeg_err
                     << " (please consult the: "
                        "https://docs.nvidia.com/cuda/archive/12.4.0/nvjpeg/index.html#nvjpeg-api-return-codes )"
                     << "\n";

        PyErr_SetString(PyExc_ValueError, error_stream.str().c_str());
        return nullptr;
    }

    int channels = 0;
    nvjpegChromaSubsampling_t subsampling = {};
    int widths[NVJPEG_MAX_COMPONENT];
    int heights[NVJPEG_MAX_COMPONENT];

    jpeg_err = nvjpegGetImageInfo(handle, reinterpret_cast<unsigned char *>(data_read_only),
                                  static_cast<size_t>(bytes_size), &channels, &subsampling, widths, heights);
    if (jpeg_err != NVJPEG_STATUS_SUCCESS) {
        nvjpegJpegStateDestroy(state);
        nvjpegDestroy(handle);

        std::stringstream error_stream;

        error_stream << "Cannot initialize the nvjpeg jpeg status.\n"
                     << "Error: " << jpeg_err
                     << " (please consult the: "
                        "https://docs.nvidia.com/cuda/archive/12.4.0/nvjpeg/index.html#nvjpeg-api-return-codes )"
                     << "\n";

        PyErr_SetString(PyExc_ValueError, error_stream.str().c_str());
        return nullptr;
    }

    auto width = static_cast<std::size_t>(widths[0]);
    auto height = static_cast<std::size_t>(heights[0]);
    const size_t imgSize = width * height * 3;

    unsigned char *d_outputBuffer;
    cudaError_t err = cudaMalloc(reinterpret_cast<void **>(&d_outputBuffer), imgSize);
    if (err != cudaSuccess) {
        nvjpegJpegStateDestroy(state);
        nvjpegDestroy(handle);

        std::stringstream error_stream;

        error_stream << "Cuda Malloc failed.\n"
                     << "Error: " << cudaGetErrorString(err) << "\n";

        PyErr_SetString(PyExc_ValueError, error_stream.str().c_str());
        return nullptr;
    }

    nvjpegImage_t imgDesc = {
        {d_outputBuffer,        nullptr, nullptr, nullptr},
        {width + width + width, 0,       0,       0      },
    };

    jpeg_err = nvjpegDecode(handle, state, reinterpret_cast<unsigned char *>(data_read_only), bytes_size,
                            NVJPEG_OUTPUT_RGBI, &imgDesc,
                            nullptr  // No cuda stream because we need the synchronous call
    );
    if (jpeg_err != NVJPEG_STATUS_SUCCESS) {
        cudaFree(d_outputBuffer);
        nvjpegJpegStateDestroy(state);
        nvjpegDestroy(handle);

        std::stringstream error_stream;

        error_stream << "Cuda malloc failed.\n"
                     << "Error: " << cudaGetErrorString(err) << "\n";

        PyErr_SetString(PyExc_ValueError, error_stream.str().c_str());
        return nullptr;
    }

    npy_intp dims[3] = {static_cast<npy_intp>(height), static_cast<npy_intp>(width), 3};
    PyObject *numpy_array = PyArray_SimpleNew(3, dims, NPY_UINT8);
    auto *numpy_data = reinterpret_cast<unsigned char *>(PyArray_DATA(reinterpret_cast<PyArrayObject *>(numpy_array)));
    if (numpy_array == nullptr) {
        cudaFree(d_outputBuffer);
        nvjpegJpegStateDestroy(state);
        nvjpegDestroy(handle);

        std::stringstream error_stream;

        error_stream << "Numpy malloc failed.\n";

        PyErr_SetString(PyExc_ValueError, error_stream.str().c_str());
        return nullptr;
    }

    err = cudaMemcpy(numpy_data,      // Destination (Host)
                     d_outputBuffer,  // Source (GPU)
                     imgSize, cudaMemcpyDeviceToHost);
    if (err != cudaSuccess) {
        cudaFree(d_outputBuffer);
        nvjpegJpegStateDestroy(state);
        nvjpegDestroy(handle);

        std::stringstream error_stream;

        error_stream << "Cuda Memcopy failed.\n"
                     << "Error: " << cudaGetErrorString(err) << "\n";

        PyErr_SetString(PyExc_ValueError, error_stream.str().c_str());
        return nullptr;
    }

    cudaFree(d_outputBuffer);
    nvjpegJpegStateDestroy(state);
    nvjpegDestroy(handle);

    return numpy_array;
}

static int fast_module_exec(PyObject *module) {
    if (FastError != nullptr) {
        PyErr_SetString(PyExc_ImportError, "cannot initialize numpy module more than once");
        return -1;
    }

    FastError = PyErr_NewException("fast.error", nullptr, nullptr);
    if (PyModule_AddObjectRef(module, "FastError", FastError) < 0) {
        return -1;
    }

    return 0;
}

static PyMethodDef fast_methods[] = {
    {"encode_jpeg", fast_encode_jpeg, METH_VARARGS,
     "Encodes the numpy array data as jpeg image. Returns bytes that form a jpeg image."    },
    {"decode_jpeg", fast_decode_jpeg, METH_VARARGS,
     "Decodes the bytes as a JPEG image and returns the numpy array of the underlying data."},
    {nullptr,       nullptr,          0,            nullptr                                 }  /* Sentinel */
};

static PyModuleDef_Slot fast_module_slots[] = {
    {Py_mod_exec, reinterpret_cast<void *>(fast_module_exec)},
    {0,           nullptr                                   },
};

static struct PyModuleDef fast_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "fast",
    .m_size = 0,  // non-negative
    .m_methods = fast_methods,
    .m_slots = fast_module_slots,
};

PyMODINIT_FUNC PyInit_fast(void) {
    int deviceCount = 0;
    const cudaError_t error = cudaGetDeviceCount(&deviceCount);

    // This check handles this type of errors:
    // https://docs.nvidia.com/cuda/archive/12.4.0/cuda-runtime-api/group__CUDART__DEVICE.html#group__CUDART__DEVICE_1g18808e54893cfcaafefeab31a73cc55f
    if (error != cudaSuccess) {
        std::stringstream error_stream;

        error_stream << "CUDA driver is not installed or no CUDA-capable GPU found.\n"
                     << "Error: " << cudaGetErrorString(error) << "\n";

        PyErr_SetString(PyExc_ImportError, error_stream.str().c_str());
        return nullptr;
    }

    PyObject *module_obj = PyModuleDef_Init(&fast_module);
    import_array();
    return module_obj;
}