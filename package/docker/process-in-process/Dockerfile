ARG DOCKER_BASE

FROM $DOCKER_BASE

ARG SRC_REPO
ARG SRC_REF
ARG PIP_VERSION

LABEL maintainer="PiP - Process in Process <procinproc-info@googlegroups.com>"

RUN set -x && \
	git clone $SRC_REPO src && \
	cd src && \
	git fetch origin $SRC_REF:ga-work-branch && \
	git checkout ga-work-branch && \
	`[ -x /usr/bin/python3 ] && echo python3` ./pip-pip \
		--prefix /opt/process-in-process --version $PIP_VERSION \
		--yes --nosubdir --notest && \
	cd .. && \
	rm -rf src
