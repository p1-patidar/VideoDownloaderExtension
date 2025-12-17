#!/usr/bin/env python3
import struct
import json
import subprocess

# Create a properly formatted Native Messaging message
message = {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
encoded_content = json.dumps(message).encode('utf-8')
encoded_length = struct.pack('@I', len(encoded_content))

# Send to native host
proc = subprocess.Popen(
    ['/Users/pp/Desktop/VideoDownloaderExtension/.venv/bin/python', 
     '/Users/pp/Desktop/VideoDownloaderExtension/backend/native_host.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Write message
proc.stdin.write(encoded_length)
proc.stdin.write(encoded_content)
proc.stdin.flush()

# Read response
raw_length = proc.stdout.read(4)
if len(raw_length) == 4:
    message_length = struct.unpack('@I', raw_length)[0]
    response = proc.stdout.read(message_length).decode('utf-8')
    print("Response:", response)
else:
    print("No response length received")
    
stderr_output = proc.stderr.read().decode('utf-8')
if stderr_output:
    print("Errors:", stderr_output)

proc.terminate()
