# PACKING-PACKAGES

[![CI](https://github.com/yu9824/packing-packages/actions/workflows/CI.yml/badge.svg)](https://github.com/yu9824/packing-packages/actions/workflows/CI.yml)
[![docs](https://github.com/yu9824/packing-packages/actions/workflows/docs.yml/badge.svg)](https://github.com/yu9824/packing-packages/actions/workflows/docs.yml)

[![release-pypi](https://github.com/yu9824/packing-packages/actions/workflows/release-pypi.yml/badge.svg)](https://github.com/yu9824/packing-packages/actions/workflows/release-pypi.yml)

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://github.com/python/mypy)

<!--
[![python_badge](https://img.shields.io/pypi/pyversions/packing-packages)](https://pypi.org/project/packing-packages/)
[![license_badge](https://img.shields.io/pypi/l/packing-packages)](https://pypi.org/project/packing-packages/)
[![PyPI version](https://badge.fury.io/py/packing-packages.svg)](https://pypi.org/project/packing-packages/)
[![Downloads](https://static.pepy.tech/badge/packing-packages)](https://pepy.tech/project/packing-packages)

[![Conda Version](https://img.shields.io/conda/vn/conda-forge/packing-packages.svg)](https://anaconda.org/conda-forge/packing-packages)
[![Conda Platforms](https://img.shields.io/conda/pn/conda-forge/packing-packages.svg)](https://anaconda.org/conda-forge/packing-packages)
-->

This module provides functionality to pack conda environments and their dependencies into a specified directory.

You can use this package to migrate a conda environment to another offline machine with the same operating system.


## Install

```bash
# Need python, setuptools, pip package
pip install git+https://github.com/yu9824/packing-packages.git --no-build-isolation --no-deps

```

## How to use

see `--help`.

### Pack

```bash
packing-package pack .

```

### Install

```bash
packing-package install .

```

## Example

### Source device

```bash
conda activate <envname>
python -m pip install git+https://github.com/yu9824/packing-packages.git --no-build-isolation --no-deps
python -m packing_packages pack .

```

### Destination device (offline)

```bash
conda create -yn <envname> --offline
conda activate <envname>
conda install --use-local --offline ./conda/*
python -m pip install --no-deps --no-build-isolation ./pypi/*

```


