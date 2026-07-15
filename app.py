import asyncio
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS so other apps/websites can access your streams if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active BBC Radio station slugs for global Akamai streams
STATIONS = {
    "radio1": {"name": "BBC Radio 1", "slug": "bbc_radio_one"},
    "radio1xtra": {"name": "BBC Radio 1Xtra", "slug": "bbc_1xtra"},
    "radio2": {"name": "BBC Radio 2", "slug": "bbc_radio_two"},
    "radio3": {"name": "BBC Radio 3", "slug": "bbc_radio_three"},
    "radio4": {"name": "BBC Radio 4", "slug": "bbc_radio_fourfm"},
    "radio4extra": {"name": "BBC Radio 4 Extra", "slug": "bbc_radio_four_extra"},
    "radio5": {"name": "BBC Radio 5 Live", "slug": "bbc_radio_five_live"},
    "6music": {"name": "BBC Radio 6 Music", "slug": "bbc_6music"}
}

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>📻 BBC Radio FLAC Proxy Online</h1><p>Append /radio1.flac to the URL to stream.</p>"

@app.get("/{station_token}.flac")
async def stream_radio(station_token: str):
    token = station_token.lower()
    if token not in STATIONS:
        raise HTTPException(status_code=404, detail=f"Station '{station_token}' not found")
        
    slug = STATIONS[token]["slug"]
    
    # Live Akamai high-quality streams
    hls_url = f"http://as-hls-ww-live.akamaized.net/pool_904/live/ww/{slug}/{slug}.isml/{slug}-audio=96000.norewind.m3u8"
    
    # ffmpeg command to convert incoming stream directly into FLAC on the fly
    cmd = ['ffmpeg', '-i', hls_url, '-c:a', 'flac', '-f', 'flac', 'pipe:1']
    
    async def generate_chunks():
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
        )
        try:
            while True:
                chunk = await process.stdout.read(4096)
                if not chunk:
                    break
                yield chunk
                await asyncio.sleep(0) # keeps the event loop non-blocking
        except Exception:
            pass
        finally:
            try:
                process.terminate()
                await process.wait()
            except:
                pass
                
    return StreamingResponse(
        generate_chunks(),
        media_type="audio/flac",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )
