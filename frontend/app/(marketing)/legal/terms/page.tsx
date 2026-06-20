import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Service — Captapi",
  description: "Read the Terms of Service for the Captapi social media data API — covering acceptable use, accounts, credits and billing, fair use, liability, and account termination.",
  alternates: { canonical: "/legal/terms" },
};

export default function TermsPage() {
  return (
    <article className="container max-w-3xl py-16 prose prose-neutral dark:prose-invert">
      <h1>Terms of Service</h1>
      <p className="text-sm text-muted-foreground">
        Last updated: {new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}
      </p>

      <h2>1. Acceptance of Terms</h2>
      <p>
        By creating an account or using the Captapi API (the &quot;Service&quot;),
        you agree to these Terms of Service. If you do not agree, do not use the
        Service.
      </p>

      <h2>2. Description of Service</h2>
      <p>
        Captapi provides a REST API to extract publicly available data from
        social media platforms (YouTube, TikTok, Instagram, Facebook), including
        video metadata, transcripts, AI-generated summaries, and comments.
      </p>

      <h2>3. Acceptable Use</h2>
      <p>You agree NOT to use Captapi to:</p>
      <ul>
        <li>Scrape private or non-public content (e.g., private profiles, DMs).</li>
        <li>Violate any social platform&apos;s Terms of Service in ways that expose us to liability.</li>
        <li>Re-identify individuals, harass, dox, or otherwise harm people.</li>
        <li>Build a directly competing scraping service or resell raw Captapi access.</li>
        <li>Process personal data in violation of GDPR, CCPA, or other applicable laws.</li>
      </ul>

      <h2>4. Credits & Billing</h2>
      <p>
        The Service uses a credit-based pricing model. Subscription credits reset
        monthly; top-up credits never expire. Failed requests (e.g., 4xx, 5xx
        responses) do not consume credits. You may cancel paid subscriptions at
        any time from the dashboard; cancellations take effect at the end of the
        current billing period.
      </p>

      <h2>5. Service Availability</h2>
      <p>
        We strive for high availability but do not guarantee uninterrupted
        service. Captapi depends on third-party scrapers and the availability of
        public content on source platforms. We are not liable for downtime
        caused by upstream providers.
      </p>

      <h2>6. Intellectual Property</h2>
      <p>
        You retain all rights to the data you extract via the Service. We retain
        all rights to the Captapi software, brand, and documentation.
      </p>

      <h2>7. Limitation of Liability</h2>
      <p>
        To the maximum extent permitted by law, Captapi&apos;s total liability for
        any claim arising from the Service is limited to the amount you paid in
        the 12 months preceding the claim.
      </p>

      <h2>8. Termination</h2>
      <p>
        We may suspend or terminate your account for violations of these Terms,
        non-payment, or abuse of the Service. You may close your account at any
        time from the dashboard.
      </p>

      <h2>9. Changes to These Terms</h2>
      <p>
        We may update these Terms periodically. Material changes will be
        communicated via email or in-app notification.
      </p>

      <h2>10. Contact</h2>
      <p>
        Questions about these Terms? Email{" "}
        <a href="mailto:support@captapi.com">support@captapi.com</a>.
      </p>
    </article>
  );
}
