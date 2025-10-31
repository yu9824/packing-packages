# PACKING-PACKAGES

[![CI](https://github.com/yu9824/packing-packages/actions/workflows/CI.yml/badge.svg)](https://github.com/yu9824/packing-packages/actions/workflows/CI.yml)
[![docs](https://github.com/yu9824/packing-packages/actions/workflows/docs.yml/badge.svg)](https://github.com/yu9824/packing-packages/actions/workflows/docs.yml)
[![release-pypi](https://github.com/yu9824/packing-packages/actions/workflows/release-pypi.yml/badge.svg)](https://github.com/yu9824/packing-packages/actions/workflows/release-pypi.yml)

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://github.com/python/mypy)

[![python_badge](https://img.shields.io/pypi/pyversions/packing-packages)](https://pypi.org/project/packing-packages/)
[![license_badge](https://img.shields.io/pypi/l/packing-packages)](https://pypi.org/project/packing-packages/)
[![PyPI version](https://badge.fury.io/py/packing-packages.svg)](https://pypi.org/project/packing-packages/)
[![Downloads](https://static.pepy.tech/badge/packing-packages)](https://pepy.tech/project/packing-packages)

<!-- [![Conda Version](https://img.shields.io/conda/vn/conda-forge/packing-packages.svg)](https://anaconda.org/conda-forge/packing-packages)
[![Conda Platforms](https://img.shields.io/conda/pn/conda-forge/packing-packages.svg)](https://anaconda.org/conda-forge/packing-packages) -->

This tool packs a conda environment and all its dependencies into a directory.

You can migrate the packed environment to another offline machine with the same operating system.


## Install

```bash
# Need python, setuptools, pip package
pip install packing-packages

```

## How to use

See help for available commands and options:

```bash
packing-packages --help
packing-packages pack --help
packing-packages install --help

```

### Pack

```bash
packing-packages pack -d .

```

### Install

```bash
packing-packages install .

```

### Generate install scripts (instead of installing directly)

Use `--generate-scripts` to create reusable install scripts that do not depend on this package. These scripts can be copied and executed on another machine (offline), and work across platforms (Windows batch and Unix/Linux shell).

```bash
# Generate scripts in the package directory (default)
packing-packages install . --generate-scripts

# Specify environment name and output directory explicitly
packing-packages install /path/to/packages \
  --generate-scripts \
  --env-name myenv \
  --output-dir /path/to/output

```

Generated files:

- install_packages.bat (Windows)
- install_packages.sh (Unix/Linux)

Notes:

- If `--env-name` is omitted with `--generate-scripts`, the environment name defaults to the package directory name.
- If `--output-dir` is omitted, scripts are written to the package directory.

## Example

### Source device

```bash
conda activate <envname>
python -m pip install packing-packages
python -m packing_packages pack -d .

```

### Destination device (offline)

```bash
conda create -yn <envname> --offline
conda activate <envname>
conda install --use-local --offline ./conda/*
python -m pip install --no-deps --no-build-isolation ./pypi/*

```

Alternatively, if you generated install scripts on the source device:

```bash
# Windows
install_packages.bat

# Unix/Linux
./install_packages.sh
```

## Notes

### Installing PyTorch from a Non-PyPI Source

If you need to download packages from a source other than PyPI (e.g., the official PyTorch index), standard methods may not complete successfully. Some packages may fail to download and require manual handling. Automated support is not currently provided for that case.

```bash
# Installation command
pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cu124

# Download command (without dependencies)
# --no-deps: download only the specified package
# -d: set the destination directory
pip download torch==2.5.1 --index-url https://download.pytorch.org/whl/cu124 --no-deps -d .
```

### Handling Installation Failures with `--use-pep517`

Some older packages may not install successfully using `pip install`. In such cases, installing with the `--use-pep517` option may help:

```bash
pip install <package-name> --use-pep517
```

### Choosing Between Standard Install Commands and `packing-packages install`

There are two main methods for installing packages:

1. Using `conda install` or `pip install`
2. Using the `packing-packages install` command, which wraps these tools and provides error handling

| Command                         | Advantages                             | Disadvantages                |
| ------------------------------- | -------------------------------------- | ---------------------------- |
| `conda install` / `pip install` | Fast execution                         | Stops immediately upon error |
| `packing-packages install`      | Skips failed packages and reports them | Slower overall process       |


### Packing an Environment Using a `.yaml` File

~~If you already have an environment file (`.yaml`), you can create and pack the environment on an online machine with the same OS:~~

You can now pack from a YAML file even on a different OS using the following command:

```bash
packing-packages pack yaml /path/to/file.yaml
```

### Using a Proxy (If Required)

If you are in an environment that requires a proxy, you may need to configure the proxy settings before downloading or installing packages:

```bash
export HTTP_PROXY="your proxy"
export HTTPS_PROXY="your proxy"
```
