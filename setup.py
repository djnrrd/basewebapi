#!/usr/bin/env python

import distutils.core

name = 'basewebapi_python'

distutils.core.setup(name=name,
    version='0.1.1',
    author="Ralph Taylor",
    author_email="djnrrd@gmail.com",
    url="https://github.com/djnrrd/basewebapi",
    description="Basic model for expanding when writing web api wrappers",
    long_description="Basic model for expanding when writing web api wrappers",
    license="GPL3",
    packages = [ 'basewebapi' ]
)
