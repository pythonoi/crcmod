import os, shutil

version = '1.3'

curdir = os.getcwd()
crcdir = os.path.join(curdir,'dist/crcmod-%s' % version)
moddir = os.path.join(crcdir,'crcmod')
srcdir = os.path.join(crcdir,'src')
testdir = os.path.join(crcdir,'test')

#-----------------------------------------------------------------------------
# Clean out any previous distribution and create the base directories.
if os.path.isdir(crcdir):
    shutil.rmtree(crcdir)

os.makedirs(crcdir)
os.makedirs(moddir)
os.makedirs(srcdir)
os.makedirs(testdir)

#-----------------------------------------------------------------------------
def copy(fname, dir):
    dst = os.path.join(dir,fname)
    src = os.path.join(curdir,fname)
    shutil.copyfile(src, dst)

#-----------------------------------------------------------------------------

copy('README', crcdir)
copy('changelog', crcdir)

copy('crcmod.py', moddir)
copy('_crcfunpy.py', moddir)

fd = open(os.path.join(moddir,'__init__.py'),'w')
fd.write('''from crcmod import *
__doc__ = crcmod.__doc__
''')
fd.close()

shutil.copyfile('extmod/_crcfunext.c', os.path.join(srcdir,'_crcfunext.c'))

copy('test_crcmod.py', testdir)
copy('timing_test.py', testdir)

basic = '''setup(
name='crcmod',
version='%s',
description='CRC Generator',
author='Ray Buvel',
author_email='rlbuvel@gmail.com',
url='http://crcmod.sourceforge.net/',
packages=['crcmod'],
''' % version

setup = '''from distutils.core import setup
from distutils.extension import Extension

%s
ext_modules=[ 
    Extension('crcmod._crcfunext', ['src/_crcfunext.c', ],
    ),
],
)
''' % basic

setup_py = '''from distutils.core import setup

%s
)
''' % basic

fd = open(os.path.join(crcdir,'setup.py'),'w')
fd.write(setup)
fd.close()

fd = open(os.path.join(crcdir,'setup_py.py'),'w')
fd.write(setup_py)
fd.close()
