# -*- coding: utf-8 -*-

import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="pyver",
    version="0.2",
    description="version control for dummies",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/nagordon/pyver",
    author="Neal Gordon",
)