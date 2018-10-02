# !/usr/bin/env python

from setuptools import setup, find_packages

setup(name='symbtrsynthesis',
      version='1.0.1-dev',
      description='An (adaptive) synthesizer for SymbTr-MusicXML scores',
      author='Hasan Sercan Atli',
      url='https://github.com/hsercanatli/symbtrsynthesis',
      packages=find_packages(),
      include_package_data=True, install_requires=['numpy']
      )
