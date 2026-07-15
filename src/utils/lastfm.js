// Last.fm API Integration
const LASTFM_API_KEY = import.meta.env.VITE_LASTFM_API_KEY || "d41d8cd98f00b204e9800998ecf8427e"; // Demo key
const LASTFM_API_SECRET = import.meta.env.VITE_LASTFM_API_SECRET || "";
const LASTFM_API_ROOT = "https://ws.audioscrobbler.com/2.0/";

export const lastfmAuth = {
  getToken: async () => {
    try {
      const response = await fetch(
        `${LASTFM_API_ROOT}?method=auth.gettoken&api_key=${LASTFM_API_KEY}&format=json`
      );
      const data = await response.json();
      return data.token;
    } catch (error) {
      console.error("Failed to get Last.fm token:", error);
      return null;
    }
  },

  getSessionKey: (token) => {
    // Open Last.fm auth window
    const authUrl = `https://www.last.fm/api/auth/?api_key=${LASTFM_API_KEY}&token=${token}`;
    window.open(authUrl, "lastfm_auth", "width=500,height=600");
  },

  getSession: async (token) => {
    try {
      const response = await fetch(
        `${LASTFM_API_ROOT}?method=auth.getsession&token=${token}&api_key=${LASTFM_API_KEY}&format=json`
      );
      const data = await response.json();
      if (data.session) {
        return data.session.key;
      }
    } catch (error) {
      console.error("Failed to get Last.fm session:", error);
    }
    return null;
  },
};

export const lastfmScrobble = {
  scrobble: async (track, artist, album, sessionKey) => {
    if (!sessionKey) return false;

    try {
      const timestamp = Math.floor(Date.now() / 1000);
      const params = new URLSearchParams({
        method: "track.scrobble",
        track: track,
        artist: artist,
        album: album,
        timestamp: timestamp,
        sk: sessionKey,
        api_key: LASTFM_API_KEY,
        format: "json",
      });

      const response = await fetch(LASTFM_API_ROOT, {
        method: "POST",
        body: params,
      });

      const data = await response.json();
      return !data.error;
    } catch (error) {
      console.error("Failed to scrobble to Last.fm:", error);
      return false;
    }
  },

  updateNowPlaying: async (track, artist, album, sessionKey) => {
    if (!sessionKey) return false;

    try {
      const params = new URLSearchParams({
        method: "track.updateNowPlaying",
        track: track,
        artist: artist,
        album: album,
        sk: sessionKey,
        api_key: LASTFM_API_KEY,
        format: "json",
      });

      const response = await fetch(LASTFM_API_ROOT, {
        method: "POST",
        body: params,
      });

      const data = await response.json();
      return !data.error;
    } catch (error) {
      console.error("Failed to update now playing on Last.fm:", error);
      return false;
    }
  },
};
