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
- 📦 **Complete Environment Snapshot**: Packs every conda and pip package installed in the environment
- 🔄 **Cross-Platform Support**: Pack from YAML files even on different operating systems
- 🛠️ **Standalone Install Scripts**: `pack` generates install scripts that work without `packing-packages` on the target machine
- ⚡ **Incremental Updates**: Use `--diff-only` to download only new packages
- 🎯 **Error Reporting**: Failed packages are reported in detail; use `--strict` to fail fast in CI
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

**Requirements**: conda (e.g., [Miniforge](https://github.com/conda-forge/miniforge)) on the source machine. To use `pack yaml` (PyYAML) and progress bars / colored logs, install the optional dependencies:

```bash
pip install "packing-packages[optional]"
```

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
    ├── conda/                 # Conda packages
    ├── pypi/                  # PyPI packages
    ├── install_packages.bat   # Standalone install script (Windows)
    └── install_packages.sh    # Standalone install script (Unix/Linux)
```

Install scripts are generated automatically. Use `--no-scripts` to skip them.

### 2. Install on Target Machine

Transfer `myenv/` to your destination machine (offline).

> **Tip (from the author's experience):** Archive the directory into a single `.tar` file before transferring it. Packages (`.conda`, `.whl`, ...) are already compressed, so the size barely changes, but transferring one file is noticeably faster in practice than transferring many small files.

```bash
tar -cf myenv.tar myenv   # source machine
tar -xf myenv.tar         # destination machine (also works on Windows 10+)
```

Then run the generated script. `packing-packages` is not required there:

```bash
# Windows (run from "Miniforge Prompt" or "Anaconda Prompt")
myenv\install_packages.bat

# Unix/Linux/macOS
./myenv/install_packages.sh
```

The script creates the environment and installs all packages (it asks before recreating an existing environment). To install into an environment with another name, regenerate the scripts:

```bash
packing-packages scripts ./myenv -n another-env
```

You can also install manually with `conda install` / `pip install`, or with `packing-packages install`. See [Installation Methods](#installation-methods).

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

New packages are saved to `myenv/diffs/<timestamp>/`, together with install scripts that add them to the existing environment (without `conda create`).

### Strict Mode

Fail with an error if any package cannot be packed (useful in CI):

```bash
packing-packages pack -d . --strict
```

### Error-Resilient Installation

`packing-packages install` continues even if some packages fail, providing detailed error reports for manual handling.

## Documentation

For detailed command-line options, advanced usage, and troubleshooting, see the [full documentation](https://yu9824.github.io/packing-packages/) or the [command-line tutorial](docs_src/tutorials/commandline.md).

## Important Notes

### Installation Methods

- **Generated install scripts** (recommended): No `packing-packages` needed on the target machine
- **Standard commands** (`conda install` / `pip install`): Install manually; wildcards are not expanded on Windows `cmd`
- **`packing-packages install`**: Slower, but continues on errors and provides detailed reports

### Special Cases

- **PyTorch**: Wheels with a local version label (e.g., `2.1.0+cu118`) are downloaded from the PyTorch index automatically
- **Non-PyPI sources** (other package indexes, local paths, editable installs, VCS URLs): Cannot be downloaded and are reported as failures; handle them manually
- **Older packages**: Some may need `--use-pep517` flag for successful installation
- **Proxy environments**: Set `HTTP_PROXY` and `HTTPS_PROXY` environment variables

For detailed troubleshooting and edge cases, please refer to the [command-line tutorial](docs_src/tutorials/commandline.md).
