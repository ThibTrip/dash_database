import setuptools
import os

here = os.path.abspath(os.path.dirname(__file__))
description = 'Manages user values for a dash app.'

# Import the README and use it as the long-description.
try:
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = description


with open(os.path.join(here, "requirements.txt"),"r") as f:
    requirements = [line.strip() for line in f.readlines()]


setuptools.setup(
    name="dash_database",
    version="0.1",
    author="Thibault Bétrémieux",
    author_email="thibault.betremieux@gmail.com",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires= requirements,
    classifiers=["Programming Language :: Python :: 3",
                 "License :: None",
                 "Operating System :: OS Independent"])
