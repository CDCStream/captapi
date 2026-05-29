"""Transactional email via Resend's HTTP API."""

from __future__ import annotations

import httpx
import structlog

from app.core.config import get_settings

log = structlog.get_logger(__name__)

RESEND_ENDPOINT = "https://api.resend.com/emails"


def send_email(to: str, subject: str, html: str, *, from_: str | None = None) -> bool:
    """Send an email through Resend. Returns True on success, False otherwise.

    Never raises — email is best-effort and must not break request flows.
    """
    settings = get_settings()
    if not settings.RESEND_API_KEY:
        log.warning("resend_not_configured", to=to)
        return False
    try:
        resp = httpx.post(
            RESEND_ENDPOINT,
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": from_ or settings.EMAIL_FROM,
                "to": [to],
                "subject": subject,
                "html": html,
            },
            timeout=15.0,
        )
        if resp.status_code >= 400:
            log.error("resend_send_failed", status=resp.status_code, body=resp.text)
            return False
        return True
    except Exception as e:  # noqa: BLE001
        log.error("resend_send_error", error=str(e))
        return False


def welcome_email_html(name: str, dashboard_url: str) -> str:
    return f"""\
<!DOCTYPE html>
<html>
  <body style="margin:0;background:#f4f5f7;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="padding:32px 0;">
      <tr><td align="center">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
               style="max-width:480px;background:#ffffff;border-radius:16px;overflow:hidden;border:1px solid #e5e7eb;">
          <tr><td style="padding:32px 32px 0;">
            <span style="font-size:22px;font-weight:800;letter-spacing:-0.02em;color:#0f172a;">
              Capt<span style="color:#2563eb;">api</span>
            </span>
          </td></tr>
          <tr><td style="padding:24px 32px 8px;">
            <h1 style="margin:0;font-size:22px;color:#0f172a;">Welcome aboard, {name} 👋</h1>
          </td></tr>
          <tr><td style="padding:0 32px;color:#475569;font-size:15px;line-height:1.6;">
            <p style="margin:0 0 16px;">
              Your Captapi account is ready. You've got <strong>100 free credits</strong> to start
              pulling structured data from YouTube, TikTok, Instagram &amp; Facebook.
            </p>
            <p style="margin:0 0 24px;">Create an API key and make your first call in under a minute.</p>
          </td></tr>
          <tr><td style="padding:0 32px 8px;">
            <a href="{dashboard_url}"
               style="display:inline-block;background:#2563eb;color:#ffffff;text-decoration:none;
                      padding:12px 22px;border-radius:10px;font-weight:600;font-size:15px;">
              Open your dashboard
            </a>
          </td></tr>
          <tr><td style="padding:24px 32px 32px;color:#94a3b8;font-size:12px;line-height:1.6;">
            <p style="margin:0;">Need help? Just reply to this email.</p>
            <p style="margin:8px 0 0;">— The Captapi team</p>
          </td></tr>
        </table>
      </td></tr>
    </table>
  </body>
</html>"""


def send_welcome_email(to: str, name: str) -> bool:
    settings = get_settings()
    dashboard_url = f"{settings.FRONTEND_URL.rstrip('/')}/dashboard"
    return send_email(
        to,
        "Welcome to Captapi 🎉",
        welcome_email_html(name, dashboard_url),
    )
