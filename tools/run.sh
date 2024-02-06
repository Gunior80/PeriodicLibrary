#!/bin/bash

rootdir="$(cd "$(dirname "$0")" && pwd)"
cd "$rootdir"

source set_env.sh
waitress-serve --host 127.0.0.1 --port=8001 PeriodicLibrary.wsgi:application
deactivate