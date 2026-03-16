import { useState, useEffect } from "react";

export default function Landing({ onStartCandidate, onOpenDashboard }) {
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setTick((x) => x + 1), 80);
    return () => clearInterval(t);
  }, []);

  const metrics = [
    { label: "Semantic Drift", value: "SDM", color: "#00e5ff" },
    { label: "Cognitive Load", value: "CLI", color: "#00ff88" },
    { label: "Emotion Align", value: "ECAM", color: "#ffaa00" },
    { label: "Stress Resilience", value: "ACPT", color: "#a855f7" },
  ];

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        background: "var(--bg-primary)",
        position: "relative",
        overflow: "hidden",
      }}
      className="grid-bg"
    >
      {/* Ambient glow */}
      <div style={{
        position: "absolute", top: "-200px", left: "50%", transform: "translateX(-50%)",
        width: "800px", height: "400px",
        background: "radial-gradient(ellipse, rgba(0,229,255,0.06) 0%, transparent 70%)",
        pointerEvents: "none",
      }} />

      {/* Header */}
      <header style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "20px 40px", borderBottom: "1px solid var(--border)",
        backdropFilter: "blur(8px)",
        position: "relative", zIndex: 10,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 6,
            background: "linear-gradient(135deg, var(--neon-cyan), var(--neon-purple))",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 16,
          }}>⬡</div>
          <div>
            <div style={{ fontFamily: "var(--font-display)", fontWeight: 800, fontSize: 16, letterSpacing: "-0.02em" }}>
              AIHRT
            </div>
            <div style={{ fontSize: 10, color: "var(--text-muted)", letterSpacing: "0.08em" }}>
              v1.0.0 · NBCAM ENGINE
            </div>
          </div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-ghost" onClick={onOpenDashboard}>Recruiter Dashboard</button>
          <button className="btn btn-primary" onClick={onStartCandidate}>Begin Assessment</button>
        </div>
      </header>

      {/* Hero */}
      <main style={{
        flex: 1, display: "flex", flexDirection: "column", alignItems: "center",
        justifyContent: "center", padding: "80px 40px", textAlign: "center",
        position: "relative", zIndex: 10,
      }}>
        <div className="tag tag-cyan" style={{ marginBottom: 24 }}>
          Neuro-Behavioral Cognitive Alignment Model
        </div>

        <h1 style={{
          fontFamily: "var(--font-display)", fontSize: "clamp(48px, 7vw, 96px)",
          fontWeight: 800, letterSpacing: "-0.04em", lineHeight: 1,
          marginBottom: 24,
          background: "linear-gradient(135deg, #e8f0fe 0%, var(--neon-cyan) 60%, var(--neon-purple) 100%)",
          WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
        }}>
          Artificially Intelligent<br />Head Recruiter
        </h1>

        <p style={{
          maxWidth: 560, color: "var(--text-secondary)", fontSize: 16,
          lineHeight: 1.7, marginBottom: 48,
        }}>
          Beyond grammar and fluency. AIHRT models reasoning stability, real-time cognitive strain,
          emotional authenticity, and adaptive stress resilience through the NBCAM pipeline.
        </p>

        {/* NBCAM layer cards */}
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16,
          maxWidth: 800, width: "100%", marginBottom: 48,
        }}>
          {metrics.map((m, i) => (
            <div
              key={m.label}
              className="card"
              style={{
                textAlign: "left", padding: 20,
                borderColor: `${m.color}22`,
                animation: `slide-up 0.5s ease ${i * 0.1}s both`,
              }}
            >
              <div style={{
                fontFamily: "var(--font-display)", fontSize: 22,
                fontWeight: 800, color: m.color, marginBottom: 4,
              }}>{m.value}</div>
              <div style={{ fontSize: 11, color: "var(--text-muted)", letterSpacing: "0.05em" }}>
                {m.label}
              </div>
              <div style={{
                marginTop: 12, height: 2, borderRadius: 1,
                background: `linear-gradient(90deg, ${m.color}, transparent)`,
                width: `${40 + ((tick * (i + 1) * 7) % 60)}%`,
                transition: "width 0.08s linear",
              }} />
            </div>
          ))}
        </div>

        {/* CTA */}
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap", justifyContent: "center" }}>
          <button
            className="btn btn-primary"
            style={{ padding: "14px 32px", fontSize: 14 }}
            onClick={onStartCandidate}
          >
            ▶ Start Candidate Assessment
          </button>
          <button
            className="btn btn-ghost"
            style={{ padding: "14px 32px", fontSize: 14 }}
            onClick={onOpenDashboard}
          >
            View Recruiter Dashboard
          </button>
        </div>
      </main>

      {/* Bottom bar */}
      <footer style={{
        padding: "16px 40px", borderTop: "1px solid var(--border)",
        display: "flex", justifyContent: "space-between", alignItems: "center",
        fontSize: 11, color: "var(--text-muted)", letterSpacing: "0.06em",
      }}>
        <span>AIHRT · NBCAM ENGINE · COGNITIVE ASSESSMENT PLATFORM</span>
        <span style={{ display: "flex", gap: 24 }}>
          <span>ASR: Whisper</span>
          <span>NLP: SBERT + RoBERTa</span>
          <span>Audio: Wav2Vec2</span>
        </span>
      </footer>
    </div>
  );
}
