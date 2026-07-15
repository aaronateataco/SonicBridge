from http.server import BaseHTTPRequestHandler
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

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
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        stations = []
        for token, config in STATIONS.items():
            stations.append({
                "id": token,
                "name": config["name"],
                "description": f"Live {config['name']} stream",
                "image": f"https://sounds.files.bbci.co.uk/3.9.4/networks/{config['slug']}/colour_default.svg"
            })
        
        import json
        self.wfile.write(json.dumps(stations).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
