"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Download, Upload, Trash2 } from "lucide-react";
import { toast } from "sonner";

const W = 2560;
const H = 1440;
// Safe zone visible on all devices: 1546×423, centered.
const SAFE_W = 1546;
const SAFE_H = 423;

const FONTS = [
  { value: "Anton", label: "Anton (bold)" },
  { value: "Bebas Neue", label: "Bebas Neue" },
  { value: "Impact", label: "Impact" },
  { value: "Arial Black", label: "Arial Black" },
];

type Template = { name: string; bg1: string; bg2: string; textColor: string; name2: string; slogan: string };

const TEMPLATES: Template[] = [
  { name: "Gaming", bg1: "#240b36", bg2: "#c31432", textColor: "#ffffff", name2: "GAME ZONE", slogan: "New videos every day" },
  { name: "Music", bg1: "#0f0c29", bg2: "#928dab", textColor: "#ffd6ff", name2: "SOUND WAVE", slogan: "Original tracks & covers" },
  { name: "Tech", bg1: "#000428", bg2: "#004e92", textColor: "#00e5ff", name2: "TECH DAILY", slogan: "Reviews · Tips · News" },
  { name: "Lifestyle", bg1: "#ee9ca7", bg2: "#ffdde1", textColor: "#5a2a3a", name2: "MY LIFESTYLE", slogan: "Living the everyday" },
];

export default function YouTubeBannerClient() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [bgType, setBgType] = useState<"gradient" | "solid" | "image">("gradient");
  const [bg1, setBg1] = useState("#240b36");
  const [bg2, setBg2] = useState("#c31432");
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  const [channel, setChannel] = useState("GAME ZONE");
  const [slogan, setSlogan] = useState("New videos every day");
  const [handles, setHandles] = useState("@yourchannel");
  const [font, setFont] = useState("Anton");
  const [textColor, setTextColor] = useState("#ffffff");
  const [showGuide, setShowGuide] = useState(true);
  const [fontsReady, setFontsReady] = useState(false);

  useEffect(() => {
    const id = "gf-banner-fonts";
    if (!document.getElementById(id)) {
      const link = document.createElement("link");
      link.id = id;
      link.rel = "stylesheet";
      link.href = "https://fonts.googleapis.com/css2?family=Anton&family=Bebas+Neue&display=swap";
      document.head.appendChild(link);
    }
    const fonts = (document as Document & { fonts?: FontFaceSet }).fonts;
    if (fonts) {
      Promise.all([fonts.load("700 120px Anton"), fonts.load("400 120px 'Bebas Neue'")])
        .then(() => setFontsReady(true))
        .catch(() => setFontsReady(true));
    } else {
      setFontsReady(true);
    }
  }, []);

  const render = useCallback(
    (ctx: CanvasRenderingContext2D, withGuide: boolean) => {
      ctx.clearRect(0, 0, W, H);
      // Background
      if (bgType === "image" && image) {
        const scale = Math.max(W / image.width, H / image.height);
        const dw = image.width * scale;
        const dh = image.height * scale;
        ctx.drawImage(image, (W - dw) / 2, (H - dh) / 2, dw, dh);
        ctx.fillStyle = "rgba(0,0,0,0.35)";
        ctx.fillRect(0, 0, W, H);
      } else if (bgType === "solid") {
        ctx.fillStyle = bg1;
        ctx.fillRect(0, 0, W, H);
      } else {
        const g = ctx.createLinearGradient(0, 0, W, H);
        g.addColorStop(0, bg1);
        g.addColorStop(1, bg2);
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, W, H);
      }

      const cx = W / 2;
      const cy = H / 2;

      // Channel name
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillStyle = textColor;
      ctx.shadowColor = "rgba(0,0,0,0.45)";
      ctx.shadowBlur = 16;
      ctx.shadowOffsetY = 4;
      ctx.font = `${font === "Bebas Neue" ? "400" : "700"} 150px "${font}", Impact, sans-serif`;
      ctx.fillText(channel.toUpperCase(), cx, cy - 40);

      // Slogan
      if (slogan.trim()) {
        ctx.font = `600 56px "${font}", Impact, sans-serif`;
        ctx.globalAlpha = 0.9;
        ctx.fillText(slogan, cx, cy + 70);
        ctx.globalAlpha = 1;
      }

      // Handles
      if (handles.trim()) {
        ctx.font = `600 40px "${font}", Impact, sans-serif`;
        ctx.globalAlpha = 0.8;
        ctx.fillText(handles, cx, cy + 150);
        ctx.globalAlpha = 1;
      }
      ctx.shadowColor = "transparent";

      // Safe-zone guide (never exported)
      if (withGuide) {
        const sx = (W - SAFE_W) / 2;
        const sy = (H - SAFE_H) / 2;
        ctx.strokeStyle = "rgba(255,255,255,0.85)";
        ctx.lineWidth = 4;
        ctx.setLineDash([24, 16]);
        ctx.strokeRect(sx, sy, SAFE_W, SAFE_H);
        ctx.setLineDash([]);
        ctx.fillStyle = "rgba(255,255,255,0.85)";
        ctx.font = "600 30px Arial, sans-serif";
        ctx.textAlign = "left";
        ctx.fillText("Safe zone — visible on all devices", sx + 12, sy + 28);
      }
    },
    [bgType, bg1, bg2, image, channel, slogan, handles, font, textColor],
  );

  useEffect(() => {
    const ctx = canvasRef.current?.getContext("2d");
    if (ctx) render(ctx, showGuide);
  }, [render, showGuide, fontsReady]);

  const onUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const img = new Image();
    img.onload = () => {
      setImage(img);
      setBgType("image");
    };
    img.src = URL.createObjectURL(file);
  };

  const applyTemplate = (t: Template) => {
    setBgType("gradient");
    setBg1(t.bg1);
    setBg2(t.bg2);
    setTextColor(t.textColor);
    setChannel(t.name2);
    setSlogan(t.slogan);
    toast.success(`Applied "${t.name}" template`);
  };

  const download = () => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;
    render(ctx, false);
    const url = canvas.toDataURL("image/png");
    render(ctx, showGuide);
    const a = document.createElement("a");
    a.download = `youtube-banner-${Date.now()}.png`;
    a.href = url;
    a.click();
    toast.success("Banner downloaded (2560×1440 PNG)");
  };

  return (
    <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_minmax(0,360px)]">
      <div className="space-y-4">
        <div className="overflow-hidden rounded-xl border border-white/10 bg-black/40">
          <canvas ref={canvasRef} width={W} height={H} className="aspect-[16/9] w-full" />
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {TEMPLATES.map((t) => (
            <button
              key={t.name}
              type="button"
              onClick={() => applyTemplate(t)}
              className="rounded-full border border-white/15 bg-white/5 px-3 py-1.5 text-sm text-gray-200 hover:bg-white/10"
            >
              {t.name}
            </button>
          ))}
          <label className="ml-auto flex items-center gap-2 text-sm text-gray-300">
            <input type="checkbox" checked={showGuide} onChange={(e) => setShowGuide(e.target.checked)} />
            Safe zone
          </label>
        </div>
        <button
          type="button"
          onClick={download}
          className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground hover:opacity-90"
        >
          <Download className="size-4" /> Download PNG — 2560×1440, no watermark
        </button>
      </div>

      <div className="space-y-5 rounded-2xl border border-white/10 bg-white/5 p-5">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-white">Channel name</label>
          <input value={channel} onChange={(e) => setChannel(e.target.value)} className="w-full rounded-lg border border-white/15 bg-black/30 px-3 py-2 text-sm text-white outline-none focus:border-primary" />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-white">Slogan / tagline</label>
          <input value={slogan} onChange={(e) => setSlogan(e.target.value)} className="w-full rounded-lg border border-white/15 bg-black/30 px-3 py-2 text-sm text-white outline-none focus:border-primary" />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-white">Social handle(s)</label>
          <input value={handles} onChange={(e) => setHandles(e.target.value)} placeholder="@yourchannel · IG @you" className="w-full rounded-lg border border-white/15 bg-black/30 px-3 py-2 text-sm text-white placeholder:text-gray-500 outline-none focus:border-primary" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-white">Font</label>
            <select value={font} onChange={(e) => setFont(e.target.value)} className="w-full rounded-lg border border-white/15 bg-black/30 px-3 py-2 text-sm text-white outline-none focus:border-primary">
              {FONTS.map((f) => (
                <option key={f.value} value={f.value} className="bg-zinc-900">{f.label}</option>
              ))}
            </select>
          </div>
          <label className="flex items-end justify-between rounded-lg border border-white/15 bg-black/30 px-3 py-2 text-sm text-white">
            Text color
            <input type="color" value={textColor} onChange={(e) => setTextColor(e.target.value)} className="h-6 w-8 bg-transparent" />
          </label>
        </div>

        <div className="border-t border-white/10 pt-4">
          <p className="mb-2 text-sm font-medium text-white">Background</p>
          <div className="mb-3 flex gap-2">
            {(["gradient", "solid", "image"] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setBgType(t)}
                className={`rounded-md px-3 py-1.5 text-xs capitalize ${bgType === t ? "bg-primary text-primary-foreground" : "border border-white/15 text-gray-300 hover:bg-white/10"}`}
              >
                {t}
              </button>
            ))}
          </div>
          {bgType !== "image" && (
            <div className="grid grid-cols-2 gap-3">
              <label className="flex items-center justify-between rounded-lg border border-white/15 bg-black/30 px-3 py-2 text-sm text-white">
                Color 1
                <input type="color" value={bg1} onChange={(e) => setBg1(e.target.value)} className="h-6 w-8 bg-transparent" />
              </label>
              {bgType === "gradient" && (
                <label className="flex items-center justify-between rounded-lg border border-white/15 bg-black/30 px-3 py-2 text-sm text-white">
                  Color 2
                  <input type="color" value={bg2} onChange={(e) => setBg2(e.target.value)} className="h-6 w-8 bg-transparent" />
                </label>
              )}
            </div>
          )}
          {bgType === "image" && (
            <div className="space-y-3">
              <label className="flex cursor-pointer items-center justify-center gap-2 rounded-lg border border-dashed border-white/20 px-3 py-3 text-sm text-gray-300 hover:bg-white/5">
                <Upload className="size-4" />
                {image ? "Replace image" : "Upload background image"}
                <input type="file" accept="image/*" onChange={onUpload} className="hidden" />
              </label>
              {image && (
                <button type="button" onClick={() => { setImage(null); setBgType("gradient"); }} className="inline-flex items-center gap-1.5 text-xs text-rose-400 hover:underline">
                  <Trash2 className="size-3.5" /> Remove image
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
