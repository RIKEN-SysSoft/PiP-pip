#!/bin/sh

failed=false
result=/host/result

if [ -x /usr/bin/python ]; then
	PYTHON=
else
	PYTHON=python3	# for CentOS 8
fi

cd /root && (

if $PYTHON ./pip-pip --prefix /opt/process-in-process --yes --nosubdir --keep
then
	status=0
else
	status=$?
	failed=true
fi

if [ -d work/*/log ]; then
	mkdir $result &&
	cd work/* &&
	(
		mkdir $result/log &&
			cp log/* $result/log/
		mkdir $result/PiP-Testsuite &&
			cp PiP-Testsuite/test.log* $result/PiP-Testsuite/
		mkdir $result/PiP-gdb && (
			cp PiP-gdb/gdb/testsuite/gdb.sum $result/PiP-gdb/
			cp PiP-gdb/gdb/testsuite/gdb.log $result/PiP-gdb/
			cp PiP-gdb/gdb/testsuite/gdb.pip.xml $result/PiP-gdb/
		)
	)		
fi
if $failed; then
	echo ==== `pwd`. ====
	ls
	echo ==== work ====
	ls work
	echo ==== work/* ====
	ls work/*
	echo ==== work/*/log ====
	ls work/*/log
	echo ====  ====
fi

echo "**** pip-pip exit status: $status ****"

# always returns 0, otherwise actions/upload-artifact won't run
exit 0
)
