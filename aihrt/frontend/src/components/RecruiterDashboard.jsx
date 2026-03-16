import { useState, useEffect } from "react";
import { api } from "../utils/api";
import ScoreBar from "./ScoreBar";

function GaugeDial({ value, label, color }) {
  const pct = Math.round(value * 100);
  const circumference = 2 * Math.PI * 40;
  const offset = circumference - (pct / 100) * circumference;

  return (
    <div style={{ textAlign: "center" }}>
      <div style={{ position: "relative", display: "inline-block" }}>
        <svg width={100} height={100} viewBox="0 0 100 100">
          <circle cx={50} cy={50} r={40} fill="none" stroke="var(--border)" strokeWidth={6} />
          <circle
            cx={50} cy={50} r={40} fill="none"
            stroke={color} strokeWidth={6}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            transform="rotate(-90 50 50)"
            style={{ transition: "stroke-dashoffset 1.2s ease", filter: `drop-shadow(0 0 6px ${color})` }}
          />
        </svg>
        <div style={{
          position: "absolute", inset: 0,
          display: "flex", flexDirection: "column",
          alignItems: "center", justifyContent: "center",
        }}>
          <div style={{ fontFamily: "var(--font-display)", fontSize: 22, fontWeight: 800, color }}>
            {pct}
          </div>
          <div style={{ fontSize: 9, color: "var(--text-muted)", letterSpacing: "0.06em" }}>/ 100</div>
        </div>
      </div>
      <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 4, letterSpacing: "0.05em" }}>
        {label}
      </div>
    </div>
  );
}

function TimelineRow({ item, index }) {
  return (
    <div style={{
      display: "grid", gridTemplateColumns: "32px 1fr 80px 80px 80px",
      gap: 16, alignItems: "center", padding: "14px 0",
      borderBottom: "1px solid var(--border)",
      fontSize: 12,
    }}>
      <div style={{
        width: 28, height: 28, borderRadius: "50%",
        background: "var(--bg-secondary)", border: "1px solid var(--border-light)",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 12,
        color: "var(--text-secondary)",
      }}>
        {index + 1}
      </div>
      <div style={{ color: "var(--text-secondary)", overflow: "hidden" }}>
        <div style={{ color: "var(--text-primary)", marginBottom: 2, fontSize: 12, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
          {item.transcript_preview}…
        </div>
      </div>
      {[
        { v: item.css, c: "#00e5ff", label: "CSS" },
        { v: 1 - item.cli, c: "#00ff88", label: "CLI" },
        { v: item.ecs, c: "#ffaa00", label: "ECS" },
      ].map(({ v, c, label }) => (
        <div key={label} style={{ textAlign: "center" }}>
          <div style={{ color: c, fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 14 }}>
            {v != null ? Math.round(v * 100) : "—"}
          </div>
          <div style={{ color: "var(--text-muted)", fontSize: 10 }}>{label}</div>
        </div>
      ))}
    </div>
  );
}

export default function RecruiterDashboard({ interviewId, onBack }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [inputId, setInputId] = useState(interviewId || "");
  const [error, setError] = useState("");
  const [candidates, setCandidates] = useState([]);

  useEffect(() => {
    api.get("/candidates").then(setCandidates).catch(() => {});
    if (interviewId) loadDashboard(interviewId);
  }, [interviewId]);

  const loadDashboard = async (id) => {
    setLoading(true);
    setError("");
    try {
      const result = await api.get(`/scores/dashboard/${id}`);
      setData(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const fcs = data?.final_score?.fcs;
  const fcsColor = fcs >= 75 ? "#00ff88" : fcs >= 50 ? "#ffaa00" : "#ff2d55";

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-primary)", display: "flex", flexDirection: "column" }}>

      {/* Header */}
      <header style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "16px 32px", borderBottom: "1px solid var(--border)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <button className="btn btn-ghost" onClick={onBack} style={{ padding: "6px 12px" }}>← Back</button>
          <span style={{ fontFamily: "var(--font-display)", fontWeight: 800, fontSize: 18 }}>
            Recruiter Dashboard
          </span>
        </div>

        {/* ID lookup */}
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <input
            className="input"
            style={{ width: 160 }}
            placeholder="Interview ID"
            value={inputId}
            onChange={(e) => setInputId(e.target.value)}
          />
          <button
            className="btn btn-primary"
            onClick={() => loadDashboard(inputId)}
            disabled={loading || !inputId}
          >
            {loading ? "Loading..." : "Load"}
          </button>
        </div>
      </header>

      <div style={{ flex: 1, padding: "32px", display: "flex", flexDirection: "column", gap: 24 }}>

        {error && (
          <div style={{
            padding: "12px 16px", borderRadius: 6,
            background: "rgba(255,45,85,0.1)", border: "1px solid rgba(255,45,85,0.3)",
            color: "var(--neon-red)", fontSize: 13,
          }}>{error}</div>
        )}

        {!data && !loading && (
          <div style={{
            flex: 1, display: "flex", alignItems: "center", justifyContent: "center",
            flexDirection: "column", gap: 16, color: "var(--text-muted)",
          }}>
            <div style={{ fontSize: 48 }}>⬡</div>
            <div>Enter an Interview ID above to load assessment results</div>
            {candidates.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <div style={{ fontSize: 11, color: "var(--text-muted)", letterSpacing: "0.06em", marginBottom: 12, textAlign: "center" }}>
                  RECENT CANDIDATES
                </div>
                {candidates.slice(0, 5).map((c) => (
                  <div key={c.id} style={{
                    padding: "8px 16px", marginBottom: 4, borderRadius: 4,
                    background: "var(--bg-card)", border: "1px solid var(--border)",
                    fontSize: 13, color: "var(--text-secondary)", cursor: "pointer",
                  }}>
                    {c.name} – {c.position || "N/A"}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {data && (
          <>
            {/* Candidate info */}
            <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
              <div>
                <h2 style={{ fontFamily: "var(--font-display)", fontSize: 28, fontWeight: 800, letterSpacing: "-0.02em" }}>
                  {data.candidate.name}
                </h2>
                <div style={{ color: "var(--text-secondary)", fontSize: 13, marginTop: 2 }}>
                  {data.candidate.position} · {data.candidate.email}
                </div>
              </div>
              <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
                <span className={`tag ${data.interview.status === "completed" ? "tag-green" : "tag-amber"}`}>
                  {data.interview.status.toUpperCase()}
                </span>
                <span className="tag tag-cyan">
                  Session {data.interview.session_id.slice(0, 8).toUpperCase()}
                </span>
              </div>
            </div>

            {/* Scores row */}
            {data.final_score ? (
              <>
                <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
                  {/* FCS big number */}
                  <div className="card" style={{ flex: "0 0 220px", textAlign: "center" }}>
                    <div style={{ fontSize: 11, color: "var(--text-muted)", letterSpacing: "0.08em", marginBottom: 16 }}>
                      FINAL COGNITIVE SCORE
                    </div>
                    <div style={{
                      fontFamily: "var(--font-display)", fontSize: 72, fontWeight: 800,
                      color: fcsColor, lineHeight: 1,
                      textShadow: `0 0 40px ${fcsColor}66`,
                    }}>
                      {Math.round(fcs)}
                    </div>
                    <div style={{ color: "var(--text-muted)", fontSize: 12, marginTop: 4 }}>/ 100</div>
                    <div style={{ marginTop: 16 }}>
                      <div style={{
                        padding: "6px 12px", borderRadius: 20, display: "inline-block",
                        background: `${fcsColor}20`, border: `1px solid ${fcsColor}40`,
                        fontSize: 12, color: fcsColor,
                      }}>
                        {fcs >= 75 ? "✓ Strong Candidate" : fcs >= 50 ? "⚠ Average Candidate" : "✗ Below Threshold"}
                      </div>
                    </div>
                  </div>

                  {/* Gauge dials */}
                  <div className="card" style={{ flex: 1 }}>
                    <div style={{ fontSize: 11, color: "var(--text-muted)", letterSpacing: "0.08em", marginBottom: 20 }}>
                      NBCAM COMPONENT SCORES
                    </div>
                    <div style={{ display: "flex", gap: 24, justifyContent: "space-around", flexWrap: "wrap" }}>
                      <GaugeDial value={data.final_score.avg_css} label="Cognitive Stability" color="#00e5ff" />
                      <GaugeDial value={1 - data.final_score.avg_cli} label="Low Cognitive Load" color="#00ff88" />
                      <GaugeDial value={data.final_score.avg_ecs} label="Emotional Consistency" color="#ffaa00" />
                      <GaugeDial value={data.final_score.avg_srs} label="Stress Resilience" color="#a855f7" />
                    </div>
                  </div>
                </div>

                {/* Insights */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
                  <div className="card">
                    <div style={{ fontSize: 11, color: "var(--text-muted)", letterSpacing: "0.08em", marginBottom: 12 }}>
                      BEHAVIORAL INSIGHTS
                    </div>
                    <p style={{ color: "var(--text-secondary)", fontSize: 13, lineHeight: 1.8 }}>
                      {data.final_score.behavioral_insights || "Not yet computed."}
                    </p>
                  </div>
                  <div className="card">
                    <div style={{ fontSize: 11, color: "var(--text-muted)", letterSpacing: "0.08em", marginBottom: 12 }}>
                      RECOMMENDATIONS
                    </div>
                    <div style={{ color: "var(--text-secondary)", fontSize: 13, lineHeight: 1.8 }}>
                      {data.final_score.recommendations || "Not yet computed."}
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="card" style={{ color: "var(--text-muted)", textAlign: "center", padding: "32px" }}>
                Interview not yet completed. Scores will appear after the session is finalized.
              </div>
            )}

            {/* Response Timeline */}
            {data.response_timeline.length > 0 && (
              <div className="card">
                <div style={{ fontSize: 11, color: "var(--text-muted)", letterSpacing: "0.08em", marginBottom: 8 }}>
                  RESPONSE TIMELINE
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "32px 1fr 80px 80px 80px", gap: 16, padding: "8px 0", borderBottom: "1px solid var(--border)", fontSize: 11, color: "var(--text-muted)", letterSpacing: "0.06em" }}>
                  <div>#</div><div>TRANSCRIPT</div><div style={{ textAlign: "center" }}>CSS</div><div style={{ textAlign: "center" }}>CLI↓</div><div style={{ textAlign: "center" }}>ECS</div>
                </div>
                {data.response_timeline.map((item, i) => (
                  <TimelineRow key={i} item={item} index={i} />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
