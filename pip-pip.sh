#!/bin/sh

set -eu

cmd=$0
cwd=`pwd`

pip_default_version=2

begin_str=">>>"

print_usage () {
    echo "`basename $cmd` <OPTIONS>"
    echo "   OPTIONS:"
    echo "     --prefix <PREFIX_DIR>"
    echo "     --build <BUILD_DIR>"
    echo "     --pip <PIP_VERSION:2|3>"
    echo "     --clean"
    echo "     --dryrun"
    if [ $# -ne 0 ]; then
	echo "     --repo=GITHUB|RCCS"
	echo "     --all"
    fi
    exit 1
}

if ! [ -f /etc/redhat-release ]; then
    echo "Unsupported Linux distribution"; exit 1
fi
release=`cat /etc/redhat-release`
case $release in
    *Linux*7.*) linux_version=7;;
    *Linux*8.*) linux_version=8;;
    *)		echo "Unsupported Linux distribution"; exit 1;;
esac

config_guess=`./config.guess`
case $config_guess in
    x86_64-*)  arch=x86_64;;
    aarch64-*) arch=aarch64;;
    *)	       echo "Unsupported architecture"; exit 1;;
esac

prefix=$cwd
build=$cwd
pip_version=$pip_default_version
git="GITHUB"			# default
flag_clean=false
flag_all=false
flag_dryrun=false

while [ $# -gt 0 ]; do
    case $1 in
	-*prefix)	shift; prefix=`realpath $1`;;
	-*build)	shift; build=`realpath $1`;;
	-*pip)		shift; pip_version=$1;;
	-*git)		shift; git=$1;;
	-*clean)	flag_clean=true;;
	-*dry*)		flag_dryrun=true;;
	-*all)		flag_all=true;;
        -*secret)	print_usage 1;;
	*)		echo "Unknown option"; print_usage;;
    esac
    shift
done

is_partof () {
    path0=$1
    path1=$2
    if [ $path0 == $path1 ]; then return 0; fi
    case $path0 in
	"${path1}/"*) return 0;;
    esac
    return 1
}

build () {
    logfile=$1
    shift
    echo "$@ >> $logfile "
    $@ >> $logfile 2>&1 &
    pid=$!
    while kill -0 $pid > /dev/null 2>&1; do
	sleep 1
	echo -n "."
    done
    wait $pid
    exst=$?
    if [ $exst == 0 ]; then
	echo " SUCCEEDED"
    else
	echo " FAILED"
	exit 1;
    fi
    return $?
}

if $flag_clean; then
    if is_partof $prefix $build ]; then
	echo "--clean is disabled since PREFIX is part of BUILD"
	flag_clean=false
    fi
fi

if ! $flag_all; then
    case "$pip_version" in
	-1) pip_version=1;;		# hidden, deprecated version
	2)  pip_vcrsion=2;;
	3)  pip_vcrsion=3;;
	*)  echo "Illegal PiP version"; print_usage;;
    esac
fi

if [ $pip_version == 1 -a $linux_version == 8 ]; then
    echo "RHEL/CentOS8 is not supported by pip-1"; exit 1
fi

case $git in
    github|GITHUB)
	repo=https://github.com/RIKEN-SysSoft/;
	pip="PiP";;
    rccs|RCCS)			# private repo
	repo=git@git.sys.r-ccs.riken.jp:software/;
	pip="PIP";;
    *)
	echo "Unknown repo"; print_usage;;
esac

pip_pip () {
    prefix=$1
    build=$2
    pip_version=$3

    if $flag_all; then
	prefix_base=${prefix}/${arch}_redhat-${linux_version}_pip-${pip_version}
    else
	prefix_base=${prefix}
    fi

    if $flag_all; then
	build_base=${build}/${arch}_redhat-${linux_version}_pip-${pip_version}
    else
	build_base=${build}
    fi

    if [ -d $build_base ]; then
	echo "Build dir. exists"
	return 1;
    else
	mkdir -p $build_base
    fi

    repo_glibc=${repo}${pip}-glibc.git
    repo_pip=${repo}${pip}.git
    repo_gdb=${repo}${pip}-gdb.git

    branch_pip=pip-$pip_version

    if [ $linux_version == 7 ]; then
	branch_glibc=centos/glibc-2.17-260.el7.pip.branch
	branch_gdb=centos/gdb-7.6.1-94.el7.pip.branch
    else
	branch_glibc=centos/glibc-2.28-72.el8_1.1.pip.branch
	branch_gdb=centos/gdb-7.6.1-94.el7.pip.branch # temporaly should be fixed !!
    fi

    echo "Linux: " $linux_version
    echo "Arch:  " $arch
    echo "PiP:   " ${pip}-${pip_version}
    echo "Repo:  " $repo
    echo "Build: " $build_base
    echo "Prefix:" $prefix_base

    if $flag_dryrun; then return 0; fi

    log_base=$build_base/log
    if ! [ -d $log_base ]; then
	mkdir $log_base
    fi

    cd $build_base

    echo "[ PiP-Glibc ]"
    build_log=$log_base/pip-glibc-build.log
    echo -n > $build_log
    mkdir $build_base/${pip}-glibc
    echo; echo "$begin_str Cloning PiP-glibc"
    build $build_log git clone -b $branch_glibc $repo_glibc

    echo "$begin_str Building PiP-glibc"
    glibc_builddir=${build_base}/glibc-build
    mkdir $glibc_builddir
    (
	cd $glibc_builddir
	build $build_log ../${pip}-glibc/build.sh ${prefix_base}/glibc-install
    )

    if ! [ -x ${prefix_base}/glibc-install/bin/piplnlibs.sh ]; then
	echo "FAIL"; exit 1;
    fi

    echo "[ PiP Lib. ]"
    build_log=${log_base}/pip-lib-build.log
    echo -n > $build_log
    echo; echo "$begin_str Cloning PiP lib."
    build $build_log git clone -b $branch_pip $repo_pip

    echo "$begin_str Building PiP lib."
    (
	cd ${pip}
	build $build_log ./configure \
	    --prefix=${prefix_base}/pip-install \
	    --with-glibc-libdir=${prefix_base}/glibc-install/lib
	build $build_log make
	build $build_log make test
	if [ $? -ne 0 ]; then
	    echo "CHECK FAIL"; exit 1
	fi
	build $build_log make install
	build $build_log make check-installed
	if [ $? -ne 0 ]; then
	    echo "CHECK-INSTALLED FAIL"; exit 1
	fi
	build $build_log make doc-install
    )

    if ! [ -x ${prefix_base}/pip-install/bin/pipcc ]; then
	echo "FAIL"; exit 1
    fi

    echo "[ PiP-gdb ]"
    build_log=${log_base}/pip-gdb-build.log
    echo -n > $build_log
    echo; echo "$begin_str Cloning PiP-gdb"
    build $build_log git clone -b $branch_gdb $repo_gdb

    echo "$begin_str Building PiP-gdb"
    (
	cd ${pip}-gdb
	build $build_log ./build.sh --prefix=${prefix_base}/gdb-install \
	    --with-pip=${prefix_base}/pip-install
    )

    if ! [ -x ${prefix_base}/gdb-install/bin/pip-gdb ]; then
	echo "FAIL"; exit 1
    fi

    if $flag_clean; then
	rm -f -r $build_base
    fi

    return 0
}

if $flag_all; then
    if [ $linux_version == 7 ]; then
	versions="1 2 3"
    else
	versions="2 3"		# pip-1 does not support RHEL8
    fi
    for ver in $versions; do
	pip_pip "$prefix" "$build" "$ver"
	if [ $? != 0 ]; then exit $?; fi
    done
else
    pip_pip "$prefix" "$build" "$pip_version"
fi

exit $?
