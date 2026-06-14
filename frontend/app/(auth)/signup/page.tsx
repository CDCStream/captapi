"use client";

import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";
import { Loader2, MailCheck } from "lucide-react";
import { GoogleButton } from "@/components/auth/google-button";
import { PasswordInput } from "@/components/auth/password-input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createClient } from "@/lib/supabase/client";
import { track } from "@/lib/analytics";

export default function SignupPage() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [sentTo, setSentTo] = useState<string | null>(null);
  const [resending, setResending] = useState(false);

  function isDisposableEmail(addr: string) {
    const blocked = ["web-library.net","mailinator.com","guerrillamail.com","tempmail.com","throwaway.email","temp-mail.org","10minutemail.com","trashmail.com","yopmail.com","sharklasers.com","guerrillamailblock.com","grr.la","dispostable.com","mailnesia.com","maildrop.cc","fakeinbox.com","mailcatch.com","tempail.com","tempr.email","discard.email","tmpmail.net","tmpmail.org","emailondeck.com","mohmal.com","getnada.com","burnermail.io","mailsac.com","inboxkitten.com","mytemp.email","spam4.me","tmail.ws"];
    const domain = addr.split("@")[1]?.toLowerCase();
    return domain ? blocked.includes(domain) : false;
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (password.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }
    if (isDisposableEmail(email)) {
      toast.error("Disposable email addresses are not allowed. Please use a real email.");
      return;
    }
    setLoading(true);
    const sb = createClient();
    const first = firstName.trim();
    const last = lastName.trim();
    const { error } = await sb.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback?next=/dashboard`,
        data: {
          first_name: first,
          last_name: last,
          full_name: [first, last].filter(Boolean).join(" "),
        },
      },
    });
    setLoading(false);
    if (error) {
      toast.error(error.message);
      return;
    }
    track("signup", { method: "password" });
    setSentTo(email);
  }

  async function resend() {
    if (!sentTo) return;
    setResending(true);
    const sb = createClient();
    const { error } = await sb.auth.resend({
      type: "signup",
      email: sentTo,
      options: { emailRedirectTo: `${window.location.origin}/auth/callback?next=/dashboard` },
    });
    setResending(false);
    if (error) {
      toast.error(error.message);
      return;
    }
    toast.success("Verification email resent.");
  }

  if (sentTo) {
    return (
      <Card className="w-full max-w-sm">
        <CardHeader className="items-center text-center">
          <div className="mb-2 flex size-12 items-center justify-center rounded-full bg-primary/10">
            <MailCheck className="size-6 text-primary" />
          </div>
          <CardTitle>Check your email</CardTitle>
          <CardDescription>
            We sent a verification link to{" "}
            <span className="font-medium text-foreground">{sentTo}</span>. Click it to
            activate your account.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Didn&apos;t get it? Check your spam folder, or resend below.
          </p>
          <Button
            variant="outline"
            className="w-full"
            onClick={resend}
            disabled={resending}
          >
            {resending && <Loader2 className="size-4 animate-spin" />}
            {resending ? "Resending…" : "Resend email"}
          </Button>
          <p className="text-center text-sm text-muted-foreground">
            Already verified?{" "}
            <Link href="/login" className="text-primary hover:underline">Sign in</Link>
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-sm">
      <CardHeader>
        <CardTitle>Create your account</CardTitle>
        <CardDescription>100 free credits to get you started.</CardDescription>
      </CardHeader>
      <CardContent>
        <GoogleButton />
        <div className="my-4 flex items-center gap-3">
          <span className="h-px flex-1 bg-border" />
          <span className="text-xs text-muted-foreground">or</span>
          <span className="h-px flex-1 bg-border" />
        </div>
        <form onSubmit={onSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label htmlFor="firstName">First name</Label>
              <Input id="firstName" autoComplete="given-name" value={firstName}
                onChange={(e) => setFirstName(e.target.value)} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="lastName">Last name</Label>
              <Input id="lastName" autoComplete="family-name" value={lastName}
                onChange={(e) => setLastName(e.target.value)} required />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" autoComplete="email" value={email}
              onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <PasswordInput id="password" autoComplete="new-password" minLength={8}
              value={password} onChange={(e) => setPassword(e.target.value)} required />
            <p className="text-xs text-muted-foreground">At least 8 characters.</p>
          </div>
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Creating account..." : "Create account"}
          </Button>
          <p className="text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link href="/login" className="text-primary hover:underline">Sign in</Link>
          </p>
        </form>
      </CardContent>
    </Card>
  );
}
