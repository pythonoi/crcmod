import tarfile, os

version = '1.2'

arcname = 'crcmod-%s.tar.gz' % version
arcdir = 'crcmod-%s' % version

files = '''
README
_crcfunpy.py
crcmod.py
test_crcmod.py
timing_test.py
'''.split()

extfiles = '''
Makefile
_crcfunext.c
setup.py
'''.split()

def addFiles(arc, dir, arcdir, names):
    for name in names:
        fname = os.path.join(dir,name)
        arcname = os.path.join(arcdir,name)
        arc.add(fname, arcname)

arc = tarfile.open(arcname, 'w:gz')
os.chdir('..')

arc.add('crcpkg', arcdir, recursive=False)
addFiles(arc, 'crcpkg', arcdir, files)

arc.add('crcpkg/extmod', arcdir+'/extmod', recursive=False)
addFiles(arc, 'crcpkg/extmod', arcdir+'/extmod', extfiles)
arc.close()

