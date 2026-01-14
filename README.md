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

![logo](https://github.com/yu9824/packing-packages/blob/main/docs_src/_static/site_logo.png?raw=true)

## Overview

**Packing-Packages** is a powerful tool for packaging conda environments and their dependencies into portable directories. Perfect for deploying Python environments to offline machines, air-gapped systems, or ensuring reproducible environments across different machines with the same operating system.

### Key Features

- 🚀 **Simple & Fast**: Pack entire conda environments with a single command
- 📦 **Complete Dependency Resolution**: Automatically includes all conda and pip dependencies
- 🔄 **Cross-Platform Support**: Pack from YAML files even on different operating systems
- 🛠️ **Flexible Installation**: Install packages directly or generate standalone install scripts
- ⚡ **Incremental Updates**: Use `--diff-only` to download only new packages
- 🎯 **Error Resilient**: Installation continues even if some packages fail, with detailed error reporting
- 📋 **YAML-Based Packing**: Create packages directly from conda environment YAML files

### Use Cases

- Deploy Python environments to offline or air-gapped systems
- Create reproducible environment snapshots for production deployments
- Migrate conda environments between machines without internet access
- Archive complete environment states for backup or compliance
- Prepare environment packages for different target platforms


## Installation

```bash
pip install packing-packages
```

**Requirements**: Python, setuptools, and pip

## Quick Start

### 1. Pack Your Environment

On your source machine (with internet access), pack the current conda environment:

```bash
conda activate myenv
packing-packages pack -d .
```

This creates a directory structure:
```
.
└── myenv/
    ├── conda/    # Conda packages
    └── pypi/     # PyPI packages
```

### 2. Install on Target Machine

On your destination machine (offline), install the packed packages:

```bash
conda create -yn myenv --offline
conda activate myenv
packing-packages install ./myenv
```

### Alternative: Generate Standalone Scripts

Generate install scripts that work independently without requiring `packing-packages`:

```bash
packing-packages install ./myenv --generate-scripts
```

This creates `install_packages.bat` (Windows) and `install_packages.sh` (Unix/Linux) that can be executed directly on the target machine.

## Advanced Features

### Pack from YAML Files

Pack environments directly from conda environment YAML files, even on a different operating system:

```bash
packing-packages pack yaml environment.yaml -p linux-64
```

### Incremental Updates

Only download packages that don't already exist in the target directory:

```bash
packing-packages pack -d . --diff-only
```

### Error-Resilient Installation

The `packing-packages install` command continues even if some packages fail, providing detailed error reports for manual handling.

## Documentation

For detailed command-line options, advanced usage, and troubleshooting, see the [full documentation](https://yu9824.github.io/packing-packages/) or the [command-line tutorial](docs_src/tutorials/commandline.md).

## Important Notes

### Installation Methods

You can install packages using either:
- **Standard commands** (`conda install` / `pip install`): Faster, but stops on first error
- **`packing-packages install`**: Slower, but continues on errors and provides detailed reports

### Special Cases

- **Non-PyPI sources** (e.g., PyTorch official index): May require manual handling
- **Older packages**: Some may need `--use-pep517` flag for successful installation
- **Proxy environments**: Set `HTTP_PROXY` and `HTTPS_PROXY` environment variables

For detailed troubleshooting and edge cases, please refer to the [command-line tutorial](docs_src/tutorials/commandline.md).
