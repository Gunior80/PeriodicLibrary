#!/bin/bash

source venv/bin/activate
export PYTHONPATH="$PYTHONPATH:$(pwd)"

if [ -e .env ]; then
    while IFS= read -r line; do
        export "$line"
    done < .env
fi