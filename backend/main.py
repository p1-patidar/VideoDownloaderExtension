from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import yt_dlp
import os
import json
import asyncio
from typing import Optional

app = FastAPI()

class VideoURL(BaseModel):
    url: str

DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Store for active WebSocket connections
active_connections: list[WebSocket] = []

@app.get("/health")
async def health_check():
    """Health check endpoint for the extension to verify server is running."""
    return {"status": "ok"}

@app.get("/open-folder")
async def open_folder():
    """Open the project folder in Finder."""
    import subprocess
    folder_path = "/Users/pp/Desktop/VideoDownloaderExtension"
    subprocess.run(["open", folder_path])
    return {"status": "opened"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Receive video URL from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "download":
                url = message.get("url")
                if not url:
                    await websocket.send_json({"type": "error", "message": "No URL provided"})
                    continue
                
                # Start download with progress tracking
                await download_with_progress(websocket, url)
                
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass
        if websocket in active_connections:
            active_connections.remove(websocket)

async def download_with_progress(websocket: WebSocket, url: str):
    """Download video with real-time progress updates via WebSocket."""
    abs_download_dir = os.path.expanduser("~/Downloads")
    
    # Progress hook for yt-dlp
    loop = asyncio.get_event_loop()
    
    def progress_hook(d):
        try:
            if d['status'] == 'downloading':
                # Calculate progress
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                
                if total > 0:
                    percent = (downloaded / total) * 100
                else:
                    percent = 0
                
                speed = d.get('speed', 0)
                if speed:
                    speed_str = f"{speed / 1024 / 1024:.1f} MB/s"
                else:
                    speed_str = "-- MB/s"
                
                eta = d.get('eta', 0)
                if eta:
                    eta_str = f"{eta}s"
                else:
                    eta_str = "--"
                
                filename = d.get('filename', '').split('/')[-1]
                
                # Send progress update
                asyncio.run_coroutine_threadsafe(
                    websocket.send_json({
                        "type": "progress",
                        "percent": round(percent, 1),
                        "speed": speed_str,
                        "eta": eta_str,
                        "filename": filename,
                        "downloaded": f"{downloaded / 1024 / 1024:.1f} MB",
                        "total": f"{total / 1024 / 1024:.1f} MB" if total else "-- MB"
                    }),
                    loop
                )
                
            elif d['status'] == 'finished':
                filename = d.get('filename', '').split('/')[-1]
                asyncio.run_coroutine_threadsafe(
                    websocket.send_json({
                        "type": "processing",
                        "message": f"Processing: {filename}"
                    }),
                    loop
                )
                
        except Exception as e:
            print(f"Progress hook error: {e}")
    
    try:
        await websocket.send_json({
            "type": "status",
            "message": "Fetching video info..."
        })
        
        ydl_opts = {
            'outtmpl': os.path.join(abs_download_dir, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
        }
        
        # Run yt-dlp in a thread pool to avoid blocking
        def do_download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return info.get('title', 'Video')
        
        title = await asyncio.get_event_loop().run_in_executor(None, do_download)
        
        await websocket.send_json({
            "type": "complete",
            "message": f"Downloaded: {title}",
            "path": abs_download_dir
        })
        
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })

# Keep the REST endpoint for backward compatibility
@app.post("/download")
async def download_video(video: VideoURL):
    try:
        abs_download_dir = os.path.expanduser("~/Downloads")
        print(f"Downloading to: {abs_download_dir}")
        
        ydl_opts = {
            'outtmpl': os.path.join(abs_download_dir, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video.url])
        return {"message": f"Download started successfully. Saved to: {abs_download_dir}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
