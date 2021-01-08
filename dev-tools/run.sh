#!/bin/bash

cat $(dirname "$BASH_SOURCE")/asciiArt.txt

if [[ "$VIRTUAL_ENV" != "" ]] 
then
    echo "This script runs in an active virtual environment. This is fine for me. But is it fine for you?"
    INVENV=1
else
    echo "This script doesn't run in an virtual environment. This is fine. I will start it for you."
    INVENV=0
fi

if [ ! -x "$(command -v python3.8)" ]; then
    echo "Python3.8 is not installed. Please install it manually and run this script again." >&2
    exit 1
fi

cd $(dirname "$BASH_SOURCE")/..

if [ "$INVENV" = 0 ]; then
    echo "Run virtual environment..."
    source venv/bin/activate
fi

python -m image_analyzer "$@"

if [ "$INVENV" = 0 ]; then
    echo "Stop virtual environment..."
    deactivate
fi
