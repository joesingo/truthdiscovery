"""
Adapted from https://github.com/pypa/sampleproject
"""
from os import path

from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

with open(path.join(HERE, "requirements.txt"), encoding="utf-8") as f:
    REQUIREMENTS = f.read().split("\n")

setup(
    name="truthdiscovery",
    version="0.0.1",
    description=("Python3 library implementing a selection of truth-discovery"
                 "algorithms"),
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/joesingo/truthdiscovery",
    author="Joe Singleton",
    author_email="joesingo@gmail.com",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    python_requires=">=3.5",
    # Note: this includes test and code style packages and requirements, which
    # should really go in extras_require...
    install_requires=REQUIREMENTS
)
