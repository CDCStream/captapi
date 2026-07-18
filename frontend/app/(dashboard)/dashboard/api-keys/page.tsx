"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import {
  Check,
  Copy,
  Eye,
  EyeOff,
  KeyRound,
  Loader2,
  Plus,
  ShieldAlert,
  Trash2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { api, type ApiKey, type CreatedKey } from "@/lib/api-client";
import { track } from "@/lib/analytics";
import { formatDate } from "@/lib/utils";

export default function ApiKeysPage() {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);

  const [createOpen, setCreateOpen] = useState(false);
  const [name, setName] = useState("");
  const [creating, setCreating] = useState(false);

  const [newKey, setNewKey] = useState<CreatedKey | null>(null);
  const [reveal, setReveal] = useState(false);
  const [copied, setCopied] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const data = await api.listKeys();
      setKeys(data.keys);
    } catch (e) {
      toast.error(String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    try {
      const created = await api.createKey(name.trim() || "Default");
      track("api_key_created");
      setCreateOpen(false);
      setName("");
      setReveal(false);
      setCopied(false);
      setNewKey(created);
      await load();
    } catch (e) {
      toast.error(String(e));
    } finally {
      setCreating(false);
    }
  }

  async function onRevoke(id: string) {
    if (!confirm("Revoke this API key? Active integrations will stop working.")) return;
    try {
      await api.revokeKey(id);
      toast.success("Key revoked");
      await load();
    } catch (e) {
      toast.error(String(e));
    }
  }

  async function copyNewKey() {
    if (!newKey) return;
    await navigator.clipboard.writeText(newKey.key);
    setCopied(true);
    toast.success("API key copied to clipboard");
    setTimeout(() => setCopied(false), 2500);
  }

  const active = keys.filter((k) => !k.revoked_at);
  const masked = newKey
    ? `${newKey.key.slice(0, 10)}${"•".repeat(24)}`
    : "";

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-end justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">API Keys</h1>
          <p className="text-muted-foreground mt-1">
            Create keys to authenticate API requests. Treat them like passwords.
          </p>
        </div>
        <Button onClick={() => { setName(""); setCreateOpen(true); }}>
          <Plus className="size-4" /> Create key
        </Button>
      </div>

      {/* Active keys */}
      <div className="rounded-2xl border bg-background">
        <div className="flex items-center justify-between border-b px-5 py-4">
          <h2 className="font-semibold">
            Active keys{" "}
            <span className="text-muted-foreground font-normal">({active.length})</span>
          </h2>
        </div>

        {loading ? (
          <div className="flex items-center gap-2 px-5 py-10 text-sm text-muted-foreground">
            <Loader2 className="size-4 animate-spin" /> Loading keys…
          </div>
        ) : active.length === 0 ? (
          <div className="px-5 py-14 text-center">
            <span className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
              <KeyRound className="size-6" />
            </span>
            <p className="mt-4 font-medium">No API keys yet</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Create your first key to start making requests.
            </p>
            <Button className="mt-4" onClick={() => { setName(""); setCreateOpen(true); }}>
              <Plus className="size-4" /> Create key
            </Button>
          </div>
        ) : (
          <ul className="divide-y">
            {active.map((k) => (
              <li key={k.id} className="flex items-center gap-4 px-5 py-4">
                <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-muted text-muted-foreground">
                  <KeyRound className="size-5" />
                </span>
                <div className="min-w-0 flex-1">
                  <div className="font-medium truncate">{k.name}</div>
                  <code className="text-xs text-muted-foreground font-mono">
                    {k.key_prefix}••••••••
                  </code>
                </div>
                <div className="hidden sm:flex flex-col items-end gap-1 text-xs text-muted-foreground shrink-0">
                  <Badge variant="outline">Created {formatDate(k.created_at).split(",")[0]}</Badge>
                  <span>Last used: {k.last_used_at ? formatDate(k.last_used_at) : "never"}</span>
                </div>
                <Button
                  onClick={() => onRevoke(k.id)}
                  variant="ghost"
                  size="icon"
                  className="text-muted-foreground hover:text-destructive shrink-0"
                  title="Revoke key"
                >
                  <Trash2 className="size-4" />
                </Button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="rounded-2xl border bg-background p-5 space-y-3">
        <h2 className="font-semibold">How to authenticate</h2>
        <p className="text-sm text-muted-foreground">
          Send your key on every request. Both headers work:
        </p>
        <div className="space-y-2 font-mono text-xs">
          <pre className="overflow-x-auto rounded-lg border bg-muted/50 p-3">{`Authorization: Bearer capt_live_...`}</pre>
          <pre className="overflow-x-auto rounded-lg border bg-muted/50 p-3">{`x-api-key: capt_live_...`}</pre>
        </div>
        <p className="text-xs text-muted-foreground">
          Keys are scoped to your account only. Anyone with a key can use your credits — keep them secret.
        </p>
      </div>

      {/* Create key modal */}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Create API key</DialogTitle>
            <DialogDescription>
              Give your key a name so you can recognize it later.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={onCreate} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="key-name">Key name</Label>
              <Input
                id="key-name"
                autoFocus
                placeholder="e.g. Production server"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <DialogFooter>
              <Button type="button" variant="ghost" onClick={() => setCreateOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={creating}>
                {creating ? <Loader2 className="size-4 animate-spin" /> : <KeyRound className="size-4" />}
                Create key
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* New key reveal modal */}
      <Dialog
        open={Boolean(newKey)}
        onOpenChange={(o) => {
          if (!o) setNewKey(null);
        }}
      >
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Your new API key</DialogTitle>
            <DialogDescription className="flex items-center gap-1.5 text-amber-600 dark:text-amber-400">
              <ShieldAlert className="size-4 shrink-0" />
              Copy it now — for security, it won&apos;t be shown again.
            </DialogDescription>
          </DialogHeader>

          <div className="flex items-center gap-2 rounded-lg border bg-muted/50 p-2">
            <code className="flex-1 truncate px-2 font-mono text-sm">
              {reveal ? newKey?.key : masked}
            </code>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => setReveal((r) => !r)}
              title={reveal ? "Hide" : "Reveal"}
            >
              {reveal ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
            </Button>
            <Button
              type="button"
              variant={copied ? "secondary" : "default"}
              size="icon"
              onClick={copyNewKey}
              title="Copy"
            >
              {copied ? <Check className="size-4" /> : <Copy className="size-4" />}
            </Button>
          </div>

          {copied && (
            <div className="flex items-center gap-2 rounded-lg border border-green-500/30 bg-green-500/10 px-3 py-2 text-sm text-green-700 dark:text-green-400">
              <Check className="size-4" /> Copied to clipboard.
            </div>
          )}

          <DialogFooter>
            <Button onClick={() => setNewKey(null)}>Done</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
