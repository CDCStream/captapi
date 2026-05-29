import { DocsSidebar } from "@/components/docs/docs-sidebar";
import { OnThisPage } from "@/components/docs/on-this-page";

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="container max-w-[90rem]">
      <div className="flex gap-8">
        <DocsSidebar />
        <article
          id="docs-content"
          className="min-w-0 flex-1 py-10 lg:border-x lg:px-10"
        >
          {children}
        </article>
        <OnThisPage />
      </div>
    </div>
  );
}
