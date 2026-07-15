import http from "http";
import url from "url";
import fs from "fs";
import path from "path";

const PORT = 3001;

// BBC Stations - verified working Akamai live stream pools for global access
const BBC_STATIONS = {
  "radio1": {"name": "BBC Radio 1", "pool": "pool_01505109", "slug": "bbc_radio_one", "description": "The biggest new pop & all day vibes.", "type": "bbc"},
  "radio1_anthems": {"name": "BBC Radio 1 Anthems", "pool": "pool_01505109", "slug": "bbc_radio_one_anthems", "description": "All day anthems from the 00s to now.", "type": "bbc"},
  "radio1_dance": {"name": "BBC Radio 1 Dance", "pool": "pool_01505109", "slug": "bbc_radio_one_dance", "description": "The biggest current, future and classic dance vibes.", "type": "bbc"},
  "radio1xtra": {"name": "BBC Radio 1Xtra", "pool": "pool_92079267", "slug": "bbc_1xtra", "description": "Amplifying black music & culture.", "type": "bbc"},
  "radio2": {"name": "BBC Radio 2", "pool": "pool_74208725", "slug": "bbc_radio_two", "description": "Lift your day with the best tunes from your favourite DJs.", "type": "bbc"},
  "radio3": {"name": "BBC Radio 3", "pool": "pool_23461179", "slug": "bbc_radio_three", "description": "Adventures in classical.", "type": "bbc"},
  "radio3_unwind": {"name": "BBC Radio 3 Unwind", "pool": "pool_23461179", "slug": "bbc_radio_three_unwind", "description": "Music to unwind your mind.", "type": "bbc"},
  "radio4_extra": {"name": "BBC Radio 4 Extra", "pool": "pool_55057080", "slug": "bbc_radio_four_extra", "description": "Journey into the Radio 4 archive.", "type": "bbc"},
  "radio5": {"name": "BBC Radio 5 Live", "pool": "pool_89021708", "slug": "bbc_radio_five_live", "description": "The voice of the UK - breaking news & live sport.", "type": "bbc"},
  "6music": {"name": "BBC Radio 6 Music", "pool": "pool_81827798", "slug": "bbc_6music", "description": "Music beyond the mainstream.", "type": "bbc"},
  "asian_network": {"name": "BBC Asian Network", "pool": "pool_01505109", "slug": "bbc_asian_network", "description": "Celebrating British Asian identity.", "type": "bbc"},
  "scotland": {"name": "BBC Radio Scotland", "pool": "pool_01505109", "slug": "bbc_radio_scotland_fm", "description": "The sound of Scotland's news, sport, music and culture.", "type": "bbc"},
  "scotland_extra": {"name": "BBC Radio Scotland Extra", "pool": "pool_01505109", "slug": "bbc_radio_scotland_mw", "description": "The sound of where you live.", "type": "bbc"},
  "orkney": {"name": "BBC Radio Orkney", "pool": "pool_01505109", "slug": "bbc_radio_orkney", "description": "The sound of where you live.", "type": "bbc"},
  "shetland": {"name": "BBC Radio Shetland", "pool": "pool_01505109", "slug": "bbc_radio_shetland", "description": "The sound of where you live.", "type": "bbc"},
  "nan_gaidheal": {"name": "BBC Radio nan Gàidheal", "pool": "pool_01505109", "slug": "bbc_radio_nan_gaidheal", "description": "Guthan nan Gaidheal gach là as gach ceàrnaidh.", "type": "bbc"},
  "ulster": {"name": "BBC Radio Ulster", "pool": "pool_01505109", "slug": "bbc_radio_ulster", "description": "Local news, sport, music and chat.", "type": "bbc"},
  "foyle": {"name": "BBC Radio Foyle", "pool": "pool_01505109", "slug": "bbc_radio_foyle", "description": "Local news, sport, music and chat.", "type": "bbc"},
  "wales": {"name": "BBC Radio Wales", "pool": "pool_01505109", "slug": "bbc_radio_wales_fm", "description": "News, sport, music and entertainment for Wales.", "type": "bbc"},
  "wales_extra": {"name": "BBC Radio Wales Extra", "pool": "pool_01505109", "slug": "bbc_radio_wales_am", "description": "The sound of where you live.", "type": "bbc"},
  "cymru": {"name": "BBC Radio Cymru", "pool": "pool_01505109", "slug": "bbc_radio_cymru", "description": "Newyddion, cerddoriaeth a chwmni da.", "type": "bbc"},
  "cymru2": {"name": "BBC Radio Cymru 2", "pool": "pool_01505109", "slug": "bbc_radio_cymru_2", "description": "Tiwns trwy'r dydd.", "type": "bbc"},
};

// Internet Radio Stations - direct streams
const INTERNET_STATIONS = {
  "listen_moe": {"name": "Listen.moe", "url": "https://listen.moe/stream", "description": "24/7 anime music radio", "type": "direct"},
};

const STATIONS = {**BBC_STATIONS, **INTERNET_STATIONS};

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
    const stations = [];
    for (const [token, config] of Object.entries(STATIONS)) {
      stations.push({
        id: token,
        name: config.name,
        description: config.description,
        type: config.type,
      });
    }
    res.end(JSON.stringify(stations));
  } else if (pathname.startsWith("/api/") && req.method === "GET") {
    // Stream endpoint - return an HLS playlist
    const stationId = pathname.replace("/api/", "").toLowerCase().replace(/\.(flac|ogg)$/, "");
    const config = STATIONS[stationId];

    if (!config) {
      res.writeHead(404);
      res.end("Station not found");
      return;
    }

    // Handle direct internet radio streams
    if (config.type === "direct") {
      res.writeHead(200, {
        "Content-Type": "application/vnd.apple.mpegurl",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
      });
      const m3u8Content = `#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXTINF:10.0,
${config.url}`;
      res.end(m3u8Content);
      return;
    }

    // Handle BBC HLS stations
    if (config.type === "bbc") {
      const m3u8Content = `#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXTINF:10.0,
https://as-hls-ww-live.akamaized.net/${config.pool}/live/ww/${config.slug}/${config.slug}-audio=96000.norewind.m3u8`;

      res.writeHead(200, {
        "Content-Type": "application/vnd.apple.mpegurl",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
      });
      res.end(m3u8Content);
      return;
    }

    res.writeHead(400);
    res.end("Invalid station type");
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
