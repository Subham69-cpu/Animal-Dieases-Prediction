"""Send transactional emails (SMTP) with safe fallback to logging."""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app

log = logging.getLogger(__name__)


def send_email(to_addr: str, subject: str, body_text: str) -> bool:
    """Send plain-text email. Returns True if sent or simulated as success in dev."""
    cfg = current_app.config
    if not cfg.get("EMAIL_ENABLED") or not cfg.get("SMTP_HOST"):
        log.info("[email disabled] To=%s Subject=%s\n%s", to_addr, subject, body_text)
        return True
    try:
        msg = MIMEMultipart()
        msg["From"] = cfg.get("SMTP_FROM", "noreply@local")
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg.attach(MIMEText(body_text, "plain"))
        port = int(cfg.get("SMTP_PORT", 587))
        with smtplib.SMTP(cfg["SMTP_HOST"], port, timeout=15) as server:
            server.starttls()
            user = cfg.get("SMTP_USER")
            pw = cfg.get("SMTP_PASSWORD")
            if user and pw:
                server.login(user, pw)
            server.send_message(msg)
        log.info("Email sent to %s: %s", to_addr, subject)
        return True
    except Exception as e:
        log.exception("Email send failed: %s", e)
        return False
