#-----------------------------------------------------------------------------
# crcmod is a Python module for gererating objects that compute the Cyclic
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
__all__ = '''mkCrcFun Crc
'''.split()

# Select the appropriate set of low-level CRC functions for this installation.
# If the extension module was not built, drop back to the Python implementation
# even though it is significantly slower.
try:
    import _crcfunext as _crcfun
    _usingExtension = True
except ImportError:
    import _crcfunpy as _crcfun
    _usingExtension = False

import sys, struct

#-----------------------------------------------------------------------------
class Crc:
    def __init__(self, poly, initCrc=~0L, rev=True, initialize=True):
        if not initialize:
            return

        x = _mkCrcFun(poly, initCrc, rev)
        self._crc = x[0]
        self.digest_size = x[1]//8
        self.initCrc = x[2]
        self.table = x[3]
        self.crcValue = self.initCrc
        self.reverse = rev
        self.poly = poly

    def new(self, arg=None):
        n = Crc(poly=None, initialize=False)
        n._crc = self._crc
        n.digest_size = self.digest_size
        n.initCrc = self.initCrc
        n.table = self.table
        n.crcValue = self.initCrc
        n.reverse = self.reverse
        n.poly = self.poly
        if arg is not None:
            n.update(arg)
        return n

    def copy(self):
        c = self.new()
        c.crcValue = self.crcValue
        return c

    def update(self, data):
        self.crcValue = self._crc(data, self.crcValue)

    def digest(self):
        n = self.digest_size
        crc = self.crcValue
        lst = []
        while n > 0:
            lst.append(chr(crc & 0xFF))
            crc = crc >> 8
            n -= 1
        lst.reverse()
        return ''.join(lst)

    def hexdigest(self):
        n = self.digest_size
        crc = self.crcValue
        lst = []
        while n > 0:
            lst.append('%02X' % (crc & 0xFF))
            crc = crc >> 8
            n -= 1
        lst.reverse()
        return ''.join(lst)

    def generateCode(self, functionName, out, dataType=None, crcType=None):
        if dataType is None:
            dataType = 'UINT8'

        if crcType is None:
            crcType = 'UINT%d' % (8*self.digest_size)

        if self.digest_size == 1:
            crcAlgor = 'table[*data ^ (%s)crc]'
        elif self.reverse:
            crcAlgor = 'table[*data ^ (%s)crc] ^ (crc >> 8)'
        else:
            shift = 8*(self.digest_size - 1)
            crcAlgor = 'table[*data ^ (%%s)(crc >> %d)] ^ (crc << 8)' % shift

        fmt = '0x%%0%dX' % (2*self.digest_size)
        if self.digest_size <= 4:
            fmt = fmt + 'U,'
        else:
            fmt = fmt + 'ULL,'

        n = {1:8, 2:8, 4:4, 8:2}[self.digest_size]

        lst = []
        for i, val in enumerate(self.table):
            if (i % n) == 0:
                lst.append('\n    ')
            lst.append(fmt % val)

        poly = 'polynomial: 0x%X' % self.poly
        if self.reverse:
            poly = poly + ', bit reverse algorithm'

        parms = {
            'dataType' : dataType,
            'crcType' : crcType,
            'name' : functionName,
            'crcAlgor' : crcAlgor % dataType,
            'crcTable' : ''.join(lst),
            'poly' : poly,
        }
        out.write(_codeTemplate % parms) 

#-----------------------------------------------------------------------------
def mkCrcFun(poly, initCrc=~0L, rev=True):
    '''Return a function that computes the CRC using the specified polynomial.

    poly - integer representation of the generator polynomial
    initCrc - default initial CRC value
    rev - when true, indicates that the data is processed bit reversed.

    The returned function has the following user interface
    def crcfun(data, crc=initCrc):
    '''

    return _mkCrcFun(poly, initCrc, rev)[0]

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
    raise ValueError(msg)

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
# Build a mapping of size to struct module type code.  This table is
# constructed dynamically so that it has the best chance of picking the best
# code to use for the platform we are running on.  This should properly adapt
# to 32 and 64 bit machines.

_sizeToTypeCode = {}

for typeCode in 'B H I L Q'.split():
    size = {1:8, 2:16, 4:32, 8:64}.get(struct.calcsize(typeCode),None)
    if size is not None and size not in _sizeToTypeCode:
        _sizeToTypeCode[size] = '256%s' % typeCode

del typeCode, size

#-----------------------------------------------------------------------------
# The following function returns a Python function to compute the CRC.  The
# returned function calls a low level function that is written in C if the
# extension module could be loaded.  Otherwise, a Python implementation is
# used.  In addition to this function, the size of the CRC, the initial CRC,
# and a list containing the CRC table are returned.

def _mkCrcFun(poly, initCrc, rev):
    size = _verifyPoly(poly)

    # Adjust the initial CRC to the correct data type (unsigned value).
    mask = (1L<<size) - 1
    initCrc = long(initCrc) & mask
    if mask <= sys.maxint:
        initCrc = int(initCrc)

    if rev:
        tableList = _mkTable_r(poly, size)
        _fun = _sizeMap[size][1]
    else:
        tableList = _mkTable(poly, size)
        _fun = _sizeMap[size][0]

    _table = tableList
    if _usingExtension:
        _table = struct.pack(_sizeToTypeCode[size], *tableList)

    def crcfun(data, crc=initCrc, table=_table, fun=_fun):
        return fun(data, crc, table)

    return crcfun, size, initCrc, tableList

#-----------------------------------------------------------------------------
_codeTemplate = '''// Automatically generated CRC function
// %(poly)s
%(crcType)s
%(name)s(%(dataType)s *data, int len, %(crcType)s crc)
{
    static const %(crcType)s table[256] = {%(crcTable)s
    };
  
    while(len > 0) {
        crc = %(crcAlgor)s;
        data++;
        len--;
    }
    return crc;
}
'''

