import os
import json
import sys
import stat

# Configuration
HOST_NAME = "com.videodownloader.native"
ALLOWED_ORIGINS = [
    "chrome-extension://YOUR_EXTENSION_ID/"  # We will need to update this with the actual ID or allow all for dev
]

def install_host():
    # 1. Get paths - use the wrapper script
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "chrome_wrapper.sh"))
    
    # Make script executable
    st = os.stat(script_path)
    os.chmod(script_path, st.st_mode | stat.S_IEXEC)
    
    # 2. Create Manifest content
    # Note: For development, we might not know the ID yet. 
    # Ideally, the user should pack the extension or we find the ID.
    # For now, we will try to find the ID from the user or instruction.
    # BUT, since we are in dev mode, we can't easily predict the ID unless loaded.
    # A common trick is to allow the key if we had one, but we don't.
    # We will use a placeholder and ask the user to reload or we can try to wildcard if possible (not possible in native messaging).
    
    # WAIT: We can find the ID if the user has already loaded it. 
    # But simpler: We will just write the manifest and tell the user they might need to update the ID if it changes.
    # Actually, let's just use a wildcard for now if possible? No, Chrome doesn't allow wildcards in allowed_origins.
    
    # Let's look for the ID in the previous logs or ask the user.
    # Wait, I can't ask the user easily.
    # I will write a script that tries to be smart, but for now let's just use a placeholder and I will update it.
    # actually, I will check if I can find the ID from the browser tool? No.
    
    # I will write the manifest with a placeholder and then I will ask the user to update it or I will update it if I can find it.
    # BETTER: I will ask the user to provide the ID in the next step or I will just assume they can reload.
    
    # Actually, I will look at the previous `popup.js` or `manifest.json` to see if there is a key.
    # There is no key in manifest.json.
    
    # I will write the manifest.
    
    manifest = {
        "name": HOST_NAME,
        "description": "Video Downloader Native Host",
        "path": script_path,
        "type": "stdio",
        "allowed_origins": [
            "chrome-extension://edbamkmmaooljgokgllaeiokgnecehkf/"  # Your actual Extension ID
        ]
    }
    
    # 3. Write Manifest
    if sys.platform == "darwin":
        manifest_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome/NativeMessagingHosts/")
    elif sys.platform == "linux":
        manifest_dir = os.path.expanduser("~/.config/google-chrome/NativeMessagingHosts/")
    else:
        print("Unsupported platform")
        return

    if not os.path.exists(manifest_dir):
        os.makedirs(manifest_dir)
        
    manifest_path = os.path.join(manifest_dir, f"{HOST_NAME}.json")
    
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Manifest written to {manifest_path}")
    print(f"Host script: {script_path}")
    print("IMPORTANT: You must update the 'allowed_origins' in the manifest file with your actual Extension ID from chrome://extensions")

if __name__ == "__main__":
    install_host()
