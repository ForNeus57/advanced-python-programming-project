#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <numpy/arrayobject.h>

static PyObject * 
numpy_grayscale(PyObject *self, PyObject *args){
    PyArrayObject *arr;
    PyArg_ParseTuple(args, "O", &arr);
    if(PyErr_Occurred()){
        return NULL;
    }

    if(!PyArray_Check(arr) || PyArray_TYPE(arr) != NPY_DOUBLE) {
        PyErr_SetString(PyExc_TypeError, "Argument must be a numpy array of type double!");
        return NULL;
    }
    Py_INCREF(arr);

//    PyObject* arr_copy = (PyArrayObject *)PyArray_NewCopy(arr, NPY_CORDER);

    int src_nd = PyArray_NDIM(arr);
    if (src_nd != 3) {
        PyErr_SetString(PyExc_TypeError, "Array number of dimensions must be equal to 3");
        return NULL;
    }

    npy_intp* src_shape = PyArray_SIZE(arr);
    if (src_shape[2] != 3) {
        PyErr_SetString(PyExc_TypeError, "Array number of must have 3 channels for colors");
        return NULL;
    }

    npy_intp result[2] = {src_shape[0], src_shape[1]};

    PyArrayObject *new_array = (PyArrayObject *)PyArray_SimpleNew(src_nd - 1, result, NPY_DOUBLE);

    Py_DECREF(arr);

    double *data = PyArray_DATA(arr);
    int64_t size = PyArray_SIZE(arr);

    double* new_data = PyArray_DATA(new_array);
    for (int i = 0; i < src_shape[0]; i++)
    {
        for (int j = 0; j < src_shape[1]; ++j)
        {
            for (int k = 0; k < src_shape[2]; ++k)
            {
                new_data[i * src_shape[1] + j] = (
                    data[i * src_shape[1] * src_shape[2] + j * src_shape[2] + 0]
                    + data[i * src_shape[1] * src_shape[2] + j * src_shape[2] + 1]
                    + data[i * src_shape[1] * src_shape[2] + j * src_shape[2] + 2]
                ) / 3;
            }
        }
    }

    return new_array;
}

static PyObject *SpamError = NULL;

static int
fast_module_exec(PyObject *m)
{
    if (SpamError != NULL) {
        PyErr_SetString(PyExc_ImportError,
                        "cannot initialize fast module more than once");
        return -1;
    }
    SpamError = PyErr_NewException("fast.error", NULL, NULL);
    if (PyModule_AddObjectRef(m, "SpamError", SpamError) < 0) {
        return -1;
    }

    return 0;
}

static PyMethodDef fast_methods[] = {
     {"grayscale", numpy_grayscale, METH_VARARGS,
    "Perform grayscale operation, return copy."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static PyModuleDef_Slot fast_module_slots[] = {
    {Py_mod_exec, fast_module_exec},
    {0, NULL}
};

static struct PyModuleDef fast_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "fast",
    .m_size = 0,  // non-negative
    .m_slots = fast_module_slots,
    .m_methods = fast_methods
};

PyMODINIT_FUNC
PyInit_fast(void)
{
    PyObject* module_obj = PyModuleDef_Init(&fast_module);
    import_array();
    return module_obj;
}