from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from packing_packages.scripts._core import generate_install_scripts


def scripts(args: argparse.Namespace) -> None:
    """Generate install scripts for packed packages."""
    dirpath_packages = Path(args.dirpath_packages).resolve()
    if not dirpath_packages.is_dir():
        raise FileNotFoundError(dirpath_packages)

    generate_install_scripts(
        dirpath_packages=dirpath_packages,
        env_name=args.env_name,
        output_dir=args.output_dir,
        encoding=args.encoding,
        create_env=args.create_env,
    )


def add_arguments_scripts(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        type=Path,
        default=".",
        nargs="?",
        help=(
            "Path to the directory containing packed packages (e.g., *.tar.bz2, *.conda, *.whl). "
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
            "Name of the conda environment the scripts install into. "
            "If not specified, uses the directory name of DIRPATH_PACKAGES."
        ),
    )
    parser.add_argument(
        "-e",
        "--encoding",
        type=str,
        default=None,
        help=(
            "Encoding for the generated .bat file. "
            "Defaults to the system encoding if not specified."
        ),
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "Output directory for generated scripts. "
            "Defaults to DIRPATH_PACKAGES if not specified."
        ),
    )
    parser.add_argument(
        "--no-create-env",
        action="store_false",
        dest="create_env",
        help=(
            "Do not create a new conda environment in the scripts; "
            "install into an existing one instead."
        ),
    )
    parser.set_defaults(func=scripts)


def main(cli_args: Sequence[str], prog: str | None = None) -> None:
    """Main function to parse arguments and generate install scripts."""
    parser = argparse.ArgumentParser(
        prog=prog, description="Generate install scripts for packed packages"
    )
    add_arguments_scripts(parser)
    args = parser.parse_args(cli_args)
    args.func(args)


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
