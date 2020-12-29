#!/bin/bash

if [ ! -x "$(command -v python3.8)" ]; then
    echo "Python3.8 is not installed. Please install it manually and run this script again." >&2
    exit 1
fi

cd $(dirname "$BASH_SOURCE")/..

echo "Run virtual environment..."
source venv/bin/activate

make init

deactivate