#!/usr/bin/env python

from setuptools import setup
import os

reqs = []
if os.path.isfile('requirements.txt'):
    with open('requirements.txt') as f:
        required = f.read().splitlines()
    reqs.extend(required)

long_descr = None
if os.path.isfile('README.md'):
    with open("README.md", "rb") as f:
        long_descr = f.read().decode("utf-8")
 
params = {
    'data_files': [],
}

setup(name='crow-plot',
    version='0.1',
    description='Crow-plot - visualization library for crow data.',
    long_description = long_descr,
    url='http://github.com/acopar/crow-plot',
    author='Andrej Copar',
    author_email='andrej.copar@gmail.com',
    license='LGPL',
    packages=[
        'crowpl',
    ],
    entry_points = {
        "console_scripts": ['crow-plot = crowpl.__main__:main']
    },
    zip_safe=False,
    install_requires=reqs,
    **params
)

