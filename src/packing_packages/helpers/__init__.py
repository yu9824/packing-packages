"""utils module for packing_packages.

This module provides utility functions and classes for the packing_packages package.
It includes functions for checking if a package is installed, creating dummy progress bars,
and checking if an argument is passed to a function.
"""

from ._helpers import (
    check_encoding,
    check_env_name,
    dummy_tqdm,
    is_argument,
    is_installed,
)

# ドキュメント化したい場合は、モジュールメソッドとして登録するため、__all__に入れる。
__all__ = (
    "check_encoding",
    "check_env_name",
    "dummy_tqdm",
    "is_argument",
    "is_installed",
)
