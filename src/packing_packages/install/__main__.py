import argparse
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Optional

from packing_packages.install._core import install_packages


def install(args: argparse.Namespace) -> None:
    """Install packages in the conda environment."""
    if args.env_name is None:
        env_name = os.environ["CONDA_DEFAULT_ENV"]
    else:
        env_name = args.env_name

    dirpath_packages = Path(args.dirpath_packages).resolve()
    if not dirpath_packages.is_dir():
        raise FileNotFoundError(dirpath_packages)

    install_packages(
        dirpath_packages=dirpath_packages,
        env_name=env_name,
        encoding=args.encoding,
    )


def main(cli_args: Sequence[str], prog: Optional[str] = None) -> None:
    """Main function to parse arguments and call the install function."""
    parser = argparse.ArgumentParser(
        prog=prog, description="Install packages in the conda environment"
    )
    parser.add_argument(
        "dirpath-packages",
        type=str,
        default=".",
        help="directory path of packages",
        metavar="DIRPATH_PACKAGES",
    )
    parser.add_argument(
        "-e",
        "-n",
        "--env-name",
        type=str,
        default=None,
        help="conda environment name",
    )
    parser.add_argument(
        "--encoding",
        type=str,
        default=None,
        help="encoding for subprocess",
    )
    parser.set_defaults(func=install)
    args = parser.parse_args(cli_args)
    args.func(args)
