#!/bin/sh

pip_pip=../pip-pip

if [ -f test.log ]; then
    mv -f test.log test.log.bak > /dev/null 2>&1
fi

fail=false

retval=
execute () {
    $pip_pip $@ >> test.log 2>&1
    retval=$?
}

OK () {
    echo -n "OK TESTING ${pip_pip} $@"
    echo "OK TESTING ${pip_pip} $@" >> test.log
    execute $@
    if [ $retval == 0 ]; then
	echo -e "\tSUCCESS"
	echo "SUCCESS" >> test.log
    else
	echo -e "\t**** FAILED"
	echo "FAILED" >> test.log
	fail=true
    fi
}

NG () {
    echo -n "NG TESTING ${pip_pip} $@"
    echo "NG TESTING ${pip_pip} $@" >> test.log
    execute $@
    if [ $retval != 0 ]; then
	echo -e "\tSUCCESS"
	echo "SUCCESS" >> test.log
    else
	echo -e "\t****FAILED"
	echo "FAILED" >> test.log
	fail=true
    fi
}

OK --help
OK --dryrun
OK --ready
OK --ready=all
OK --ready=ALL
OK --ready=arch
OK --ready=linux

#OK --dryrun --how=yum
#OK --dryrun --how=yum --sudo
OK --dryrun --how=docker
OK --dryrun --how=docker --sudo
OK --dryrun --how=spack
OK --dryrun --how=github
#OK --dryrun --how=yum,docker --sudo
OK --dryrun --how=docker,spack
OK --dryrun --how=spack,github
OK --dryrun --how=all
OK --dryrun --how=ALL

#OK --dryrun --how=yum --sudo --noupdate
OK --dryrun --how=docker --sudo --noupdate
OK --dryrun --how=spack --noupdate

#OK --dryrun --how=yum      --version=all --sudo
OK --dryrun --how=docker   --version=ALL --sudo
#OK --dryrun --how=spack    --version=-1  --sudo
OK --dryrun --how=github   --version=3   --sudo

#OK --dryrun --how=yum    --prefix=INSTALL --sudo
OK --dryrun --how=docker --prefix=INSTALL --sudo
OK --dryrun --how=spack  --prefix=INSTALL
OK --dryrun --how=github --prefix=INSTALL
OK --dryrun --how=github --prefix=INSTALL//

#OK --dryrun --how=yum    --work=WORK --sudo
OK --dryrun --how=docker --work=WORK --sudo
OK --dryrun --how=spack  --work=WORK
OK --dryrun --how=github --work=WORK

#OK --dryrun --how=yum    --sudo --notest
OK --dryrun --how=docker --sudo --notest
OK --dryrun --how=spack  --notest
OK --dryrun --how=github --notest

OK --dryrun --how=docker --sudo --centos=7
OK --dryrun --how=docker --sudo --centos=8
OK --dryrun --how=docker --sudo --centos=7,8
OK --dryrun --how=docker --sudo --centos=all
NG --dryrun --how=docker --sudo --centos=5
NG --dryrun --how=docker --sudo --centos=10

OK --dryrun --how=github --prefix=INSTALL --work=WORK
OK --dryrun --how=github --prefix=INSTALL --work=WORK --noglibc
OK --dryrun --how=github --prefix=INSTALL --work=WORK --nogdb

OK --dryrun --how=all --version=all
OK --dryrun --how=ALL --version=ALL

OK --dryrun --how=all --version=all --quiet
OK --dryrun --how=ALL --version=ALL --keep
OK --dryrun --how=all --version=all --yes

OK --dryrun --how=all --version=all --threshold=0
OK --dryrun --how=all --version=all --threshold=-10
OK --dryrun --how=ALL --version=ALL --threshold=100

NG --dryrun --nosuchoption
NG --dryrun --how=unknown
NG --dryrun --version=999

if $fail; then
    echo "FAILED !!!"
    exit 1
fi

echo "Succeeded"
exit 0
