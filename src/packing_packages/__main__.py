import argparse
import os
import sys
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 9):
    from collections.abc import Sequence
else:
    from typing import Sequence

from packing_packages import __version__
from packing_packages._core import packing_packages

__all__ = ("main",)


def pack(args: argparse.Namespace) -> None:
    """pack conda environment"""
    if args.env_name is None:
        env_name = os.environ["CONDA_DEFAULT_ENV"]
    else:
        env_name = args.env_name

    dirpath_target = Path(args.dirpath_target).resolve()
    if not dirpath_target.is_dir():
        raise FileNotFoundError(dirpath_target)

    packing_packages(
        env_name=env_name,
        dirpath_target=dirpath_target,
        dry_run=args.dry_run,
    )


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
        "--dry-run",
        action="store_true",
        help="do not download files",
    )
    parser_pack.set_defaults(func=pack)

    args = parser.parse_args(cli_args)
    args.func(parser.parse_args(cli_args))


def entrypoint() -> None:
    main(sys.argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:], prog="packing-packages")
