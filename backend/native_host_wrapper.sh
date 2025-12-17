#!/bin/bash
# Wrapper to run the python script with the correct virtual environment
# and log output for debugging.

# Absolute path to the project directory
PROJECT_DIR="/Users/pp/Desktop/VideoDownloaderExtension"
LOG_FILE="$PROJECT_DIR/native_host.log"

# Ensure log file exists and is writable
touch "$LOG_FILE"

# Log start time
echo "--- Starting Native Host at $(date) ---" >> "$LOG_FILE"

# Run the python script using the venv python
# CRITICAL: stdout must go to Chrome (fd 1), so we only redirect stderr (fd 2) to the log.
"$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/backend/native_host.py" 2>> "$LOG_FILE"
