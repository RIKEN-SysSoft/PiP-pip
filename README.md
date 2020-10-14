# PiP-pip

[PiP](../../../PiP) package installing program

# Description

`pip-pip` is the program to build and install
[PiP](../../PiP), [PiP-glibc](../../../PiP-glibc) and
[PiP-gdb](../../../PiP-gdb).

# Prerequisite

Supported architectures:

- x86_64
- AArch64

Supported Linux (RHEL and CentOS are the guaranteed distributions):

- RHLE/CentOS 7
- RHEL/CentOS 8

# Usage

    $ ./pip-pip <OPTIONS>

- `--prefix=<PREFIX_DIR>`
  Specifying install directory. Default is `--prefix=./install`.

- `--build=<BUILD_DIR>`
  Specifying build directory. Default is `--build=./build`.

- `--version=<PIP_VERSION>`
  Specifying PiP version number. Currently, "2" (PiP-v2) and "3"
  (PiP-v3) are valid.  Default if "2."  PiP-v1 ("1") is deprecated and
  unable to specify. Refer to [PiP](../../PiP) for the version
  differences.

- `--clean`
  Remove the specified build directory when the installation finishes
  successfully.  If the build directory is the
  same with the prefix directory, or the build directory includes the
  prefix directory, then this option is disabled automatically.

- `--dryrun`
  Dryrun.

- `--help`
  Display help message.

# Author

Atsushi Hori, Riken CCS
