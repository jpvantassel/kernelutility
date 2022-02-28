"""A setuptools based setup module."""

from setuptools import setup, find_packages


def parse_meta(path_to_meta):
    with open(path_to_meta) as f:
        meta = {}
        for line in f.readlines():
            if line.startswith("__version__"):
                meta["__version__"] = line.split('"')[1]
    return meta

meta = parse_meta("kernelutility/meta.py")

with open('README.md', "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='kernelutility',
    version=meta['__version__'],
    description='A Python package for managing Python kernels',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jpvantassel/kernelutility',
    author='Joseph P. Vantassel',
    author_email='jvantassel@tacc.utexas.edu',
    classifiers=[
        "Development Status :: 4 - Beta",

        "Framework :: Jupyter",
        "Framework :: Jupyter :: JupyterLab",

        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",

        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords='jupyter kernel conda',
    packages=find_packages(),
    python_requires='>3.7',
    install_requires=[],
    extras_require={
    },
    package_data={
    },
    data_files=[
    ],
    entry_points={
    },
    project_urls={
    },
)
