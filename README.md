# PiP-pip

[PiP](../../../PiP/) package installing program

# Description

The `pip-pip.sh` is the program to build and install
[PiP](../../PiP/README.md) and related software
([PiP-glibc](../../../PiP-glibc) and [PiP-gdb](../../../PiP-gdb)).

# Prerequisite

Supported architectures:

- x86_64
- AArch64

Supported Linux (RHEL and Centos are tested and guaranteed):

- RHLE 7 (Centos 7)
- RHEL 8 (CentOS 8)

# How To Use

    $ ./pip-pip.sh <OPTIONS>

- `--prefix <PREFIX_DIR>`
  Specifying install directory. Default is the current directory

- `--build <BUILD DIR>`
  Specifying build directory. Default is the current directory

- `--pip <PIP_VERSION>`
  Specifying PiP version number. Currently, "2" or "3" is valid. "1"
  (PiP-v1) is deprecatde and unable to specify.

- `--clean`
  Remove the specified build directory.

- `--dryrun`
  Dryrun

# Author

Atsushi Hori (Riken CCS)

# Date

Oct. 12 2020
