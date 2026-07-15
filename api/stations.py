from http.server import BaseHTTPRequestHandler
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# BBC Stations - verified working Akamai live stream pools for global access
BBC_STATIONS = {
    "radio1": {"name": "BBC Radio 1", "pool": "pool_01505109", "slug": "bbc_radio_one", "description": "The biggest new pop & all day vibes.", "image": "p0mw72yd", "type": "bbc"},
    "radio1_anthems": {"name": "BBC Radio 1 Anthems", "pool": "pool_01505109", "slug": "bbc_radio_one_anthems", "description": "All day anthems from the 00s to now.", "image": "p0mw73cr", "type": "bbc"},
    "radio1_dance": {"name": "BBC Radio 1 Dance", "pool": "pool_01505109", "slug": "bbc_radio_one_dance", "description": "The biggest current, future and classic dance vibes.", "image": "p0mw73jl", "type": "bbc"},
    "radio1xtra": {"name": "BBC Radio 1Xtra", "pool": "pool_92079267", "slug": "bbc_1xtra", "description": "Amplifying black music & culture.", "image": "p0mw73ww", "type": "bbc"},
    "radio2": {"name": "BBC Radio 2", "pool": "pool_74208725", "slug": "bbc_radio_two", "description": "Lift your day with the best tunes from your favourite DJs.", "image": "p0mw747g", "type": "bbc"},
    "radio3": {"name": "BBC Radio 3", "pool": "pool_23461179", "slug": "bbc_radio_three", "description": "Adventures in classical.", "image": "p0mw74jk", "type": "bbc"},
    "radio3_unwind": {"name": "BBC Radio 3 Unwind", "pool": "pool_23461179", "slug": "bbc_radio_three_unwind", "description": "Music to unwind your mind.", "image": "p0mw74rj", "type": "bbc"},
    "radio4_extra": {"name": "BBC Radio 4 Extra", "pool": "pool_55057080", "slug": "bbc_radio_four_extra", "description": "Journey into the Radio 4 archive.", "image": "p0mw751h", "type": "bbc"},
    "radio5": {"name": "BBC Radio 5 Live", "pool": "pool_89021708", "slug": "bbc_radio_five_live", "description": "The voice of the UK - breaking news & live sport.", "image": "p0mw75bg", "type": "bbc"},
    "6music": {"name": "BBC Radio 6 Music", "pool": "pool_81827798", "slug": "bbc_6music", "description": "Music beyond the mainstream.", "image": "p0mwrlsp", "type": "bbc"},
    "asian_network": {"name": "BBC Asian Network", "pool": "pool_01505109", "slug": "bbc_asian_network", "description": "Celebrating British Asian identity.", "image": "p0mwrmw1", "type": "bbc"},
    "scotland": {"name": "BBC Radio Scotland", "pool": "pool_01505109", "slug": "bbc_radio_scotland_fm", "description": "The sound of Scotland's news, sport, music and culture.", "image": "p0mwrnb1", "type": "bbc"},
    "scotland_extra": {"name": "BBC Radio Scotland Extra", "pool": "pool_01505109", "slug": "bbc_radio_scotland_mw", "description": "The sound of where you live.", "image": "p0mwrnh8", "type": "bbc"},
    "orkney": {"name": "BBC Radio Orkney", "pool": "pool_01505109", "slug": "bbc_radio_orkney", "description": "The sound of where you live.", "image": "p0mwrpc9", "type": "bbc"},
    "shetland": {"name": "BBC Radio Shetland", "pool": "pool_01505109", "slug": "bbc_radio_shetland", "description": "The sound of where you live.", "image": "p0mwrpw1", "type": "bbc"},
    "nan_gaidheal": {"name": "BBC Radio nan Gàidheal", "pool": "pool_01505109", "slug": "bbc_radio_nan_gaidheal", "description": "Guthan nan Gaidheal gach là as gach ceàrnaidh.", "image": "p0mwrsnm", "type": "bbc"},
    "ulster": {"name": "BBC Radio Ulster", "pool": "pool_01505109", "slug": "bbc_radio_ulster", "description": "Local news, sport, music and chat.", "image": "p0mwrvhs", "type": "bbc"},
    "foyle": {"name": "BBC Radio Foyle", "pool": "pool_01505109", "slug": "bbc_radio_foyle", "description": "Local news, sport, music and chat.", "image": "p0mwrz4p", "type": "bbc"},
    "wales": {"name": "BBC Radio Wales", "pool": "pool_01505109", "slug": "bbc_radio_wales_fm", "description": "News, sport, music and entertainment for Wales.", "image": "p0mws3dw", "type": "bbc"},
    "wales_extra": {"name": "BBC Radio Wales Extra", "pool": "pool_01505109", "slug": "bbc_radio_wales_am", "description": "The sound of where you live.", "image": "p0mwt9gz", "type": "bbc"},
    "cymru": {"name": "BBC Radio Cymru", "pool": "pool_01505109", "slug": "bbc_radio_cymru", "description": "Newyddion, cerddoriaeth a chwmni da.", "image": "p0mwtb2k", "type": "bbc"},
    "cymru2": {"name": "BBC Radio Cymru 2", "pool": "pool_01505109", "slug": "bbc_radio_cymru_2", "description": "Tiwns trwy'r dydd.", "image": "p0mwtbt8", "type": "bbc"},
}

# Internet Radio Stations - direct streams
INTERNET_STATIONS = {
    "listen_moe": {"name": "Listen.moe", "url": "https://listen.moe/stream", "description": "24/7 anime music radio", "image": "🎌", "type": "direct"},
}

# Combine all stations
STATIONS = {**BBC_STATIONS, **INTERNET_STATIONS}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        stations = []
        for token, config in STATIONS.items():
            stations.append({
                "id": token,
                "name": config["name"],
                "description": config["description"],
                "image": config.get("image", "default"),
                "type": config.get("type", "bbc")
            })
        
        import json
        self.wfile.write(json.dumps(stations).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
