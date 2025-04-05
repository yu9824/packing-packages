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

ENCODING: Literal["utf-8"] = "utf-8"
"""Encoding for file operations.
This is the encoding used for file operations in the project.
It is set to 'utf-8' to ensure compatibility with most text files.
"""
