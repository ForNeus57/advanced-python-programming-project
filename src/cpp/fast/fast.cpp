#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <numpy/arrayobject.h>

static PyObject *numpy_system(PyObject */*self*/, PyObject *args) {
    const char *command = nullptr;
    int sts = 0;

    if (PyArg_ParseTuple(args, "s", &command) == 0) {
        return nullptr;
    }

    sts = system(command);
    return PyLong_FromLong(sts);
}

static PyObject *numpy_add(PyObject */*self*/, PyObject *args) {
    PyArrayObject *arr = nullptr;
    PyArg_ParseTuple(args, "O", &arr);

    if (PyErr_Occurred() != nullptr) {
        return nullptr;
    }
    if (!PyArray_Check(arr) || PyArray_TYPE(arr) != NPY_DOUBLE) {
        PyErr_SetString(PyExc_TypeError, "Argument must be a numpy array of type double!");
        return nullptr;
    }

    auto* data = reinterpret_cast<double *>(PyArray_DATA(arr));
    const int64_t size = PyArray_SIZE(arr);

    double total = 0.;
    for (std::size_t i = 0; i < size; i++) {
        total += data[i];
    }

    return PyFloat_FromDouble(total);
}

static PyObject *NumpyError = nullptr;

static int numpy_module_exec(PyObject *module) {
    if (NumpyError != nullptr) {
        PyErr_SetString(PyExc_ImportError, "cannot initialize numpy module more than once");
        return -1;
    }

    NumpyError = PyErr_NewException("numpy.error", nullptr, nullptr);
    if (PyModule_AddObjectRef(module, "NumpyError", NumpyError) < 0) {
        return -1;
    }

    return 0;
}

static PyMethodDef numpy_methods[] = {
    {"system",    numpy_system, METH_VARARGS, "Execute a shell command." },
    {"numpy_add", numpy_add,    METH_VARARGS, "Perform adding operation."},
    {nullptr,     nullptr,      0,            nullptr                    }  /* Sentinel */
};

static PyModuleDef_Slot numpy_module_slots[] = {
    {Py_mod_exec, reinterpret_cast<void *>(numpy_module_exec)},
    {0,           nullptr                                    }
};

static struct PyModuleDef numpy_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "numpy",
    .m_size = 0,  // non-negative
    .m_methods = numpy_methods,
    .m_slots = numpy_module_slots,
};

PyMODINIT_FUNC PyInit_fast(void) {
    PyObject *module_obj = PyModuleDef_Init(&numpy_module);
    import_array();
    return module_obj;
}