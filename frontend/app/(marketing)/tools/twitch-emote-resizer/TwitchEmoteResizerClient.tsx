"use client";

import { useCallback, useRef, useState } from "react";
import { Upload, Download, ImageIcon } from "lucide-react";

const SIZES = [
  { px: 112, label: "112 × 112", use: "Twitch (required)" },
  { px: 56, label: "56 × 56", use: "Twitch (required)" },
  { px: 28, label: "28 × 28", use: "Twitch (required)" },
  { px: 128, label: "128 × 128", use: "Discord emoji" },
];

interface Resized {
  px: number;
  url: string;
}

function resizeToSquare(img: HTMLImageElement, px: number): string {
  const canvas = document.createElement("canvas");
  canvas.width = px;
  canvas.height = px;
  const ctx = canvas.getContext("2d")!;
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = "high";

  // Center-crop to square, then scale down.
  const side = Math.min(img.naturalWidth, img.naturalHeight);
  const sx = (img.naturalWidth - side) / 2;
  const sy = (img.naturalHeight - side) / 2;
  ctx.drawImage(img, sx, sy, side, side, 0, 0, px, px);
  return canvas.toDataURL("image/png");
}

export default function TwitchEmoteResizerClient() {
  const [results, setResults] = useState<Resized[]>([]);
  const [fileName, setFileName] = useState("");
  const [error, setError] = useState("");
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((file: File) => {
    setError("");
    if (!file.type.startsWith("image/")) {
      setError("Please choose an image file (PNG, JPG, GIF, or WebP).");
      return;
    }
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      setResults(SIZES.map((s) => ({ px: s.px, url: resizeToSquare(img, s.px) })));
      setFileName(file.name.replace(/\.[^.]+$/, ""));
      URL.revokeObjectURL(url);
    };
    img.onerror = () => {
      setError("Couldn't read that image — try a different file.");
      URL.revokeObjectURL(url);
    };
    img.src = url;
  }, []);

  const download = (r: Resized) => {
    const a = document.createElement("a");
    a.href = r.url;
    a.download = `${fileName || "emote"}-${r.px}x${r.px}.png`;
    a.click();
  };

  return (
    <div className="mt-8">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          const f = e.dataTransfer.files?.[0];
          if (f) handleFile(f);
        }}
        onClick={() => inputRef.current?.click()}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-10 text-center transition-colors ${
          dragging ? "border-primary bg-primary/5" : "hover:bg-muted/40"
        }`}
      >
        <Upload className="size-8 text-muted-foreground" />
        <p className="mt-3 font-medium">Drop your emote image here, or click to browse</p>
        <p className="mt-1 text-sm text-muted-foreground">
          PNG with transparency works best. Square images avoid cropping — everything stays in your browser.
        </p>
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
        />
      </div>

      {error && <p className="mt-3 text-sm text-red-500">{error}</p>}

      {results.length > 0 && (
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {results.map((r) => {
            const spec = SIZES.find((s) => s.px === r.px)!;
            return (
              <div key={r.px} className="rounded-2xl border bg-card p-4 text-center">
                {/* checkerboard shows transparency */}
                <div
                  className="mx-auto flex size-32 items-center justify-center rounded-lg border"
                  style={{
                    backgroundImage:
                      "linear-gradient(45deg,#8882 25%,transparent 25%,transparent 75%,#8882 75%),linear-gradient(45deg,#8882 25%,transparent 25%,transparent 75%,#8882 75%)",
                    backgroundSize: "16px 16px",
                    backgroundPosition: "0 0,8px 8px",
                  }}
                >
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={r.url} alt={`${spec.label} emote preview`} width={r.px} height={r.px} style={{ imageRendering: r.px <= 28 ? "pixelated" : "auto" }} />
                </div>
                <p className="mt-3 font-semibold tabular-nums">{spec.label}</p>
                <p className="text-xs text-muted-foreground">{spec.use}</p>
                <button
                  type="button"
                  onClick={() => download(r)}
                  className="mt-3 inline-flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground hover:opacity-90"
                >
                  <Download className="size-3.5" /> PNG
                </button>
              </div>
            );
          })}
        </div>
      )}

      {results.length === 0 && (
        <div className="mt-6 flex items-center gap-3 rounded-xl border bg-muted/40 p-4 text-sm text-muted-foreground">
          <ImageIcon className="size-5 shrink-0" />
          Upload once and get all four sizes — Twitch requires 112, 56, and 28 px versions of every emote; Discord emojis are 128 px.
        </div>
      )}
    </div>
  );
}
