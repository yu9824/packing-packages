import argparse
import sys
from typing import Optional

if sys.version_info >= (3, 9):
    from collections.abc import Sequence
else:
    from typing import Sequence

from packing_packages import __version__
from packing_packages.install.__main__ import install
from packing_packages.pack.__main__ import pack

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
    parser_pack.add_argument(
        "-e",
        "-n",
        "--env-name",
        type=str,
        default=None,
        help="conda environment name",
    )
    parser_pack.add_argument(
        "-d",
        "--dirpath-target",
        type=str,
        default=".",
        help="target directory path",
    )
    parser_pack.add_argument(
        "-D",
        "--dry-run",
        action="store_true",
        help="do not download files",
    )
    parser_pack.set_defaults(func=pack)

    parser_install = subparsers.add_parser(
        "install",
        help="install packages in the conda environment",
    )
    parser_install.add_argument(
        "-e",
        "-n",
        "--env-name",
        type=str,
        default=None,
        help="conda environment name",
    )
    parser_install.add_argument(
        type=str,
        default=".",
        help="directory path of packages",
        metavar="DIRPATH_PACKAGES",
        dest="dirpath_packages",
    )
    parser_install.set_defaults(func=install)

    args = parser.parse_args(cli_args)
    args.func(args)


def entrypoint() -> None:
    main(sys.argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:], prog="packing-packages")
