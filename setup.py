#!/usr/bin/env python3

from distutils.core import setup

subpackages = ['aircraft', 'system', 'proto', 'base']
pkg = ['pyflightcontrol']
for sp in subpackages:
    pkg.append(pkg[0] + '.' + sp)

setup(name='PyFlightControl',
      version='0.1',
      description='Python Flight Control Software',
      author='Blair Mason',
      author_email='rbmj@verizon.net',
      url='https://github.com/rbmj/pyflightcontrol',
      packages=pkg
)

