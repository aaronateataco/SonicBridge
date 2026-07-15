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
    "radio1": {"name": "Radio 1", "pool": "pool_01505109", "slug": "bbc_radio_one", "description": "The biggest new pop & all day vibes.", "image": "p0mw72yd"},
    "radio1_anthems": {"name": "Radio 1 Anthems", "pool": "pool_01505109", "slug": "bbc_radio_one_anthems", "description": "All day anthems from the 00s to now.", "image": "p0mw73cr"},
    "radio1_dance": {"name": "Radio 1 Dance", "pool": "pool_01505109", "slug": "bbc_radio_one_dance", "description": "The biggest current, future and classic dance vibes.", "image": "p0mw73jl"},
    "radio1xtra": {"name": "Radio 1Xtra", "pool": "pool_92079267", "slug": "bbc_1xtra", "description": "Amplifying black music & culture.", "image": "p0mw73ww"},
    "radio2": {"name": "Radio 2", "pool": "pool_74208725", "slug": "bbc_radio_two", "description": "Lift your day with the best tunes from your favourite DJs.", "image": "p0mw747g"},
    "radio3": {"name": "Radio 3", "pool": "pool_23461179", "slug": "bbc_radio_three", "description": "Adventures in classical.", "image": "p0mw74jk"},
    "radio3_unwind": {"name": "Radio 3 Unwind", "pool": "pool_23461179", "slug": "bbc_radio_three_unwind", "description": "Music to unwind your mind.", "image": "p0mw74rj"},
    "radio4_extra": {"name": "Radio 4 Extra", "pool": "pool_55057080", "slug": "bbc_radio_four_extra", "description": "Journey into the Radio 4 archive.", "image": "p0mw751h"},
    "radio5": {"name": "Radio 5 Live", "pool": "pool_89021708", "slug": "bbc_radio_five_live", "description": "The voice of the UK - breaking news & live sport.", "image": "p0mw75bg"},
    "6music": {"name": "Radio 6 Music", "pool": "pool_81827798", "slug": "bbc_6music", "description": "Music beyond the mainstream.", "image": "p0mwrlsp"},
    "asian_network": {"name": "Asian Network", "pool": "pool_01505109", "slug": "bbc_asian_network", "description": "Celebrating British Asian identity.", "image": "p0mwrmw1"},
    "scotland": {"name": "Radio Scotland", "pool": "pool_01505109", "slug": "bbc_radio_scotland_fm", "description": "The sound of Scotland's news, sport, music and culture.", "image": "p0mwrnb1"},
    "scotland_extra": {"name": "Radio Scotland Extra", "pool": "pool_01505109", "slug": "bbc_radio_scotland_mw", "description": "The sound of where you live.", "image": "p0mwrnh8"},
    "orkney": {"name": "Radio Orkney", "pool": "pool_01505109", "slug": "bbc_radio_orkney", "description": "The sound of where you live.", "image": "p0mwrpc9"},
    "shetland": {"name": "Radio Shetland", "pool": "pool_01505109", "slug": "bbc_radio_shetland", "description": "The sound of where you live.", "image": "p0mwrpw1"},
    "nan_gaidheal": {"name": "Radio nan Gàidheal", "pool": "pool_01505109", "slug": "bbc_radio_nan_gaidheal", "description": "Guthan nan Gaidheal gach là as gach ceàrnaidh.", "image": "p0mwrsnm"},
    "ulster": {"name": "Radio Ulster", "pool": "pool_01505109", "slug": "bbc_radio_ulster", "description": "Local news, sport, music and chat.", "image": "p0mwrvhs"},
    "foyle": {"name": "Radio Foyle", "pool": "pool_01505109", "slug": "bbc_radio_foyle", "description": "Local news, sport, music and chat.", "image": "p0mwrz4p"},
    "wales": {"name": "Radio Wales", "pool": "pool_01505109", "slug": "bbc_radio_wales_fm", "description": "News, sport, music and entertainment for Wales.", "image": "p0mws3dw"},
    "wales_extra": {"name": "Radio Wales Extra", "pool": "pool_01505109", "slug": "bbc_radio_wales_am", "description": "The sound of where you live.", "image": "p0mwt9gz"},
    "cymru": {"name": "Radio Cymru", "pool": "pool_01505109", "slug": "bbc_radio_cymru", "description": "Newyddion, cerddoriaeth a chwmni da.", "image": "p0mwtb2k"},
    "cymru2": {"name": "Radio Cymru 2", "pool": "pool_01505109", "slug": "bbc_radio_cymru_2", "description": "Tiwns trwy'r dydd.", "image": "p0mwtbt8"},
}

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>📻 BBC Radio Stream Proxy Online</h1><p>Use /stations for the station list or append /radio1 to the URL to stream.</p>"

@app.get("/stations")
async def list_stations():
    stations = []
    for token, config in STATIONS.items():
        stations.append({
            "id": token,
            "name": config["name"],
            "description": config.get("description", f"Live {config['name']} stream"),
            "image": f"https://ichef.bbci.co.uk/images/ic/raw/{config['image']}.png.webp"
        })
    return stations

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
