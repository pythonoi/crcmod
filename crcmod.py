#-----------------------------------------------------------------------------
# crcmod is a Python module for gererating functions that compute the Cyclic
# Redundancy Check.  Any 8, 16, 32, or 64 bit polynomial can be used.  
#
# Copyright (c) 2004  Raymond L. Buvel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#-----------------------------------------------------------------------------
__all__ = '''
'''.split()

# Select the appropriate set of low-level CRC functions for this installation.
# If the extension module was not built, drop back on the Python implementation
# even though it is significantly slower.
try:
    import _crcfunext as _crcfun
    usingExtension = True
except ImportError:
    import _crcfunpy as _crcfun
    usingExtension = False

import sys, struct

#-----------------------------------------------------------------------------
# Naming convention:
# All function names ending with r are bit reverse variants of the ones
# without the r.

#-----------------------------------------------------------------------------
# Check the polynomial to make sure that it is acceptable and return the number
# of bits in the CRC.

def _verifyPoly(poly):
    msg = 'The degree of the polynomial must be 8, 16, 32 or 64'
    poly = long(poly) # Use a common representation for all operations
    for n in 8,16,32,64:
        low = 1L<<n
        high = low*2
        if low <= poly < high:
            return n
    raise msg

#-----------------------------------------------------------------------------
# Bit reverse the input value.

def _bitrev(x, n):
    x = long(x)
    y = 0L
    for i in xrange(n):
        y = (y << 1) | (x & 1L)
        x = x >> 1
    if ((1L<<n)-1) <= sys.maxint:
        return int(y)
    return y

#-----------------------------------------------------------------------------
# The following functions compute the CRC for a single byte.  These are used
# to build up the tables needed in the CRC algorithm.  Assumes the high order
# bit of the polynomial has been stripped off.

def _bytecrc(crc, poly, n):
    crc = long(crc)
    poly = long(poly)
    mask = 1L<<(n-1)
    for i in xrange(8):
        if crc & mask:
            crc = (crc << 1) ^ poly
        else:
            crc = crc << 1
    mask = (1L<<n) - 1
    crc = crc & mask
    if mask <= sys.maxint:
        return int(crc)
    return crc

def _bytecrc_r(crc, poly, n):
    crc = long(crc)
    poly = long(poly)
    for i in xrange(8):
        if crc & 1L:
            crc = (crc >> 1) ^ poly
        else:
            crc = crc >> 1
    mask = (1L<<n) - 1
    crc = crc & mask
    if mask <= sys.maxint:
        return int(crc)
    return crc

#-----------------------------------------------------------------------------
# The following functions compute the table needed to compute the CRC.  The
# table is returned as a list.  Note that the array module does not support
# 64-bit integers on a 32-bit architecture as of Python 2.3.
#
# These routines assume that the polynomial and the number of bits in the CRC
# have been checked for validity by the caller.

def _mkTable(poly, n):
    mask = (1L<<n) - 1
    poly = long(poly) & mask
    table = [_bytecrc(long(i)<<(n-8),poly,n) for i in xrange(256)]
    return table

def _mkTable_r(poly, n):
    mask = (1L<<n) - 1
    poly = _bitrev(long(poly) & mask, n)
    table = [_bytecrc_r(long(i),poly,n) for i in xrange(256)]
    return table

#-----------------------------------------------------------------------------
# Map the CRC size onto the functions that handle these sizes.

_sizeMap = {
     8 : [_crcfun._crc8, _crcfun._crc8r],
    16 : [_crcfun._crc16, _crcfun._crc16r],
    32 : [_crcfun._crc32, _crcfun._crc32r],
    64 : [_crcfun._crc64, _crcfun._crc64r],
}

#-----------------------------------------------------------------------------
# The following function returns a Python function to compute the CRC.  The
# returned function calls a routine written in C to efficiently do the
# calculation.

def mkCrcFun(poly, initCrc=0, rev=False):
    '''Return a function that computes the CRC using the specified polynomial.
    poly - integer representation of the generator polynomial
    initCrc - default initial CRC value
    rev - when true, indicates that the data is processed bit reversed.

    The returned function has the following user interface
    def crcfun(data, crc=initCrc):
    '''

    n = _verifyPoly(poly)

    if rev:
        _table = _mkTable_r(poly, n)
        _fun = _sizeMap[n][1]
    else:
        _table = _mkTable(poly, n)
        _fun = _sizeMap[n][0]

    if usingExtension:
        tableType = {
             8 : '256B',
            16 : '256H',
            32 : '256L',
            64 : '256Q',
        }[n]
        _table = struct.pack(tableType, *_table)

    def crcfun(data, crc=initCrc, table=_table, fun=_fun):
        return fun(data, crc, table)

    return crcfun

