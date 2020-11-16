#!/bin/sh

execute () {
    echo "TESTING -- $@"
    $@
    echo
}

execute ./pip-pip --help
execute ./pip-pip --dryrun

execute ./pip-pip --dryrun --how=yum
execute ./pip-pip --dryrun --how=yum --sudo
execute ./pip-pip --dryrun --how=docker
execute ./pip-pip --dryrun --how=docker --sudo
execute ./pip-pip --dryrun --how=spack
execute ./pip-pip --dryrun --how=github
execute ./pip-pip --dryrun --how=git-rccs
execute ./pip-pip --dryrun --how=yum,docker --sudo
execute ./pip-pip --dryrun --how=docker,spack
execute ./pip-pip --dryrun --how=spack,github
execute ./pip-pip --dryrun --how=github,git-rccs
execute ./pip-pip --dryrun --how=git-rccs,yum
execute ./pip-pip --dryrun --how=all
execute ./pip-pip --dryrun --how=ALL

execute ./pip-pip --dryrun --how=yum      --version=all --sudo
execute ./pip-pip --dryrun --how=docker   --version=ALL --sudo
execute ./pip-pip --dryrun --how=spack    --version=-1  --sudo
execute ./pip-pip --dryrun --how=git-rccs --version=2   --sudo
execute ./pip-pip --dryrun --how=github   --version=3   --sudo

execute ./pip-pip --dryrun --how=yum    --prefix=INSTALL --sudo
execute ./pip-pip --dryrun --how=docker --prefix=INSTALL --sudo
execute ./pip-pip --dryrun --how=spack  --prefix=INSTALL
execute ./pip-pip --dryrun --how=github --prefix=INSTALL
execute ./pip-pip --dryrun --how=github --prefix=INSTALL//

execute ./pip-pip --dryrun --how=yum    --work=WORK --sudo
execute ./pip-pip --dryrun --how=docker --work=WORK --sudo
execute ./pip-pip --dryrun --how=spack  --work=WORK
execute ./pip-pip --dryrun --how=github --work=WORK
execute ./pip-pip --dryrun --how=github --work=WORK

execute ./pip-pip --dryrun --how=github --prefix=INSTALL --work=WORK
execute ./pip-pip --dryrun --how=github --prefix=INSTALL --work=WORK --noglibc
execute ./pip-pip --dryrun --how=github --prefix=INSTALL --work=WORK --nogdb

execute ./pip-pip --dryrun --how=all --version=all
execute ./pip-pip --dryrun --how=ALL --version=ALL

execute ./pip-pip --dryrun --how=all --version=all --quiet
execute ./pip-pip --dryrun --how=ALL --version=ALL --keep
execute ./pip-pip --dryrun --how=all --version=all --force

execute ./pip-pip --dryrun --how=all --version=all --test=0
execute ./pip-pip --dryrun --how=ALL --version=ALL --test=100
