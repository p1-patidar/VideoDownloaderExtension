#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment and start server
cd "$DIR"
source .venv/bin/activate
python backend/main.py
