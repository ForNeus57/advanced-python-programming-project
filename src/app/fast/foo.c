#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <numpy/arrayobject.h>

static PyObject *
spam_system(PyObject *self, PyObject *args)
{
    const char *command;
    int sts;

    if (!PyArg_ParseTuple(args, "s", &command))
        return NULL;
    sts = system(command);
    return PyLong_FromLong(sts);
}

static PyObject * 
numpy_add(PyObject *self, PyObject *args){
    PyArrayObject *arr;
    PyArg_ParseTuple(args, "O", &arr);
    if(PyErr_Occurred()){
        return NULL;
    }
    if(!PyArray_Check(arr) || PyArray_TYPE(arr) != NPY_DOUBLE) {
        PyErr_SetString(PyExc_TypeError, "Argument must be a numpy array of type double!");
        return NULL;
    }


    double *data = PyArray_DATA(arr);
    int64_t size = PyArray_SIZE(arr);

    double total=0;
    for (int i=0; i < size; i++){
        total += data[i];
    }
    return PyFloat_FromDouble(total);
}

static PyObject *SpamError = NULL;

static int
spam_module_exec(PyObject *m)
{
    if (SpamError != NULL) {
        PyErr_SetString(PyExc_ImportError,
                        "cannot initialize spam module more than once");
        return -1;
    }
    SpamError = PyErr_NewException("spam.error", NULL, NULL);
    if (PyModule_AddObjectRef(m, "SpamError", SpamError) < 0) {
        return -1;
    }

    return 0;
}

static PyMethodDef spam_methods[] = {
    {"system",  spam_system, METH_VARARGS,
     "Execute a shell command."},
     {"numpy_add", numpy_add, METH_VARARGS,
    "Perform adding operation."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static PyModuleDef_Slot spam_module_slots[] = {
    {Py_mod_exec, spam_module_exec},
    {0, NULL}
};

static struct PyModuleDef spam_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "spam",
    .m_size = 0,  // non-negative
    .m_slots = spam_module_slots,
    .m_methods = spam_methods
};

PyMODINIT_FUNC
PyInit_fast(void)
{
    PyObject* module_obj = PyModuleDef_Init(&spam_module);
    import_array();
    return module_obj;
}