# -*- coding: utf-8 -*-

import pathlib
from distutils.core import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="pyver-vc",
    version="0.2",
    description="version control for dummies",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/nagordon/pyver",
    author="Neal Gordon",
    py_modules=['pyver']
)
