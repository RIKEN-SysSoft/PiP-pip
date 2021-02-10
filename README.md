# PiP-pip

[PiP](../../../PiP) package installing program

# Description

`pip-pip` is the program to build and install
[PiP](../../../PiP), [PiP-glibc](../../../PiP-glibc) and
[PiP-gdb](../../../PiP-gdb).

# Prerequisite

This program is written in Python.

Required software packages:

- **Python** (mandatory, version 2.7.5 or higher)
- **Git** (mandatory)
<!-- - Yum [optional] -->
- Docker [optional]
- Spack [optional]

Supported architectures:

- x86_64
- AArch64

Supported Linux (RHEL and CentOS are the guaranteed distributions):

- RHLE/CentOS 7
- RHEL/CentOS 8

# Usage

    $ [<PYTHON>] ./pip-pip <OPTIONS>

`pip-pip` is designed to work and tested on both Python 2.7.5 and
3.7.4. When `./pip-pip` does not work, try explicitly specifying
`python[2|3]` when invoking `pip-pip`.

- `--how=<HOW>`
  Specifying how to install PiP. Choice is one of `yum`, `docker`,
  `spack` and `github`. `yum` and `docker` installations require root
  privilege. Refer to the `--sudo` option below. `spack` will be
  installed automatically if `spack` is not yet installed (or not in
  the PATH). Default is `--how=github`.

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
  (PiP-v3) are valid.  Default is `--version=2`.  PiP-v1 ("1") is deprecated and
  unable to specify. Refer to [PiP](../../PiP) for the version
  differences.

- `--sudo`
  Allow `sudo` when installing `yum` and `docker`. To enable this
  option, user must be a sudoer.

- `--yes`
  This option stops asking if the installing (prefix) directory will
  be re-used when it already exists, and/or if the work directory will
  be deleted when it already exists.

- `--noglibc`
  Do not install PiP-(patched-)glibc and PiP-(patched-)gdb. This
  option is only effective with the `--how=github` option. (refer to the
  next section for more details)

- `--nogdb`
  Do not install PiP-(patched-)gdb. This option is only effective with
  the `--how=github` option. (refer to the next section for more details)

- `--noupdate`
  Do not update PiP lib. if it is already installed (`docker` and `spack`)

- `--nosubdir`
  Do not create subdirectory(ies) in the prefix (install)
  directory. See below.

- `--notest`
  Do not run PiP testsuite after installed

- `--keep`
  Do not remove the work directory(ies) when the installation succeeds.
  If the build directory is the same with the prefix directory, or the
  build directory is somewhere above the prefix directory, then the
  deletion is disabled.

- `--dryrun`
  Dryrun. No actual actions will take place.

- `--quiet`
  Run quietly.

- `--help`
  Display help message.

## Prefix subdirectory(ies)

The `--how` and/or `--version` options may have mutiple values. To
handle this case, `pip-pip` will try to install all possible
combinations of the two options. `pip-pip` will create subdirectories
right under the install directory (`--prefix`) named in the

    <ARCH>-<LINUX>-<HOW>-<PIP-VERSION>
    e.g) x86_64_redhat-7_spack_pip-3, aarch64_redhat-8_github_pip-2, ..

style and each installation of the combinations will be installed in
one of those subdirectries. The `--nosubdir` option supresses this
subdirectory creation.

# PiP-glibc and PiP-gdb

PiP itself can run without the patched PiP-glibc, however, it can
create up to around 10 PiP tasks (actual number depends on the PiP
program) at the same time in the same virtual address space. This
limitation comes from the current glibc implementation. PiP-glibc
relaxes this limitation up to 300 PiP tasks.  In addition to this,
PiP-glibc allows PiP-gdb to access symbols defined in the PiP tasks.
This implies PiP-gdb depends on PiP-glibc.

On CentOS/RedHat 8, PiP will not work at all without having PiP-glibc.

# Mailing Lists

If you have any questions or comments on PiP-pip and/or PiP iteself, 
send e-mails to;

    procinproc-info+noreply@googlegroups.com

Or, join our PiP users' mailing list;

    procinproc-users+noreply@googlegroups.com

# Author

Atsushi Hori, Riken CCS (Japan)
