import http from "http";
import url from "url";
import fs from "fs";
import path from "path";

const PORT = 3001;

// Mock stations data from api/stations.py
const STATIONS = [
  { id: "radio1", name: "BBC Radio 1", pool: "music_live", slug: "bbc_radio_one", description: "Dance, pop and indie hits", image: "raw/e51f27b2-54b1-4c58-b5e1-12345678901a" },
  { id: "radio1_anthems", name: "BBC Radio 1 Anthems", pool: "music_live", slug: "bbc_radio_one_anthems", description: "Classic 1Xtra bangers", image: "raw/e51f27b2-54b1-4c58-b5e1-12345678901a" },
  { id: "radio1_dance", name: "BBC Radio 1 Dance", pool: "music_live", slug: "bbc_radio_one_dance", description: "Dance and electronic", image: "raw/e51f27b2-54b1-4c58-b5e1-12345678901a" },
  { id: "radio1xtra", name: "BBC Radio 1Xtra", pool: "music_live", slug: "bbc_radio_1xtra", description: "Hip-hop, grime, UK rap", image: "raw/e51f27b2-54b1-4c58-b5e1-12345678901a" },
  { id: "radio2", name: "BBC Radio 2", pool: "music_live", slug: "bbc_radio_two", description: "Pop, rock, and entertainment", image: "raw/e51f27b2-54b1-4c58-b5e1-12345678901a" },
  { id: "radio3", name: "BBC Radio 3", pool: "music_live", slug: "bbc_radio_three", description: "Classical and world music", image: "raw/e51f27b2-54b1-4c58-b5e1-12345678901a" },
  { id: "radio3_unwind", name: "BBC Radio 3 Unwind", pool: "music_live", slug: "bbc_radio_three_unwind", description: "Peaceful and ambient", image: "raw/e51f27b2-54b1-4c58-b5e1-12345678901a" },
  { id: "radio4_extra", name: "BBC Radio 4 Extra", pool: "speech_live", slug: "bbc_radio_four_extra", description: "Comedy, drama, and talks", image: "raw/e51f27b2-54b1-4c58-b5e1-12345678901a" },
  { id: "radio5", name: "BBC Radio 5 Live", pool: "speech_live", slug: "bbc_radio_five_live", description: "News and sports", image: "raw/e51f27b2-54b1-4c58-b5e1-12345678901a" },
  { id: "6music", name: "BBC Radio 6 Music", pool: "music_live", slug: "bbc_radio_six_music", description: "Alternative and independent", image: "raw/e51f27b2-54b1-4c58-b5e1-12345678901a" },
];

const server = http.createServer(async (req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;

  // CORS headers
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.writeHead(200);
    res.end();
    return;
  }

  // Routes
  if (pathname === "/api/stations" && req.method === "GET") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify(STATIONS));
  } else if (pathname.startsWith("/api/") && req.method === "GET") {
    // Stream endpoint - return a mock HLS playlist
    const stationId = pathname.replace("/api/", "");
    const station = STATIONS.find((s) => s.id === stationId);

    if (station) {
      // Return a mock HLS playlist
      const m3u8Content = `#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXTINF:10.0,
https://as-hls-ww-live.akamaized.net/${station.pool}/live/ww/${station.slug}/${station.slug}-audio=96000.norewind.m3u8`;

      res.writeHead(200, {
        "Content-Type": "application/vnd.apple.mpegurl",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
      });
      res.end(m3u8Content);
    } else {
      res.writeHead(404);
      res.end("Station not found");
    }
  } else {
    res.writeHead(404);
    res.end("Not found");
  }
});

server.listen(PORT, () => {
  console.log(`\n✅ Mock API server running on http://localhost:${PORT}`);
  console.log(`📡 Available endpoints:`);
  console.log(`   GET /api/stations - List all stations`);
  console.log(`   GET /api/{station_id} - Get stream for station\n`);
});
