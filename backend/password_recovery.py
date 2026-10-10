"""Email delivery helpers for account password recovery."""

import os
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit


class RecoveryConfigurationError(Exception):
    pass


def make_reset_url(request, token, frontend_reset_url=None):
    configured_url = os.getenv("PASSWORD_RESET_URL", "").strip()
    if configured_url:
        parts = urlsplit(configured_url)
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            raise RecoveryConfigurationError("PASSWORD_RESET_URL must be an absolute HTTP or HTTPS URL.")
        if os.getenv("APP_ENV", "").lower() == "production" and parts.scheme != "https":
            raise RecoveryConfigurationError("PASSWORD_RESET_URL must use HTTPS in production.")
        query = parse_qs(parts.query, keep_blank_values=True)
        query["token"] = [token]
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query, doseq=True), ""))

    if os.getenv("APP_ENV", "").lower() == "production":
        raise RecoveryConfigurationError("Set PASSWORD_RESET_URL to the public reset page URL.")
    origin_parts = urlsplit(request.headers.get("Origin", ""))
    candidate = urlsplit(frontend_reset_url or "")
    if (
        origin_parts.scheme != "http"
        or origin_parts.hostname not in {"localhost", "127.0.0.1"}
        or candidate.scheme != "http"
        or candidate.netloc != origin_parts.netloc
        or not candidate.path.endswith("/reset_password.html")
    ):
        raise RecoveryConfigurationError("Set PASSWORD_RESET_URL to your frontend reset page URL.")
    return urlunsplit((candidate.scheme, candidate.netloc, candidate.path, urlencode({"token": token}), ""))


def validate_smtp_configuration():
    host = os.getenv("SMTP_HOST", "").strip()
    sender = os.getenv("SMTP_FROM", os.getenv("SMTP_USERNAME", "")).strip()
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "")
    try:
        port = int(os.getenv("SMTP_PORT", "587"))
    except ValueError as error:
        raise RecoveryConfigurationError("SMTP_PORT must be a number.") from error
    if not 1 <= port <= 65535:
        raise RecoveryConfigurationError("SMTP_PORT must be between 1 and 65535.")
    if not host or not sender:
        raise RecoveryConfigurationError("Set SMTP_HOST and SMTP_FROM to enable email recovery.")
    if bool(username) != bool(password):
        raise RecoveryConfigurationError("Set both SMTP_USERNAME and SMTP_PASSWORD, or leave both blank.")
    return host, port, sender, username, password


def send_reset_email(recipient, username, reset_url):
    host, port, sender, smtp_username, smtp_password = validate_smtp_configuration()
    message = EmailMessage()
    message["Subject"] = "Reset your GitHub Repository Analytics password"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(
        "Hello {},\n\nUse this one-time link to reset your GitHub Repository Analytics password. "
        "It expires in 30 minutes.\n\n{}\n\nIf you did not request this, you can ignore this email."
        .format(username, reset_url)
    )

    context = ssl.create_default_context()
    if port == 465:
        with smtplib.SMTP_SSL(host, port, timeout=20, context=context) as server:
            if smtp_username:
                server.login(smtp_username, smtp_password)
            server.send_message(message)
    else:
        with smtplib.SMTP(host, port, timeout=20) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            if smtp_username:
                server.login(smtp_username, smtp_password)
            server.send_message(message)
