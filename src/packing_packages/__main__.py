import argparse
import sys
from collections.abc import Sequence
from typing import Optional

from packing_packages import __version__
from packing_packages.install.__main__ import add_arguments_install
from packing_packages.pack.__main__ import add_arguments_pack

__all__ = ("main",)


def main(cli_args: Sequence[str], prog: Optional[str] = None) -> None:
    parser = argparse.ArgumentParser(prog=prog, description="")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        help="show current version",
        version=f"%(prog)s: {__version__}",
    )
    subparsers = parser.add_subparsers()
    parser_pack = subparsers.add_parser(
        "pack",
        help="pack conda environment",
    )
    add_arguments_pack(parser_pack)

    parser_install = subparsers.add_parser(
        "install",
        help="install packages in the conda environment",
    )
    add_arguments_install(parser_install)

    args = parser.parse_args(cli_args)
    args.func(args)


def entrypoint() -> None:
    main(sys.argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:], prog="packing-packages")
