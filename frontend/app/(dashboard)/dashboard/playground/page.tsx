"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { createClient } from "@/lib/supabase/client";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const ENDPOINTS = [
  { id: "yt-transcript", platform: "youtube", path: "/v1/youtube/transcript",     placeholder: "https://youtube.com/watch?v=..." },
  { id: "yt-summarize",  platform: "youtube", path: "/v1/youtube/summarize",      placeholder: "https://youtube.com/watch?v=..." },
  { id: "yt-details",    platform: "youtube", path: "/v1/youtube/video-details",  placeholder: "https://youtube.com/watch?v=..." },
  { id: "yt-comments",   platform: "youtube", path: "/v1/youtube/comments",       placeholder: "https://youtube.com/watch?v=..." },
  { id: "tt-details",    platform: "tiktok",  path: "/v1/tiktok/video-details",   placeholder: "https://tiktok.com/@user/video/..." },
  { id: "tt-transcript", platform: "tiktok",  path: "/v1/tiktok/transcript",      placeholder: "https://tiktok.com/@user/video/..." },
  { id: "ig-details",    platform: "instagram", path: "/v1/instagram/details",    placeholder: "https://instagram.com/reel/..." },
  { id: "ig-transcript", platform: "instagram", path: "/v1/instagram/transcript", placeholder: "https://instagram.com/reel/..." },
  { id: "fb-details",    platform: "facebook", path: "/v1/facebook/details",      placeholder: "https://facebook.com/..." },
];

export default function PlaygroundPage() {
  const [selected, setSelected] = useState(ENDPOINTS[0]);
  const [url, setUrl] = useState("");
  const [response, setResponse] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [sessionReady, setSessionReady] = useState(false);

  useEffect(() => {
    const sb = createClient();
    sb.auth.getSession().then(({ data }) => setSessionReady(!!data.session));
  }, []);

  async function run() {
    if (!url) {
      toast.error("Enter a URL");
      return;
    }
    setLoading(true);
    setResponse("");
    try {
      const sb = createClient();
      const { data: { session } } = await sb.auth.getSession();
      if (!session) {
        toast.error("Session expired. Please sign in again.");
        setLoading(false);
        return;
      }
      const params = new URLSearchParams({ url });
      const res = await fetch(`${API_URL}${selected.path}?${params.toString()}`, {
        headers: { Authorization: `Bearer ${session.access_token}` },
      });
      const text = await res.text();
      try {
        setResponse(JSON.stringify(JSON.parse(text), null, 2));
      } catch {
        setResponse(text);
      }
      if (!res.ok) toast.error(`HTTP ${res.status}`);
    } catch (e) {
      toast.error(String(e));
    } finally {
      setLoading(false);
    }
  }

  const curl = `curl "${API_URL}${selected.path}?url=${encodeURIComponent(url || selected.placeholder)}" \\
  -H "Authorization: Bearer capt_live_..."`;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Playground</h1>
        <p className="text-muted-foreground mt-1">
          Test endpoints right from your browser — authenticated automatically with your account.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Endpoint</CardTitle>
          <CardDescription>Pick an endpoint and provide a URL.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {ENDPOINTS.map((e) => (
              <Button key={e.id} variant={selected.id === e.id ? "default" : "outline"}
                onClick={() => setSelected(e)} size="sm" className="justify-start font-mono text-xs">
                {e.path.replace("/v1/", "")}
              </Button>
            ))}
          </div>
          <div className="space-y-2">
            <Label>URL</Label>
            <Input placeholder={selected.placeholder} value={url} onChange={(e) => setUrl(e.target.value)} />
          </div>
          <Button onClick={run} disabled={loading || !sessionReady}>
            <Play className="size-4 mr-2" /> {loading ? "Running..." : "Send request"}
          </Button>
          {!sessionReady && (
            <p className="text-xs text-muted-foreground">Loading session…</p>
          )}
        </CardContent>
      </Card>

      <Tabs defaultValue="response">
        <TabsList>
          <TabsTrigger value="response">Response</TabsTrigger>
          <TabsTrigger value="curl">cURL (external use)</TabsTrigger>
        </TabsList>
        <TabsContent value="response">
          <pre className="bg-muted/50 p-4 rounded-md text-xs overflow-auto max-h-[500px] whitespace-pre-wrap">
            {response || "Hit 'Send request' to see the response here."}
          </pre>
        </TabsContent>
        <TabsContent value="curl">
          <p className="text-xs text-muted-foreground mb-2">
            For programmatic use outside the dashboard, create an API key in{" "}
            <a href="/dashboard/api-keys" className="text-primary underline">API Keys</a> and replace{" "}
            <code>capt_live_...</code> below.
          </p>
          <pre className="bg-muted/50 p-4 rounded-md text-xs overflow-auto">{curl}</pre>
        </TabsContent>
      </Tabs>
    </div>
  );
}
