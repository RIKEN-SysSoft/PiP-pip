#!/bin/sh

if [ -f test.log ]; then
    mv -f test.log test.log.bak > /dev/null 2>&1
fi

fail=false

retval=
execute () {
    $@ >> test.log 2>&1
    retval=$?
}

OK () {
    echo -n "OK TESTING -- $@"
    echo "OK TESTING -- $@" >> test.log
    execute $@
    if [ $retval == 0 ]; then
	echo -e "\tSUCCESS"
	echo "SUCCESS -- $@" >> test.log
    else
	echo -e "\t**** FAILED"
	echo "FAILED -- $@" >> test.log
	fail=true
    fi
}

NG () {
    echo -n "NG TESTING -- $@"
    echo "NG TESTING -- $@" >> test.log
    execute $@
    if [ $retval != 0 ]; then
	echo -e "\tSUCCESS -- $@"
	echo "SUCCESS -- $@" >> test.log
    else
	echo -e "\t****FAILED -- $@"
	echo "FAILED -- $@" >> test.log
	fail=true
    fi
}

OK ./pip-pip --help
OK ./pip-pip --dryrun

OK ./pip-pip --dryrun --how=yum
OK ./pip-pip --dryrun --how=yum --sudo
OK ./pip-pip --dryrun --how=docker
OK ./pip-pip --dryrun --how=docker --sudo
OK ./pip-pip --dryrun --how=spack
OK ./pip-pip --dryrun --how=github
OK ./pip-pip --dryrun --how=git-rccs
OK ./pip-pip --dryrun --how=yum,docker --sudo
OK ./pip-pip --dryrun --how=docker,spack
OK ./pip-pip --dryrun --how=spack,github
OK ./pip-pip --dryrun --how=github,git-rccs
OK ./pip-pip --dryrun --how=git-rccs,yum
OK ./pip-pip --dryrun --how=all
OK ./pip-pip --dryrun --how=ALL

OK ./pip-pip --dryrun --how=yum --sudo --noupdate
OK ./pip-pip --dryrun --how=docker --sudo --noupdate
OK ./pip-pip --dryrun --how=spack --noupdate

OK ./pip-pip --dryrun --how=yum      --version=all --sudo
OK ./pip-pip --dryrun --how=docker   --version=ALL --sudo
OK ./pip-pip --dryrun --how=spack    --version=-1  --sudo
OK ./pip-pip --dryrun --how=git-rccs --version=2   --sudo
OK ./pip-pip --dryrun --how=github   --version=3   --sudo

OK ./pip-pip --dryrun --how=yum    --prefix=INSTALL --sudo
OK ./pip-pip --dryrun --how=docker --prefix=INSTALL --sudo
OK ./pip-pip --dryrun --how=spack  --prefix=INSTALL
OK ./pip-pip --dryrun --how=github --prefix=INSTALL
OK ./pip-pip --dryrun --how=github --prefix=INSTALL//

OK ./pip-pip --dryrun --how=yum    --work=WORK --sudo
OK ./pip-pip --dryrun --how=docker --work=WORK --sudo
OK ./pip-pip --dryrun --how=spack  --work=WORK
OK ./pip-pip --dryrun --how=github --work=WORK

OK ./pip-pip --dryrun --how=yum    --sudo --notest
OK ./pip-pip --dryrun --how=docker --sudo --notest
OK ./pip-pip --dryrun --how=spack  --notest
OK ./pip-pip --dryrun --how=github --notest

OK ./pip-pip --dryrun --how=github --prefix=INSTALL --work=WORK
OK ./pip-pip --dryrun --how=github --prefix=INSTALL --work=WORK --noglibc
OK ./pip-pip --dryrun --how=github --prefix=INSTALL --work=WORK --nogdb

OK ./pip-pip --dryrun --how=all --version=all
OK ./pip-pip --dryrun --how=ALL --version=ALL

OK ./pip-pip --dryrun --how=all --version=all --quiet
OK ./pip-pip --dryrun --how=ALL --version=ALL --keep
OK ./pip-pip --dryrun --how=all --version=all --yes

OK ./pip-pip --dryrun --how=all --version=all --threshold=0
OK ./pip-pip --dryrun --how=all --version=all --threshold=-10
OK ./pip-pip --dryrun --how=ALL --version=ALL --threshold=100

NG ./pip-pip  --dryrun --nosuchoption
NG ./pip-pip --dryrun --how=unknown
NG ./pip-pip --dryrun --version=9

if $fail; then
    echo "FAILED !!!"
    exit 1
fi

echo "Succeeded"
exit 0
