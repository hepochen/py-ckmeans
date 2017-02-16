# coding: utf8
from setuptools import setup, find_packages
from distutils.extension import Extension

C_KMEANS = Extension(
    'ckmeans/lib',
    sources=['ckmeans/lib.c'],
    extra_compile_args=['-Wno-error=declaration-after-statement',
                        '-O3', '-std=c99']
)

setup(
    name='ckmeans',
    version='1.0.0',
    install_requires=[],
    description='ckmeans for python',
    include_package_data=True,
    platforms='any',
    packages=find_packages(exclude=('tests',)),
    ext_modules=[C_KMEANS]
)
