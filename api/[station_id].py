import json
from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.error

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
