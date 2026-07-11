import { ImageResponse } from "next/og";
import { getServiceClient } from "@/lib/supabase/admin";

export const runtime = "nodejs";

const WIDTH = 1200;
const HEIGHT = 630;

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ slug: string }> },
) {
  const { slug } = await params;
  const sb = getServiceClient();
  const { data } = sb
    ? await sb
        .from("blog_posts")
        .select("title,description,tags")
        .eq("slug", slug)
        .maybeSingle()
    : { data: null };

  const title = data?.title || slug.replace(/-/g, " ");
  const description =
    data?.description || "Clean social media data for developers";
  const tag = Array.isArray(data?.tags) && data.tags.length
    ? String(data.tags[0])
    : "Developer guide";

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          position: "relative",
          overflow: "hidden",
          padding: "72px 82px",
          color: "#f8fafc",
          background:
            "linear-gradient(135deg, #07111f 0%, #101d35 55%, #0b2f3b 100%)",
          fontFamily: "Arial, sans-serif",
        }}
      >
        <div
          style={{
            position: "absolute",
            width: 520,
            height: 520,
            right: -120,
            top: -180,
            borderRadius: 999,
            background:
              "radial-gradient(circle, rgba(34,211,238,.34), rgba(34,211,238,0) 68%)",
          }}
        />
        <div
          style={{
            position: "absolute",
            width: 420,
            height: 420,
            left: -180,
            bottom: -240,
            borderRadius: 999,
            background:
              "radial-gradient(circle, rgba(99,102,241,.38), rgba(99,102,241,0) 70%)",
          }}
        />

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            width: "100%",
            zIndex: 1,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 16,
                fontSize: 31,
                fontWeight: 800,
                letterSpacing: -1,
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  width: 48,
                  height: 48,
                  borderRadius: 13,
                  background: "linear-gradient(135deg, #22d3ee, #6366f1)",
                  color: "#07111f",
                  fontSize: 24,
                  fontWeight: 900,
                }}
              >
                C
              </div>
              Captapi
            </div>
            <div
              style={{
                display: "flex",
                border: "1px solid rgba(148,163,184,.35)",
                borderRadius: 999,
                padding: "10px 18px",
                color: "#a5f3fc",
                fontSize: 18,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: 1.5,
              }}
            >
              {tag}
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", maxWidth: 930 }}>
            <div
              style={{
                display: "flex",
                fontSize: title.length > 70 ? 48 : 58,
                lineHeight: 1.08,
                fontWeight: 800,
                letterSpacing: -2.2,
                textTransform: "capitalize",
              }}
            >
              {title}
            </div>
            <div
              style={{
                display: "flex",
                marginTop: 24,
                maxWidth: 860,
                color: "#cbd5e1",
                fontSize: 24,
                lineHeight: 1.35,
              }}
            >
              {description.slice(0, 145)}
            </div>
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              color: "#94a3b8",
              fontSize: 18,
            }}
          >
            <div style={{ display: "flex" }}>captapi.com/blog</div>
            <div style={{ display: "flex", color: "#67e8f9", fontWeight: 700 }}>
              One API. 29 platforms.
            </div>
          </div>
        </div>
      </div>
    ),
    {
      width: WIDTH,
      height: HEIGHT,
      headers: {
        "Cache-Control": "public, max-age=86400, s-maxage=86400",
      },
    },
  );
}
