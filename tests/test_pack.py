import subprocess
import sys
from pathlib import Path

import pytest

from packing_packages.pack import packing_packages
from packing_packages.pack.yaml import packing_packages_from_yaml

FILEPATH_YAML = Path(__file__).parent.resolve() / "env.yml"

INDEX_URL_TORCH = "https://download.pytorch.org/whl/cpu"


def test_pack(debug):
    packing_packages(dry_run=True)


def test_pack_yaml(debug):
    assert FILEPATH_YAML.is_file(), f"{FILEPATH_YAML}"
    packing_packages_from_yaml(
        FILEPATH_YAML, platform="linux-64", dry_run=True
    )


@pytest.mark.os_linux
@pytest.mark.skipif(
    not sys.platform.startswith("linux"),
    reason="Linux only",
)
def test_pack_torch(debug):
    subprocess.run(
        [
            "pip",
            "install",
            "torch",
            "torchvision",
            "--index-url",
            INDEX_URL_TORCH,
        ],
        check=True,
    )

    packing_packages(dry_run=True, index_url=INDEX_URL_TORCH)
