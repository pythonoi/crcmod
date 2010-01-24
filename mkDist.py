import os, shutil

version = '1.6'

curdir = os.getcwd()

crcdir = os.path.join(curdir,'dist/crcmod-%s' % version)
moddir = os.path.join(crcdir,'crcmod')
srcdir = os.path.join(crcdir,'src')
testdir = os.path.join(crcdir,'test')

curdir3 = os.path.join(curdir,'py3')

crcdir3 = os.path.join(crcdir,'py3')
moddir3 = os.path.join(crcdir3,'crcmod')
srcdir3 = os.path.join(crcdir3,'src')
testdir3 = os.path.join(crcdir3,'test')

#-----------------------------------------------------------------------------
# Clean out any previous distribution and create the base directories.
if os.path.isdir(crcdir):
    shutil.rmtree(crcdir)

os.makedirs(crcdir)
os.makedirs(moddir)
os.makedirs(srcdir)
os.makedirs(testdir)

os.makedirs(crcdir3)
os.makedirs(moddir3)
os.makedirs(srcdir3)
os.makedirs(testdir3)

#-----------------------------------------------------------------------------
def copy(fname, dir):
    dst = os.path.join(dir,fname)
    src = os.path.join(curdir,fname)
    shutil.copyfile(src, dst)

def copy3(fname, dir):
    dst = os.path.join(dir,fname)
    src = os.path.join(curdir3,fname)
    shutil.copyfile(src, dst)

#-----------------------------------------------------------------------------

copy('README', crcdir)
copy('changelog', crcdir)

copy('crcmod.py', moddir)
copy('_crcfunpy.py', moddir)
copy('predefined.py', moddir)

copy3('crcmod.py', moddir3)
copy3('_crcfunpy.py', moddir3)
copy3('predefined.py', moddir3)

init_file = os.path.join(moddir,'__init__.py')

fd = open(init_file,'w')
fd.write('''try:
    from crcmod.crcmod import *
except ImportError:
    # Make this backward compatible
    from crcmod import *
__doc__ = crcmod.__doc__
''')
fd.close()

shutil.copyfile(init_file, os.path.join(moddir3,'__init__.py'))

shutil.copyfile('extmod/_crcfunext.c', os.path.join(srcdir,'_crcfunext.c'))

shutil.copyfile('py3/extmod/_crcfunext.c', os.path.join(srcdir3,'_crcfunext.c'))

copy('test_crcmod.py', testdir)
copy('timing_test.py', testdir)

copy3('test_crcmod.py', testdir3)

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

fd = open(os.path.join(crcdir3,'setup.py'),'w')
fd.write(setup)
fd.close()

fd = open(os.path.join(crcdir3,'setup_py.py'),'w')
fd.write(setup_py)
fd.close()
