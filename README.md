# PiP-pip

[PiP](../../../PiP) package installing program

# Description

`pip-pip` is the program to build and install
[PiP](../../PiP), [PiP-glibc](../../../PiP-glibc) and
[PiP-gdb](../../../PiP-gdb).

# Prerequisite

This program is written in Python (version 3).

Required software packages:

- git
- yum (optional)
- docker (optional)
- spack (optional)

Supported architectures:

- x86_64
- AArch64

Supported Linux (RHEL and CentOS are the guaranteed distributions):

- RHLE/CentOS 7
- RHEL/CentOS 8

# Usage

    $ ./pip-pip <OPTIONS>

- `--how=<HOW>`
  Specifying how to install PiP. Choice is one of `yum`, `docker`,
  `spack` and `github`. `yum` and `docker` installations require root
  privilege. Refer to the `--sudo` option below. `spack` will be
  installed automatically if `spack` is not yet installed (or not in
  the PATH). Default is `github`.

- `--prefix=<PREFIX_DIR>`
  Specifying install directory. Relative, absolute and tilde slash
  paths are all valid. Default is `--prefix=install`.

- `--work=<BUILD_DIR>`
  Specifying build directory. Relative, absolute and tilde slash
  paths are all valid. Default is `--work=work`.
  When installing from a github repo, all required source trees will be
  downloaded into the specified work directory.  And the specified
  work directory must not exist, otherwise `git` will get mad.
  All installing operations will be logged into a file (named
  `pip-pip.log`) under this directory.

- `--version=<PIP_VERSION>`
  Specifying PiP version number. Currently, "2" (PiP-v2) and "3"
  (PiP-v3) are valid.  Default if "2."  PiP-v1 ("1") is deprecated and
  unable to specify. Refer to [PiP](../../PiP) for the version
  differences.

- `--sudo`
  Allow `sudo` when installing `yum` and `docker`. To enable this
  option, user must be a sudoer.

- `--force`
  This option stops asking.

- `--noglibc`
  Do not install PiP-(patched-)glibc and PiP-(patched-)gdb. This
  option is only effective with the `--github` option. (refer to the
  next section for more details)

- `--nogdb`
  Do not install PiP-(patched-)gdb. This option is only effective with
  the `--github` option. (refer to the next section for more details)

- `--clean`
  Remove the specified work directory when the installation finishes
  successfully.  If the build directory is the
  same with the prefix directory, or the build directory includes the
  prefix directory, then this option is disabled automatically.

- `--dryrun`
  Dryrun.

- `--quiet`
  Run quietly.

- `--help`
  Display help message.

# PiP-glibc and PiP-gdb

PiP itself can run without the patched PiP-glibc, however, it can
create up to around 10 PiP tasks (actual number depends on the PiP
program) at the same time in the same virtual address space. This
limitation comes from the current glibc implementation. PiP-glibc
relaxes this limitation up to 300 PiP tasks.  In addition to this,
PiP-glibc allows PiP-gdb to access symbols defined in the PiP tasks.
This implies PiP-gdb depends on PiP-glibc.

# Author

Atsushi Hori, Riken CCS
