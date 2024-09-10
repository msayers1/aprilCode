from distutils.core import setup
setup(
    name='pyb', 
    version='0.5',
    py_modules=['pyb'],
    packages=['pyb','pyb.tasks'],
    author='Anthony Eden',
    author_email='me@anthonyeden.com',
    url='http://pyb.sf.net/',
    download_url='http://pyb.sf.net/download.html',
    description='Ant-like build tool',
    long_description='Ant-like build tool which uses Python build scripts',
    license='GPL',
    platforms=['Any'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools'
    ],
)
