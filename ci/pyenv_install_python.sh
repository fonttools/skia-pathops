#!/bin/bash
# Script to install a specific version of Python from source using pyenv.
# This is meant to be run from inside the manylinux1 docker container.

set -x

version=${PYENV_PYTHON_VERSION:-3.8.0}
multibuild_root=${MULTIBUILD_ROOT:-multibuild}

# install pyenv
export PYENV_ROOT="$HOME/.pyenv"
git clone --depth 1 https://github.com/yyuu/pyenv.git "$PYENV_ROOT"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# install python deps
yum install -y zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel tk-devel libffi-devel

# build openssl from source
source "${multibuild_root}/common_utils.sh"
source "${multibuild_root}/library_builders.sh"
build_openssl

# install python
pyenv install -v $version
