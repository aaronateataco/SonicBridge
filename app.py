import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Verified working Akamai live stream pools for global access
STATIONS = {
    "radio1": {"name": "BBC Radio 1", "pool": "pool_01505109", "slug": "bbc_radio_one"},
    "radio1xtra": {"name": "BBC Radio 1Xtra", "pool": "pool_92079267", "slug": "bbc_1xtra"},
    "radio2": {"name": "BBC Radio 2", "pool": "pool_74208725", "slug": "bbc_radio_two"},
    "radio3": {"name": "BBC Radio 3", "pool": "pool_23461179", "slug": "bbc_radio_three"},
    "radio4": {"name": "BBC Radio 4", "pool": "pool_55057080", "slug": "bbc_radio_fourfm"},
    "radio4extra": {"name": "BBC Radio 4 Extra", "pool": "pool_26173715", "slug": "bbc_radio_four_extra"},
    "radio5": {"name": "BBC Radio 5 Live", "pool": "pool_89021708", "slug": "bbc_radio_five_live"},
    "6music": {"name": "BBC Radio 6 Music", "pool": "pool_81827798", "slug": "bbc_6music"}
}

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>📻 BBC Radio Stream Proxy Online</h1><p>Append /radio1 to the URL to stream.</p>"

# This captures requests matching /radio1, /radio1.flac, or /radio1.ogg smoothly
@app.get("/{station_token}")
async def stream_radio(station_token: str):
    # Strip any trailing file extensions to match our dictionary keys
    token = station_token.lower().replace(".flac", "").replace(".ogg", "")
    
    if token not in STATIONS:
        raise HTTPException(status_code=404, detail=f"Station '{token}' not found")
        
    pool = STATIONS[token]["pool"]
    slug = STATIONS[token]["slug"]
    
    # Absolute direct Akamai HLS endpoint
    hls_url = f"http://as-hls-ww-live.akamaized.net/{pool}/live/ww/{slug}/{slug}.isml/{slug}-audio=96000.norewind.m3u8"
    
    # Transcode HLS source into high-fidelity FLAC encased in an Ogg stream container
    cmd = ['ffmpeg', '-i', hls_url, '-c:a', 'flac', '-f', 'ogg', 'pipe:1']
    
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
                await asyncio.sleep(0)
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
        media_type="audio/ogg",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )
