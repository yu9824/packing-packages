import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Optional

from packing_packages.pack._core import packing_packages


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
        encoding=args.encoding,
        dry_run=args.dry_run,
    )


def main(cli_args: Sequence[str], prog: Optional[str] = None) -> None:
    """Main function to parse arguments and call the packing function."""
    parser = argparse.ArgumentParser(
        prog=prog, description="pack conda environment"
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
        "-d",
        "--dirpath-target",
        type=str,
        default=".",
        help="target directory path for packing the environment",
    )
    parser.add_argument("-D", "--dry-run", action="store_true", help="dry run")
    parser.add_argument(
        "--encoding",
        type=str,
        default=None,
        help="encoding for subprocess",
    )
    parser.set_defaults(func=pack)

    args = parser.parse_args(cli_args)
    args.func(args)


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
