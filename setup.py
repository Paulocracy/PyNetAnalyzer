#!/usr/bin/env python3
#
# Copyright 2019 PSB & ST
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='cnapy',
    version='0.0.2',
    url='https://github.com/arblab/cnapy/',
    license='GPLv3+',
    description='A CellNetAnalyzer GUI in Python.',
    long_description='TODO: add long_description to setup.py',
    # long_description_content_type="text/asciidoc",
    author='Sven Thiele',
    author_email='sthiele78@gmail.com',
    packages=['cnapy', 'cnapy.gui_elements'],
    package_dir={'cnapy': 'cnapy'},
    package_data={'cnapy': ['data/*.svg']},
    entry_points={'console_scripts': ['cnapy = cnapy.__main__:main_cnapy']},
    # packages not in conda on windows
    # install_requires=['cobra==0.18.1','cameo==0.11.15','qtconsole==4.7.7',]
)
