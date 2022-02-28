# _kernelutility_ - A Python package for managing Python kernels

> Joseph P. Vantassel, Texas Advanced Computing Center - The University of Texas at Austin

## About _kernelutility_

_kernelutility_ was developed to allow users of the DesignSafe-CyberInfrastructure's
JupyterHub to easily manage their own Python kernels, which include a dedicated Python
interpreter and associated packages.

## Getting Started

- Start a notebook or terminal in DesignSafe's JupyterHub. Note that you must use the latest
Jupyter notebook image.
- Install _kernelutility_ with `!pip install kernelutility` (if in notebook) or
`pip install kernelutility` (if in terminal).
If you are in a notebook you must restart your kernel for the installation of _kernelutility_
to be visible to Python.
- Load kernelset with `from kernelutility import kernelset`. This will initialize your kernel
set and reactivate any prior kernels
if they are present.
- Use the methods of `kernelset` to modify your available kernels. The key methods are `add`,
`remove`, `create`, and `destroy`. See the example `kernelutility.ipynb` and the API documentation
for more information.
