import os, shutil

version = '1.7'

curdir = os.getcwd()

crcdir = os.path.join(curdir,'dist/crcmod-%s' % version)

curdir2 = os.path.join(curdir,'python2')

crcdir2 = os.path.join(crcdir,'python2')
moddir2 = os.path.join(crcdir2,'crcmod')
srcdir2 = os.path.join(crcdir2,'src')
testdir2 = os.path.join(crcdir2,'test')

curdir3 = os.path.join(curdir,'python3')

crcdir3 = os.path.join(crcdir,'python3')
moddir3 = os.path.join(crcdir3,'crcmod')
srcdir3 = os.path.join(crcdir3,'src')
testdir3 = os.path.join(crcdir3,'test')

#-----------------------------------------------------------------------------
# Clean out any previous distribution and create the base directories.
if os.path.isdir(crcdir):
    shutil.rmtree(crcdir)

os.makedirs(crcdir2)
os.makedirs(moddir2)
os.makedirs(srcdir2)
os.makedirs(testdir2)

os.makedirs(crcdir3)
os.makedirs(moddir3)
os.makedirs(srcdir3)
os.makedirs(testdir3)

#-----------------------------------------------------------------------------
def copy(fname, dir):
    dst = os.path.join(dir,fname)
    src = os.path.join(curdir,fname)
    shutil.copyfile(src, dst)

def copy2(fname, dir):
    dst = os.path.join(dir,fname)
    src = os.path.join(curdir2,fname)
    shutil.copyfile(src, dst)

def copy3(fname, dir):
    dst = os.path.join(dir,fname)
    src = os.path.join(curdir3,fname)
    shutil.copyfile(src, dst)

#-----------------------------------------------------------------------------

copy('README', crcdir)
copy('changelog', crcdir)

copy2('crcmod.py', moddir2)
copy2('_crcfunpy.py', moddir2)
copy2('predefined.py', moddir2)

copy3('crcmod.py', moddir3)
copy3('_crcfunpy.py', moddir3)
copy3('predefined.py', moddir3)

init_file = os.path.join(moddir2,'__init__.py')

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

shutil.copyfile('python2/extmod/_crcfunext.c', os.path.join(srcdir2,'_crcfunext.c'))

shutil.copyfile('python3/extmod/_crcfunext.c', os.path.join(srcdir3,'_crcfunext.c'))

copy2('test_crcmod.py', testdir2)
copy2('timing_test.py', testdir2)

copy3('test_crcmod.py', testdir3)


setup = '''from distutils.core import setup
from distutils.extension import Extension
import sys,os

if sys.version_info[0] == 2:
    base_dir = 'python2'
elif sys.version_info[0] == 3:
    base_dir = 'python3'

setup_dict = dict(
name='crcmod',
version='%s',
description='CRC Generator',
author='Ray Buvel',
author_email='rlbuvel@gmail.com',
url='http://crcmod.sourceforge.net/',
packages=['crcmod'],
package_dir={
    'crcmod' : os.path.join(base_dir,'crcmod'),
},

ext_modules=[ 
    Extension('crcmod._crcfunext', [os.path.join(base_dir,'src/_crcfunext.c'), ],
    ),
],
)

try:
    setup(**setup_dict)
except:
    del setup_dict['ext_modules']
    setup(**setup_dict)
''' % version


fd = open(os.path.join(crcdir,'setup.py'),'w')
fd.write(setup)
fd.close()

