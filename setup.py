#!/usr/bin/env python

from distutils.core import setup

setup(name='basewebapi_python',
      version='0.3.1',
      install_requires=['requests'],
      author='Ralph Taylor',
      author_email='djnrrd@gmail.com',
      url='https://github.com/djnrrd/basewebapi',
      description='Basic model for expanding when writing web api wrappers',
      long_description='Basic model for expanding when writing web api '
                       'wrappers',
      license='GPL3',
      packages=['basewebapi']
)
