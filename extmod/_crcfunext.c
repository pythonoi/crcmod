//-----------------------------------------------------------------------------
// Low level CRC functions for use by crcmod.  This version is the C
// implementation that corresponds to the Python module _crcfunpy.  This module
// will be used by crcmod if it is built for the target platform.  Otherwise,
// the Python module is used.
//
// Copyright (c) 2004  Raymond L. Buvel
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to
// deal in the Software without restriction, including without limitation the
// rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
// sell copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
// IN THE SOFTWARE.
//-----------------------------------------------------------------------------

#include <Python.h>

// Define a few types to make it easier to port to other platforms.
typedef unsigned char UINT8;
typedef unsigned short UINT16;
typedef unsigned int UINT32;  // Works for 32-bit and some 64-bit processors
typedef unsigned PY_LONG_LONG UINT64;

// Define some macros that extract the specified byte from an integral value in
// what should be a platform indepent manner.
#define BYTE0(x) ((UINT8)(x))
#define BYTE1(x) ((UINT8)((x) >> 8))
#define BYTE3(x) ((UINT8)((x) >> 24))
#define BYTE7(x) ((UINT8)((x) >> 56))

//-----------------------------------------------------------------------------
// Compute a 8-bit crc over the input data.
// Inputs:
//   data - string containing the data
//   crc - unsigned integer containing the initial crc
//   table - string containing the 8-bit table corresponding to the generator
//           polynomial.
// Returns:
//   crc - unsigned integer containing the resulting crc

static PyObject*
_crc8(PyObject* self, PyObject* args)
{
    int crcin;
    UINT8 crc;
    UINT8* data;
    int dataLen;
    UINT8* table;
    int tableLen;

    if (!PyArg_ParseTuple(args, "s#is#", &data, &dataLen, &crcin,
                            &table, &tableLen)) {
        return NULL;
    }

    if (tableLen != 256) {
        PyErr_SetString(PyExc_ValueError, "invalid CRC table");
        return NULL;
    }

    // Expecting a 8-bit unsigned value
    crc = (UINT8)crcin;

    while (dataLen--) {
        crc = table[*data ^ crc];
        data++;
    }

    // This makes sure an unsigned value is returned.
    return Py_BuildValue("i", (int)crc);
}

//-----------------------------------------------------------------------------
// Compute a 8-bit crc over the input data.  The data stream is bit reversed
// during the computation.
// Inputs:
//   data - string containing the data
//   crc - unsigned integer containing the initial crc
//   table - string containing the 8-bit table corresponding to the generator
//           polynomial.
// Returns:
//   crc - unsigned integer containing the resulting crc

static PyObject*
_crc8r(PyObject* self, PyObject* args)
{
    int crcin;
    UINT8 crc;
    UINT8* data;
    int dataLen;
    UINT8* table;
    int tableLen;

    if (!PyArg_ParseTuple(args, "s#is#", &data, &dataLen, &crcin,
                            &table, &tableLen)) {
        return NULL;
    }

    if (tableLen != 256) {
        PyErr_SetString(PyExc_ValueError, "invalid CRC table");
        return NULL;
    }

    // Expecting a 8-bit unsigned value
    crc = (UINT8)crcin;

    while (dataLen--) {
        crc = table[*data ^ crc];
        data++;
    }

    // This makes sure an unsigned value is returned.
    return Py_BuildValue("i", (int)crc);
}

//-----------------------------------------------------------------------------
// Compute a 16-bit crc over the input data.
// Inputs:
//   data - string containing the data
//   crc - unsigned integer containing the initial crc
//   table - string containing the 16-bit table corresponding to the generator
//           polynomial.
// Returns:
//   crc - unsigned integer containing the resulting crc

static PyObject*
_crc16(PyObject* self, PyObject* args)
{
    int crcin;
    UINT16 crc;
    UINT8* data;
    int dataLen;
    UINT16* table;
    int tableLen;

    if (!PyArg_ParseTuple(args, "s#is#", &data, &dataLen, &crcin,
                            &table, &tableLen)) {
        return NULL;
    }

    if (tableLen != 256*2) {
        PyErr_SetString(PyExc_ValueError, "invalid CRC table");
        return NULL;
    }

    // Expecting a 16-bit unsigned value
    crc = (UINT16)crcin;

    while (dataLen--) {
        crc = table[*data ^ BYTE1(crc)] ^ (crc << 8);
        data++;
    }

    // This makes sure an unsigned value is returned.
    return Py_BuildValue("i", (int)crc);
}

//-----------------------------------------------------------------------------
// Compute a 16-bit crc over the input data.  The data stream is bit reversed
// during the computation.
// Inputs:
//   data - string containing the data
//   crc - unsigned integer containing the initial crc
//   table - string containing the 16-bit table corresponding to the generator
//           polynomial.
// Returns:
//   crc - unsigned integer containing the resulting crc

static PyObject*
_crc16r(PyObject* self, PyObject* args)
{
    int crcin;
    UINT16 crc;
    UINT8* data;
    int dataLen;
    UINT16* table;
    int tableLen;

    if (!PyArg_ParseTuple(args, "s#is#", &data, &dataLen, &crcin,
                            &table, &tableLen)) {
        return NULL;
    }

    if (tableLen != 256*2) {
        PyErr_SetString(PyExc_ValueError, "invalid CRC table");
        return NULL;
    }

    // Expecting a 16-bit unsigned value
    crc = (UINT16)crcin;

    while (dataLen--) {
        crc = table[*data ^ BYTE0(crc)] ^ (crc >> 8);
        data++;
    }

    // This makes sure an unsigned value is returned.
    return Py_BuildValue("i", (int)crc);
}

//-----------------------------------------------------------------------------
// Compute a 32-bit crc over the input data.
// Inputs:
//   data - string containing the data
//   crc - unsigned integer containing the initial crc
//   table - string containing the 32-bit table corresponding to the generator
//           polynomial.
// Returns:
//   crc - unsigned integer containing the resulting crc

static PyObject*
_crc32(PyObject* self, PyObject* args)
{
    UINT32 crc;
    UINT8* data;
    int dataLen;
    UINT32* table;
    int tableLen;

    if (!PyArg_ParseTuple(args, "s#is#", &data, &dataLen, &crc,
                            &table, &tableLen)) {
        return NULL;
    }

    if (tableLen != 256*4) {
        PyErr_SetString(PyExc_ValueError, "invalid CRC table");
        return NULL;
    }

    while (dataLen--) {
        crc = table[*data ^ BYTE3(crc)] ^ (crc << 8);
        data++;
    }

    return Py_BuildValue("i", crc);
}

//-----------------------------------------------------------------------------
// Compute a 32-bit crc over the input data.  The data stream is bit reversed
// during the computation.
// Inputs:
//   data - string containing the data
//   crc - unsigned integer containing the initial crc
//   table - string containing the 32-bit table corresponding to the generator
//           polynomial.
// Returns:
//   crc - unsigned integer containing the resulting crc

static PyObject*
_crc32r(PyObject* self, PyObject* args)
{
    UINT32 crc;
    UINT8* data;
    int dataLen;
    UINT32* table;
    int tableLen;

    if (!PyArg_ParseTuple(args, "s#is#", &data, &dataLen, &crc,
                            &table, &tableLen)) {
        return NULL;
    }

    if (tableLen != 256*4) {
        PyErr_SetString(PyExc_ValueError, "invalid CRC table");
        return NULL;
    }

    while (dataLen--) {
        crc = table[*data ^ BYTE0(crc)] ^ (crc >> 8);
        data++;
    }

    return Py_BuildValue("i", crc);
}

//-----------------------------------------------------------------------------
// Compute a 64-bit crc over the input data.
// Inputs:
//   data - string containing the data
//   crc - unsigned integer containing the initial crc
//   table - string containing the 64-bit table corresponding to the generator
//           polynomial.
// Returns:
//   crc - unsigned integer containing the resulting crc

static PyObject*
_crc64(PyObject* self, PyObject* args)
{
    UINT64 crc;
    UINT8* data;
    int dataLen;
    UINT64* table;
    int tableLen;

    if (!PyArg_ParseTuple(args, "s#is#", &data, &dataLen, &crc,
                            &table, &tableLen)) {
        return NULL;
    }

    if (tableLen != 256*4) {
        PyErr_SetString(PyExc_ValueError, "invalid CRC table");
        return NULL;
    }

    while (dataLen--) {
        crc = table[*data ^ BYTE3(crc)] ^ (crc << 8);
        data++;
    }

    return Py_BuildValue("i", crc);
}

//-----------------------------------------------------------------------------
// Compute a 64-bit crc over the input data.  The data stream is bit reversed
// during the computation.
// Inputs:
//   data - string containing the data
//   crc - unsigned integer containing the initial crc
//   table - string containing the 64-bit table corresponding to the generator
//           polynomial.
// Returns:
//   crc - unsigned integer containing the resulting crc

static PyObject*
_crc64r(PyObject* self, PyObject* args)
{
    UINT64 crc;
    UINT8* data;
    int dataLen;
    UINT64* table;
    int tableLen;

    if (!PyArg_ParseTuple(args, "s#is#", &data, &dataLen, &crc,
                            &table, &tableLen)) {
        return NULL;
    }

    if (tableLen != 256*4) {
        PyErr_SetString(PyExc_ValueError, "invalid CRC table");
        return NULL;
    }

    while (dataLen--) {
        crc = table[*data ^ BYTE0(crc)] ^ (crc >> 8);
        data++;
    }

    return Py_BuildValue("i", crc);
}

//-----------------------------------------------------------------------------
static PyMethodDef methodTable[] = {
{"_crc8", _crc8, METH_VARARGS},
{"_crc8r", _crc8r, METH_VARARGS},
{"_crc16", _crc16, METH_VARARGS},
{"_crc16r", _crc16r, METH_VARARGS},
{"_crc32", _crc32, METH_VARARGS},
{"_crc32r", _crc32r, METH_VARARGS},
{"_crc64", _crc64, METH_VARARGS},
{"_crc64r", _crc64r, METH_VARARGS},
{NULL, NULL}
};

//-----------------------------------------------------------------------------
void init_crcfunext(void)
{
  PyObject *m;

  m = Py_InitModule("_crcfunext", methodTable);
}

