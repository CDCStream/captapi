import Link from "next/link";
import { notFound } from "next/navigation";
import { DashboardToolRunner } from "@/components/dashboard/dashboard-tool-runner";
import { TOOL_SLUGS, getTool } from "@/lib/tools";

export function generateStaticParams() {
  return TOOL_SLUGS.map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const t = getTool(slug);
  if (!t) return {};
  return {
    title: `${t.shortTitle || t.title} | Dashboard`,
    description: t.description,
  };
}

export default async function DashboardToolPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const t = getTool(slug);
  if (!t) notFound();

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <p className="text-sm text-muted-foreground">
          <Link href="/dashboard" className="hover:text-foreground">
            Dashboard
          </Link>
          {" / "}
          <Link href="/dashboard/tools" className="hover:text-foreground">
            Tools
          </Link>
          {" / "}
          <span className="text-foreground">{t.shortTitle || t.title}</span>
        </p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight">{t.shortTitle || t.title}</h1>
        <p className="mt-1 text-muted-foreground">
          Billed to your account — automate with the API when you need scale.
        </p>
      </div>
      <DashboardToolRunner tool={t} />
    </div>
  );
}
