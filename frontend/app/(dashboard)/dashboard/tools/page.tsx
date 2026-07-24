import Link from "next/link";
import { TOOL_LIST } from "@/lib/tools";
import { ALL_ENDPOINTS } from "@/lib/api-catalog";

export const metadata = {
  title: "Tools | Dashboard",
  description: "Run Captapi transcript and summarizer tools with your account credits.",
};

export default function DashboardToolsPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Tools</h1>
        <p className="mt-1 text-muted-foreground">
          Same free-tool experience, billed to your account. Cache hits are free.
        </p>
      </div>
      <ul className="divide-y rounded-xl border">
        {TOOL_LIST.map((t) => {
          const credits = ALL_ENDPOINTS.find((e) => e.slug === t.slug)?.credits;
          return (
            <li key={t.slug}>
              <Link
                href={`/dashboard/tools/${t.slug}`}
                className="flex items-center justify-between gap-4 px-4 py-3 transition-colors hover:bg-muted/50"
              >
                <div className="min-w-0">
                  <p className="font-medium">{t.shortTitle || t.title}</p>
                  <p className="truncate text-sm text-muted-foreground">{t.description}</p>
                </div>
                <span className="shrink-0 text-xs text-muted-foreground">
                  {credits != null ? `${credits} cr` : ""}
                </span>
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
