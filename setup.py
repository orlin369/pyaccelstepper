#!/usr/bin/env python
# -*- coding: utf8 -*-

"""

MIT License

Copyright (c) [2023] [Orlin Dimitrov]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial SerialPortions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import sys

from setuptools import find_packages, setup

import pyaccellstepper

#region File Attributes

__author__ = "Orlin Dimitrov"
"""Author of the file."""

__copyright__ = "Copyright 2023, Orlin Dimitrov"
"""Copyright holder"""

__credits__ = []
"""Credits"""

__license__ = "MIT"
"""License
"""

__version__ = "1.0.0"
"""Version of the file."""

__maintainer__ = "Orlin Dimitrov"
"""Name of the maintainer."""

__email__ = "robko01@8bitclub.com"
"""E-mail of the author."""

__status__ = "Debug"
"""File status."""

#endregion

def long_description():
    with open('README.md', encoding='utf-8') as f:
        return f.read()

install_requires = ["pygame", "pyserial",\
               "PySide6", "PySide6-Addons",\
               "PySide6-Essentials", "shiboken6"],

setup(
    name="robko01",
    packages=find_packages(include=["robko01", 'robko01.*']),
    entry_points={
        'console_scripts': [
            'robko01 = robko01.__main__:main'
        ]
    },
    version=__version__,
    description="Robko 01 control library.",
    long_description=long_description(),
    long_description_content_type='text/markdown',
    author=__author__,
    license=__license__,
    author_email=__email__,
    python_requires='>=3.7',
    install_requires=install_requires,
    setup_requires=[],
    tests_require=[],
    test_suite="",
    project_urls={
        'GitHub': 'https://github.com/robko01/app_python3',
    },
    classifiers=[
        'Development Status :: 1 - Debug',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: GPLv3 License',
        'Topic :: Software Development',
        'Topic :: Robot Programming'
    ],
    package_data={'robko01.tasks.task_ui_qt.ui': ['*.ui']}
)
