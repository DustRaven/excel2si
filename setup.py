"""
Setup script for the CSV2JSON package.
"""

import os
from setuptools import setup, find_packages


def read_file(filename):
    with open(filename, encoding='utf-8') as f:
        return f.read()


# Get version from package
about = {}
with open(os.path.join('src', 'csv2json', '__init__.py'), encoding='utf-8') as f:
    exec(f.read(), about)

setup(
    name="csv2json",
    version=about['__version__'],
    description="Convert Excel/CSV files to JSON with support for nested structures",
    long_description=read_file('README.md'),
    long_description_content_type="text/markdown",
    author="CSV2JSON Team",
    author_email="example@example.com",
    url="https://github.com/example/csv2json",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "csv2json.data": ["*.dt"],
    },
    install_requires=[
        "pandas>=2.0.0",
        "PyQt6>=6.5.0",
        "openpyxl>=3.1.2",
    ],
    entry_points={
        "console_scripts": [
            "csv2json=csv2json.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
