import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Refund Policy — Captapi",
  description:
    "The Captapi Refund Policy — how refunds work for our credit-based, pre-paid social media data API, including statutory withdrawal rights, unused credits, service issues, and how to request a refund.",
  alternates: { canonical: "/legal/refund" },
};

export default function RefundPage() {
  return (
    <article className="container max-w-3xl py-16 prose prose-neutral dark:prose-invert">
      <h1>Refund Policy</h1>
      <p className="text-sm text-muted-foreground">
        Last updated: {new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}
      </p>

      <p>
        This Refund Policy is part of our{" "}
        <Link href="/legal/terms">Terms of Service</Link>. It explains when you can get
        a refund for purchases of Captapi credits and subscriptions. Payments and
        refunds are handled by Paddle.com Market Ltd, our merchant-of-record payment
        provider, which is the seller of record for your purchase.
      </p>

      <h2>1. What You Are Buying</h2>
      <p>
        Captapi is a pre-paid, credit-based digital service. When you subscribe or buy
        top-up credits, you receive access to the API immediately. Because credits are
        a digital product delivered instantly and consumed as you make API calls, they
        are generally non-refundable once used, except as set out below or as required
        by law.
      </p>

      <h2>2. Statutory Withdrawal Rights</h2>
      <p>
        If you are a consumer in a jurisdiction that grants a cooling-off / withdrawal
        period (for example, the EU/UK 14-day right of withdrawal), that right applies.
        Where you begin using the Service (consume credits) during the withdrawal
        period, you acknowledge that performance has begun and your right of withdrawal
        may be reduced in proportion to the credits already used. Unused credits within
        the withdrawal window are fully refundable.
      </p>

      <h2>3. Service Problems</h2>
      <p>
        We want you to be happy with the Service. We will consider a refund of the
        affected amount if:
      </p>
      <ul>
        <li>You were charged in error or double-charged.</li>
        <li>A sustained outage on our side prevented you from using purchased credits.</li>
        <li>You were charged for a subscription renewal you had already cancelled.</li>
      </ul>
      <p>
        Note that failed API requests (4xx/5xx responses) do not consume credits, so
        they do not require a refund. We are not responsible for outcomes caused by
        changes on third-party source platforms.
      </p>

      <h2>4. Subscriptions</h2>
      <p>
        You can cancel a subscription at any time from the dashboard. Cancellation
        stops future renewals and takes effect at the end of the current billing
        period; the current period is generally not pro-rated, and you keep access to
        your remaining credits until it ends.
      </p>

      <h2>5. How to Request a Refund</h2>
      <p>
        Email <a href="mailto:support@captapi.com">support@captapi.com</a> from your
        account email within <strong>14 days</strong> of the charge, including your
        account email and the transaction reference. We aim to respond within 3
        business days. Approved refunds are returned to your original payment method by
        our payment provider; the time to appear on your statement depends on your
        bank.
      </p>

      <h2>6. Chargebacks</h2>
      <p>
        If you believe a charge is wrong, please contact us first — we can almost
        always resolve it faster than a bank dispute. Filing a chargeback without
        contacting us may result in suspension of your account pending review.
      </p>

      <h2>7. Contact</h2>
      <p>
        Questions about refunds? Email{" "}
        <a href="mailto:support@captapi.com">support@captapi.com</a>.
      </p>
    </article>
  );
}
