"""Install packages for the packing_packages project.

This module provides a function to install packages from a specified
directory into a conda environment.
"""

from ._core import install_packages

__all__ = ("install_packages",)
