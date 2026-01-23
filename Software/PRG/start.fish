#!/usr/bin/env fish

# Benning Device Manager - Start Script für Fish Shell

source venv/bin/activate.fish
set -x PYTHONPATH (pwd):$PYTHONPATH
python src/main.py
