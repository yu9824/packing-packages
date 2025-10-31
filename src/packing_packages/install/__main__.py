import argparse
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Optional

from packing_packages.install._core import (
    generate_install_scripts,
    install_packages,
)


def install(args: argparse.Namespace) -> None:
    """Install packages in the conda environment."""
    dirpath_packages = Path(args.dirpath_packages).resolve()
    if not dirpath_packages.is_dir():
        raise FileNotFoundError(dirpath_packages)

    if args.generate_scripts:
        # For generate_scripts, if env_name is not specified, pass None
        # so it will be determined from directory name in the function
        generate_install_scripts(
            dirpath_packages=dirpath_packages,
            env_name=args.env_name,
            output_dir=args.output_dir,
        )
    else:
        # For install_packages, use current environment if not specified
        if args.env_name is None:
            env_name = os.environ["CONDA_DEFAULT_ENV"]
        else:
            env_name = args.env_name
        install_packages(
            dirpath_packages=dirpath_packages,
            env_name=env_name,
            encoding=args.encoding,
        )


def add_arguments_install(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        type=Path,
        default=".",
        help=(
            "Path to the directory containing packages to install (e.g., *.tar.bz2, *.conda). "
            "Defaults to the current directory ('.') if not specified."
        ),
        metavar="DIRPATH_PACKAGES",
        dest="dirpath_packages",
    )
    parser.add_argument(
        "-n",
        "--env-name",
        type=str,
        default=None,
        help=(
            "Name of the conda environment where packages will be installed. "
            "If not specified: "
            "for install command, uses currently active environment; "
            "for --generate-scripts, uses directory name of packages directory."
        ),
    )
    parser.add_argument(
        "-e",
        "--encoding",
        type=str,
        default=None,
        help=(
            "Encoding to use for subprocess execution (e.g., when calling conda commands). "
            "Defaults to the system encoding if not specified."
        ),
    )
    parser.add_argument(
        "--generate-scripts",
        action="store_true",
        help=(
            "Generate install scripts (install_packages.bat, install_packages.ps1, "
            "install_packages.sh) instead of installing packages directly. "
            "These scripts can be distributed and used independently."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "Output directory for generated scripts. "
            "Defaults to the package directory if not specified."
        ),
    )
    parser.set_defaults(func=install)


def main(cli_args: Sequence[str], prog: Optional[str] = None) -> None:
    """Main function to parse arguments and call the install function."""
    parser = argparse.ArgumentParser(
        prog=prog, description="Install packages in the conda environment"
    )
    add_arguments_install(parser)
    args = parser.parse_args(cli_args)
    args.func(args)
