"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Download, Upload, Trash2 } from "lucide-react";
import { toast } from "sonner";

const W = 1280;
const H = 720;

const FONTS = [
  { value: "Anton", label: "Anton (bold)" },
  { value: "Bebas Neue", label: "Bebas Neue" },
  { value: "Impact", label: "Impact" },
  { value: "Arial Black", label: "Arial Black" },
];

type Template = {
  name: string;
  bg1: string;
  bg2: string;
  textColor: string;
  outline: string;
  title: string;
  sub: string;
};

const TEMPLATES: Template[] = [
  { name: "Gaming", bg1: "#7c0a02", bg2: "#1a0000", textColor: "#ffe600", outline: "#000000", title: "INSANE WIN!", sub: "you won't believe this" },
  { name: "Vlog", bg1: "#ff7eb3", bg2: "#ff758c", textColor: "#ffffff", outline: "#7a2048", title: "A DAY IN MY LIFE", sub: "vlog #12" },
  { name: "Tutorial", bg1: "#0f2027", bg2: "#2c5364", textColor: "#00e5ff", outline: "#001014", title: "HOW TO DO IT", sub: "step by step" },
  { name: "Reaction", bg1: "#f7971e", bg2: "#ffd200", textColor: "#1a1a1a", outline: "#ffffff", title: "NO WAY 😱", sub: "my honest reaction" },
  { name: "Before / After", bg1: "#11998e", bg2: "#38ef7d", textColor: "#ffffff", outline: "#0a3d2a", title: "BEFORE & AFTER", sub: "the results" },
];

export default function YouTubeThumbnailClient() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [bgType, setBgType] = useState<"gradient" | "solid" | "image">("gradient");
  const [bg1, setBg1] = useState("#7c0a02");
  const [bg2, setBg2] = useState("#1a0000");
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  const [imageOpacity, setImageOpacity] = useState(1);
  const [title, setTitle] = useState("INSANE WIN!");
  const [sub, setSub] = useState("you won't believe this");
  const [font, setFont] = useState("Anton");
  const [textColor, setTextColor] = useState("#ffe600");
  const [outline, setOutline] = useState("#000000");
  const [fontSize, setFontSize] = useState(120);
  const [vAlign, setVAlign] = useState<"top" | "middle" | "bottom">("bottom");
  const [fontsReady, setFontsReady] = useState(false);

  useEffect(() => {
    const id = "gf-thumb-fonts";
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

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.clearRect(0, 0, W, H);

    // Background
    if (bgType === "image" && image) {
      const scale = Math.max(W / image.width, H / image.height);
      const dw = image.width * scale;
      const dh = image.height * scale;
      ctx.globalAlpha = imageOpacity;
      ctx.drawImage(image, (W - dw) / 2, (H - dh) / 2, dw, dh);
      ctx.globalAlpha = 1;
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

    // Title text (uppercase, outlined, shadowed)
    const text = title.toUpperCase();
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = `${font === "Bebas Neue" ? "400" : "700"} ${fontSize}px "${font}", Impact, sans-serif`;

    const cx = W / 2;
    let cy = H / 2;
    if (vAlign === "top") cy = fontSize * 0.7 + 40;
    if (vAlign === "bottom") cy = H - fontSize * 0.7 - (sub ? 80 : 40);

    // wrap into lines (max width 92%)
    const maxW = W * 0.92;
    const words = text.split(" ");
    const lines: string[] = [];
    let line = "";
    for (const w of words) {
      const test = line ? `${line} ${w}` : w;
      if (ctx.measureText(test).width > maxW && line) {
        lines.push(line);
        line = w;
      } else {
        line = test;
      }
    }
    if (line) lines.push(line);

    const lineH = fontSize * 1.05;
    const startY = cy - ((lines.length - 1) * lineH) / 2;

    ctx.lineJoin = "round";
    ctx.lineWidth = Math.max(8, fontSize * 0.14);
    ctx.shadowColor = "rgba(0,0,0,0.55)";
    ctx.shadowBlur = 18;
    ctx.shadowOffsetX = 6;
    ctx.shadowOffsetY = 6;
    lines.forEach((ln, i) => {
      const y = startY + i * lineH;
      ctx.strokeStyle = outline;
      ctx.strokeText(ln, cx, y);
    });
    ctx.shadowColor = "transparent";
    ctx.fillStyle = textColor;
    lines.forEach((ln, i) => {
      const y = startY + i * lineH;
      ctx.fillText(ln, cx, y);
    });

    // Subtitle pill
    if (sub.trim()) {
      const subSize = Math.round(fontSize * 0.34);
      ctx.font = `700 ${subSize}px "${font}", Impact, sans-serif`;
      const subText = sub.toUpperCase();
      const padX = 24;
      const tw = ctx.measureText(subText).width;
      const pillH = subSize + 22;
      const pillW = tw + padX * 2;
      const subY = startY + (lines.length - 1) * lineH + lineH * 0.7 + pillH;
      const pillX = cx - pillW / 2;
      ctx.fillStyle = textColor;
      ctx.beginPath();
      const r = pillH / 2;
      ctx.roundRect(pillX, subY - pillH / 2, pillW, pillH, r);
      ctx.fill();
      ctx.fillStyle = outline;
      ctx.fillText(subText, cx, subY);
    }
  }, [bgType, bg1, bg2, image, imageOpacity, title, sub, font, textColor, outline, fontSize, vAlign]);

  useEffect(() => {
    draw();
  }, [draw, fontsReady]);

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
    setOutline(t.outline);
    setTitle(t.title);
    setSub(t.sub);
    toast.success(`Applied "${t.name}" template`);
  };

  const download = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const a = document.createElement("a");
    a.download = `youtube-thumbnail-${Date.now()}.png`;
    a.href = canvas.toDataURL("image/png");
    a.click();
    toast.success("Thumbnail downloaded (1280×720 PNG)");
  };

  return (
    <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_minmax(0,360px)]">
      {/* Canvas preview */}
      <div className="space-y-4">
        <div className="overflow-hidden rounded-xl border border-white/10 bg-black/40">
          <canvas
            ref={canvasRef}
            width={W}
            height={H}
            className="aspect-video w-full"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {TEMPLATES.map((t) => (
            <button
              key={t.name}
              type="button"
              onClick={() => applyTemplate(t)}
              className="rounded-full border border-white/15 bg-white/5 px-3 py-1.5 text-sm text-gray-200 transition-colors hover:bg-white/10"
            >
              {t.name}
            </button>
          ))}
        </div>
        <button
          type="button"
          onClick={download}
          className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground hover:opacity-90"
        >
          <Download className="size-4" /> Download PNG — 1280×720, no watermark
        </button>
      </div>

      {/* Controls */}
      <div className="space-y-5 rounded-2xl border border-white/10 bg-white/5 p-5">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-white">Title text</label>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full rounded-lg border border-white/15 bg-black/30 px-3 py-2 text-sm text-white outline-none focus:border-primary"
          />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-white">Subtitle (optional)</label>
          <input
            value={sub}
            onChange={(e) => setSub(e.target.value)}
            className="w-full rounded-lg border border-white/15 bg-black/30 px-3 py-2 text-sm text-white outline-none focus:border-primary"
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-white">Font</label>
            <select
              value={font}
              onChange={(e) => setFont(e.target.value)}
              className="w-full rounded-lg border border-white/15 bg-black/30 px-3 py-2 text-sm text-white outline-none focus:border-primary"
            >
              {FONTS.map((f) => (
                <option key={f.value} value={f.value} className="bg-zinc-900">
                  {f.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-white">Vertical position</label>
            <select
              value={vAlign}
              onChange={(e) => setVAlign(e.target.value as typeof vAlign)}
              className="w-full rounded-lg border border-white/15 bg-black/30 px-3 py-2 text-sm text-white outline-none focus:border-primary"
            >
              <option value="top" className="bg-zinc-900">Top</option>
              <option value="middle" className="bg-zinc-900">Middle</option>
              <option value="bottom" className="bg-zinc-900">Bottom</option>
            </select>
          </div>
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-white">
            Text size — {fontSize}px
          </label>
          <input
            type="range"
            min={60}
            max={180}
            value={fontSize}
            onChange={(e) => setFontSize(Number(e.target.value))}
            className="w-full accent-[color:var(--primary)]"
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <label className="flex items-center justify-between rounded-lg border border-white/15 bg-black/30 px-3 py-2 text-sm text-white">
            Text
            <input type="color" value={textColor} onChange={(e) => setTextColor(e.target.value)} className="h-6 w-8 bg-transparent" />
          </label>
          <label className="flex items-center justify-between rounded-lg border border-white/15 bg-black/30 px-3 py-2 text-sm text-white">
            Outline
            <input type="color" value={outline} onChange={(e) => setOutline(e.target.value)} className="h-6 w-8 bg-transparent" />
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
                className={`rounded-md px-3 py-1.5 text-xs capitalize ${
                  bgType === t ? "bg-primary text-primary-foreground" : "border border-white/15 text-gray-300 hover:bg-white/10"
                }`}
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
                <>
                  <label className="block text-xs text-gray-400">
                    Image brightness — {Math.round(imageOpacity * 100)}%
                    <input
                      type="range"
                      min={0.2}
                      max={1}
                      step={0.05}
                      value={imageOpacity}
                      onChange={(e) => setImageOpacity(Number(e.target.value))}
                      className="mt-1 w-full"
                    />
                  </label>
                  <button
                    type="button"
                    onClick={() => { setImage(null); setBgType("gradient"); }}
                    className="inline-flex items-center gap-1.5 text-xs text-rose-400 hover:underline"
                  >
                    <Trash2 className="size-3.5" /> Remove image
                  </button>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
