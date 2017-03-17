# !/usr/bin/env python

from setuptools import setup

setup(name='symbtrsynthesis',
      version='1.0.0-dev',
      description='An (adaptive) synthesizer for SymbTr-MusicXML scores',
      author='Hasan Sercan Atli',
      url='https://github.com/hsercanatli/symbtrsynthesis',
      packages=['symbtrsynthesis'],
      include_package_data=True, install_requires=['numpy']
      )
