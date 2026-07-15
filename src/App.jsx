import { useEffect, useMemo, useRef, useState } from "react";

const API_BASE = (import.meta.env.VITE_API_BASE || "https://sonicbridge.onrender.com").replace(/\/+$/, "");

// Decorative dial numbers only - not real broadcast frequencies. Gives each
// card the "tuner" feel the rest of the UI is built around.
function dialFrequency(index) {
  return (87.6 + (index * 1.7) % 20.4).toFixed(1);
}

function StreamUrlRow({ url }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      className="copy-row"
      onClick={async (e) => {
        e.stopPropagation();
        try {
          await navigator.clipboard.writeText(url);
          setCopied(true);
          setTimeout(() => setCopied(false), 1500);
        } catch {
          /* clipboard may be unavailable; silently ignore */
        }
      }}
      title="Copy stream URL — paste into Navidrome, VLC, or any player"
    >
      <code>{url}</code>
      <span className="copy-label">{copied ? "copied" : "copy"}</span>
    </button>
  );
}

export default function App() {
  const [stations, setStations] = useState([]);
  const [status, setStatus] = useState("loading"); // loading | ready | error
  const [current, setCurrent] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isBuffering, setIsBuffering] = useState(false);
  const [volume, setVolume] = useState(0.9);
  const audioRef = useRef(null);

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_BASE}/stations`)
      .then((r) => {
        if (!r.ok) throw new Error(`${r.status}`);
        return r.json();
      })
      .then((data) => {
        if (cancelled) return;
        setStations(data);
        setStatus("ready");
      })
      .catch(() => {
        if (!cancelled) setStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (audioRef.current) audioRef.current.volume = volume;
  }, [volume]);

  const streamUrl = useMemo(
    () => (station) => `${API_BASE}/${station.id}`,
    []
  );

  function play(station) {
    const audio = audioRef.current;
    if (!audio) return;
    if (current?.id === station.id) {
      togglePlay();
      return;
    }
    setCurrent(station);
    setIsBuffering(true);
    audio.src = streamUrl(station);
    audio.play().catch(() => setIsBuffering(false));
  }

  function togglePlay() {
    const audio = audioRef.current;
    if (!audio || !current) return;
    if (audio.paused) {
      setIsBuffering(true);
      audio.play().catch(() => setIsBuffering(false));
    } else {
      audio.pause();
    }
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="dial-mark" aria-hidden="true" />
          <div>
            <h1>SonicBridge</h1>
            <p className="tagline">BBC Sounds, bridged to anywhere</p>
          </div>
        </div>
        <div className="topbar-hint">
          Point Navidrome's Internet Radio at any station's stream URL below.
        </div>
      </header>

      <main className="grid-wrap">
        {status === "loading" && <p className="status-msg">Tuning in…</p>}
        {status === "error" && (
          <p className="status-msg status-error">
            Couldn't reach the backend at <code>{API_BASE}</code>. Set{" "}
            <code>VITE_API_BASE</code> to your deployed Render URL.
          </p>
        )}

        {status === "ready" && (
          <div className="grid">
            {stations.map((station, i) => {
              const active = current?.id === station.id;
              return (
                <article
                  key={station.id}
                  className={`card${active ? " card-active" : ""}`}
                  onClick={() => play(station)}
                >
                  <div className="card-art">
                    <img src={station.image} alt={station.name} loading="lazy" />
                    <span className="freq">{dialFrequency(i)}</span>
                    {active && isPlaying && (
                      <span className="live-pill">
                        <span className="live-dot" /> live
                      </span>
                    )}
                  </div>
                  <div className="card-body">
                    <h2>{station.name}</h2>
                    <p>{station.description}</p>
                  </div>
                  <StreamUrlRow url={streamUrl(station)} />
                </article>
              );
            })}
          </div>
        )}
      </main>

      <footer className={`nowplaying${current ? " nowplaying-active" : ""}`}>
        <audio
          ref={audioRef}
          onPlaying={() => {
            setIsPlaying(true);
            setIsBuffering(false);
          }}
          onPause={() => setIsPlaying(false)}
          onWaiting={() => setIsBuffering(true)}
          onError={() => setIsBuffering(false)}
        />
        {current ? (
          <>
            <img className="np-art" src={current.image} alt="" />
            <div className="np-info">
              <strong>{current.name}</strong>
              <span>{isBuffering ? "buffering…" : isPlaying ? "on air" : "paused"}</span>
            </div>
            <button className="np-toggle" onClick={togglePlay} aria-label={isPlaying ? "Pause" : "Play"}>
              {isPlaying ? "❚❚" : "▶"}
            </button>
            <input
              className="np-volume"
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={volume}
              onChange={(e) => setVolume(Number(e.target.value))}
              aria-label="Volume"
            />
          </>
        ) : (
          <span className="np-placeholder">Select a station to start listening</span>
        )}
      </footer>
    </div>
  );
}
