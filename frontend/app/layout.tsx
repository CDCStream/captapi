import type { Metadata } from "next";
import { Suspense } from "react";
import { Bricolage_Grotesque, Caveat } from "next/font/google";
import { Toaster } from "sonner";
import { PageViewTracker } from "@/components/analytics/page-view-tracker";
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

export const metadata: Metadata = {
  title: {
    default: "Captapi — One API for YouTube, TikTok, Instagram & Facebook",
    template: "%s — Captapi",
  },
  description:
    "Extract transcripts, AI summaries, comments, and engagement metrics from YouTube, TikTok, Instagram, and Facebook videos with a single API call.",
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
    "video data API",
  ],
  alternates: { canonical: "/" },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, "max-image-preview": "large", "max-snippet": -1 },
  },
  openGraph: {
    title: "Captapi — One API for YouTube, TikTok, Instagram & Facebook",
    description:
      "Transcripts, AI summaries, comments & engagement metrics from social video — one REST API, clean JSON.",
    url: SITE,
    siteName: "Captapi",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Captapi — Social Media Data API",
    description:
      "One API for structured data from YouTube, TikTok, Instagram & Facebook.",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning className={`${handwritten.variable} ${display.variable}`}>
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
        <Suspense fallback={null}>
          <PageViewTracker />
        </Suspense>
        <Toaster richColors closeButton position="top-right" />
      </body>
    </html>
  );
}
