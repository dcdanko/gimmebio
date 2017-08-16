#include "ckmers.h"
#include <Python.h>

static char  module_docstring[] =
  "A module for kmer related fucntions that interface between c and python";
static char nextRabinFingerprint_docstring[] =
  "Calculate the next rabin fingerprint";
static char rabinFingerprints_docstring[] =
  "Calculate rabin fingerprints for a sequence";
  

static PyObject * ckmers_nextRabinFingerprint(PyObject* self, PyObject* args);
static PyObject * ckmers_rabinFingerprints(PyObject* self, PyObject* args);


static PyMethodDef ckmers_methods[] = {
  {"nextRabinFingerprint", ckmers_nextRabinFingerprint, METH_VARARGS, nextRabinFingerprint_docstring},
  {"rabinFingerprints", ckmers_rabinFingerprints, METH_VARARGS, rabinFingerprints_docstring}
};

static struct PyModuleDef ckmersmodule = {
  PyModuleDef_HEAD_INIT,
  "ckmers",
  module_docstring,
  -1,
  ckmers_methods
};

PyMODINIT_FUNC PyInit_ckmers(void){
  return PyModule_Create(&ckmersmodule);
}

static PyObject * ckmers_nextRabinFingerprint(PyObject *self, PyObject *args){
  uint64_t oldHash;
  uint8_t oldBase, newBase, power, radix;
  if (!PyArg_ParseTuple(args, "Lbbbb", &oldHash, &oldBase, &newBase, &power, &radix)){
    return NULL;
  }

  uint64_t newHash = nextRabinFingerprint(oldHash, oldBase, newBase, power, radix);
  PyObject *ret= Py_BuildValue("L", newHash);
  return ret;
    
}

static PyObject * ckmers_rabinFingerprints(PyObject *self, PyObject *args){
  char * seqObj;
  uint8_t seqLen, power, radix;
  if (!PyArg_ParseTuple(args, "sbbb", &seqObj, &seqLen, &power, &radix)){
    return NULL;
  }

  return rabinFingerprints(seqObj, seqLen, power, radix);
    
}

