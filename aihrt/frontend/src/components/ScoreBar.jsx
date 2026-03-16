export default function ScoreBar({ label, sublabel, value = 0, color = "#00e5ff", inverted = false }) {
  const display = inverted ? (1 - value) : value;
  const pct = Math.round(display * 100);
  const effectiveColor = inverted
    ? value > 0.7 ? "#ff2d55" : value > 0.4 ? "#ffaa00" : "#00ff88"
    : color;

  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
        <div>
          <span style={{
            fontFamily: "var(--font-display)", fontWeight: 700,
            fontSize: 13, color: effectiveColor, marginRight: 8,
          }}>{label}</span>
          {sublabel && (
            <span style={{ fontSize: 11, color: "var(--text-muted)" }}>{sublabel}</span>
          )}
        </div>
        <span style={{
          fontFamily: "var(--font-mono)", fontSize: 13, fontWeight: 500,
          color: effectiveColor,
        }}>
          {pct}%
        </span>
      </div>
      <div style={{
        height: 4, borderRadius: 2, background: "var(--border)",
        overflow: "hidden",
      }}>
        <div style={{
          height: "100%", width: `${pct}%`,
          background: effectiveColor,
          boxShadow: `0 0 8px ${effectiveColor}88`,
          borderRadius: 2,
          transition: "width 0.8s cubic-bezier(0.4, 0, 0.2, 1)",
        }} />
      </div>
    </div>
  );
}
