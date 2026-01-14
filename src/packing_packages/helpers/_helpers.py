import importlib.util
import inspect
import os
import subprocess
import sys
from collections.abc import Callable, Iterable, Iterator
from typing import Any, Optional, TypeVar

from packing_packages.logging import get_child_logger

_logger = get_child_logger(__name__)

T = TypeVar("T")


def is_installed(package_name: str) -> bool:
    """Check if the package is installed.

    Parameters
    ----------
    package_name : str
        package name like `sklearn`

    Returns
    -------
    bool
        if installed, True
    """
    return bool(importlib.util.find_spec(package_name))


def is_argument(__callable: "Callable[..., Any]", arg_name: str) -> bool:
    """Check to see if it is included in the callable argument.

    Parameters
    ----------
    __callable : Callable

    arg_name : str
        argument name

    Returns
    -------
    bool
        if included, True
    """
    return arg_name in set(inspect.signature(__callable).parameters.keys())


class dummy_tqdm(Iterable[T]):
    """dummy class for 'tqdm'

    Parameters
    ----------
    __iterable : Iterable[T]
        iterable object
    """

    def __init__(self, __iterable: "Iterable[T]", *args, **kwargs) -> None:
        self.__iterable = __iterable

    def __iter__(self) -> "Iterator[T]":
        return iter(self.__iterable)

    def __getattr__(self, name: str) -> "Callable[..., None]":
        return self.__no_operation

    @staticmethod
    def __no_operation(*args, **kwargs) -> None:
        """no-operation"""
        return


def check_encoding(encoding: Optional[str]) -> str:
    """Check if the encoding is valid.

    Parameters
    ----------
    encoding : str
        encoding name

    Returns
    -------
    str
        encoding name
    """
    if encoding is None:
        encoding = sys.getdefaultencoding()
        _logger.info(f"Use default encoding: {encoding}.")
    try:
        "".encode(encoding)
        return encoding
    except LookupError as e:
        raise ValueError(f"Invalid encoding: {encoding}") from e


def get_env_list(encoding: Optional[str] = None) -> set[str]:
    """Get list of conda environments.

    Parameters
    ----------
    encoding : str, optional
        Encoding for subprocess output. If None, uses system default encoding, by default None

    Returns
    -------
    set[str]
        List of conda environments
    """
    encoding = check_encoding(encoding)
    result_conda_env_list = subprocess.run(
        [
            os.environ["CONDA_EXE"],
            "info",
            "-e",
        ],
        stdout=subprocess.PIPE,
        check=True,
    )
    return {
        line.split()[0]
        for line in result_conda_env_list.stdout.decode(encoding).splitlines()
        if line and not line.startswith("#")
    }


def check_env_name(
    env_name: Optional[str] = None, encoding: Optional[str] = None
) -> str:
    """Check if the environment name is valid.

    Parameters
    ----------
    env_name : str, optional
        Environment name. If None, uses the current conda environment, by default None
    encoding : str, optional
        Encoding for subprocess output. If None, uses system default encoding, by default None

    Returns
    -------
    str
        Environment name
    """
    encoding = check_encoding(encoding)

    if env_name is None:
        env_name = os.environ["CONDA_DEFAULT_ENV"]
    else:
        # check environment name
        env_name_list = get_env_list(encoding)
        if env_name not in env_name_list:
            raise ValueError(
                f"Environment '{env_name}' not found. "
                "Environments: ('{{}}')".format("','".join(env_name_list))
            )
    return env_name
