#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# setup.py
# Description: exm setup file
# -----------------------------------------------------------------------------
#
# Login   <carlos.linares@uc3m.es>
#

"""
exm setup file
"""

# import sys
import setuptools

# import the version file
import sys
sys.path.insert(1, 'exm/')
import exmversion

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="exm",
    version=exmversion.__version__,
    author=exmversion.__author__,
    author_email=exmversion.__email__,
    description=exmversion.__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='GNU General Public License v3 (GPLv3)',
    url="https://github.com/clinaresl/exm",
    keywords="constraints-satisfaction artificial-intelligence",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "exm = exm.exm:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires = [
        "setuptools>=42",
        "wheel",
        "xlsxwriter>=1.3.7",
        "pyexcel>=0.6.6",
        "icalendar>=4.0.7",
        "pytz>=2020.1",
        "python-constraint>=1.4.0"
    ],
    python_requires='>=3.6',
)

# Local Variables:
# mode:python
# fill-column:80
# End:
