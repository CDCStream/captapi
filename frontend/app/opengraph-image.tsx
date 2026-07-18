import { ImageResponse } from "next/og";
import { readFile } from "node:fs/promises";
import { join } from "node:path";

export const runtime = "nodejs";
export const alt = "Captapi — One API for structured social data across 27 platforms";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function OpengraphImage() {
  let logoSrc: string | null = null;
  try {
    const buf = await readFile(join(process.cwd(), "public", "logo.png"));
    logoSrc = `data:image/png;base64,${buf.toString("base64")}`;
  } catch {
    logoSrc = null;
  }

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "72px",
          background:
            "linear-gradient(135deg, #0b1224 0%, #0f1b3d 55%, #0a1530 100%)",
          color: "#ffffff",
          fontFamily: "sans-serif",
        }}
      >
        {/* decorative glow */}
        <div
          style={{
            position: "absolute",
            top: -180,
            right: -120,
            width: 520,
            height: 520,
            borderRadius: 9999,
            background:
              "radial-gradient(circle, rgba(56,189,248,0.35) 0%, rgba(37,99,235,0.0) 70%)",
            display: "flex",
          }}
        />

        {/* brand row */}
        <div style={{ display: "flex", alignItems: "center", gap: 28 }}>
          {logoSrc ? (
            <img src={logoSrc} width={104} height={104} style={{ borderRadius: 26 }} />
          ) : null}
          <div style={{ display: "flex", fontSize: 88, fontWeight: 800, letterSpacing: -2 }}>
            <span style={{ color: "#ffffff" }}>Capt</span>
            <span
              style={{
                backgroundImage: "linear-gradient(90deg, #3b82f6, #22d3ee)",
                backgroundClip: "text",
                color: "transparent",
              }}
            >
              api
            </span>
          </div>
        </div>

        {/* headline */}
        <div style={{ display: "flex", flexDirection: "column", gap: 22 }}>
          <div
            style={{
              fontSize: 60,
              fontWeight: 800,
              lineHeight: 1.08,
              letterSpacing: -1.5,
              maxWidth: 980,
            }}
          >
            One API for structured social data across 27 platforms
          </div>
          <div style={{ fontSize: 30, color: "#94a3b8", maxWidth: 940, lineHeight: 1.35 }}>
            170 endpoints for transcripts, AI summaries, comments, search, ads,
            commerce &amp; engagement — clean JSON.
          </div>
        </div>

        {/* footer */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", gap: 14 }}>
            {["YouTube", "TikTok", "Instagram", "X", "Reddit", "Ads", "Commerce"].map((p) => (
              <div
                key={p}
                style={{
                  display: "flex",
                  fontSize: 22,
                  color: "#cbd5e1",
                  padding: "10px 20px",
                  borderRadius: 9999,
                  border: "1px solid rgba(148,163,184,0.3)",
                  background: "rgba(148,163,184,0.08)",
                }}
              >
                {p}
              </div>
            ))}
          </div>
          <div style={{ display: "flex", fontSize: 28, fontWeight: 700, color: "#38bdf8" }}>
            captapi.com
          </div>
        </div>
      </div>
    ),
    { ...size },
  );
}
