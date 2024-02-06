#!/bin/bash

if [ -z "$1" ]; then
    echo "Please provide the path to the auto-replenishment directory."
    exit 1
fi

rootdir="$(cd "$(dirname "$0")" && pwd)"
cd "$rootdir"

source set_env.sh
"$rootdir/autoadd.py" "$1"
deactivate
