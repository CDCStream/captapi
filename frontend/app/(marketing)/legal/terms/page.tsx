import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Terms of Service — Captapi",
  description:
    "Read the Terms of Service for the Captapi social media data API — covering the service, acceptable use, accounts, credits and billing, refunds, compliance, liability, and termination.",
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
        By creating an account or using the Captapi API and website (together, the
        &quot;Service&quot;), you agree to these Terms of Service and to our{" "}
        <Link href="/legal/acceptable-use">Acceptable Use Policy</Link>,{" "}
        <Link href="/legal/refund">Refund Policy</Link>, and{" "}
        <Link href="/legal/privacy">Privacy Policy</Link>, which are incorporated by
        reference. If you do not agree, do not use the Service. If you use the Service
        on behalf of an organization, you represent that you are authorized to bind
        that organization to these Terms.
      </p>

      <h2>2. Description of the Service</h2>
      <p>
        Captapi is a developer tool that provides a REST API and related SDKs and
        integrations for retrieving <strong>publicly available information</strong>{" "}
        from public web pages and public profiles across social and web platforms
        (such as YouTube, TikTok, Instagram, Facebook, X, Reddit, Threads, Bluesky,
        Pinterest, LinkedIn, Spotify, and others). The Service returns this public
        information as structured JSON and may add derived analytics and optional
        AI-generated summaries.
      </p>
      <p>
        Captapi accesses only information that is publicly accessible without logging
        in and without circumventing any technical access control. The Service does
        not access private accounts, private messages, password-protected content, or
        any content that requires authentication. Captapi is not affiliated with,
        endorsed by, or sponsored by any of the platforms referenced above.
      </p>

      <h2>3. Accounts &amp; API Keys</h2>
      <p>
        You are responsible for maintaining the confidentiality of your account
        credentials and API keys and for all activity that occurs under them. You must
        provide accurate registration information, be at least 18 years old, and keep
        your account details current. Notify us promptly at{" "}
        <a href="mailto:support@captapi.com">support@captapi.com</a> of any
        unauthorized use.
      </p>

      <h2>4. Acceptable Use</h2>
      <p>
        Your use of the Service must comply at all times with our{" "}
        <Link href="/legal/acceptable-use">Acceptable Use Policy</Link>. In summary,
        you agree that you will not use the Service to access non-public content,
        circumvent access controls or rate limits, infringe intellectual property,
        process personal data unlawfully, surveil or harm individuals, or use the
        output in any way that is illegal or that violates the rights of others. You
        are solely responsible for how you use the data you retrieve and for ensuring
        that your use complies with all applicable laws and the terms of any platform
        you interact with.
      </p>

      <h2>5. Credits &amp; Billing</h2>
      <p>
        The Service uses a credit-based, pre-paid pricing model. Subscription credits
        reset each billing period; separately purchased top-up credits do not expire.
        Failed requests (e.g., 4xx or 5xx responses) do not consume credits. Prices
        are shown at checkout. Payments are handled by Paddle.com Market Ltd, our
        merchant-of-record payment provider, which acts as the seller of record,
        processes your payment, and handles applicable taxes. You may cancel a paid subscription at any time from
        the dashboard; cancellation takes effect at the end of the current billing
        period and stops future renewals.
      </p>

      <h2>6. Refunds</h2>
      <p>
        Refunds are governed by our <Link href="/legal/refund">Refund Policy</Link>.
        Because credits are a digital product delivered immediately, refunds are
        generally limited to the situations described there (including any mandatory
        statutory withdrawal rights that apply to you).
      </p>

      <h2>7. Service Availability</h2>
      <p>
        We strive for high availability but do not guarantee uninterrupted service.
        The Service depends on third-party infrastructure and on the continued public
        availability of content on source platforms, which can change without notice.
        We are not liable for downtime or data gaps caused by upstream providers or by
        changes on source platforms.
      </p>

      <h2>8. Intellectual Property</h2>
      <p>
        The public information returned by the Service is provided as-is; we do not
        claim ownership of it, and you are responsible for having any rights necessary
        for your intended use of it. We retain all rights to the Captapi software,
        API, brand, and documentation. You may not resell, sublicense, or redistribute
        raw Captapi API access as a standalone substitute for the Service, or build a
        product whose primary purpose is to replicate the Service.
      </p>

      <h2>9. Compliance &amp; Takedowns</h2>
      <p>
        We respect intellectual property and privacy rights. If you believe content
        made available through the Service infringes your rights or should not be
        processed, contact us at <a href="mailto:support@captapi.com">support@captapi.com</a>{" "}
        and we will review and act on valid requests, including removing data from our
        cache. We cooperate with lawful requests and reserve the right to restrict
        access to specific data or endpoints to remain compliant.
      </p>

      <h2>10. Indemnification</h2>
      <p>
        You agree to indemnify and hold harmless Captapi and our payment providers from
        any claims, damages, or costs arising out of your use of the Service or your
        breach of these Terms, including any claim related to how you use, store, or
        redistribute data you retrieve.
      </p>

      <h2>11. Disclaimer &amp; Limitation of Liability</h2>
      <p>
        The Service is provided &quot;as is&quot; and &quot;as available&quot; without
        warranties of any kind. To the maximum extent permitted by law, Captapi&apos;s
        total liability for any claim arising from the Service is limited to the amount
        you paid for the Service in the 12 months preceding the claim.
      </p>

      <h2>12. Termination</h2>
      <p>
        We may suspend or terminate your account for violation of these Terms or the
        Acceptable Use Policy, non-payment, suspected fraud, or abuse of the Service.
        You may close your account at any time from the dashboard.
      </p>

      <h2>13. Changes to These Terms</h2>
      <p>
        We may update these Terms periodically. Material changes will be communicated
        via email or in-app notification. Continued use after changes take effect means
        you accept the updated Terms.
      </p>

      <h2>14. Contact</h2>
      <p>
        Questions about these Terms? Email{" "}
        <a href="mailto:support@captapi.com">support@captapi.com</a>.
      </p>
    </article>
  );
}
