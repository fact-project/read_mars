from setuptools import setup
from Cython.Build import cythonize


setup(
    name='read_mars',
    version='0.0.3',
    author='Maximilian Nöthe',
    author_email='maximilian.noethe@tu-dortmund.de',
    packages=['read_mars'],
    install_requires=[
        'pyfact>=0.9.4',
    ],
    ext_modules=cythonize('read_mars/core.pyx'),
    entry_points={
        'console_scripts': [
            'ganymed_runlist_to_h5py = read_mars.ganymed_runlist_to_h5py:main',
            'mars_to_h5py = read_mars.mars_to_h5py:main',
        ]
    }
)
