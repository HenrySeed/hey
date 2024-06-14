#!/bin/bash     

VENV_DIR="hey-env"

python -m venv $VENV_DIR

source $VENV_DIR/bin/activate

pip install -e

deactivate