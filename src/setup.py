import sys
import setuptools

with open('README.md', "r") as fh:
    long_description = fh.read()

install_requires = [
    "requests"
]

if sys.version_info < (3, 0):
    install_requires = ["future"]


setuptools.setup(
    name="ForemanApiUtilites",
    version="1.0.0",
    author="tschneider",
    author_email="tschneider@live.com",
    description="A lightweight library for interacting with a Foreman API v2.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires= install_requires,
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "LICENSE :: OSI APPROVED :: GNU GENERAL PUBLIC LICENSE V3 (GPLV3)",
        "Operating System :: OS Independent",
    ],
)