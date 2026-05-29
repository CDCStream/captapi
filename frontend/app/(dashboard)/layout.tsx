import Link from "next/link";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { Button } from "@/components/ui/button";
import { LogoutButton } from "@/components/logout-button";
import { Code2, Key, BarChart3, CreditCard, PlayCircle, LayoutDashboard } from "lucide-react";

const nav = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/api-keys", label: "API Keys", icon: Key },
  { href: "/dashboard/playground", label: "Playground", icon: PlayCircle },
  { href: "/dashboard/usage", label: "Usage", icon: BarChart3 },
  { href: "/dashboard/billing", label: "Billing", icon: CreditCard },
];

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const sb = await createClient();
  const { data: { user } } = await sb.auth.getUser();
  if (!user) redirect("/login");

  return (
    <div className="min-h-screen flex">
      <aside className="hidden md:flex flex-col w-60 border-r p-4 gap-1">
        <Link href="/" className="flex items-center gap-2 mb-6 px-2">
          <div className="size-7 rounded-md bg-primary" />
          <span className="font-bold">Captapi</span>
        </Link>
        {nav.map((n) => (
          <Button key={n.href} asChild variant="ghost" className="justify-start">
            <Link href={n.href}>
              <n.icon className="size-4 mr-2" />
              {n.label}
            </Link>
          </Button>
        ))}
        <div className="mt-auto pt-4 border-t">
          <div className="text-xs text-muted-foreground px-2 mb-2 truncate">{user.email}</div>
          <LogoutButton />
        </div>
      </aside>
      <div className="flex-1 flex flex-col">
        <header className="md:hidden border-b p-4 flex items-center justify-between">
          <Link href="/" className="font-bold">Captapi</Link>
          <LogoutButton />
        </header>
        <main className="flex-1 p-6 md:p-10">{children}</main>
      </div>
    </div>
  );
}
