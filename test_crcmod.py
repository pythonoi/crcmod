#-----------------------------------------------------------------------------
# Test script for crcmod.
#-----------------------------------------------------------------------------

from crcmod import mkCrcFun

#-----------------------------------------------------------------------------
# Test function to verify CRC functions against the test cases listed in
# Numerical Recipes in C.

msg = 'CatMouse987654321'

def checkResult(crc, expected):
    if crc != expected:
        print 'Expected: 0x%X, Got: 0x%X' % (expected, crc)
        raise RuntimeError('Test failed')

def test(crcfun, v0, v1):
    checkResult(crcfun('T'), v0)
    checkResult(crcfun(msg), v1)
    checkResult(crcfun('',0), 0)
    checkResult(crcfun(msg[4:], crcfun(msg[:4])), v1)
    checkResult(crcfun(msg[-1], crcfun(msg[:-1])), v1)

#-----------------------------------------------------------------------------
# This polynomial was chosen because it is the product of two irreducible
# polynomials.
# g8 = (x^7+x+1)*(x+1)

g8 = 0x185
test(mkCrcFun(g8,0,0),  0xFE, 0x9D)
test(mkCrcFun(g8,-1,1), 0x4F, 0x9B)
test(mkCrcFun(g8,0,1),  0xFE, 0x62)

#-----------------------------------------------------------------------------
# The following reproduces all of the entries in the Numerical Recipes table.
# This is the standard CCITT polynomial.

g16 = 0x11021
test(mkCrcFun(g16,0,0),  0x1A71, 0xE556)
test(mkCrcFun(g16,-1,1), 0x1B26, 0xF56E)
test(mkCrcFun(g16,0,1),  0x14A1, 0xC28D)

#-----------------------------------------------------------------------------
# This is the standard AUTODIN-II polynomial which appears to be used in a
# wide variety of standards and applications.

g32 = 0x104C11DB7
test(mkCrcFun(g32,0,0), 0x6B93DDDB, 0x12DCA0F4)
test(mkCrcFun(g32,0xFFFFFFFFL,1), 0x41FB859FL, 0xF7B400A7L)
test(mkCrcFun(g32,0,1), 0x6C0695EDL, 0xC1A40EE5L)

#-----------------------------------------------------------------------------
# The binascii module has a 32-bit CRC function that is used in a wide range
# of applications including the checksum used in the ZIP file format.  This
# test is to use crcmod to reproduce the same function.

from binascii import crc32 as crc32binascii

# Work around the future warning on constants.
def crc32(d, crc=0):
    if crc > 0x7FFFFFFFL:
        x = int(crc & 0x7FFFFFFFL)
        crc = x | -2147483648
    x = crc32binascii(d,crc)
    return long(x) & 0xFFFFFFFFL

# The following function produces the same result as crc32.
def try32(d, crc=0, fun=mkCrcFun(g32,0,1)):
  return fun(d, crc ^ 0xFFFFFFFFL) ^ 0xFFFFFFFFL

test(crc32, 0xBE047A60L, 0x084BFF58L)
test(try32, 0xBE047A60L, 0x084BFF58L)

#-----------------------------------------------------------------------------
# This class is used to check the CRC calculations against a direct
# implementation using polynomial division.

class poly:
  '''Class implementing polynomials over the field of integers mod 2'''
  def __init__(self,p):
    p = long(p)
    if p < 0: raise 'invalid polynomial'
    self.p = p

  def __long__(self):
    return self.p

  def __eq__(self,other):
    return self.p == other.p

  def __ne__(self,other):
    return self.p != other.p

  # To allow sorting of polynomials, use their long integer form for comparison
  def __cmp__(self,other):
    return cmp(self.p, other.p)

  def __nonzero__(self):
    return self.p != 0L

  def __neg__(self):
    return self # These polynomials are their own inverse under addition

  def __invert__(self):
    n = max(self.deg() + 1, 1)
    x = (1L << n) - 1
    return poly(self.p ^ x)

  def __add__(self,other):
    return poly(self.p ^ other.p)

  def __sub__(self,other):
    return poly(self.p ^ other.p)

  def __mul__(self,other):
    a = self.p
    b = other.p
    if a == 0 or b == 0: return poly(0)
    x = 0L
    while b:
      if b&1:
        x = x ^ a
      a = a<<1
      b = b>>1
    return poly(x)

  def __divmod__(self,other):
    u = self.p
    m = self.deg()
    v = other.p
    n = other.deg()
    if v == 0: raise ZeroDivisionError, 'polynomial division by zero'
    if n == 0: return (self,poly(0))
    if m < n: return (poly(0),self)
    k = m-n
    a = 1L << m
    v = v << k
    q = 0L
    while k > 0:
      if a & u:
        u = u ^ v
        q = q | 1L
      q = q << 1
      a = a >> 1
      v = v >> 1
      k -= 1
    if a & u:
      u = u ^ v
      q = q | 1L
    return (poly(q),poly(u))

  def __div__(self,other):
    return self.__divmod__(other)[0]

  def __mod__(self,other):
    return self.__divmod__(other)[1]

  def __repr__(self):
    return 'poly(0x%XL)' % self.p

  def __str__(self):
    p = self.p
    if p == 0: return '0'
    lst = { 0:[], 1:['1'], 2:['x'], 3:['1','x'] }[p&3]
    p = p>>2
    n = 2
    while p:
      if p&1: lst.append('x^%d' % n)
      p = p>>1
      n += 1
    lst.reverse()
    return '+'.join(lst)

  def deg(self):
    '''return the degree of the polynomial'''
    a = self.p
    if a == 0: return -1
    n = 0
    while a >= 0x10000L:
      n += 16
      a = a >> 16
    a = int(a)
    while a > 1:
      n += 1
      a = a >> 1
    return n

#-----------------------------------------------------------------------------
# The following functions compute the CRC using direct polynomial division.
# These functions are checked against the result of the table driven
# algorithms.

g8p = poly(g8)
x8p = poly(0x100)
def crc8p(d):
  d = map(ord, d)
  p = 0L
  for i in d:
    p = p*256L + i
  p = poly(p)
  return long(p*x8p%g8p)

g16p = poly(g16)
x16p = poly(0x10000)
def crc16p(d):
  d = map(ord, d)
  p = 0L
  for i in d:
    p = p*256L + i
  p = poly(p)
  return long(p*x16p%g16p)

g32p = poly(g32)
x32p = poly(0x100000000)
def crc32p(d):
  d = map(ord, d)
  p = 0L
  for i in d:
    p = p*256L + i
  p = poly(p)
  return long(p*x32p%g32p)

# Check the CRC calculations against the same calculation done directly with
# polynomial division.

test(mkCrcFun(g8,0,0),  crc8p('T'),  crc8p(msg))
test(mkCrcFun(g16,0,0), crc16p('T'), crc16p(msg))
test(mkCrcFun(g32,0,0), crc32p('T'), crc32p(msg))

print 'All tests PASS'

