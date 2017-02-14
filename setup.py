#!/usr/bin/python

from confu import __version__, __maintainer__, __email__
from setuptools import setup, find_packages


setup(
    name="confu",
    version=__version__,
    description="Configuration generator for Ninja build system",
    url="https://github.com/Maratyszcza/confu",
    packages=find_packages(),
    scripts=["bin/confu"],
    keywords=["build", "ninja"],
    maintainer=__maintainer__,
    maintainer_email=__email__,
    requires=[],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools"
    ],
    setup_requires=["six"],
    install_requires=["six", "pygit2", "ninja_syntax>=1.7.2"])
