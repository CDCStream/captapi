"use client";

import { useMemo, useState } from "react";
import { Download, ImagePlus, Loader2, Sparkles, Upload, X } from "lucide-react";
import { toast } from "sonner";

type GeneratedImage = {
  mimeType: string;
  data: string;
  note?: string;
};

type UploadState = {
  name: string;
  dataUrl: string;
};

const STYLE_OPTIONS = [
  "Viral YouTube high contrast",
  "MrBeast-style bold challenge",
  "Clean tech tutorial",
  "Gaming reaction",
  "Finance / business authority",
  "Beauty / lifestyle glossy",
  "Documentary cinematic",
  "Minimal premium brand",
];

const EMOTION_OPTIONS = [
  "curiosity and urgency",
  "surprise reaction",
  "before vs after transformation",
  "clear how-to promise",
  "controversy without clickbait",
  "premium expert trust",
];

function fileToDataUrl(file: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(new Error("Could not read image."));
    reader.readAsDataURL(file);
  });
}

function UploadBox({
  label,
  help,
  value,
  onChange,
}: {
  label: string;
  help: string;
  value: UploadState | null;
  onChange: (value: UploadState | null) => void;
}) {
  async function handleFile(file: File | undefined) {
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      toast.error("Please upload an image file.");
      return;
    }
    if (file.size > 7 * 1024 * 1024) {
      toast.error("Images must be smaller than 7 MB.");
      return;
    }
    try {
      onChange({ name: file.name, dataUrl: await fileToDataUrl(file) });
    } catch {
      toast.error("Could not read that image.");
    }
  }

  return (
    <div className="rounded-xl border border-white/10 bg-zinc-900 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-white">{label}</p>
          <p className="mt-1 text-xs leading-relaxed text-gray-400">{help}</p>
        </div>
        {value ? (
          <button
            type="button"
            onClick={() => onChange(null)}
            className="rounded-md border border-white/10 p-1.5 text-gray-300 hover:bg-white/10 hover:text-white"
            aria-label={"Remove " + label}
          >
            <X className="size-4" />
          </button>
        ) : null}
      </div>

      {value ? (
        <div className="mt-3 overflow-hidden rounded-lg border border-white/10 bg-black">
          <img src={value.dataUrl} alt={value.name} className="h-32 w-full object-cover" />
        </div>
      ) : (
        <label className="mt-3 flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-white/20 bg-black/30 px-4 py-6 text-center text-sm text-gray-300 hover:border-primary hover:text-white">
          <Upload className="mb-2 size-5" />
          Upload image
          <input type="file" accept="image/png,image/jpeg,image/webp" className="hidden" onChange={(event) => handleFile(event.target.files?.[0])} />
        </label>
      )}
    </div>
  );
}

export default function YouTubeThumbnailClient() {
  const [topic, setTopic] = useState("");
  const [audience, setAudience] = useState("");
  const [style, setStyle] = useState(STYLE_OPTIONS[0]);
  const [emotion, setEmotion] = useState(EMOTION_OPTIONS[0]);
  const [variantCount, setVariantCount] = useState(2);
  const [portraitImage, setPortraitImage] = useState<UploadState | null>(null);
  const [referenceImage, setReferenceImage] = useState<UploadState | null>(null);
  const [images, setImages] = useState<GeneratedImage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const canGenerate = useMemo(() => topic.trim().length >= 5 && !loading, [topic, loading]);

  async function generate() {
    if (!topic.trim()) {
      toast.error("Enter a video title or topic first.");
      return;
    }

    setLoading(true);
    setError("");
    setImages([]);

    try {
      const res = await fetch("/api/thumbnail-generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic,
          audience,
          style,
          emotion,
          variantCount,
          portraitImage: portraitImage ? { dataUrl: portraitImage.dataUrl } : null,
          referenceImage: referenceImage ? { dataUrl: referenceImage.dataUrl } : null,
        }),
      });
      const data = (await res.json()) as { images?: GeneratedImage[]; error?: string };
      if (!res.ok) throw new Error(data.error || "Generation failed.");
      setImages(data.images || []);
      toast.success("AI thumbnails generated.");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Generation failed.";
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }

  function download(image: GeneratedImage, index: number) {
    const extension = image.mimeType.includes("jpeg") ? "jpg" : image.mimeType.includes("webp") ? "webp" : "png";
    const link = document.createElement("a");
    link.href = "data:" + image.mimeType + ";base64," + image.data;
    link.download = "captapi-ai-youtube-thumbnail-" + (index + 1) + "." + extension;
    link.click();
  }

  return (
    <section className="mt-8 grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
      <div className="rounded-2xl border border-white/10 bg-zinc-950 p-5 shadow-sm">
        <div className="mb-5 flex items-center gap-2 text-white">
          <Sparkles className="size-5 text-primary" />
          <h2 className="text-lg font-semibold">Generate AI thumbnails</h2>
        </div>

        <div className="space-y-4">
          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-white">Video title or topic</span>
            <textarea
              value={topic}
              onChange={(event) => setTopic(event.target.value)}
              placeholder="Example: I tried cold plunges for 30 days - here is what changed"
              className="min-h-24 w-full resize-y rounded-lg border border-white/15 bg-zinc-900 px-3 py-2 text-sm text-white placeholder:text-gray-500 outline-none focus:border-primary"
            />
          </label>

          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-white">Target audience (optional)</span>
            <input
              value={audience}
              onChange={(event) => setAudience(event.target.value)}
              placeholder="Beginner creators, SaaS founders, gamers, fitness fans..."
              className="w-full rounded-lg border border-white/15 bg-zinc-900 px-3 py-2 text-sm text-white placeholder:text-gray-500 outline-none focus:border-primary"
            />
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-white">Thumbnail style</span>
              <select
                value={style}
                onChange={(event) => setStyle(event.target.value)}
                className="w-full rounded-lg border border-white/15 bg-zinc-900 px-3 py-2 text-sm text-white outline-none focus:border-primary"
              >
                {STYLE_OPTIONS.map((option) => (
                  <option key={option} value={option} className="bg-zinc-900">
                    {option}
                  </option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-white">Hook emotion</span>
              <select
                value={emotion}
                onChange={(event) => setEmotion(event.target.value)}
                className="w-full rounded-lg border border-white/15 bg-zinc-900 px-3 py-2 text-sm text-white outline-none focus:border-primary"
              >
                {EMOTION_OPTIONS.map((option) => (
                  <option key={option} value={option} className="bg-zinc-900">
                    {option}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-white">Variations</span>
            <select
              value={variantCount}
              onChange={(event) => setVariantCount(Number(event.target.value))}
              className="w-full rounded-lg border border-white/15 bg-zinc-900 px-3 py-2 text-sm text-white outline-none focus:border-primary"
            >
              <option value={1} className="bg-zinc-900">1 thumbnail</option>
              <option value={2} className="bg-zinc-900">2 thumbnails</option>
              <option value={3} className="bg-zinc-900">3 thumbnails</option>
            </select>
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            <UploadBox
              label="Portrait / face (optional)"
              help="Upload a selfie or creator photo. The AI will blend it into the thumbnail."
              value={portraitImage}
              onChange={setPortraitImage}
            />
            <UploadBox
              label="Reference thumbnail (optional)"
              help="Upload a style reference. The AI uses the layout and mood, not a direct copy."
              value={referenceImage}
              onChange={setReferenceImage}
            />
          </div>

          <button
            type="button"
            onClick={generate}
            disabled={!canGenerate}
            className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-60"
          >
            {loading ? <Loader2 className="size-4 animate-spin" /> : <Sparkles className="size-4" />}
            {loading ? "Generating thumbnails..." : "Generate AI thumbnails"}
          </button>
          <p className="text-center text-xs text-gray-500">Free beta ? no sign-up required ? public, brand-safe prompts only</p>
        </div>
      </div>

      <div className="rounded-2xl border border-white/10 bg-zinc-950 p-5 shadow-sm">
        <div className="mb-4 flex items-center gap-2 text-white">
          <ImagePlus className="size-5 text-primary" />
          <h2 className="text-lg font-semibold">Generated thumbnails</h2>
        </div>

        {loading ? (
          <div className="flex min-h-[420px] flex-col items-center justify-center rounded-xl border border-dashed border-white/15 bg-zinc-900 text-center text-gray-300">
            <Loader2 className="mb-3 size-7 animate-spin text-primary" />
            <p className="font-medium text-white">Creating 16:9 YouTube thumbnails...</p>
            <p className="mt-1 max-w-sm text-sm text-gray-400">Gemini is composing high-contrast variations. This can take a moment.</p>
          </div>
        ) : error ? (
          <div className="flex min-h-[420px] flex-col items-center justify-center rounded-xl border border-rose-500/30 bg-rose-500/10 p-6 text-center">
            <p className="text-sm text-rose-200">{error}</p>
            <button type="button" onClick={generate} className="mt-4 rounded-md border border-white/15 px-4 py-2 text-sm text-white hover:bg-white/10">
              Try again
            </button>
          </div>
        ) : images.length ? (
          <div className="grid gap-4">
            {images.map((image, index) => (
              <div key={image.data.slice(0, 16) + "-" + index} className="overflow-hidden rounded-xl border border-white/10 bg-zinc-900">
                <img
                  src={"data:" + image.mimeType + ";base64," + image.data}
                  alt={"AI generated YouTube thumbnail variation " + (index + 1)}
                  className="aspect-video w-full bg-black object-cover"
                />
                <div className="flex flex-wrap items-center justify-between gap-3 p-3">
                  <div>
                    <p className="text-sm font-medium text-white">Variation {index + 1}</p>
                    <p className="text-xs text-gray-400">16:9 thumbnail, ready to download</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => download(image, index)}
                    className="inline-flex items-center gap-1.5 rounded-md border border-white/15 px-3 py-1.5 text-sm text-white hover:bg-white/10"
                  >
                    <Download className="size-4" /> Download
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex min-h-[420px] flex-col items-center justify-center rounded-xl border border-dashed border-white/15 bg-zinc-900 p-6 text-center">
            <ImagePlus className="mb-3 size-8 text-gray-500" />
            <p className="font-medium text-white">Your AI thumbnails will appear here.</p>
            <p className="mt-2 max-w-sm text-sm text-gray-400">Add a title, choose a style, optionally upload a portrait or reference, and generate click-ready options.</p>
          </div>
        )}
      </div>
    </section>
  );
}
