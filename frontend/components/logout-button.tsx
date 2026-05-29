"use client";

import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { createClient } from "@/lib/supabase/client";

export function LogoutButton() {
  const router = useRouter();
  async function onClick() {
    const sb = createClient();
    await sb.auth.signOut();
    router.push("/login");
    router.refresh();
  }
  return (
    <Button onClick={onClick} variant="ghost" className="w-full justify-start">
      <LogOut className="size-4 mr-2" /> Sign out
    </Button>
  );
}
