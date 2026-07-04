import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  getChangelog,
  groupByDate,
  CATEGORY_LABELS,
  type ChangelogCategory,
} from "@/lib/changelog";
import { SITE_URL } from "@/lib/api-catalog";
import { buildMetadata, breadcrumbLd } from "@/lib/seo";

export const revalidate = 300;

const DESCRIPTION =
  "Every Captapi release: new endpoints, platforms, integrations, SDKs, and fixes — dated and documented. See what shipped and when.";

export const metadata = buildMetadata({
  title: "Changelog — What's new in Captapi",
  description: DESCRIPTION,
  path: "/changelog",
});

const BADGE_STYLES: Record<ChangelogCategory, string> = {
  feature: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
  improvement: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20",
  fix: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
  integration: "bg-violet-500/10 text-violet-600 dark:text-violet-400 border-violet-500/20",
  platform: "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20",
};

function formatDate(iso: string): string {
  return new Date(`${iso}T00:00:00Z`).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  });
}

export default async function ChangelogPage() {
  const entries = await getChangelog();
  const groups = groupByDate(entries);

  const itemList = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: "Captapi Changelog",
    description: DESCRIPTION,
    numberOfItems: entries.length,
    itemListElement: entries.map((e, i) => ({
      "@type": "ListItem",
      position: i + 1,
      item: {
        "@type": "Article",
        headline: e.title,
        description: e.description,
        datePublished: e.publishedAt,
        url: `${SITE_URL}/changelog`,
        author: { "@type": "Organization", name: "Captapi" },
      },
    })),
  };

  return (
    <div className="py-16">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(itemList) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(
            breadcrumbLd([
              { name: "Home", path: "/" },
              { name: "Changelog", path: "/changelog" },
            ]),
          ),
        }}
      />
      <div className="container max-w-3xl">
        <div className="mb-14">
          <h1 className="text-4xl font-bold tracking-tight">Changelog</h1>
          <p className="mt-3 text-lg text-muted-foreground">
            New endpoints, platforms, integrations, and fixes — everything we
            ship, dated and documented.
          </p>
          <div className="mt-4 flex flex-wrap gap-2 text-xs">
            {(Object.keys(CATEGORY_LABELS) as ChangelogCategory[]).map((c) => (
              <span
                key={c}
                className={`inline-flex items-center rounded-full border px-2.5 py-0.5 font-medium ${BADGE_STYLES[c]}`}
              >
                {CATEGORY_LABELS[c]}
              </span>
            ))}
          </div>
        </div>

        <div className="relative border-l pl-8 sm:pl-10">
          {groups.map((group) => (
            <section key={group.date} className="relative mb-14 last:mb-0">
              <span className="absolute -left-[41px] top-1.5 size-3 rounded-full border-2 border-background bg-primary sm:-left-[49px]" />
              <time
                dateTime={group.date}
                className="text-sm font-semibold uppercase tracking-wide text-muted-foreground"
              >
                {formatDate(group.date)}
              </time>
              <div className="mt-4 space-y-6">
                {group.entries.map((entry) => (
                  <article
                    key={entry.id}
                    className="rounded-xl border bg-card p-5 transition-colors hover:border-primary/40"
                  >
                    <div className="flex flex-wrap items-center gap-2.5">
                      <span
                        className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${BADGE_STYLES[entry.category]}`}
                      >
                        {CATEGORY_LABELS[entry.category]}
                      </span>
                      <h2 className="text-base font-semibold leading-snug">
                        {entry.title}
                      </h2>
                    </div>
                    {entry.description && (
                      <p className="mt-2.5 text-sm leading-relaxed text-muted-foreground">
                        {entry.description}
                      </p>
                    )}
                    {entry.items.length > 0 && (
                      <ul className="mt-3 space-y-1.5 text-sm text-muted-foreground">
                        {entry.items.map((item, i) => (
                          <li key={i} className="flex gap-2">
                            <span className="mt-[7px] size-1 shrink-0 rounded-full bg-muted-foreground/50" />
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </article>
                ))}
              </div>
            </section>
          ))}
        </div>

        <div className="mt-16 rounded-xl border bg-card p-8 text-center">
          <h2 className="text-2xl font-bold">Try what&apos;s new</h2>
          <p className="mt-2 text-muted-foreground">
            Start with 100 free credits — no credit card required.
          </p>
          <div className="mt-6 flex flex-col sm:flex-row gap-3 justify-center">
            <Button asChild size="lg">
              <Link href="/signup">Get your API key</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/docs">Read the docs</Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
