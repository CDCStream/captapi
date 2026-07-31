import Link from "next/link";
import {
  FileText,
  Sparkles,
  BarChart3,
  MessageCircle,
  Users,
  Search,
  Clapperboard,
  type LucideIcon,
} from "lucide-react";
import {
  PLATFORM_GROUPS,
  type ApiEndpoint,
  type Category,
} from "@/lib/api-catalog";
import { PlatformGlyph } from "@/components/marketing/platform-glyph";

const CATEGORY_ICONS: Record<Category, LucideIcon> = {
  transcript: FileText,
  summarize: Sparkles,
  details: BarChart3,
  comments: MessageCircle,
  channel: Users,
  search: Search,
  list: Clapperboard,
};

function EndpointCell({ ep }: { ep: ApiEndpoint }) {
  const Icon = CATEGORY_ICONS[ep.category];
  return (
    <Link
      href={`/apis/${ep.slug}`}
      className="flex items-center gap-2.5 px-4 py-3 text-sm text-muted-foreground transition-colors hover:bg-muted/60 hover:text-foreground"
    >
      <Icon className="size-4 shrink-0 text-muted-foreground/70" />
      <span className="leading-tight">{ep.name}</span>
    </Link>
  );
}

export function ApiCatalog() {
  return (
    <div className="space-y-6">
      {PLATFORM_GROUPS.map((group) => {
        return (
          <div
            key={group.id}
            className="overflow-hidden rounded-xl border bg-card"
          >
            <div className="flex items-start gap-3 border-b bg-muted/30 px-4 py-4 md:px-6">
              <PlatformGlyph
                icon={group.icon}
                colorClass={group.color}
                size={28}
                className="mt-0.5"
              />
              <div>
                <h3 className="font-semibold leading-tight">{group.name}</h3>
                <p className="mt-0.5 text-sm text-muted-foreground">
                  {group.blurb}
                </p>
              </div>
            </div>
            <div className="grid grid-cols-1 divide-y sm:grid-cols-2 sm:divide-y-0 md:grid-cols-3 lg:grid-cols-4 [&>a]:border-t [&>a]:border-l-0 sm:[&>a]:border-l">
              {group.endpoints.map((ep) => (
                <EndpointCell key={ep.slug} ep={ep} />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
