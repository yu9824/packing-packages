# Command Line Usage

This tutorial explains how to use the `packing-packages` command-line interface.

## Basic Usage

### Display Help

To see available commands and options, display the help:

```bash
packing-packages --help
packing-packages pack --help
packing-packages install --help
packing-packages scripts --help
```

### Check Version

To check the current version:

```bash
packing-packages --version
```

## `pack` Command

The `pack` command packs a conda environment and all its dependencies into a directory.

### Basic Usage

To pack the currently active conda environment:

```bash
packing-packages pack
# same as
packing-packages pack -d .
```

This will save the packages to the current directory (`.`) with the following structure:

```
.
└── <envname>/
    ├── conda/
    │   ├── python-3.11.0-h1234567_0.tar.bz2
    │   ├── numpy-1.24.3-py311h1234567_0.conda
    │   ├── pandas-2.0.0-py311h1234567_0.tar.bz2
    │   └── ...
    ├── pypi/
    │   ├── requests-2.31.0-py3-none-any.whl
    │   ├── beautifulsoup4-4.12.2-py3-none-any.whl
    │   ├── somepackage-1.0.0.tar.gz
    │   └── ...
    ├── install_packages.bat   # Generated install script (Windows)
    └── install_packages.sh    # Generated install script (Unix/Linux/macOS)
```

**Directory Structure:**
- `<envname>/`: Directory named after the conda environment
  - `conda/`: Contains conda packages (`.tar.bz2` or `.conda` files)
  - `pypi/`: Contains PyPI packages (`.whl` or `.tar.gz` files)
  - `install_packages.bat` / `install_packages.sh`: Install scripts (skip with `--no-scripts`)

### Options

#### `-n, --env-name`

Specify the name of the conda environment to pack. If not specified, the currently active environment is used.

```bash
packing-packages pack -n myenv -d ./packages
```

#### `-d, --dirpath-target`

Specify the path to the directory where the packed environment will be saved. Defaults to the current directory (`.`).

```bash
packing-packages pack -d /path/to/output
```

This creates the following structure:
```
/path/to/output/
└── <envname>/
    ├── conda/
    │   └── *.tar.bz2, *.conda files
    └── pypi/
        └── *.whl, *.tar.gz files
```

#### `-D, --dry-run`

Perform a dry run without actually packing the environment. Useful for testing.

```bash
packing-packages pack -d . --dry-run
```

#### `--diff-only`

Skip packages that already exist in the target directory and only download new packages.

```bash
packing-packages pack -d . --diff-only
```

New packages are saved to `<envname>/diffs/<timestamp>/`. The install scripts generated there install into the existing environment (without `conda create`).

#### `--no-scripts`

Do not generate install scripts. By default, `install_packages.bat` and `install_packages.sh` are generated in the output directory after packing (skipped with `--dry-run`). See [`scripts` Command](#scripts-command).

```bash
packing-packages pack -d . --no-scripts
```

#### `--strict`

Exit with an error if any package fails to be packed (e.g., for CI). Install scripts are not generated in that case. In the Python API, use `strict=True`; it raises `packing_packages.pack.PackingError`.

```bash
packing-packages pack -d . --strict
```

#### `-e, --encoding`

Specify the encoding to use for subprocess execution. If not specified, the system default encoding is used.

```bash
packing-packages pack -d . -e utf-8
```

### Examples

```bash
# Pack the current environment to the current directory
packing-packages pack -d .

# Pack a specific environment
packing-packages pack -n myenv -d ./myenv_packages

# Check with a dry run
packing-packages pack -n myenv -d ./myenv_packages --dry-run

# Skip existing packages and download only differences
packing-packages pack -n myenv -d ./myenv_packages --diff-only
```

## `pack yaml` Command

The `pack yaml` command packs packages directly from a conda environment file (`.yaml`). It can be executed on a different OS.

### Basic Usage

```bash
packing-packages pack yaml /path/to/environment.yaml
```

### Options

#### `filepath_yaml` (required)

Specify the path to the conda environment file (`.yaml`).

```bash
packing-packages pack yaml environment.yaml
```

The output structure is the same as the `pack` command:
```
.
└── <envname>/          # Named after the `name:` field of the YAML file
    ├── conda/
    │   └── *.tar.bz2, *.conda files
    ├── pypi/
    │   └── *.whl, *.tar.gz files
    ├── install_packages.bat
    └── install_packages.sh
```

`pack yaml` requires PyYAML (`pip install "packing-packages[optional]"`).

#### `-p, --platform`

Specify the platform. Choose one of the following:

- `win-64`
- `win-32`
- `linux-64`
- `linux-aarch64`
- `linux-ppc64le`
- `linux-s390x`
- `osx-64`
- `osx-arm64`

```bash
packing-packages pack yaml environment.yaml -p linux-64
```

#### `-d, --dirpath-target`

Specify the path to the directory where the packed environment will be saved. Defaults to the current directory (`.`).

```bash
packing-packages pack yaml environment.yaml -p linux-64 -d ./packages
```

#### `-D, --dry-run`

Perform a dry run without actually packing the environment.

```bash
packing-packages pack yaml environment.yaml -p linux-64 --dry-run
```

#### `--diff-only`

Skip packages that already exist in the target directory and only download new packages.

```bash
packing-packages pack yaml environment.yaml -p linux-64 --diff-only
```

New packages are saved to `<envname>/diffs/<timestamp>/`. The install scripts generated there install into the existing environment (without `conda create`).

#### `--no-scripts`

Do not generate install scripts. By default, `install_packages.bat` and `install_packages.sh` are generated in the output directory after packing (skipped with `--dry-run`). See [`scripts` Command](#scripts-command).

```bash
packing-packages pack yaml environment.yaml -p linux-64 --no-scripts
```

#### `--strict`

Exit with an error if any package fails to be packed (e.g., for CI). Install scripts are not generated in that case. In the Python API, use `strict=True`; it raises `packing_packages.pack.PackingError`.

```bash
packing-packages pack yaml environment.yaml -p linux-64 --strict
```

#### `-e, --encoding`

Specify the encoding to use for subprocess execution.

```bash
packing-packages pack yaml environment.yaml -p linux-64 -e utf-8
```

### Examples

```bash
# Pack from a YAML file with platform specification
packing-packages pack yaml environment.yaml -p linux-64

# Specify output directory
packing-packages pack yaml environment.yaml -p linux-64 -d ./output

# Check with a dry run
packing-packages pack yaml environment.yaml -p linux-64 --dry-run
```

## `install` Command

The `install` command installs packed packages into a conda environment.

### Basic Usage

To install packages into the currently active conda environment:

```bash
packing-packages install .
```

### Options

#### `DIRPATH_PACKAGES` (positional argument)

Specify the path to the directory containing packages to install. This should point to the directory containing the `conda/` and `pypi/` subdirectories (or the parent directory containing the environment-named folder). Defaults to the current directory (`.`) if not specified.

```bash
packing-packages install /path/to/packages
```

**Expected directory structure:**
```
/path/to/packages/          # Can be either:
├── conda/                  # Option 1: Direct access to conda/ and pypi/
│   └── *.tar.bz2, *.conda
└── pypi/
    └── *.whl, *.tar.gz

# OR

/path/to/packages/
└── <envname>/              # Option 2: Environment-named directory
    ├── conda/
    │   └── *.tar.bz2, *.conda
    └── pypi/
        └── *.whl, *.tar.gz
```

The command automatically detects and installs packages from both `conda/` and `pypi/` subdirectories.

#### `-n, --env-name`

Specify the name of the conda environment where packages will be installed. If not specified, the currently active environment is used.

```bash
packing-packages install . -n myenv
```

#### `-e, --encoding`

Specify the encoding to use for subprocess execution. If not specified, the system default encoding is used.

```bash
packing-packages install . -e utf-8
```

### Examples

```bash
# Install packages into the current environment
packing-packages install .

# Install into a specific environment
packing-packages install ./packages -n myenv
```

## `scripts` Command

Generate standalone install scripts (`install_packages.bat`, `install_packages.sh`). `pack` and `pack yaml` run this automatically, so use this command to regenerate scripts (e.g., with another environment name). The scripts do not depend on `packing-packages` and can be distributed independently.

The generated scripts:

- abort with guidance if `conda` is not found (on Windows, run them from "Miniforge Prompt" or "Anaconda Prompt")
- ask `y/[n]` before removing and recreating an environment that already exists (empty input aborts)

### Basic Usage

```bash
packing-packages scripts ./myenv
```

**Directory structure after generation:**
```
./myenv/
├── conda/
│   └── *.tar.bz2, *.conda
├── pypi/
│   └── *.whl, *.tar.gz
├── install_packages.bat      # Generated
└── install_packages.sh       # Generated
```

### Options

#### `DIRPATH_PACKAGES` (positional argument)

Path to the directory containing packed packages. Defaults to the current directory.

#### `-n, --env-name`

Name of the conda environment the scripts install into. If not specified, the directory name of `DIRPATH_PACKAGES` is used (it must exist as a local conda environment).

```bash
packing-packages scripts ./myenv -n another-env
```

#### `-o, --output-dir`

Output directory for generated scripts. If not specified, scripts are written to the package directory.

```bash
packing-packages scripts ./myenv -o ./scripts
```

#### `--no-create-env`

Do not create a new environment in the scripts; install into an existing one instead.

```bash
packing-packages scripts ./myenv/diffs/20260101_1200 -n myenv --no-create-env
```

#### `-e, --encoding`

Encoding for the generated `.bat` file. If not specified, the system default encoding is used.

## Practical Examples

### Source Device (Online Environment)

1. Activate the conda environment:

```bash
conda activate myenv
```

2. Install `packing-packages`:

```bash
python -m pip install packing-packages
```

3. Pack the environment:

```bash
python -m packing_packages pack -d .
```

This creates the following structure:
```
.
└── myenv/
    ├── conda/
    │   ├── python-3.11.0-h1234567_0.tar.bz2
    │   ├── numpy-1.24.3-py311h1234567_0.conda
    │   └── ...
    ├── pypi/
    │   ├── requests-2.31.0-py3-none-any.whl
    │   └── ...
    ├── install_packages.bat
    └── install_packages.sh
```

Or from a YAML file:

```bash
python -m packing_packages pack yaml environment.yaml -p linux-64
```

This creates the same structure, but packages are downloaded for the specified platform (`linux-64` in this example).

### Destination Device (Offline Environment)

Copy the packed directory (e.g., `./myenv/`) to the destination device.

#### Recommended: Using Generated Install Scripts

`pack` generates install scripts automatically. They do not require `packing-packages` on the destination device:

```bash
# Windows (run from "Miniforge Prompt" or "Anaconda Prompt")
myenv\install_packages.bat

# Unix/Linux/macOS
./myenv/install_packages.sh
```

The scripts:

- create the environment and install conda packages first, then PyPI packages
- ask `y/[n]` before removing and recreating an environment that already exists
- `install_packages.sh` stops at the first error

To install into an environment with another name, regenerate the scripts with [`scripts` Command](#scripts-command).

#### Alternative 1: Using Standard Install Commands

```bash
# Create the environment
conda create -yn myenv --offline
conda activate myenv

# Install conda packages
conda install --use-local --offline ./myenv/conda/*

# Install pip packages
python -m pip install --no-deps --no-build-isolation ./myenv/pypi/*
```

Wildcards (`*`) are not expanded on Windows `cmd`; use the generated scripts there.

#### Alternative 2: Using `packing-packages install`

If `packing-packages` is installed on the destination device:

```bash
conda create -yn myenv --offline
conda activate myenv
packing-packages install ./myenv
```

This installs packages one by one and continues even if some fail, reporting the failed packages at the end. It is slower, but useful when you want to install as much as possible and handle the rest manually.

## Troubleshooting

### Encoding Issues

If encoding errors occur in certain environments, explicitly specify the encoding with the `-e` option:

```bash
packing-packages pack -d . -e utf-8
packing-packages install . -e utf-8
```

### Proxy Configuration

If you are in an environment that requires a proxy, set the environment variables:

```bash
export HTTP_PROXY="your proxy"
export HTTPS_PROXY="your proxy"
```

### Handling Packing Errors

Packages that cannot be downloaded are reported at the end of `pack` (use `--strict` to make it an error). Typical causes:

- Packages installed from a local path, in editable mode (`pip install -e`), or from a VCS URL
- Packages from a package index other than PyPI

PyTorch wheels with a local version label (e.g., `torch==2.1.0+cu118`) are downloaded from the PyTorch index (`https://download.pytorch.org/whl/cu118`) automatically.

### Handling Installation Errors

`install_packages.sh` stops at the first error. The `packing-packages install` command skips packages that fail and continues. Check the error logs and install them manually if necessary.
