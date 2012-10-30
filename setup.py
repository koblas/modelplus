#!/usr/bin/env python
import os

version = '0.1.0'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='modelplus',
      version=version,
      description='Python Containers and Simple Models for Redis, MongoDB, Riak, MySQL',
      url='http://github.com/koblas/modelplus',
      download_url='',
      long_description=read('README.rst'),
      install_requires=read('requirements.txt').splitlines(),
      author='David Koblas',
      author_email='david@koblas.com',
      maintainer='David Koblas',
      maintainer_email='david@koblas.com',
      keywords=['NoSQL', 'model', 'container'],
      license='MIT',
      packages=['modelplus'],
      test_suite='tests.all_tests',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
    )

