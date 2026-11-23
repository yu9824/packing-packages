"""Install packages for the packing_packages project.

This module provides a function to install packages from a specified
directory into a conda environment.

.. code-block:: bash

    $ python -m packing_packages install --help

    or

    $ packing-packages install --help

"""

from packing_packages.scripts import generate_install_scripts

from ._core import install_packages

__all__ = ("install_packages", "generate_install_scripts")
