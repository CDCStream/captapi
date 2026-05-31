import type { Metadata } from "next";
import { Suspense } from "react";
import { Bricolage_Grotesque, Caveat } from "next/font/google";
import { Toaster } from "sonner";
import { PageViewTracker } from "@/components/analytics/page-view-tracker";
import { ThirdPartyScripts } from "@/components/analytics/third-party-scripts";
import "./globals.css";

const handwritten = Caveat({
  subsets: ["latin"],
  variable: "--font-handwritten",
  display: "swap",
});

const display = Bricolage_Grotesque({
  subsets: ["latin"],
  weight: ["600", "700", "800"],
  variable: "--font-display",
  display: "swap",
});

const SITE = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";
const AHREFS_KEY = process.env.NEXT_PUBLIC_AHREFS_KEY || "";

export const metadata: Metadata = {
  title: {
    default: "Captapi — One API for Social Media videos, posts, comments & more",
    template: "%s — Captapi",
  },
  description:
    "Extract transcripts, AI summaries, comments, followers, and engagement metrics from YouTube, TikTok, Instagram, and Facebook — 45 endpoints, one API call.",
  metadataBase: new URL(SITE),
  applicationName: "Captapi",
  keywords: [
    "social media API",
    "YouTube transcript API",
    "TikTok API",
    "Instagram Reels API",
    "Facebook video API",
    "video summarizer API",
    "transcript API",
    "comments API",
    "followers API",
    "social media posts API",
    "video data API",
    "social media scraping API",
  ],
  verification: process.env.NEXT_PUBLIC_GSC_VERIFICATION
    ? { google: process.env.NEXT_PUBLIC_GSC_VERIFICATION }
    : undefined,
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, "max-image-preview": "large", "max-snippet": -1 },
  },
  openGraph: {
    title: "Captapi — One API for Social Media videos, posts, comments & more",
    description:
      "Transcripts, AI summaries, comments, followers & engagement metrics from YouTube, TikTok, Instagram & Facebook — one REST API, clean JSON.",
    url: SITE,
    siteName: "Captapi",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Captapi — Social Media Data API",
    description:
      "One API for structured data from Social Media videos, posts, comments & more — YouTube, TikTok, Instagram & Facebook.",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning className={`${handwritten.variable} ${display.variable}`}>
      <body className="min-h-screen bg-background font-sans antialiased">
        {/* Ahrefs Web Analytics — static tag so analytics.js can read data-key
            from document.currentScript (breaks if injected dynamically). */}
        {AHREFS_KEY && (
          // eslint-disable-next-line @next/next/no-sync-scripts
          <script src="https://analytics.ahrefs.com/analytics.js" data-key={AHREFS_KEY} async />
        )}
        {children}
        <Suspense fallback={null}>
          <PageViewTracker />
        </Suspense>
        <ThirdPartyScripts />
        <Toaster richColors closeButton position="top-right" />
      </body>
    </html>
  );
}
