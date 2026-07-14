import Image from "next/image";
import Link from "next/link";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { BugReportDialog } from "@/components/bug-report-dialog";
import { LogoutButton } from "@/components/logout-button";
import { SidebarNav } from "@/components/dashboard/sidebar-nav";
import { WelcomePing } from "@/components/dashboard/welcome-ping";

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const sb = await createClient();
  const { data: { user } } = await sb.auth.getUser();
  if (!user) redirect("/login");

  return (
    <div className="min-h-screen flex bg-muted/30">
      <WelcomePing />
      <aside className="hidden md:flex flex-col w-60 shrink-0 border-r bg-background p-4 sticky top-0 h-screen">
        <Link href="/" className="flex items-center gap-2 mb-6 px-2">
          <Image src="/logo.png" alt="Captapi" width={28} height={28} className="size-7 rounded-md" />
          <span className="brand-wordmark text-lg">
            Capt<span className="gradient-text">api</span>
          </span>
        </Link>
        <div className="flex-1 min-h-0 overflow-y-auto -mx-1 px-1">
          <SidebarNav />
        </div>
        <div className="mt-4 pt-4 border-t">
          <BugReportDialog
            loggedIn
            variant="ghost"
            size="sm"
            className="w-full justify-start gap-3 px-2 text-muted-foreground hover:text-foreground"
          />
          <Link
            href="/dashboard/account"
            className="flex items-center gap-2 rounded-lg px-2 py-2 transition-colors hover:bg-muted"
          >
            <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold uppercase text-primary">
              {(user.email ?? "?").charAt(0)}
            </span>
            <span className="min-w-0">
              <span className="block truncate text-sm font-medium">{user.email}</span>
              <span className="block text-xs text-muted-foreground">Account settings</span>
            </span>
          </Link>
          <div className="mt-1">
            <LogoutButton />
          </div>
        </div>
      </aside>
      <div className="flex-1 flex flex-col min-w-0">
        <header className="md:hidden border-b bg-background p-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <Image src="/logo.png" alt="Captapi" width={24} height={24} className="size-6 rounded-md" />
            <span className="brand-wordmark">Capt<span className="gradient-text">api</span></span>
          </Link>
          <LogoutButton />
        </header>
        <main className="flex-1 p-6 md:p-10">{children}</main>
      </div>
    </div>
  );
}
