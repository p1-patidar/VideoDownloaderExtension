#!/Users/pp/Desktop/VideoDownloaderExtension/.venv/bin/python3
import sys
import json
import struct
import os
import traceback
import subprocess

# Log to stderr for debugging (Chrome doesn't read stderr)
import sys
sys.stderr.write(f"[DEBUG] Native host starting at {os.getcwd()}\n")
sys.stderr.flush()

# Windows/Posix compatibility
if sys.platform == "win32":
    import msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

def get_message():
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        sys.exit(0)
    message_length = struct.unpack('@I', raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode('utf-8')
    return json.loads(message)

def send_message(message_content):
    encoded_content = json.dumps(message_content).encode('utf-8')
    encoded_length = struct.pack('@I', len(encoded_content))
    sys.stdout.buffer.write(encoded_length)
    sys.stdout.buffer.write(encoded_content)
    sys.stdout.buffer.flush()

def download_video(url):
    try:
        # Determine download directory (User's Downloads folder)
        download_dir = os.path.expanduser("~/Downloads")
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        
        # Get the path to yt-dlp in the venv
        script_dir = os.path.dirname(os.path.abspath(__file__))
        venv_python = os.path.join(os.path.dirname(script_dir), ".venv", "bin", "python3")
        
        # Use subprocess to call yt-dlp
        import subprocess
        result = subprocess.run(
            [venv_python, "-m", "yt_dlp",
             "-f", "bestvideo+bestaudio/best",
             "--merge-output-format", "mp4",
             "-o", os.path.join(download_dir, "%(title)s.%(ext)s"),
             url],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        if result.returncode == 0:
            return {"status": "success", "message": f"Downloaded to {download_dir}"}
        else:
            return {"status": "error", "message": f"yt-dlp error: {result.stderr}"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Download timeout (>2 minutes)"}
    except Exception as e:
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

def start_server():
    """Open Finder to the folder containing start_server.command"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.dirname(script_dir)  # Parent folder
        
        # Simple AppleScript to open Finder to the folder
        applescript = f'''
        tell application "Finder"
            activate
            open POSIX file "{folder_path}"
        end tell
        '''
        
        result = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return {"status": "success", "message": "Opened folder in Finder"}
        else:
            return {"status": "error", "message": f"AppleScript error: {result.stderr}"}
            
    except Exception as e:
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

def main():
    sys.stderr.write("[DEBUG] Entering main loop\n")
    sys.stderr.flush()
    while True:
        try:
            sys.stderr.write("[DEBUG] Waiting for message\n")
            sys.stderr.flush()
            message = get_message()
            sys.stderr.write(f"[DEBUG] Received message: {message}\n")
            sys.stderr.flush()
            
            action = message.get('action')
            
            if action == 'start_server':
                result = start_server()
                send_message(result)
            elif 'url' in message:
                result = download_video(message['url'])
                send_message(result)
            else:
                send_message({"status": "error", "message": "Unknown action"})
        except Exception as e:
            sys.stderr.write(f"[DEBUG] Exception: {str(e)}\n")
            sys.stderr.flush()
            send_message({"status": "error", "message": str(e)})

if __name__ == '__main__':
    main()
