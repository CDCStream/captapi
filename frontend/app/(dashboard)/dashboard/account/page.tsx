"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Loader2, KeyRound, MailCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { createClient } from "@/lib/supabase/client";
import { track } from "@/lib/analytics";

export default function AccountPage() {
  const [email, setEmail] = useState("");
  const [provider, setProvider] = useState<string>("email");
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);

  useEffect(() => {
    (async () => {
      const sb = createClient();
      const { data: { user } } = await sb.auth.getUser();
      if (!user) return;
      setEmail(user.email ?? "");
      setProvider((user.app_metadata?.provider as string) ?? "email");
    })();
  }, []);

  async function sendResetEmail() {
    if (!email) {
      toast.error("No email on file.");
      return;
    }
    setSending(true);
    const sb = createClient();
    const redirectTo = `${window.location.origin}/auth/callback?next=/reset-password`;
    const { error } = await sb.auth.resetPasswordForEmail(email, { redirectTo });
    setSending(false);
    if (error) {
      toast.error(error.message);
      return;
    }
    track("password_reset_requested", { provider });
    setSent(true);
    toast.success("Check your inbox for the password reset link.");
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Account</h1>
        <p className="text-muted-foreground mt-1">Manage your profile and security.</p>
      </div>

      {/* Profile */}
      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
          <CardDescription>Your account details.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex items-center gap-3">
            <span className="flex size-11 items-center justify-center rounded-full bg-primary/10 text-lg font-semibold text-primary uppercase">
              {email.charAt(0) || "?"}
            </span>
            <div className="min-w-0">
              <div className="truncate font-medium">{email}</div>
              <Badge variant="secondary" className="mt-1 text-xs capitalize">
                {provider === "google" ? "Google account" : "Email & password"}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Change password */}
      <Card>
        <CardHeader>
          <CardTitle>{provider === "google" ? "Set a password" : "Change password"}</CardTitle>
          <CardDescription>
            {provider === "google"
              ? "We'll email you a secure link to set a password so you can also sign in without Google."
              : "We'll email you a secure link. Open it to choose a new password."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {sent ? (
            <div className="flex items-start gap-3 rounded-lg border border-emerald-500/30 bg-emerald-500/5 p-4">
              <MailCheck className="mt-0.5 size-5 shrink-0 text-emerald-600 dark:text-emerald-400" />
              <div className="text-sm">
                <p className="font-medium">Email sent to {email}</p>
                <p className="mt-0.5 text-muted-foreground">
                  Click the link in that email to set a new password. Didn&apos;t get it?{" "}
                  <button
                    onClick={sendResetEmail}
                    disabled={sending}
                    className="font-medium text-primary underline underline-offset-2 disabled:opacity-50"
                  >
                    Resend
                  </button>
                  .
                </p>
              </div>
            </div>
          ) : (
            <Button onClick={sendResetEmail} disabled={sending}>
              {sending ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <KeyRound className="size-4" />
              )}
              {provider === "google" ? "Email me a link to set a password" : "Change password"}
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
