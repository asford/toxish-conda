#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

from setuptools import find_packages, setup

REQUIRED = ["torch"]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

setup(
    name="proj",
    version=None,
    description="A minimum demo project.",
    author="Alex Ford",
    author_email="fordas@uw.edu",
    python_requires=">=2.7.0",
    url="https://github.com/asford/toxish-conda",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
)
