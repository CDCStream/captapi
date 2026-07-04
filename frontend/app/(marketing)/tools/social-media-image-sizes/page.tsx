import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { IMAGE_SIZES } from "@/lib/image-sizes";

const PATH = "/tools/social-media-image-sizes";
const TITLE = "Social Media Image Sizes (2026)";
const DESC =
  "Every social media image and video size in one cheat sheet — Instagram post and Story dimensions, TikTok aspect ratio, YouTube thumbnail and banner sizes, Facebook, X, LinkedIn, and Pinterest.";

export const metadata = buildMetadata({
  title: TITLE + " — The Complete Cheat Sheet | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "social media image sizes",
    "instagram dimensions",
    "instagram story dimensions",
    "instagram post size",
    "tiktok aspect ratio",
    "youtube thumbnail dimensions",
    "youtube banner dimensions",
    "youtube video size",
    "facebook cover photo size",
  ],
});

const FAQS = [
  { q: "What are the Instagram post dimensions?", a: "The recommended feed post size is 1080 × 1350 pixels (4:5 portrait) — it takes up the most screen space. Square posts are 1080 × 1080 (1:1) and landscape is 1080 × 566 (1.91:1). Stories and Reels are 1080 × 1920 (9:16)." },
  { q: "What are the Instagram Story dimensions?", a: "1080 × 1920 pixels at a 9:16 aspect ratio. Keep text and stickers inside the central safe zone (roughly 1080 × 1420), because the top and bottom are covered by the camera, username, and reply UI." },
  { q: "What is TikTok's aspect ratio?", a: "TikTok is 9:16 vertical — upload at 1080 × 1920 pixels. Other ratios play but get letterboxed with bars, which hurts watch time. Export at a high bitrate since TikTok compresses aggressively." },
  { q: "What size is a YouTube thumbnail?", a: "1280 × 720 pixels (16:9), under 2 MB, as JPG, PNG, or GIF. Design text large enough to read when the thumbnail is shrunk to about 10% — that's how most viewers see it in search and suggested feeds." },
  { q: "What are the YouTube banner dimensions?", a: "Upload 2560 × 1440 pixels, but keep all text and logos inside the central 1546 × 423 pixel safe area — that's the only region visible on every device from phone to TV." },
  { q: "What size is a Facebook cover photo?", a: "820 × 312 pixels on desktop, but mobile crops it to roughly 640 × 360 — keep important content centered so both crops work." },
  { q: "Why do wrong dimensions hurt performance?", a: "Platforms crop or letterbox mismatched media automatically: faces get cut, text gets cropped, and vertical feeds show black bars around landscape video. Correctly sized media fills the screen, looks intentional, and gets measurably better watch time and engagement." },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "ReferenceApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="All platforms"
        title={TITLE}
        subtitle="Every dimension you need in one place — posts, Stories, Reels, thumbnails, banners, and profile photos for Instagram, TikTok, YouTube, Facebook, X, LinkedIn, and Pinterest."
      />

      <nav className="mt-6 flex flex-wrap gap-2" aria-label="Jump to platform">
        {IMAGE_SIZES.map((p) => (
          <a
            key={p.id}
            href={`#${p.id}`}
            className="rounded-full border px-3.5 py-1.5 text-sm font-medium hover:bg-muted"
          >
            {p.label}
          </a>
        ))}
      </nav>

      <div className="mt-8 space-y-10">
        {IMAGE_SIZES.map((p) => (
          <section key={p.id} id={p.id} className="scroll-mt-24">
            <h2 className="text-2xl font-semibold">{p.label} sizes</h2>
            <div className="mt-4 overflow-x-auto rounded-2xl border">
              <table className="w-full text-sm">
                <thead className="bg-muted/60 text-left">
                  <tr>
                    <th className="px-4 py-3 font-medium">Placement</th>
                    <th className="px-4 py-3 font-medium">Size</th>
                    <th className="px-4 py-3 font-medium">Ratio</th>
                    <th className="px-4 py-3 font-medium">Notes</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {p.specs.map((s) => (
                    <tr key={s.name}>
                      <td className="px-4 py-3 font-medium">{s.name}</td>
                      <td className="whitespace-nowrap px-4 py-3 tabular-nums">{s.size}</td>
                      <td className="whitespace-nowrap px-4 py-3 tabular-nums text-muted-foreground">{s.ratio}</td>
                      <td className="px-4 py-3 text-muted-foreground">{s.note ?? ""}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ))}
      </div>

      <LongContent>
        <div>
          <h2>Three rules that cover almost everything</h2>
          <ul>
            <li><strong>Vertical video is 1080 × 1920 (9:16)</strong> everywhere — TikTok, Reels, Shorts, and Stories all share it, so one export fits four platforms.</li>
            <li><strong>Landscape/link images are ~1200 × 630 (1.91:1)</strong> — Facebook posts, X cards, LinkedIn posts, and Open Graph previews all use this shape.</li>
            <li><strong>Profile photos are square but shown as circles</strong> — keep the subject centered with breathing room at the edges.</li>
          </ul>
        </div>
        <div>
          <h2>Design once, export per platform</h2>
          <p>
            The efficient workflow is designing at the largest size (1080 × 1920 for vertical, 2560 × 1440
            for banners) and cropping down per platform, keeping critical content inside the smallest safe
            zone. Platforms recompress everything you upload, so always export at maximum quality — you
            cannot control their compression, but you can control what goes into it.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Need media data via API?"
        sub="Captapi returns video details, thumbnails, and profile media as clean JSON across YouTube, TikTok, Instagram, and Facebook. Start free with 100 credits."
      />
    </>
  );
}
