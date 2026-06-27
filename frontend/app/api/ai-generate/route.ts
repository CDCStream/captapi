import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const maxDuration = 30;

type Inputs = Record<string, string>;

type Item = { title?: string; value: string; meta?: string; fields?: { label: string; value: string }[] };
type Group = { title: string; items: Item[] };
type Normalized = { text?: string; items?: Item[]; groups?: Group[]; combined?: string };

const clip = (s: unknown) => (typeof s === "string" ? s.trim() : "");
const arr = (v: unknown): unknown[] => (Array.isArray(v) ? v : []);
const tags = (v: unknown): Item[] =>
  arr(v)
    .map((t) => clip(t).replace(/^#*/, "#").replace(/\s+/g, ""))
    .filter((t) => t.length > 1)
    .map((value) => ({ value }));

const BIO_LIMITS: Record<string, number> = { youtube: 1000, tiktok: 80, instagram: 150, twitter: 160 };

interface ToolSpec {
  // Instruction + JSON schema for the model.
  prompt: (i: Inputs) => string;
  // Map the model's parsed JSON into the client-facing shape.
  normalize: (json: Record<string, unknown>, i: Inputs) => Normalized;
}

const TOOLS: Record<string, ToolSpec> = {
  "youtube-hashtag-generator": {
    prompt: (i) =>
      `Generate YouTube hashtags for a video about: "${i.topic}". Return JSON: {"trending":[10 broad trending hashtags],"niche":[12 niche-specific hashtags],"broad":[8 broad-reach hashtags]}. Each hashtag starts with # and has no spaces. Keep them relevant and safe.`,
    normalize: (j) => {
      const groups: Group[] = [
        { title: "Trending", items: tags(j.trending) },
        { title: "Niche-specific", items: tags(j.niche) },
        { title: "Broad reach", items: tags(j.broad) },
      ].filter((g) => g.items.length);
      const all = groups.flatMap((g) => g.items.map((x) => x.value)).slice(0, 15);
      return { groups, combined: all.join(" ") };
    },
  },
  "youtube-title-generator": {
    prompt: (i) =>
      `Write 10 compelling YouTube video titles about "${i.topic}" for this audience: "${i.audience || "general"}". Style: ${i.style || "mixed"}. Each under 100 characters. Return JSON: {"titles":[{"title":string,"ctr":number 1-100 estimating click appeal}]}.`,
    normalize: (j) => ({
      items: arr((j as { titles?: unknown }).titles).map((t) => {
        const o = t as { title?: string; ctr?: number };
        const value = clip(o.title);
        return { value, meta: `${value.length} chars · CTR score ${Math.round(Number(o.ctr) || 0)}/100` };
      }).filter((x) => x.value),
    }),
  },
  "youtube-name-generator": {
    prompt: (i) =>
      `Generate 15 YouTube channel name ideas for a ${i.accountType || "personal"} channel about "${i.niche}".${i.keywords ? ` Try to naturally incorporate these words where it fits: ${i.keywords}.` : ""} Style: ${i.style || "brandable"}. Names must be short, memorable, easy to say and spell, brandable, and hint at the niche. Each name should be at most 50 characters (YouTube's channel name limit) and may contain spaces. Avoid trademarked brand names. Return JSON: {"names":[{"name":string,"reason":a short reason it works, max 8 words}]}.`,
    normalize: (j) => ({
      items: arr((j as { names?: unknown }).names).map((n) => {
        const o = n as { name?: string; reason?: string };
        const value = clip(o.name);
        return { value, meta: [clip(o.reason), `${value.length}/50 chars${value.length > 50 ? " — too long" : ""}`].filter(Boolean).join(" · ") };
      }).filter((x) => x.value),
    }),
  },
  "youtube-description-generator": {
    prompt: (i) =>
      `Write one SEO-optimized YouTube description for a video titled "${i.title}" about "${i.topic}".${i.timestamps ? ` Include these timestamps:\n${i.timestamps}` : ""} Structure: a 2-line hook first, then a keyword-rich paragraph, a "Timestamps" section if provided, a call-to-action to subscribe and like, social link placeholders, and 3-5 relevant hashtags at the end. Return JSON: {"description": string with line breaks}.`,
    normalize: (j) => ({ text: clip((j as { description?: string }).description) }),
  },
  "youtube-shorts-idea-generator": {
    prompt: (i) =>
      `Generate 8 YouTube Shorts ideas for a ${i.niche || "general"} channel with ${i.subs || "any"} subscribers. Format focus: ${i.format || "mixed"}. Return JSON: {"ideas":[{"title":string,"hook":first 2-second on-screen text,"script":a 60-second script outline,"retention":a retention tip,"postTime":suggested posting time}]}.`,
    normalize: (j) => ({
      items: arr((j as { ideas?: unknown }).ideas).map((t) => {
        const o = t as Record<string, string>;
        return {
          title: clip(o.title),
          value: clip(o.hook) ? `Hook: ${clip(o.hook)}` : "",
          fields: [
            { label: "Script", value: clip(o.script) },
            { label: "Retention", value: clip(o.retention) },
            { label: "Best time", value: clip(o.postTime) },
          ].filter((f) => f.value),
        };
      }).filter((x) => x.title || x.value),
    }),
  },
  "tiktok-username-generator": {
    prompt: (i) =>
      `Generate 15 TikTok username ideas for someone into "${i.interest}". Vibe: ${i.style || "any"}. Each must be <= 24 characters, no spaces, only letters/numbers/underscores/periods. Return JSON: {"usernames":[string]}.`,
    normalize: (j) => ({
      items: arr((j as { usernames?: unknown }).usernames).map((u) => {
        const value = clip(u).replace(/\s+/g, "");
        return { value, meta: `${value.length}/24 chars${value.length > 24 ? " — too long" : ""}` };
      }).filter((x) => x.value),
    }),
  },
  "tiktok-hashtag-generator": {
    prompt: (i) =>
      `Generate TikTok hashtags for a video about: "${i.topic}". Return JSON: {"viral":[8 broad viral hashtags],"niche":[14 niche-specific hashtags],"fyp":["#fyp","#foryou","#foryoupage","#viral"]}. Each starts with # and has no spaces.`,
    normalize: (j) => {
      const groups: Group[] = [
        { title: "Viral / trending", items: tags(j.viral) },
        { title: "Niche-specific", items: tags(j.niche) },
        { title: "FYP boosters", items: tags(j.fyp) },
      ].filter((g) => g.items.length);
      const all = groups.flatMap((g) => g.items.map((x) => x.value));
      const combined = all.join(" ");
      return { groups, combined: `${combined}  (${combined.length}/2200 chars)` };
    },
  },
  "tiktok-video-idea-generator": {
    prompt: (i) =>
      `Generate 8 TikTok video ideas for the "${i.niche}" niche using the "${i.trendType || "original"}" format. Return JSON: {"ideas":[{"title":string,"hook":first 3-second hook,"concept":short concept description,"sounds":suggested sounds or trends,"virality":number 1-100}]}.`,
    normalize: (j) => ({
      items: arr((j as { ideas?: unknown }).ideas).map((t) => {
        const o = t as Record<string, string>;
        return {
          title: clip(o.title),
          value: clip(o.hook) ? `Hook: ${clip(o.hook)}` : "",
          fields: [
            { label: "Concept", value: clip(o.concept) },
            { label: "Sounds/Trend", value: clip(o.sounds) },
            { label: "Virality", value: o.virality ? `${Math.round(Number(o.virality) || 0)}/100` : "" },
          ].filter((f) => f.value),
        };
      }).filter((x) => x.title || x.value),
    }),
  },
  "social-media-bio-generator": {
    prompt: (i) =>
      `Write 6 ${i.tone || "engaging"} social media bios for ${i.platform || "Instagram"} for someone whose niche is "${i.niche}". Keep each within the ${i.platform || "Instagram"} character limit. Tasteful emoji use is welcome. Return JSON: {"bios":[string]}.`,
    normalize: (j, i) => {
      const limit = BIO_LIMITS[(i.platform || "instagram").toLowerCase()] ?? 150;
      return {
        items: arr((j as { bios?: unknown }).bios).map((b) => {
          const value = clip(b);
          return { value, meta: `${value.length}/${limit} chars${value.length > limit ? " — over limit" : ""}` };
        }).filter((x) => x.value),
      };
    },
  },
};

function extractJson(text: string): Record<string, unknown> {
  let t = text.trim();
  const fence = t.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fence) t = fence[1].trim();
  try {
    return JSON.parse(t);
  } catch {
    const m = t.match(/\{[\s\S]*\}/);
    if (m) return JSON.parse(m[0]);
    throw new Error("Model did not return valid JSON.");
  }
}

export async function POST(req: Request) {
  let body: { slug?: string; inputs?: Inputs };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }
  const slug = body.slug ?? "";
  const inputs = body.inputs ?? {};
  const spec = TOOLS[slug];
  if (!spec) return NextResponse.json({ error: "Unknown tool." }, { status: 404 });

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return NextResponse.json(
      { error: "AI generation is not configured yet. Please try again later." },
      { status: 503 },
    );
  }

  try {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: process.env.ANTHROPIC_MODEL || "claude-haiku-4-5",
        max_tokens: 1500,
        system:
          "You are an expert social media growth assistant. Respond with ONLY valid, minified JSON that matches the requested schema. No markdown, no commentary, no code fences.",
        messages: [{ role: "user", content: spec.prompt(inputs) }],
      }),
    });

    if (!res.ok) {
      const detail = await res.text().catch(() => "");
      console.error("Anthropic error", res.status, detail.slice(0, 500));
      return NextResponse.json({ error: "The AI service is busy. Please try again." }, { status: 502 });
    }

    const data = (await res.json()) as { content?: { text?: string }[] };
    const text = data.content?.map((c) => c.text || "").join("") ?? "";
    const json = extractJson(text);
    const normalized = spec.normalize(json, inputs);
    return NextResponse.json(normalized);
  } catch (e) {
    console.error("ai-generate failed", e);
    return NextResponse.json({ error: "Generation failed. Please try again." }, { status: 500 });
  }
}
