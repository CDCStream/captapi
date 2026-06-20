import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy — Captapi",
  description: "Read the Captapi Privacy Policy — what data the social media data API collects, how we use and store it, cookies, third-party processors, retention, and your privacy rights.",
  alternates: { canonical: "/legal/privacy" },
};

export default function PrivacyPage() {
  return (
    <article className="container max-w-3xl py-16 prose prose-neutral dark:prose-invert">
      <h1>Privacy Policy</h1>
      <p className="text-sm text-muted-foreground">
        Last updated: {new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}
      </p>

      <h2>1. Information We Collect</h2>
      <h3>Account information</h3>
      <p>
        When you sign up, we collect your email address and a securely hashed
        password. If you sign in with Google, we receive your email and basic
        profile information from Google.
      </p>
      <h3>Usage data</h3>
      <p>
        We log each API request with: timestamp, endpoint, response status,
        latency, credits consumed, and the source URL you submitted. We do
        <strong> not </strong>
        store the response payloads returned to you (transcripts, comments,
        etc.) for longer than 24 hours (cache).
      </p>
      <h3>Billing information</h3>
      <p>
        Payments are processed by Stripe. We never see or store your full credit
        card number — only a Stripe customer ID and the last four digits.
      </p>

      <h2>2. How We Use Your Information</h2>
      <ul>
        <li>Authenticate your API requests and dashboard sessions.</li>
        <li>Bill you correctly and provide usage analytics.</li>
        <li>Detect abuse, debug issues, and improve the Service.</li>
        <li>Send transactional emails (password resets, billing receipts).</li>
      </ul>

      <h2>3. Data Sharing</h2>
      <p>
        We do not sell your data. We share data only with the following
        sub-processors, all of whom have signed DPAs:
      </p>
      <ul>
        <li><strong>Supabase</strong> — authentication & database hosting</li>
        <li><strong>Stripe</strong> — payment processing</li>
        <li><strong>Apify</strong> — scraping infrastructure</li>
        <li><strong>OpenAI</strong> — AI summarization (input transcripts only; OpenAI does not train on API data per their policy)</li>
        <li><strong>Upstash</strong> — caching & rate limiting</li>
        <li><strong>Sentry</strong> — error tracking (no request bodies sent)</li>
      </ul>

      <h2>4. Data Retention</h2>
      <ul>
        <li><strong>Request logs:</strong> 90 days for analytics & abuse detection</li>
        <li><strong>Cache:</strong> 24 hours, automatically purged</li>
        <li><strong>Account data:</strong> retained until account deletion</li>
        <li><strong>Billing records:</strong> 7 years for tax / accounting compliance</li>
      </ul>

      <h2>5. Your Rights (GDPR / CCPA)</h2>
      <p>You have the right to:</p>
      <ul>
        <li>Access your personal data</li>
        <li>Correct inaccurate data</li>
        <li>Delete your account and associated data</li>
        <li>Export your data in a portable format</li>
        <li>Object to processing or restrict it</li>
      </ul>
      <p>
        To exercise these rights, email{" "}
        <a href="mailto:privacy@captapi.com">privacy@captapi.com</a>.
      </p>

      <h2>6. Security</h2>
      <p>
        API keys are stored as SHA-256 hashes — we cannot recover lost keys.
        All traffic is encrypted in transit (TLS 1.2+). Database backups are
        encrypted at rest. We follow industry best practices but cannot
        guarantee absolute security.
      </p>

      <h2>7. Cookies</h2>
      <p>
        We use only essential cookies for authentication and CSRF protection.
        We do not use third-party advertising or behavioral tracking cookies.
      </p>

      <h2>8. International Transfers</h2>
      <p>
        Your data may be processed in the EU, US, or other regions where our
        sub-processors operate. Where applicable, we rely on Standard
        Contractual Clauses (SCCs) for cross-border transfers.
      </p>

      <h2>9. Changes to This Policy</h2>
      <p>
        We may update this Policy occasionally. Material changes will be
        emailed to you. Continued use after changes means you accept the
        updated Policy.
      </p>

      <h2>10. Contact</h2>
      <p>
        Questions or concerns? Email{" "}
        <a href="mailto:privacy@captapi.com">privacy@captapi.com</a>.
      </p>
    </article>
  );
}
