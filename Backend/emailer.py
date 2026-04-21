import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import mistune
from dotenv import load_dotenv

from Backend.config import load_config

load_dotenv()

logger = logging.getLogger(__name__)

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# Shared HTML template for email
_EMAIL_TEMPLATE = """
<html>
<body style="font-family: Arial, sans-serif; background-color: #0d1117; color: #c9d1d9; padding: 30px;">
    <div style="max-width: 650px; margin: auto; background-color: #161b22; border-radius: 12px; padding: 30px; border: 1px solid #30363d;">
        <h1 style="color: #58a6ff; font-size: 24px; margin-bottom: 5px;">Orbit Daily Digest</h1>
        <p style="color: #8b949e; font-size: 13px; margin-top: 0;">Last 24 hours of activity</p>
        <hr style="border: 1px solid #30363d; margin: 20px 0;">
        <div style="font-size: 15px; line-height: 1.7; color: #c9d1d9;">
            {body_html}
        </div>
        <hr style="border: 1px solid #30363d; margin: 20px 0;">
        <p style="color: #8b949e; font-size: 12px; text-align: center;">
            Sent by <strong style="color: #58a6ff;">Orbit</strong> &bull; Munaf Studios
        </p>
    </div>
</body>
</html>
"""


def _markdown_to_html(text: str) -> str:
    """Convert Markdown text to styled HTML for email."""
    md = mistune.create_markdown()
    html = md(text)
    # Add some basic styling for email compatibility
    html = html.replace("<h1>", '<h1 style="color: #58a6ff; font-size: 20px;">')
    html = html.replace("<h2>", '<h2 style="color: #58a6ff; font-size: 18px;">')
    html = html.replace("<h3>", '<h3 style="color: #58a6ff; font-size: 16px;">')
    html = html.replace("<strong>", '<strong style="color: #f0ece4;">')
    html = html.replace("<a ", '<a style="color: #58a6ff;" ')
    html = html.replace("<ul>", '<ul style="padding-left: 20px;">')
    html = html.replace("<li>", '<li style="margin-bottom: 4px;">')
    return html


def _build_email_html(digest_text: str) -> str:
    """Build the full HTML email body from digest text."""
    body_html = _markdown_to_html(digest_text)
    return _EMAIL_TEMPLATE.format(body_html=body_html)


# ── Email Channel ──────────────────────────────────────────

def send_digest_email(to_email: str, digest_text: str) -> bool:
    """Send digest via Gmail SMTP. Returns True on success."""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        logger.error("GMAIL_USER or GMAIL_APP_PASSWORD not set in .env")
        return False

    html = _build_email_html(digest_text)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Orbit Daily Digest"
    msg["From"] = GMAIL_USER
    msg["To"] = to_email

    # Plain text fallback
    msg.attach(MIMEText(digest_text, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        logger.info("Digest email sent to %s", to_email)
        return True
    except Exception as e:
        logger.error("Failed to send email: %s", e)
        return False


# ── Slack Channel ──────────────────────────────────────────

def send_digest_slack(digest_text: str) -> bool:
    """Send digest to Slack via webhook. Returns True on success."""
    import requests as req

    config = load_config()
    webhook_url = config.get("slack_webhook_url", "")
    if not webhook_url:
        logger.warning("Slack webhook URL not configured")
        return False

    try:
        # Slack supports markdown-ish formatting in mrkdwn
        payload = {"text": f"*Orbit Daily Digest*\n\n{digest_text}"}
        res = req.post(webhook_url, json=payload, timeout=10)
        res.raise_for_status()
        logger.info("Digest sent to Slack")
        return True
    except Exception as e:
        logger.error("Failed to send to Slack: %s", e)
        return False


# ── Discord Channel ────────────────────────────────────────

def send_digest_discord(digest_text: str) -> bool:
    """Send digest to Discord via webhook. Returns True on success."""
    import requests as req

    config = load_config()
    webhook_url = config.get("discord_webhook_url", "")
    if not webhook_url:
        logger.warning("Discord webhook URL not configured")
        return False

    try:
        payload = {
            "username": "Orbit",
            "embeds": [{
                "title": "Daily Digest",
                "description": digest_text[:4096],  # Discord embed limit
                "color": 0xC9A84C,
            }],
        }
        res = req.post(webhook_url, json=payload, timeout=10)
        res.raise_for_status()
        logger.info("Digest sent to Discord")
        return True
    except Exception as e:
        logger.error("Failed to send to Discord: %s", e)
        return False


# ── Unified Send ───────────────────────────────────────────

def send_digest(to_email: str, digest_text: str) -> dict[str, bool]:
    """Send digest through all configured notification channels.

    Returns a dict of channel -> success status.
    """
    config = load_config()
    channels = config.get("notification_channels", ["email"])

    results: dict[str, bool] = {}

    if "email" in channels:
        results["email"] = send_digest_email(to_email, digest_text)

    if "slack" in channels:
        results["slack"] = send_digest_slack(digest_text)

    if "discord" in channels:
        results["discord"] = send_digest_discord(digest_text)

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_digest = """## Test Digest

**aliii-codes/groq-coding-agent**
- 1 Commit — Add agentic loop by Ali
- 0 Issues
- 0 Pull Requests
"""
    results = send_digest(GMAIL_USER, test_digest)
    print("Results:", results)
