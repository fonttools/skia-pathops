#!/bin/bash
# Script to install a specific version of Python from source using pyenv.
# This is meant to be run from inside the manylinux1 docker container.

set -x

version=${PYENV_PYTHON_VERSION:-3.8.0}
multibuild_root=${MULTIBUILD_ROOT:-multibuild}

# install pyenv
if [ -z "$PYENV_ROOT" ]; then
	export PYENV_ROOT="$HOME/.pyenv"
	if [ ! -d "$PYENV_ROOT" ]; then
		git clone --depth 1 https://github.com/yyuu/pyenv.git "$PYENV_ROOT"
	fi
fi
if ! [ -x "$(command -v pyenv)" ]; then
	export PATH="$PYENV_ROOT/bin:$PATH"
	eval "$(pyenv init -)"
fi

# install python deps
yum install -y zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel tk-devel libffi-devel

# build openssl from source
source "${multibuild_root}/common_utils.sh"
source "${multibuild_root}/library_builders.sh"
build_openssl
# clean up build files
rm -rf archives arch_tmp openssl-*

# install python
pyenv install $version

# activate python
pyenv global $version
pyenv rehash
python --version
