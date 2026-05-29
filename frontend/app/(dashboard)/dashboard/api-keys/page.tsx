"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Copy, Trash2, KeyRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { api, type ApiKey, type CreatedKey } from "@/lib/api-client";
import { formatDate } from "@/lib/utils";

export default function ApiKeysPage() {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("Default");
  const [creating, setCreating] = useState(false);
  const [newKey, setNewKey] = useState<CreatedKey | null>(null);

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

  useEffect(() => { load(); }, []);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    try {
      const created = await api.createKey(name || "Default");
      setNewKey(created);
      setName("Default");
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

  function copy(s: string) {
    navigator.clipboard.writeText(s);
    toast.success("Copied to clipboard");
  }

  const active = keys.filter((k) => !k.revoked_at);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold">API Keys</h1>
        <p className="text-muted-foreground mt-1">
          Create keys to authenticate API requests. Treat them like passwords.
        </p>
      </div>

      {newKey && (
        <Card className="border-primary">
          <CardHeader>
            <CardTitle className="text-base">Your new API key (shown once)</CardTitle>
            <CardDescription>{newKey.warning}</CardDescription>
          </CardHeader>
          <CardContent className="flex items-center gap-2">
            <code className="flex-1 bg-muted p-3 rounded font-mono text-sm break-all">{newKey.key}</code>
            <Button onClick={() => copy(newKey.key)} variant="outline" size="icon"><Copy className="size-4" /></Button>
            <Button onClick={() => setNewKey(null)} variant="ghost">Close</Button>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle className="text-base">Create new key</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={onCreate} className="flex flex-col sm:flex-row gap-3 items-end">
            <div className="flex-1 w-full space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input id="name" placeholder="e.g. Production server" value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <Button type="submit" disabled={creating}>
              <KeyRound className="size-4 mr-2" />
              {creating ? "Creating..." : "Create key"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Active keys ({active.length})</CardTitle></CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : active.length === 0 ? (
            <p className="text-sm text-muted-foreground">No active API keys yet.</p>
          ) : (
            <div className="space-y-2">
              {active.map((k) => (
                <div key={k.id} className="flex items-center justify-between border rounded-md p-3 gap-3">
                  <div className="min-w-0">
                    <div className="font-medium">{k.name}</div>
                    <div className="text-xs text-muted-foreground font-mono">{k.key_prefix}...</div>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground shrink-0">
                    <span>Last used: {formatDate(k.last_used_at)}</span>
                    <Badge variant="outline">{formatDate(k.created_at).split(",")[0]}</Badge>
                  </div>
                  <Button onClick={() => onRevoke(k.id)} variant="ghost" size="icon">
                    <Trash2 className="size-4 text-destructive" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
