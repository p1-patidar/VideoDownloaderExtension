#!/bin/bash

# Log file
LOG="/Users/pp/Desktop/VideoDownloaderExtension/chrome_native.log"

# Log that we started
echo "=== Wrapper started at $(date) ===" >> "$LOG" 2>&1

# Try to execute the Python script
/Users/pp/Desktop/VideoDownloaderExtension/.venv/bin/python3 /Users/pp/Desktop/VideoDownloaderExtension/backend/native_host.py >> "$LOG" 2>&1

# Log exit code
echo "=== Wrapper exited with code $? at $(date) ===" >> "$LOG" 2>&1
