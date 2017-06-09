#! /usr/bin/env python
# from ez_setup import use_setuptools
# use_setuptools()
from setuptools import setup, find_packages


setup(name='anugaBMI',
      version='0.1.0',
      author='Mariela Perignon',
      author_email='perignon@colorado.edu',
      license='MIT',
      description="Add-on package to use ANUGA within WMT",
      long_description=open('README.md').read(), dependency_links=['https://github.com/mperignon/anuga_core/tarball/master#egg=anuga'],
      packages=find_packages(exclude=['*.test*']),
setup_requires=['numpy', 'Cython'],
      url='https://github.com/mperignon/anuga_BMI',
      install_requires=['basic-modeling-interface',
                        'PyYAML',
                        'anuga',
                        'netCDF4',
                        'matplotlib',
                        'scipy']
)
