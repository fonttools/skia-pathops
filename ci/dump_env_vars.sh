#!/bin/bash
if [ -n "$PYENV_PYTHON_VERSION" ]; then
  echo "export PYENV_PYTHON_VERSION=$PYENV_PYTHON_VERSION" >> env_vars.sh
fi
