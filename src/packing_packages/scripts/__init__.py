"""Generate standalone install scripts for packed packages.

The generated scripts (``install_packages.bat`` / ``install_packages.sh``)
do not depend on this package and can be distributed independently.

.. code-block:: bash

    $ python -m packing_packages scripts --help

    or

    $ packing-packages scripts --help

"""

from ._core import generate_install_scripts

__all__ = ("generate_install_scripts",)
