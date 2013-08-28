#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()

required = [
    'requests>=1.2.0',
    'pyquery==1.2.4',
    'mwparserfromhell==0.1.1',
]

setup(
    name='wikipedia_template_parser',
    version='0.1',
    description='Simple library for extracting data from Wikipedia templates',
    author='Federico Scrinzi',
    author_email='scrinzi@spaziodati.eu',
    url='https://github.com/SpazioDati/Wikipedia-Template-Parser',
    packages= ['wikipedia_template_parser'],
    install_requires=required,
    license='MIT',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Internet',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)
