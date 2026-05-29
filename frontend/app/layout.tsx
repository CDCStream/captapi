import type { Metadata } from "next";
import { Caveat } from "next/font/google";
import { Toaster } from "sonner";
import "./globals.css";

const handwritten = Caveat({
  subsets: ["latin"],
  variable: "--font-handwritten",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Captapi — One API for YouTube, TikTok, Instagram & Facebook",
  description:
    "Extract transcripts, AI summaries, comments, and engagement metrics from YouTube, TikTok, Instagram, and Facebook videos with a single API call.",
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"),
  openGraph: {
    title: "Captapi",
    description: "Social media video data on demand.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning className={handwritten.variable}>
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
        <Toaster richColors closeButton position="top-right" />
      </body>
    </html>
  );
}
