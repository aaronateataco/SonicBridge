# 📻 SonicBridge

Stream BBC Radio stations directly to any app or player, with automatic scrobbling to Last.fm.

## Features

- 🎙️ **23 BBC Radio Stations** - Stream all major BBC radio channels
- 🎵 **Now Playing Info** - See what's currently on air (requires BBC API)
- 🎼 **Last.fm Scrobbling** - Automatically log your listening to Last.fm
- 🎨 **GNOME Adwaita Theme** - Clean, modern interface matching GNOME/Linux aesthetics
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🌓 **Light/Dark Mode** - Respects system theme preference
- ♿ **Accessible** - Full keyboard navigation and screen reader support
- 🔄 **Automatic Reconnection** - Keeps playing even with network hiccups
- 📋 **TV Licence Compliance** - UK legal disclaimer included

## Getting Started

### Frontend (Vite + React)

```bash
npm install
npm run dev
```

### Backend (Vercel Functions)

The backend is deployed automatically via Vercel Functions. Local development:

```bash
# Install Vercel CLI
npm install -g vercel

# Run locally
vercel dev
```

### Configuration

1. Copy `.env.example` to `.env.local`:

```bash
cp .env.example .env.local
```

2. (Optional) Add Last.fm API credentials:
   - Go to https://www.last.fm/api/account/create
   - Create an application
   - Copy your API Key and Secret to `.env.local`

## Deployment

### Vercel (Recommended)

```bash
vercel deploy
```

Or connect your GitHub repo to Vercel for automatic deployments.

### Other Providers

The app can run on any provider that supports:
- Static React build (`npm run build`)
- Python serverless functions (for `/api` endpoints)

## Usage

1. **Listen to Radio**: Click any station card to start streaming
2. **Copy Stream URL**: Use the copy button to get a direct stream URL for Navidrome, VLC, etc.
3. **Scrobble to Last.fm**: Click the 🎵 button to connect your Last.fm account
4. **Volume Control**: Use the slider in the player
5. **Auto-Recovery**: The player automatically reconnects if the stream drops

## Architecture

```
Frontend (React)
    ↓
Vercel Functions (/api)
    ↓
BBC Akamai CDN (HLS Streams)
    ↓
Your Player (Browser, Navidrome, VLC, etc.)
```

### API Endpoints

- `GET /api/stations` - List all available BBC Radio stations
- `GET /api/{station_id}` - Stream HLS playlist for a station

## Legal

🇬🇧 **UK Users**: You must have a valid TV Licence to listen to BBC Radio. This includes streaming via SonicBridge.

Check your licence status or purchase one: https://www.tvlicensing.co.uk

## License

MIT

## Acknowledgments

- BBC for the radio streams
- Last.fm for the scrobbling API
- GNOME for the Adwaita design system
- The open-source community
