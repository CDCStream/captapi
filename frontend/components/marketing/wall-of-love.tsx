import { Star, Quote, ExternalLink } from "lucide-react";
import { getServiceClient } from "@/lib/supabase/admin";

interface Testimonial {
  id: string;
  source: string;
  author_name: string;
  author_role: string;
  quote: string;
  rating: number | null;
  source_url: string | null;
}

const SOURCE_LABELS: Record<string, string> = {
  g2: "G2",
  capterra: "Capterra",
  x: "X",
  producthunt: "Product Hunt",
  reddit: "Reddit",
  email: "Customer email",
  other: "",
};

async function fetchTestimonials(): Promise<Testimonial[]> {
  const sb = getServiceClient();
  if (!sb) return [];
  const { data } = await sb
    .from("testimonials")
    .select("id, source, author_name, author_role, quote, rating, source_url")
    .eq("published", true)
    .order("sort_order", { ascending: true })
    .limit(12);
  return (data as Testimonial[]) ?? [];
}

/**
 * Social-proof wall fed by the `testimonials` table (G2, Capterra, X, PH…).
 * Renders nothing while the table is empty, so it can ship ahead of the first
 * review and light up as reviews arrive — no code change needed.
 */
export async function WallOfLove() {
  let items: Testimonial[] = [];
  try {
    items = await fetchTestimonials();
  } catch {
    return null; // table not provisioned yet — stay invisible
  }
  if (items.length === 0) return null;

  return (
    <section className="py-16 border-t bg-muted/30" id="reviews">
      <div className="container">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold">What developers are saying</h2>
          <p className="mt-3 text-muted-foreground">
            Real reviews from G2, Capterra, and the community.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((t) => (
            <figure
              key={t.id}
              className="flex flex-col rounded-xl border bg-card p-5"
            >
              <div className="flex items-center justify-between gap-2">
                <Quote className="size-5 text-primary/50" />
                {t.rating ? (
                  <span className="flex gap-0.5" aria-label={`${t.rating} out of 5 stars`}>
                    {Array.from({ length: t.rating }).map((_, i) => (
                      <Star key={i} className="size-3.5 fill-amber-400 text-amber-400" />
                    ))}
                  </span>
                ) : null}
              </div>
              <blockquote className="mt-3 flex-1 text-sm leading-relaxed text-muted-foreground">
                &ldquo;{t.quote}&rdquo;
              </blockquote>
              <figcaption className="mt-4 flex items-end justify-between gap-2 text-sm">
                <div>
                  <p className="font-medium">{t.author_name}</p>
                  {t.author_role && (
                    <p className="text-xs text-muted-foreground">{t.author_role}</p>
                  )}
                </div>
                {t.source_url ? (
                  <a
                    href={t.source_url}
                    target="_blank"
                    rel="noopener noreferrer nofollow"
                    className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
                  >
                    {SOURCE_LABELS[t.source] || "Source"}
                    <ExternalLink className="size-3" />
                  </a>
                ) : (
                  <span className="text-xs text-muted-foreground">
                    {SOURCE_LABELS[t.source]}
                  </span>
                )}
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}
