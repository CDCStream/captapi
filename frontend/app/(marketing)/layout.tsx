import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { MobileNav } from "@/components/marketing/mobile-nav";
import { SITE_URL } from "@/lib/api-catalog";

const STRUCTURED_DATA = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": `${SITE_URL}/#organization`,
      name: "Captapi",
      url: SITE_URL,
      logo: `${SITE_URL}/logo.png`,
      sameAs: [] as string[],
    },
    {
      "@type": "WebSite",
      "@id": `${SITE_URL}/#website`,
      url: SITE_URL,
      name: "Captapi",
      description:
        "One API for structured data from YouTube, TikTok, Instagram & Facebook.",
      publisher: { "@id": `${SITE_URL}/#organization` },
    },
    {
      "@type": "SoftwareApplication",
      name: "Captapi",
      applicationCategory: "DeveloperApplication",
      operatingSystem: "Any",
      url: SITE_URL,
      description:
        "Extract transcripts, AI summaries, comments, video details, and downloads from YouTube, TikTok, Instagram, and Facebook with a single REST API.",
      offers: {
        "@type": "Offer",
        price: "0",
        priceCurrency: "USD",
        description: "Free tier with 100 credits; paid plans from $9/mo.",
      },
    },
  ],
};

export default function MarketingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(STRUCTURED_DATA) }}
      />
      <header className="border-b">
        <div className="container flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <Image src="/logo.png" alt="Captapi" width={28} height={28} className="size-7 rounded-md" priority />
            <span className="brand-wordmark text-xl">
              Capt<span className="gradient-text">api</span>
            </span>
          </Link>
          <nav className="hidden md:flex items-center gap-6 text-sm">
            <Link href="/apis" className="text-muted-foreground hover:text-foreground">APIs</Link>
            <Link href="/pricing" className="text-muted-foreground hover:text-foreground">Pricing</Link>
            <Link href="/tools" className="text-muted-foreground hover:text-foreground">Free Tools</Link>
            <Link href="/blog" className="text-muted-foreground hover:text-foreground">Blog</Link>
            <Link href="/docs" className="text-muted-foreground hover:text-foreground">Docs</Link>
          </nav>
          <div className="flex items-center gap-2">
            <div className="hidden md:flex items-center gap-2">
              <Button asChild variant="ghost"><Link href="/login">Sign in</Link></Button>
              <Button asChild><Link href="/signup">Start Free</Link></Button>
            </div>
            <MobileNav />
          </div>
        </div>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="border-t py-12 mt-16">
        <div className="container">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8 text-sm">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Image src="/logo.png" alt="Captapi" width={24} height={24} className="size-6 rounded-md" />
                <span className="brand-wordmark text-base">
                  Capt<span className="gradient-text">api</span>
                </span>
              </div>
              <p className="text-muted-foreground text-xs">
                One API for YouTube, TikTok, Instagram & Facebook.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-3">Product</h3>
              <ul className="space-y-2 text-muted-foreground">
                <li><Link href="/apis" className="hover:text-foreground">APIs</Link></li>
                <li><Link href="/#features" className="hover:text-foreground">Features</Link></li>
                <li><Link href="/pricing" className="hover:text-foreground">Pricing</Link></li>
                <li><Link href="/tools" className="hover:text-foreground">Free Tools</Link></li>
                <li><Link href="/docs" className="hover:text-foreground">Documentation</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-3">Resources</h3>
              <ul className="space-y-2 text-muted-foreground">
                <li><Link href="/docs" className="hover:text-foreground">API Reference</Link></li>
                <li><Link href="/blog" className="hover:text-foreground">Blog</Link></li>
                <li><Link href="/alternatives" className="hover:text-foreground">Alternatives</Link></li>
                <li><Link href="/for" className="hover:text-foreground">Use Cases</Link></li>
                <li><Link href="/#faq" className="hover:text-foreground">FAQ</Link></li>
                <li><a href="mailto:support@captapi.com" className="hover:text-foreground">Contact</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-3">Legal</h3>
              <ul className="space-y-2 text-muted-foreground">
                <li><Link href="/legal/terms" className="hover:text-foreground">Terms of Service</Link></li>
                <li><Link href="/legal/privacy" className="hover:text-foreground">Privacy Policy</Link></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-muted-foreground">
            <span>© {new Date().getFullYear()} Captapi. All rights reserved.</span>
            <span>Made for developers, by developers.</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
