import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Acceptable Use Policy — Captapi",
  description:
    "The Captapi Acceptable Use Policy — what the API may and may not be used for. Captapi provides access to publicly available information only, and prohibits accessing private data, circumventing access controls, unlawful personal-data processing, surveillance, and other abuse.",
  alternates: { canonical: "/legal/acceptable-use" },
};

export default function AcceptableUsePage() {
  return (
    <article className="container max-w-3xl py-16 prose prose-neutral dark:prose-invert">
      <h1>Acceptable Use Policy</h1>
      <p className="text-sm text-muted-foreground">
        Last updated: {new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}
      </p>

      <p>
        This Acceptable Use Policy (&quot;AUP&quot;) explains what Captapi may and may
        not be used for. It is part of our{" "}
        <Link href="/legal/terms">Terms of Service</Link>. By using the Service you
        agree to this AUP. We may suspend or terminate accounts that violate it.
      </p>

      <h2>1. What Captapi Does</h2>
      <p>
        Captapi is a developer API for retrieving <strong>publicly available
        information</strong> — the same information any person could view in a web
        browser without logging in — and returning it as structured JSON. Typical,
        legitimate uses include:
      </p>
      <ul>
        <li>Market, brand, and competitor research and analytics.</li>
        <li>Social listening, trend discovery, and content planning.</li>
        <li>Creator and influencer discovery, vetting, and reporting.</li>
        <li>Academic, journalistic, and open-source research.</li>
        <li>Powering dashboards, AI agents, and internal tools with public data.</li>
      </ul>

      <h2>2. Public Data Only</h2>
      <p>
        Captapi accesses only information that is publicly accessible without
        authentication and without circumventing any technical protection measure. The
        Service does <strong>not</strong> access, and you may not attempt to use it to
        access:
      </p>
      <ul>
        <li>Private accounts, private posts, direct messages, or friends-only content.</li>
        <li>Password-protected, paywalled, or login-gated content.</li>
        <li>Any content behind an access control, or data obtained by defeating security measures.</li>
      </ul>

      <h2>3. Prohibited Uses</h2>
      <p>You agree not to use the Service, or data obtained through it, to:</p>
      <ul>
        <li>
          <strong>Harm or target individuals</strong> — stalking, harassment, doxxing,
          re-identification of anonymous users, or building profiles used to threaten,
          intimidate, or discriminate against people.
        </li>
        <li>
          <strong>Process personal data unlawfully</strong> — in violation of the GDPR,
          CCPA/CPRA, or other applicable data-protection laws, including using public
          personal data for a purpose the individual would not reasonably expect
          without a lawful basis.
        </li>
        <li>
          <strong>Enable unlawful discrimination</strong> — such as decisions about
          credit, employment, housing, or insurance based on protected characteristics.
        </li>
        <li>
          <strong>Infringe intellectual property</strong> — reproduce or redistribute
          content in violation of copyright, trademark, or database rights.
        </li>
        <li>
          <strong>Send spam or run deceptive campaigns</strong> — unsolicited bulk
          messaging, phishing, fraud, or impersonation.
        </li>
        <li>
          <strong>Circumvent controls</strong> — bypass authentication, rate limits, or
          access restrictions on any platform, or attempt to access non-public data.
        </li>
        <li>
          <strong>Break the law</strong> — any use that is illegal in your jurisdiction
          or that facilitates illegal activity.
        </li>
        <li>
          <strong>Resell or clone the Service</strong> — resell raw API access as a
          standalone substitute for Captapi or build a directly competing data API.
        </li>
      </ul>

      <h2>4. Your Responsibilities</h2>
      <p>
        You are solely responsible for how you use the Service and the data you
        retrieve. You must have a lawful basis for your processing, honor deletion and
        opt-out requests from data subjects, keep appropriate security, and comply with
        the terms of any platform you interact with. If your use requires consent,
        licenses, or approvals, obtaining them is your responsibility.
      </p>

      <h2>5. Enforcement</h2>
      <p>
        We may investigate suspected violations and may suspend or terminate access,
        with or without notice, to protect the Service, our providers, source
        platforms, and the public. We also honor valid takedown and data-removal
        requests — see the Compliance section of our{" "}
        <Link href="/legal/terms">Terms of Service</Link>.
      </p>

      <h2>6. Reporting Abuse</h2>
      <p>
        To report misuse or request removal of specific data, email{" "}
        <a href="mailto:support@captapi.com">support@captapi.com</a>. We review reports
        promptly and act on valid ones.
      </p>
    </article>
  );
}
