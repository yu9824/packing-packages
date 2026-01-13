from pathlib import Path

from packing_packages.pack import packing_packages
from packing_packages.pack.yaml import packing_packages_from_yaml

FILEPATH_YAML = Path(__file__).parent.resolve() / "env.yml"


def test_pack(debug):
    packing_packages(dry_run=True)


def test_pack_yaml(debug):
    assert FILEPATH_YAML.is_file(), f"{FILEPATH_YAML}"
    packing_packages_from_yaml(
        FILEPATH_YAML, platform="linux-64", dry_run=True
    )
