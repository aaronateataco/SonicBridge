import json
from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.error

# BBC Stations - Verified working Akamai live stream pools for global access
BBC_STATIONS = {
    "radio1": {"name": "BBC Radio 1", "pool": "pool_01505109", "slug": "bbc_radio_one", "type": "bbc"},
    "radio1_anthems": {"name": "BBC Radio 1 Anthems", "pool": "pool_11351741", "slug": "bbc_radio_one_anthems", "type": "bbc"},
    "radio1_dance": {"name": "BBC Radio 1 Dance", "pool": "pool_62063831", "slug": "bbc_radio_one_dance", "type": "bbc"},
    "radio1xtra": {"name": "BBC Radio 1Xtra", "pool": "pool_92079267", "slug": "bbc_1xtra", "type": "bbc"},
    "radio2": {"name": "BBC Radio 2", "pool": "pool_74208725", "slug": "bbc_radio_two", "type": "bbc"},
    "radio3": {"name": "BBC Radio 3", "pool": "pool_23461179", "slug": "bbc_radio_three", "type": "bbc"},
    "radio3_unwind": {"name": "BBC Radio 3 Unwind", "pool": "pool_23461179", "slug": "bbc_radio_three_unwind", "type": "bbc"},
    "radio4_extra": {"name": "BBC Radio 4 Extra", "pool": "pool_55057080", "slug": "bbc_radio_four_extra", "type": "bbc"},
    "radio5": {"name": "BBC Radio 5 Live", "pool": "pool_89021708", "slug": "bbc_radio_five_live", "type": "bbc"},
    "6music": {"name": "BBC Radio 6 Music", "pool": "pool_81827798", "slug": "bbc_6music", "type": "bbc"},
    "asian_network": {"name": "BBC Asian Network", "pool": "pool_22108647", "slug": "bbc_asian_network", "type": "bbc"},
    "scotland": {"name": "BBC Radio Scotland", "pool": "pool_43322914", "slug": "bbc_radio_scotland_fm", "type": "bbc"},
    "scotland_extra": {"name": "BBC Radio Scotland Extra", "pool": "pool_59378121", "slug": "bbc_radio_scotland_mw", "type": "bbc"},
    "orkney": {"name": "BBC Radio Orkney", "pool": "pool_50082558", "slug": "bbc_radio_orkney", "type": "bbc"},
    "shetland": {"name": "BBC Radio Shetland", "pool": "pool_23386112", "slug": "bbc_radio_shetland", "type": "bbc"},
    "nan_gaidheal": {"name": "BBC Radio nan Gàidheal", "pool": "pool_01935182", "slug": "bbc_radio_nan_gaidheal", "type": "bbc"},
    "ulster": {"name": "BBC Radio Ulster", "pool": "pool_31244774", "slug": "bbc_radio_ulster", "type": "bbc"},
    "foyle": {"name": "BBC Radio Foyle", "pool": "pool_43178797", "slug": "bbc_radio_foyle", "type": "bbc"},
    "wales": {"name": "BBC Radio Wales", "pool": "pool_97517794", "slug": "bbc_radio_wales_fm", "type": "bbc"},
    "wales_extra": {"name": "BBC Radio Wales Extra", "pool": "pool_34167727", "slug": "bbc_radio_wales_am", "type": "bbc"},
    "cymru": {"name": "BBC Radio Cymru", "pool": "pool_24792333", "slug": "bbc_radio_cymru", "type": "bbc"},
    "cymru2": {"name": "BBC Radio Cymru 2", "pool": "pool_98610936", "slug": "bbc_radio_cymru_2", "type": "bbc"},
}

# Internet Radio Stations - direct streams
INTERNET_STATIONS = {
    "listen_moe": {"name": "Listen.moe", "url": "https://listen.moe/stream", "type": "direct"},
}

# Combine all stations
STATIONS = {**BBC_STATIONS, **INTERNET_STATIONS}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Extract station token from path
        path_parts = self.path.strip('/').split('/')
        station_token = path_parts[1] if len(path_parts) > 1 else None
        
        if not station_token:
            self.send_error(404)
            return
        
        # Strip file extensions
        token = station_token.lower().replace('.flac', '').replace('.ogg', '')
        
        if token not in STATIONS:
            self.send_error(404)
            return
        
        config = STATIONS[token]
        station_type = config.get("type", "bbc")
        
        # Handle direct internet radio streams
        if station_type == "direct":
            self.send_response(200)
            self.send_header('Content-type', 'application/vnd.apple.mpegurl')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            # Return a simple m3u8 playlist pointing to the direct URL
            m3u8_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXTINF:10.0,
{config['url']}
"""
            self.wfile.write(m3u8_content.encode())
            return
        
        # Handle BBC HLS stations
        slug = config['slug']
        pool = config['pool']
        
        # Direct HLS endpoint - returns m3u8 playlist with segment URLs
        # Browser will fetch segments directly from BBC's CDN, avoiding timeouts
        hls_url = f"http://as-hls-ww-live.akamaized.net/{pool}/live/ww/{slug}/{slug}.isml/{slug}-audio=96000.norewind.m3u8"
        
        try:
            # Fetch the HLS playlist
            req = urllib.request.Request(hls_url, headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req, timeout=10) as response:
                playlist_data = response.read()
            
            # Return the HLS playlist with proper headers
            self.send_response(200)
            self.send_header('Content-type', 'application/vnd.apple.mpegurl')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.send_header('Content-Length', len(playlist_data))
            self.end_headers()
            self.wfile.write(playlist_data)
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(f"Failed to fetch stream: {str(e)}".encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
