#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# setup.py
from setuptools import setup

setup(
        name='akira',
        version='1.5.1',
        author='Vikas Munshi',
        author_email='vikas.munshi@gmail.com',
        url='https://github.com/vikasmunshi/tic_tac_toe.git',
        description='Tic Tac Toe Tournament',
        packages=['tic_tac_toe', 'tic_tac_toe.strategies'],
        package_dir={'tic_tac_toe': 'tic_tac_toe'},
        install_requires=['numpy > 1.14'],
        license='MIT License',
        platforms=['any'],
        long_description=open('README.md').read()
)
