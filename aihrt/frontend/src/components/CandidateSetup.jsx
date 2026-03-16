import { useState } from "react";
import { api } from "../utils/api";

export default function CandidateSetup({ onReady }) {
  const [form, setForm] = useState({ name: "", email: "", phone: "", position: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!form.name || !form.email) {
      setError("Name and email are required.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      // 1. Create candidate
      const candidate = await api.post("/candidates", form);

      // 2. Create interview session
      const interview = await api.post("/interviews", { candidate_id: candidate.id });

      onReady({
        candidateId: candidate.id,
        candidateName: candidate.name,
        interviewId: interview.id,
        sessionId: interview.session_id,
      });
    } catch (e) {
      setError(e.message || "Setup failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
      background: "var(--bg-primary)", padding: 24,
    }} className="grid-bg">
      <div style={{ width: "100%", maxWidth: 480 }} className="animate-slide-up">

        {/* Header */}
        <div style={{ marginBottom: 32 }}>
          <div className="tag tag-cyan" style={{ marginBottom: 16 }}>Step 1 of 2</div>
          <h1 style={{
            fontFamily: "var(--font-display)", fontSize: 36, fontWeight: 800,
            letterSpacing: "-0.03em", marginBottom: 8,
          }}>
            Candidate Registration
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 13, lineHeight: 1.6 }}>
            Your session will be tracked via session ID. Audio responses are analyzed by the NBCAM pipeline.
          </p>
        </div>

        {/* Form */}
        <div className="card" style={{ display: "flex", flexDirection: "column", gap: 20 }}>

          <div>
            <label>Full Name *</label>
            <input
              className="input"
              placeholder="Alex Chen"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>

          <div>
            <label>Email Address *</label>
            <input
              className="input"
              type="email"
              placeholder="alex@company.com"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>

          <div>
            <label>Phone</label>
            <input
              className="input"
              placeholder="+1 555 000 0000"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
            />
          </div>

          <div>
            <label>Position Applying For</label>
            <input
              className="input"
              placeholder="Senior Software Engineer"
              value={form.position}
              onChange={(e) => setForm({ ...form, position: e.target.value })}
            />
          </div>

          {error && (
            <div style={{
              padding: "10px 14px", borderRadius: 4,
              background: "rgba(255,45,85,0.1)", border: "1px solid rgba(255,45,85,0.3)",
              color: "var(--neon-red)", fontSize: 13,
            }}>
              {error}
            </div>
          )}

          <button
            className="btn btn-primary"
            style={{ width: "100%", justifyContent: "center", padding: "12px" }}
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? "Setting up session..." : "Begin Interview Session ▶"}
          </button>
        </div>

        {/* Info panel */}
        <div style={{
          marginTop: 20, padding: "14px 18px", borderRadius: 6,
          background: "rgba(0,229,255,0.04)", border: "1px solid rgba(0,229,255,0.1)",
          fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.7,
        }}>
          <span style={{ color: "var(--neon-cyan)" }}>ⓘ</span> NBCAM evaluates semantic coherence,
          cognitive load, emotional consistency, and stress resilience.
          Your audio is processed by Whisper ASR and analyzed with SBERT + Wav2Vec2 models.
        </div>
      </div>
    </div>
  );
}
