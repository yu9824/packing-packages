from typing import Literal

EXTENSIONS_CONDA: tuple[Literal["tar.bz2"], Literal["conda"]] = (
    "tar.bz2",
    "conda",
)
"""Extensions for conda packages.

These are the extensions used by conda packages.
"""

EXTENSIONS_PYPI: tuple[Literal["whl"], Literal["tar.gz"]] = (
    "whl",
    "tar.gz",
)
"""Extensions for PyPI packages.

These are the extensions used by PyPI packages.
"""
