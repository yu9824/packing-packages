"""utils module for packing_packages.

This module provides utility functions and classes for the packing_packages package.
It includes functions for checking if a package is installed, creating dummy progress bars,
and checking if an argument is passed to a function.
"""

from ._helpers import (
    check_encoding,
    check_env_name,
    dummy_tqdm,
    get_env_list,
    is_argument,
    is_installed,
)
from ._package_files import (
    PACKAGES_FOR_BUILD,
    get_conda_sorted_packages_path,
    get_pypi_sorted_packages_path,
)

# ドキュメント化したい場合は、モジュールメソッドとして登録するため、__all__に入れる。
__all__ = (
    "PACKAGES_FOR_BUILD",
    "check_encoding",
    "check_env_name",
    "dummy_tqdm",
    "get_conda_sorted_packages_path",
    "get_env_list",
    "get_pypi_sorted_packages_path",
    "is_argument",
    "is_installed",
)
