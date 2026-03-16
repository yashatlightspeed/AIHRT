import { useEffect, useRef } from "react";

export default function AudioWaveform({ isActive }) {
  const canvasRef = useRef(null);
  const animRef = useRef(null);
  const analyserRef = useRef(null);
  const sourceRef = useRef(null);
  const ctxRef = useRef(null);

  useEffect(() => {
    if (!isActive) {
      cancelAnimationFrame(animRef.current);
      return;
    }

    let stream;

    (async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const audioCtx = new AudioContext();
        ctxRef.current = audioCtx;
        const analyser = audioCtx.createAnalyser();
        analyser.fftSize = 256;
        analyserRef.current = analyser;

        const source = audioCtx.createMediaStreamSource(stream);
        sourceRef.current = source;
        source.connect(analyser);

        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const draw = () => {
          animRef.current = requestAnimationFrame(draw);
          analyser.getByteFrequencyData(dataArray);

          ctx.clearRect(0, 0, canvas.width, canvas.height);

          const barWidth = (canvas.width / bufferLength) * 2.5;
          let x = 0;

          for (let i = 0; i < bufferLength; i++) {
            const v = dataArray[i] / 255;
            const barHeight = v * canvas.height;

            const r = Math.floor(0 + v * 0);
            const g = Math.floor(229 * v);
            const b = Math.floor(255);

            ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${0.6 + v * 0.4})`;
            ctx.fillRect(x, canvas.height - barHeight, barWidth - 1, barHeight);
            x += barWidth + 1;
          }
        };

        draw();
      } catch (e) {
        console.warn("Waveform mic access failed:", e);
      }
    })();

    return () => {
      cancelAnimationFrame(animRef.current);
      if (ctxRef.current) ctxRef.current.close();
      if (stream) stream.getTracks().forEach((t) => t.stop());
    };
  }, [isActive]);

  return (
    <div style={{
      background: "var(--bg-secondary)", borderRadius: 6,
      border: "1px solid var(--border)", overflow: "hidden",
      position: "relative",
    }}>
      <canvas
        ref={canvasRef}
        width={480}
        height={64}
        style={{ display: "block", width: "100%", height: 64 }}
      />
      <div style={{
        position: "absolute", top: 6, left: 10,
        fontSize: 10, color: "var(--neon-cyan)", letterSpacing: "0.08em",
        display: "flex", alignItems: "center", gap: 6,
      }}>
        <span style={{
          width: 6, height: 6, borderRadius: "50%",
          background: "var(--neon-red)", animation: "blink 1s infinite",
        }} />
        LIVE INPUT
      </div>
    </div>
  );
}
