"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { createClient } from "@/lib/supabase/client";

export default function AccountPage() {
  const [email, setEmail] = useState("");
  const [provider, setProvider] = useState<string>("email");
  const [newEmail, setNewEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [savingEmail, setSavingEmail] = useState(false);
  const [savingPw, setSavingPw] = useState(false);

  useEffect(() => {
    (async () => {
      const sb = createClient();
      const { data: { user } } = await sb.auth.getUser();
      if (!user) return;
      setEmail(user.email ?? "");
      setProvider((user.app_metadata?.provider as string) ?? "email");
    })();
  }, []);

  async function updateEmail(e: React.FormEvent) {
    e.preventDefault();
    if (!newEmail || newEmail === email) {
      toast.error("Enter a new, different email.");
      return;
    }
    setSavingEmail(true);
    const sb = createClient();
    const { error } = await sb.auth.updateUser({ email: newEmail });
    setSavingEmail(false);
    if (error) {
      toast.error(error.message);
      return;
    }
    toast.success("Confirmation sent. Check both inboxes to confirm the change.");
    setNewEmail("");
  }

  async function updatePassword(e: React.FormEvent) {
    e.preventDefault();
    if (password.length < 8) {
      toast.error("Password must be at least 8 characters.");
      return;
    }
    if (password !== confirm) {
      toast.error("Passwords don't match.");
      return;
    }
    setSavingPw(true);
    const sb = createClient();
    const { error } = await sb.auth.updateUser({ password });
    setSavingPw(false);
    if (error) {
      toast.error(error.message);
      return;
    }
    toast.success("Password updated.");
    setPassword("");
    setConfirm("");
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

      {/* Change email */}
      <Card>
        <CardHeader>
          <CardTitle>Change email</CardTitle>
          <CardDescription>
            We&apos;ll email a confirmation link to verify the new address.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={updateEmail} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="newEmail">New email</Label>
              <Input id="newEmail" type="email" value={newEmail} placeholder={email}
                onChange={(e) => setNewEmail(e.target.value)} />
            </div>
            <Button type="submit" disabled={savingEmail}>
              {savingEmail && <Loader2 className="size-4 animate-spin" />} Update email
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Change password */}
      <Card>
        <CardHeader>
          <CardTitle>{provider === "google" ? "Set a password" : "Change password"}</CardTitle>
          <CardDescription>
            {provider === "google"
              ? "Add a password so you can also sign in without Google."
              : "Use at least 8 characters."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={updatePassword} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="password">New password</Label>
              <Input id="password" type="password" autoComplete="new-password" minLength={8}
                value={password} onChange={(e) => setPassword(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirm">Confirm password</Label>
              <Input id="confirm" type="password" autoComplete="new-password" minLength={8}
                value={confirm} onChange={(e) => setConfirm(e.target.value)} />
            </div>
            <Button type="submit" disabled={savingPw}>
              {savingPw && <Loader2 className="size-4 animate-spin" />} Save password
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
