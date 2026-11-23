from pathlib import Path

import pytest

from packing_packages.scripts import generate_install_scripts
from packing_packages.scripts._core import split_pypi_packages_by_priority

ENV_NAME = "dummy_env"


def _make_packages(
    dirpath: Path, conda: tuple[str, ...], pypi: tuple[str, ...]
):
    (dirpath / "conda").mkdir(parents=True, exist_ok=True)
    (dirpath / "pypi").mkdir(parents=True, exist_ok=True)
    for name in conda:
        (dirpath / "conda" / name).touch()
    for name in pypi:
        (dirpath / "pypi" / name).touch()


def _read_scripts(paths: dict[str, Path]) -> tuple[str, str]:
    return (
        paths["batch"].read_text(encoding="utf-8"),
        paths["shell"].read_text(encoding="utf-8"),
    )


@pytest.mark.parametrize("create_env", [True, False])
def test_generate_install_scripts_create_env(tmp_path: Path, create_env: bool):
    _make_packages(
        tmp_path,
        conda=("python-3.12.0-h0_0.conda", "numpy-1.26.0-py312_0.tar.bz2"),
        pypi=("pip-24.0-py3-none-any.whl", "requests-2.31.0-py3-none-any.whl"),
    )
    bat, sh = _read_scripts(
        generate_install_scripts(
            tmp_path,
            env_name=ENV_NAME,
            encoding="utf-8",
            create_env=create_env,
        )
    )

    assert ("conda create" in bat) is create_env
    assert ("conda create" in sh) is create_env
    assert f"env_name={ENV_NAME}" in sh
    assert "requests-2.31.0-py3-none-any.whl" in sh
    assert "requests-2.31.0-py3-none-any.whl" in bat


@pytest.mark.parametrize(
    "pypi",
    [
        (),
        ("pip-24.0-py3-none-any.whl", "setuptools-69.0-py3-none-any.whl"),
    ],
    ids=["no-pypi", "build-only-pypi"],
)
def test_generate_install_scripts_edge_pypi(
    tmp_path: Path, pypi: tuple[str, ...]
):
    _make_packages(tmp_path, conda=("python-3.12.0-h0_0.conda",), pypi=pypi)
    bat, sh = _read_scripts(
        generate_install_scripts(tmp_path, env_name=ENV_NAME, encoding="utf-8")
    )

    # every pip install line must have at least one package
    for line in sh.splitlines():
        assert not line.rstrip().endswith("--no-build-isolation")
    for name in pypi:
        assert sh.count(name) == 1
        assert bat.count(name) == 1


def test_split_pypi_packages_by_priority():
    paths = tuple(
        Path(p)
        for p in (
            "pip-1.whl",
            "setuptools-1.whl",
            "numpy-1.whl",
            "python_x-1.whl",
        )
    )
    assert split_pypi_packages_by_priority(paths) == (paths[:2], paths[2:])
    assert split_pypi_packages_by_priority(paths[:2]) == (paths[:2], ())
    assert split_pypi_packages_by_priority(()) == ((), ())


@pytest.mark.parametrize("create_env", [True, False])
def test_generate_install_scripts_check_conda(
    tmp_path: Path, create_env: bool
):
    _make_packages(tmp_path, conda=("python-3.12.0-h0_0.conda",), pypi=())
    bat, sh = _read_scripts(
        generate_install_scripts(
            tmp_path,
            env_name=ENV_NAME,
            encoding="utf-8",
            create_env=create_env,
        )
    )

    # the check must run before any conda command
    assert bat.index("where conda") < bat.index("call conda")
    assert sh.index("command -v conda") < sh.index("\nconda ")
    assert "Miniforge Prompt" in bat
