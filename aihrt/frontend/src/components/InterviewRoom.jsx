import { useState, useEffect, useRef } from "react";
import { api, uploadAudio } from "../utils/api";
import { useAudioRecorder, formatDuration } from "../hooks/useAudioRecorder";
import AudioWaveform from "./AudioWaveform";
import ScoreBar from "./ScoreBar";

export default function InterviewRoom({ session, onComplete }) {
  const [questions, setQuestions] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [phase, setPhase] = useState("ready"); // ready | recording | processing | result | done
  const [result, setResult] = useState(null);
  const [allResults, setAllResults] = useState([]);
  const [timeLimit, setTimeLimit] = useState(120); // seconds
  const [timeLeft, setTimeLeft] = useState(120);
  const [error, setError] = useState("");
  const timerRef = useRef(null);

  const recorder = useAudioRecorder();

  // Load questions
  useEffect(() => {
    api.get("/questions")
      .then((qs) => setQuestions(qs.slice(0, 5))) // 5 questions per session
      .catch(() => setError("Failed to load questions. Ensure backend is running."));
  }, []);

  const currentQuestion = questions[currentIdx];
  const isLastQuestion = currentIdx === questions.length - 1;

  // Countdown timer
  useEffect(() => {
    if (phase === "recording") {
      setTimeLeft(timeLimit);
      timerRef.current = setInterval(() => {
        setTimeLeft((t) => {
          if (t <= 1) {
            clearInterval(timerRef.current);
            handleStopRecording();
            return 0;
          }
          return t - 1;
        });
      }, 1000);
    } else {
      clearInterval(timerRef.current);
    }
    return () => clearInterval(timerRef.current);
  }, [phase]);

  const handleStartRecording = async () => {
    setError("");
    await recorder.startRecording();
    setPhase("recording");
  };

  const handleStopRecording = async () => {
    recorder.stopRecording();
    setPhase("processing");
  };

  // Submit audio once blob is ready
  useEffect(() => {
    if (phase === "processing" && recorder.audioBlob && currentQuestion) {
      uploadAudio(session.sessionId, currentQuestion.id, recorder.audioBlob)
        .then((res) => {
          setResult(res);
          setAllResults((prev) => [...prev, res]);
          setPhase("result");
        })
        .catch((e) => {
          setError("Processing failed: " + e.message);
          setPhase("ready");
        });
    }
  }, [phase, recorder.audioBlob]);

  const handleNext = () => {
    if (isLastQuestion) {
      handleComplete();
    } else {
      setCurrentIdx((i) => i + 1);
      setResult(null);
      recorder.reset();
      setPhase("ready");
    }
  };

  const handleComplete = async () => {
    setPhase("done");
    try {
      await api.post(`/interviews/${session.interviewId}/complete`);
    } catch (e) {
      console.error("Completion error:", e);
    }
    onComplete(session.interviewId);
  };

  if (!questions.length) {
    return (
      <div style={centeredStyle}>
        <div style={{ color: "var(--neon-cyan)", fontSize: 14, animation: "blink 1s infinite" }}>
          {error || "Loading assessment questions..."}
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: "100vh", display: "flex", flexDirection: "column",
      background: "var(--bg-primary)",
    }} className="grid-bg">

      {/* Top bar */}
      <header style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "16px 32px", borderBottom: "1px solid var(--border)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <span style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 15 }}>AIHRT</span>
          <span className="tag tag-cyan">{session.candidateName}</span>
        </div>

        {/* Progress */}
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {questions.map((_, i) => (
            <div key={i} style={{
              width: 8, height: 8, borderRadius: "50%",
              background: i < currentIdx ? "var(--neon-green)"
                : i === currentIdx ? "var(--neon-cyan)"
                  : "var(--border-light)",
              boxShadow: i === currentIdx ? "var(--glow-cyan)" : "none",
              transition: "all 0.3s",
            }} />
          ))}
          <span style={{ fontSize: 12, color: "var(--text-muted)", marginLeft: 4 }}>
            {currentIdx + 1} / {questions.length}
          </span>
        </div>

        {/* Timer */}
        {phase === "recording" && (
          <div style={{
            display: "flex", alignItems: "center", gap: 8,
            color: timeLeft < 20 ? "var(--neon-red)" : "var(--neon-amber)",
            fontFamily: "var(--font-mono)", fontSize: 20, fontWeight: 500,
          }}>
            <span style={{
              width: 8, height: 8, borderRadius: "50%",
              background: "var(--neon-red)",
              animation: "blink 1s infinite",
            }} />
            {formatDuration(timeLeft)}
          </div>
        )}
      </header>

      {/* Main content */}
      <main style={{ flex: 1, display: "flex", gap: 0 }}>

        {/* Left: Question panel */}
        <div style={{
          flex: 1, padding: "40px 48px",
          borderRight: "1px solid var(--border)",
        }}>
          <div className="tag tag-amber" style={{ marginBottom: 20 }}>
            Question {currentIdx + 1} · Difficulty {currentQuestion?.difficulty || 1}/5
          </div>

          <h2 style={{
            fontFamily: "var(--font-display)", fontSize: "clamp(20px, 2.5vw, 30px)",
            fontWeight: 700, lineHeight: 1.3, marginBottom: 32, maxWidth: 560,
            letterSpacing: "-0.02em",
          }}>
            {currentQuestion?.text}
          </h2>

          {/* Recording controls */}
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            {phase === "ready" && (
              <button className="btn btn-primary" onClick={handleStartRecording}
                style={{ width: "fit-content", padding: "12px 28px" }}>
                ⏺ Start Recording
              </button>
            )}

            {phase === "recording" && (
              <>
                <AudioWaveform isActive={true} />
                <div style={{ display: "flex", gap: 12 }}>
                  <button className="btn btn-danger" onClick={handleStopRecording}>
                    ⏹ Stop Recording
                  </button>
                  <span style={{ color: "var(--text-muted)", fontSize: 13, alignSelf: "center" }}>
                    Recording · {formatDuration(recorder.duration)}
                  </span>
                </div>
              </>
            )}

            {phase === "processing" && (
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                <div className="tag tag-cyan" style={{ width: "fit-content" }}>
                  Processing through NBCAM pipeline...
                </div>
                {["ASR · Whisper transcription", "SDM · Semantic drift analysis", "CLI · Cognitive load extraction", "ECAM · Emotion alignment"].map((step, i) => (
                  <div key={step} style={{
                    display: "flex", gap: 10, alignItems: "center",
                    fontSize: 13, color: "var(--text-secondary)",
                    opacity: 0, animation: `fade-in 0.3s ease ${i * 0.4}s forwards`,
                  }}>
                    <div style={{
                      width: 6, height: 6, borderRadius: "50%",
                      background: "var(--neon-cyan)",
                      animation: "blink 0.8s infinite",
                    }} />
                    {step}
                  </div>
                ))}
              </div>
            )}

            {error && (
              <div style={{ color: "var(--neon-red)", fontSize: 13 }}>{error}</div>
            )}
          </div>
        </div>

        {/* Right: Score panel */}
        <div style={{ width: 340, padding: "40px 32px", display: "flex", flexDirection: "column", gap: 24 }}>

          {phase === "result" && result && (
            <div className="animate-fade-in">
              <div style={{ marginBottom: 20 }}>
                <div style={{ fontSize: 11, color: "var(--text-muted)", letterSpacing: "0.06em", marginBottom: 8 }}>
                  NBCAM RESPONSE SCORES
                </div>
                <ScoreBar label="CSS" sublabel="Cognitive Stability" value={result.scores.css} color="#00e5ff" />
                <ScoreBar label="CLI" sublabel="Cognitive Load" value={result.scores.cli} color="#ff2d55" inverted />
                <ScoreBar label="ECS" sublabel="Emotional Consistency" value={result.scores.ecs} color="#ffaa00" />
              </div>

              {/* Transcript preview */}
              <div style={{ marginBottom: 24 }}>
                <div style={{ fontSize: 11, color: "var(--text-muted)", letterSpacing: "0.06em", marginBottom: 8 }}>
                  TRANSCRIPT PREVIEW
                </div>
                <div style={{
                  fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.7,
                  background: "var(--bg-secondary)", padding: "12px 14px", borderRadius: 6,
                  border: "1px solid var(--border)", maxHeight: 120, overflow: "auto",
                }}>
                  {result.transcript || "—"}
                </div>
              </div>

              {/* Emotion alignment */}
              {result.ecam && (
                <div style={{ marginBottom: 24 }}>
                  <div style={{ fontSize: 11, color: "var(--text-muted)", letterSpacing: "0.06em", marginBottom: 8 }}>
                    EMOTION ALIGNMENT
                  </div>
                  <div style={{ display: "flex", gap: 8 }}>
                    <span className="tag tag-cyan">Text: {result.ecam.dominant_text_emotion}</span>
                    <span className={`tag ${result.ecam.mismatch ? "tag-red" : "tag-green"}`}>
                      Voice: {result.ecam.dominant_audio_emotion}
                    </span>
                  </div>
                  {result.ecam.mismatch && (
                    <div style={{ marginTop: 8, fontSize: 11, color: "var(--neon-red)" }}>
                      ⚠ Emotion mismatch detected
                    </div>
                  )}
                </div>
              )}

              <button
                className="btn btn-primary"
                style={{ width: "100%", justifyContent: "center" }}
                onClick={handleNext}
              >
                {isLastQuestion ? "Complete Interview ✓" : "Next Question →"}
              </button>
            </div>
          )}

          {phase === "ready" && (
            <div style={{ color: "var(--text-muted)", fontSize: 13, lineHeight: 1.7 }}>
              <div style={{ fontSize: 11, letterSpacing: "0.06em", marginBottom: 12 }}>ASSESSMENT GUIDE</div>
              <p>Speak clearly and naturally. Your response will be analyzed for:</p>
              <ul style={{ marginTop: 10, paddingLeft: 16, display: "flex", flexDirection: "column", gap: 6 }}>
                <li>Semantic reasoning coherence</li>
                <li>Cognitive strain indicators</li>
                <li>Emotional authenticity</li>
              </ul>
              <p style={{ marginTop: 12 }}>Max time: {formatDuration(timeLimit)} per answer.</p>
            </div>
          )}

          {/* Running scores */}
          {allResults.length > 0 && phase !== "result" && (
            <div>
              <div style={{ fontSize: 11, color: "var(--text-muted)", letterSpacing: "0.06em", marginBottom: 12 }}>
                SESSION RUNNING AVERAGE
              </div>
              {["css", "cli", "ecs"].map((key) => {
                const avg = allResults.reduce((s, r) => s + (r.scores?.[key] || 0), 0) / allResults.length;
                return (
                  <ScoreBar
                    key={key}
                    label={key.toUpperCase()}
                    value={avg}
                    color={key === "cli" ? "#ff2d55" : key === "css" ? "#00e5ff" : "#ffaa00"}
                    inverted={key === "cli"}
                  />
                );
              })}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

const centeredStyle = {
  minHeight: "100vh", display: "flex", alignItems: "center",
  justifyContent: "center", background: "var(--bg-primary)",
};
