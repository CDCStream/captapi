"use client";

import { useCallback, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { slugify } from "@/lib/blog";

function extractMeta(html: string) {
  const doc = new DOMParser().parseFromString(html, "text/html");

  const titleEl = doc.querySelector("h1") || doc.querySelector("h2") || doc.querySelector("title");
  const title = titleEl?.textContent?.trim() || "";

  const firstP = doc.querySelector("p");
  const description = firstP?.textContent?.trim().slice(0, 160) || "";

  const firstImg = doc.querySelector("img");
  const image = firstImg?.getAttribute("src") || "";

  const headings = Array.from(doc.querySelectorAll("h2, h3"));
  const tagSet = new Set<string>();
  headings.forEach((h) => {
    const text = h.textContent?.trim().toLowerCase();
    if (text && text.length < 40) tagSet.add(text);
  });
  const metaKeywords = doc.querySelector('meta[name="keywords"]');
  if (metaKeywords) {
    metaKeywords.getAttribute("content")?.split(",").forEach((k) => {
      const trimmed = k.trim().toLowerCase();
      if (trimmed) tagSet.add(trimmed);
    });
  }
  const tags = Array.from(tagSet).slice(0, 8).join(", ");

  return { title, description, image, tags };
}

export default function NewBlogPostPage() {
  const [secret, setSecret] = useState("");
  const [title, setTitle] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");
  const [author, setAuthor] = useState("Captapi");
  const [image, setImage] = useState("");
  const [tags, setTags] = useState("");
  const [status, setStatus] = useState("published");
  const [content, setContent] = useState("");
  const [tab, setTab] = useState<"edit" | "preview">("edit");
  const [busy, setBusy] = useState(false);

  const effectiveSlug = slug.trim() || slugify(title);

  const handleContentChange = useCallback((html: string) => {
    setContent(html);
    if (!html.trim()) return;
    const meta = extractMeta(html);
    if (meta.title && !title) setTitle(meta.title);
    if (meta.description && !description) setDescription(meta.description);
    if (meta.image && !image) setImage(meta.image);
    if (meta.tags && !tags) setTags(meta.tags);
  }, [title, description, image, tags]);

  async function save() {
    if (!secret) return toast.error("Enter the admin secret");
    if (!title.trim() || !content.trim()) return toast.error("Title and content are required");
    setBusy(true);
    try {
      const res = await fetch("/api/blog/save", {
        method: "POST",
        headers: { "content-type": "application/json", "x-admin-secret": secret },
        body: JSON.stringify({ title, slug: effectiveSlug, description, author, image, tags, status, content }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Save failed");
      toast.success(`Saved: /blog/${data.slug}`);
    } catch (e) {
      toast.error(String(e instanceof Error ? e.message : e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="container max-w-4xl py-12">
      <h1 className="brand-wordmark text-3xl mb-2">New blog post</h1>
      <p className="text-muted-foreground mb-8 text-sm">
        Manual editor. Requires the <code>BLOG_ADMIN_SECRET</code> value.
      </p>

      <div className="grid gap-5">
        <div className="grid gap-2">
          <Label htmlFor="secret">Admin secret</Label>
          <Input id="secret" type="password" value={secret} onChange={(e) => setSecret(e.target.value)} placeholder="BLOG_ADMIN_SECRET" />
        </div>

        <div className="grid gap-2">
          <Label htmlFor="title">Title *</Label>
          <Input id="title" value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>

        <div className="grid gap-2">
          <Label htmlFor="slug">Slug</Label>
          <Input id="slug" value={slug} onChange={(e) => setSlug(e.target.value)} placeholder={slugify(title) || "auto-from-title"} />
          <span className="text-xs text-muted-foreground">URL: /blog/{effectiveSlug || "…"}</span>
        </div>

        <div className="grid gap-2">
          <Label htmlFor="description">Description</Label>
          <Input id="description" value={description} onChange={(e) => setDescription(e.target.value)} />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div className="grid gap-2">
            <Label htmlFor="author">Author</Label>
            <Input id="author" value={author} onChange={(e) => setAuthor(e.target.value)} />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="status">Status</Label>
            <select
              id="status"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="published">published</option>
              <option value="draft">draft</option>
            </select>
          </div>
        </div>

        <div className="grid gap-2">
          <Label htmlFor="image">Cover image URL</Label>
          <Input id="image" value={image} onChange={(e) => setImage(e.target.value)} placeholder="https://…" />
        </div>

        <div className="grid gap-2">
          <Label htmlFor="tags">Tags (comma-separated)</Label>
          <Input id="tags" value={tags} onChange={(e) => setTags(e.target.value)} placeholder="youtube, api, tutorial" />
        </div>

        <div className="grid gap-2">
          <div className="flex items-center gap-2">
            <Label>Content (HTML) *</Label>
            <div className="ml-auto flex gap-1 rounded-md border p-0.5">
              <button
                type="button"
                onClick={() => setTab("edit")}
                className={`rounded px-3 py-1 text-xs ${tab === "edit" ? "bg-primary text-primary-foreground" : "text-muted-foreground"}`}
              >
                Edit
              </button>
              <button
                type="button"
                onClick={() => setTab("preview")}
                className={`rounded px-3 py-1 text-xs ${tab === "preview" ? "bg-primary text-primary-foreground" : "text-muted-foreground"}`}
              >
                Preview
              </button>
            </div>
          </div>
          {tab === "edit" ? (
            <textarea
              value={content}
              onChange={(e) => handleContentChange(e.target.value)}
              rows={18}
              className="rounded-md border border-input bg-background p-3 font-mono text-sm"
              placeholder="<h2>Heading</h2><p>Body…</p>"
            />
          ) : (
            <div
              className="blog-content rounded-md border p-4 min-h-[200px]"
              dangerouslySetInnerHTML={{ __html: content }}
            />
          )}
        </div>

        <div>
          <Button onClick={save} disabled={busy}>
            {busy ? "Saving…" : "Save post"}
          </Button>
        </div>
      </div>
    </div>
  );
}
