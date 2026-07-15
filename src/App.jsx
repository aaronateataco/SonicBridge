import { useEffect, useMemo, useRef, useState } from "react";

const API_BASE = (import.meta.env.VITE_API_BASE || "/api").replace(/\/+$/, "");

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

function LicenceDisclaimer({ onAccept }) {
  return (
    <div className="disclaimer-overlay">
      <div className="disclaimer-modal">
        <h2>📻 TV Licence Required</h2>
        <p>
          In the United Kingdom, you must have a valid TV Licence to watch or listen to <strong>any live TV or radio</strong> on <strong>any channel or service</strong>, including BBC Radio via this application.
        </p>
        <p>
          A TV Licence also covers:
        </p>
        <ul>
          <li>Watching or recording live programmes on any channel</li>
          <li>Watching on-demand programmes on BBC iPlayer</li>
          <li>Listening to BBC radio (live or on-demand)</li>
        </ul>
        <p>
          <strong>You are committing an offence if you watch or record any live television or use BBC iPlayer without a TV Licence.</strong>
        </p>
        <p>
          You can check if you need a licence and purchase one at{" "}
          <a href="https://www.tvlicensing.co.uk" target="_blank" rel="noopener noreferrer">
            tvlicensing.co.uk
          </a>
        </p>
        <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginTop: "1.5rem" }}>
          If you are outside the UK, you may use this service without a TV Licence according to your local broadcasting regulations.
        </p>
        <div className="disclaimer-actions">
          <button className="disclaimer-btn" onClick={onAccept}>
            I Have a Valid TV Licence
          </button>
          <a href="https://www.tvlicensing.co.uk" target="_blank" rel="noopener noreferrer" className="disclaimer-link">
            Get a TV Licence
          </a>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [stations, setStations] = useState([]);
  const [status, setStatus] = useState("loading"); // loading | ready | error
  const [current, setCurrent] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isBuffering, setIsBuffering] = useState(false);
  const [volume, setVolume] = useState(0.9);
  const [licenceAccepted, setLicenceAccepted] = useState(false);
  const audioRef = useRef(null);
  const retryTimeoutRef = useRef(null);
  const retryCountRef = useRef(0);

  // Check for licence acceptance on mount
  useEffect(() => {
    const accepted = localStorage.getItem("sonicbridge_licence_accepted");
    if (accepted === "true") {
      setLicenceAccepted(true);
    }
  }, []);

  const handleLicenceAccept = () => {
    localStorage.setItem("sonicbridge_licence_accepted", "true");
    setLicenceAccepted(true);
  };

  useEffect(() => {
    if (!licenceAccepted) return;
    
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
  }, [licenceAccepted]);

  useEffect(() => {
    if (audioRef.current) audioRef.current.volume = volume;
  }, [volume]);

  // Cleanup retries on unmount or station change
  useEffect(() => {
    return () => {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, [current]);

  const streamUrl = useMemo(
    () => (station) => `${API_BASE}/${station.id}`,
    []
  );

  const retryPlayback = (station) => {
    const audio = audioRef.current;
    if (!audio || !station) return;
    
    const maxRetries = 5;
    const retryDelay = Math.min(1000 * Math.pow(1.5, retryCountRef.current), 10000);
    
    if (retryCountRef.current < maxRetries) {
      retryCountRef.current += 1;
      retryTimeoutRef.current = setTimeout(() => {
        if (audio.paused && isPlaying) {
          console.log(`Retrying playback (attempt ${retryCountRef.current}/${maxRetries})...`);
          audio.src = streamUrl(station);
          audio.crossOrigin = "anonymous";
          audio.play().catch(() => {
            setIsBuffering(false);
            retryPlayback(station);
          });
        }
      }, retryDelay);
    } else {
      setIsBuffering(false);
      retryCountRef.current = 0;
    }
  };

  function play(station) {
    const audio = audioRef.current;
    if (!audio) return;
    
    // Clear any pending retries
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
    }
    retryCountRef.current = 0;
    
    if (current?.id === station.id) {
      togglePlay();
      return;
    }
    setCurrent(station);
    setIsPlaying(true);
    setIsBuffering(true);
    audio.src = streamUrl(station);
    audio.crossOrigin = "anonymous";
    audio.play().catch(() => {
      setIsBuffering(false);
      retryPlayback(station);
    });
  }

  function togglePlay() {
    const audio = audioRef.current;
    if (!audio || !current) return;
    
    // Clear retries on manual pause
    if (!audio.paused) {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
        retryCountRef.current = 0;
      }
    }
    
    if (audio.paused) {
      setIsPlaying(true);
      setIsBuffering(true);
      audio.play().catch(() => {
        setIsBuffering(false);
        retryPlayback(current);
      });
    } else {
      setIsPlaying(false);
      audio.pause();
    }
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="dial-mark">📻</div>
          <div>
            <h1>SonicBridge</h1>
            <p className="tagline">BBC Sounds Radio</p>
          </div>
        </div>
        <div className="topbar-hint">
          Stream BBC Radio to any app or player. Use the stream URLs below with Navidrome, VLC, or your favourite player.
        </div>
      </header>

      <main className="grid-wrap" style={{ paddingBottom: '7rem' }}>
        {status === "loading" && <p className="status-msg">Tuning in…</p>}
        {status === "error" && (
          <p className="status-msg status-error">
            Couldn't reach the backend at <code>{API_BASE}</code>. Set{" "}
            <code>VITE_API_BASE</code> to your backend URL.
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
          onCanPlay={() => {
            setIsBuffering(false);
            retryCountRef.current = 0;
          }}
          onPlaying={() => {
            setIsPlaying(true);
            setIsBuffering(false);
            retryCountRef.current = 0;
          }}
          onPause={() => {
            setIsPlaying(false);
          }}
          onWaiting={() => {
            setIsBuffering(true);
          }}
          onStalled={() => {
            setIsBuffering(true);
          }}
          onError={(e) => {
            const error = e.currentTarget.error;
            console.error("Audio error:", error?.code, error?.message);
            setIsBuffering(false);
            // Auto-retry on error instead of stopping
            if (current && isPlaying) {
              retryPlayback(current);
            }
          }}
          crossOrigin="anonymous"
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
      <div className="legal-footer">
        <p>
          🇬🇧 <strong>UK Users:</strong> You must have a valid TV Licence to listen to BBC Radio.{" "}
          <a href="https://www.tvlicensing.co.uk" target="_blank" rel="noopener noreferrer">Check here</a>
        </p>
      </div>
      {!licenceAccepted && <LicenceDisclaimer onAccept={handleLicenceAccept} />}
    </div>
  );
}
