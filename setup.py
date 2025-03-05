"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="exceltojson",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "xlrd>=2.0.1",
        "six>=1.16.0",
        "openpyxl>=3.1.2"
    ],
    entry_points={
        'console_scripts': [
            'excel2json=excel2json:main',
        ],
    },
    author="malongge",
    author_email="",
    description="将Excel文件转换为JSON格式的工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="excel json converter",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
