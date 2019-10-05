"""
Adapted from https://github.com/pypa/sampleproject
"""
from os import path

from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

REQUIREMENTS = [
    "alabaster==0.7.12",
    "astroid==2.1.0",
    "atomicwrites==1.3.0",
    "attrs==18.2.0",
    "Babel==2.6.0",
    "bidict==0.18.0",
    "certifi==2018.11.29",
    "chardet==3.0.4",
    "Click==7.0",
    "coverage==4.5.2",
    "cycler==0.10.0",
    "docutils==0.14",
    "Flask==1.0.2",
    "idna==2.8",
    "imageio==2.5.0",
    "imagesize==1.1.0",
    "isort==4.3.4",
    "itsdangerous==1.1.0",
    "Jinja2==2.10.3",
    "kiwisolver==1.0.1",
    "lazy-object-proxy==1.3.1",
    "MarkupSafe==1.1.1",
    "matplotlib==3.0.2",
    "mccabe==0.6.1",
    "more-itertools==5.0.0",
    "numpy==1.16.1",
    "packaging==19.0",
    "Pillow==5.4.1",
    "pluggy==0.8.1",
    "py==1.7.0",
    "pycairo==1.18.0",
    "pycodestyle==2.5.0",
    "Pygments==2.3.1",
    "pylint==2.2.2",
    "pyparsing==2.3.1",
    "pytest==4.2.0",
    "python-dateutil==2.8.0",
    "pytz==2018.9",
    "PyYAML==5.1.2",
    "requests==2.21.0",
    "scipy==1.2.1",
    "six==1.12.0",
    "snowballstemmer==1.2.1",
    "Sphinx==1.8.4",
    "sphinxcontrib-websupport==1.1.0",
    "typed-ast==1.3.0",
    "Werkzeug==0.16.0",
    "wrapt==1.11.1",
]

setup(
    name="truthdiscovery",
    version="1.0.2",
    description=("Python3 library implementing a selection of truth discovery "
                 "algorithms"),
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/joesingo/truthdiscovery",
    author="Joe Singleton",
    author_email="joesingo@gmail.com",
    packages=find_packages(exclude=["contrib", "doc", "tests"]),
    python_requires=">=3.5",
    # Note: this includes test and code style packages and requirements, which
    # should really go in extras_require...
    install_requires=REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "truthdiscovery=truthdiscovery.client.cli:main"
        ]
    }
)
