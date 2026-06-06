import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const maxDuration = 60;

type UploadedImage = {
  dataUrl?: string;
  mimeType?: string;
  data?: string;
};

type RequestBody = {
  topic?: string;
  audience?: string;
  style?: string;
  emotion?: string;
  variantCount?: number;
  referenceImage?: UploadedImage | null;
  portraitImage?: UploadedImage | null;
};

type GeminiPart =
  | { text: string }
  | { inlineData: { mimeType: string; data: string } };

type GeminiResponse = {
  candidates?: {
    content?: {
      parts?: GeminiPart[];
    };
  }[];
  error?: { message?: string; code?: number; status?: string };
};

const MAX_INLINE_BYTES = 7 * 1024 * 1024;
const ALLOWED_MIME = new Set(["image/png", "image/jpeg", "image/webp"]);

function cleanText(value: unknown, fallback = "") {
  return typeof value === "string" ? value.trim().slice(0, 500) : fallback;
}

function clampVariantCount(value: unknown) {
  const parsed = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(parsed)) return 2;
  return Math.max(1, Math.min(3, Math.round(parsed)));
}

function normalizeImage(image: UploadedImage | null | undefined, label: string) {
  if (!image) return null;

  let mimeType = image.mimeType || "";
  let data = image.data || "";

  if (image.dataUrl) {
    const match = image.dataUrl.match(/^data:([^;]+);base64,(.+)$/);
    if (!match) throw new Error(label + " must be a base64 data URL.");
    mimeType = match[1];
    data = match[2];
  }

  if (!ALLOWED_MIME.has(mimeType)) {
    throw new Error(label + " must be PNG, JPG, or WebP.");
  }

  const bytes = Buffer.byteLength(data, "base64");
  if (!bytes || bytes > MAX_INLINE_BYTES) {
    throw new Error(label + " must be smaller than 7 MB.");
  }

  return { mimeType, data };
}

function buildPrompt(
  input: Required<Pick<RequestBody, "topic" | "audience" | "style" | "emotion">>,
  variant: number,
  hasPortrait: boolean,
  hasReference: boolean,
) {
  const portraitInstruction = hasPortrait
    ? "Use the uploaded portrait as the main creator face. Remove or ignore the background, keep the person recognizable, improve lighting, and place them prominently without distorting facial identity."
    : "If no portrait is provided, create a strong subject-focused thumbnail with a clear focal object or creator-style figure when useful.";

  const referenceInstruction = hasReference
    ? "Use the uploaded reference thumbnail only for layout logic, contrast, framing, and visual mood. Do not copy logos, exact text, or protected artwork. Make the final thumbnail original."
    : "Use current high-CTR YouTube thumbnail best practices: simple composition, bold contrast, clear visual hierarchy, and readable text at phone size.";

  return [
    "Create one original YouTube thumbnail image.",
    "Aspect ratio: 16:9. Target export quality: 1280x720 style, sharp, high contrast, no watermark.",
    "Video topic/title: " + input.topic + ".",
    "Target audience: " + (input.audience || "general YouTube viewers") + ".",
    "Style direction: " + input.style + ".",
    "Primary emotion/hook: " + input.emotion + ".",
    "Variation number: " + variant + ". Make this composition distinct from other variations while staying on brief.",
    portraitInstruction,
    referenceInstruction,
    "Include only short thumbnail text when it improves CTR, maximum 4 words, large and readable. Avoid tiny text, clutter, extra UI, fake platform badges, and illegible details.",
    "Design for monetized YouTube channels: original, clean, commercially usable, brand-safe, and not misleading.",
  ].join("\n");
}

async function callGemini(prompt: string, images: { mimeType: string; data: string }[]) {
  const apiKey = process.env.GEMINI_API_KEY;
  const model = process.env.GEMINI_IMAGE_MODEL || "gemini-2.5-flash-image";

  if (!apiKey) {
    return NextResponse.json(
      { error: "AI thumbnail generation is not configured yet. Please try again later." },
      { status: 503 },
    );
  }

  const parts = [
    { text: prompt },
    ...images.map((image) => ({ inlineData: image })),
  ];

  const res = await fetch(
    "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + apiKey,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ role: "user", parts }],
        generationConfig: {
          responseModalities: ["TEXT", "IMAGE"],
          imageConfig: { aspectRatio: "16:9" },
        },
      }),
    },
  );

  const text = await res.text();
  let data: GeminiResponse = {};
  try {
    data = JSON.parse(text) as GeminiResponse;
  } catch {
    data = {};
  }

  if (!res.ok) {
    console.error("Gemini image error", res.status, text.slice(0, 700));
    return NextResponse.json(
      { error: "The image generation service is busy. Please try again." },
      { status: 502 },
    );
  }

  const partsOut = data.candidates?.[0]?.content?.parts || [];
  const image = partsOut.find((part): part is { inlineData: { mimeType: string; data: string } } => "inlineData" in part);
  const responseText = partsOut
    .filter((part): part is { text: string } => "text" in part)
    .map((part) => part.text)
    .join("\n")
    .trim();

  if (!image?.inlineData?.data) {
    console.error("Gemini image missing inlineData", JSON.stringify(data).slice(0, 700));
    return NextResponse.json(
      { error: "The AI did not return an image. Please try a simpler prompt." },
      { status: 502 },
    );
  }

  return {
    mimeType: image.inlineData.mimeType || "image/png",
    data: image.inlineData.data,
    note: responseText,
  };
}

export async function POST(req: Request) {
  let body: RequestBody;
  try {
    body = (await req.json()) as RequestBody;
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  const topic = cleanText(body.topic);
  if (topic.length < 5) {
    return NextResponse.json({ error: "Enter a video title or topic first." }, { status: 400 });
  }

  let referenceImage: ReturnType<typeof normalizeImage> = null;
  let portraitImage: ReturnType<typeof normalizeImage> = null;
  try {
    referenceImage = normalizeImage(body.referenceImage, "Reference image");
    portraitImage = normalizeImage(body.portraitImage, "Portrait image");
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Invalid image upload." },
      { status: 400 },
    );
  }

  const input = {
    topic,
    audience: cleanText(body.audience, "general YouTube viewers"),
    style: cleanText(body.style, "high-CTR modern YouTube thumbnail"),
    emotion: cleanText(body.emotion, "curiosity and urgency"),
  };
  const images = [portraitImage, referenceImage].filter(Boolean) as { mimeType: string; data: string }[];
  const variantCount = clampVariantCount(body.variantCount);

  try {
    const generated = await Promise.all(
      Array.from({ length: variantCount }, async (_, index) => {
        const prompt = buildPrompt(input, index + 1, Boolean(portraitImage), Boolean(referenceImage));
        const result = await callGemini(prompt, images);
        if (result instanceof NextResponse) throw result;
        return { ...result, prompt };
      }),
    );

    return NextResponse.json({ images: generated });
  } catch (error) {
    if (error instanceof NextResponse) return error;
    console.error("thumbnail generation failed", error);
    return NextResponse.json(
      { error: "Generation failed. Please try again with a shorter prompt." },
      { status: 500 },
    );
  }
}
