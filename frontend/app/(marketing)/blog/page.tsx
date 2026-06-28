import Image from "next/image";
import Link from "next/link";
import { Clock, User } from "lucide-react";
import { getServiceClient } from "@/lib/supabase/admin";
import { formatDate, parseBlogPost, type BlogPostRow } from "@/lib/blog";
import { buildMetadata } from "@/lib/seo";

export const revalidate = 60;

export const metadata = buildMetadata({
  title: "Blog — Guides & insights on social media APIs",
  description:
    "Tutorials, guides, and insights on extracting transcripts, summaries, comments, search results, profiles, commerce data, ad intelligence, and engagement data from public social platforms.",
  path: "/blog",
});

async function getPosts() {
  const sb = getServiceClient();
  if (!sb) return [];
  const { data, error } = await sb
    .from("blog_posts")
    .select("*")
    .eq("status", "published")
    .order("published_at", { ascending: false });
  if (error || !data) return [];
  return (data as BlogPostRow[]).map(parseBlogPost);
}

export default async function BlogIndexPage() {
  const posts = await getPosts();

  return (
    <div className="container py-16">
      <div className="max-w-2xl mb-12">
        <h1 className="brand-wordmark text-4xl md:text-5xl mb-4">Blog</h1>
        <p className="text-muted-foreground text-lg">
          Guides, tutorials, and insights on building with social media data APIs.
        </p>
      </div>

      {posts.length === 0 ? (
        <div className="rounded-xl border border-dashed p-16 text-center text-muted-foreground">
          No posts yet — check back soon.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {posts.map((post) => (
            <Link
              key={post.slug}
              href={`/blog/${post.slug}`}
              className="group flex flex-col rounded-xl border bg-card overflow-hidden transition-all hover:shadow-lg hover:-translate-y-0.5"
            >
              {post.image ? (
                <div className="relative aspect-[16/9] overflow-hidden bg-muted">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={post.image}
                    alt={post.title}
                    className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                </div>
              ) : (
                <div className="aspect-[16/9] bg-gradient-to-br from-blue-500/15 to-cyan-400/10 flex items-center justify-center">
                  <Image src="/logo.png" alt="Captapi" width={48} height={48} className="size-12 opacity-60 rounded-lg" />
                </div>
              )}

              <div className="flex flex-1 flex-col p-5">
                {post.tags.length > 0 && (
                  <div className="mb-3 flex flex-wrap gap-1.5">
                    {post.tags.slice(0, 3).map((tag) => (
                      <span
                        key={tag}
                        className="rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
                <h2 className="text-lg font-semibold leading-snug group-hover:text-primary transition-colors">
                  {post.title}
                </h2>
                {post.description && (
                  <p className="mt-2 line-clamp-3 text-sm text-muted-foreground">
                    {post.description}
                  </p>
                )}
                <div className="mt-4 flex items-center gap-4 pt-4 border-t text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <User className="size-3.5" />
                    {post.author}
                  </span>
                  <span>{formatDate(post.publishedAt)}</span>
                  <span className="flex items-center gap-1">
                    <Clock className="size-3.5" />
                    {post.readingTime} min
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
