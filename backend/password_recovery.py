"""Email delivery helpers for account password recovery via Resend's HTTPS API."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
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
    """Kept under its historical name because app.py imports this validator."""
    if not os.getenv("RESEND_API_KEY", "").strip():
        raise RecoveryConfigurationError("Set RESEND_API_KEY to enable email recovery.")
    sender = os.getenv("RESEND_FROM_EMAIL", "").strip()
    if not sender or "@" not in sender:
        raise RecoveryConfigurationError("Set RESEND_FROM_EMAIL to an address on a verified sending domain.")
    return sender


def send_reset_email(recipient, username, reset_url):
    sender = validate_smtp_configuration()
    body = (
        "Hello {},\n\nUse this one-time link to reset your GitHub Repository Analytics password. "
        "It expires in 30 minutes.\n\n{}\n\nIf you did not request this, you can ignore this email."
    ).format(username, reset_url)
    payload = json.dumps({
        "from": sender,
        "to": [recipient],
        "subject": "Reset your GitHub Repository Analytics password",
        "text": body,
    }).encode("utf-8")
    request = Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": "Bearer " + os.environ["RESEND_API_KEY"].strip(),
            "Content-Type": "application/json",
            "User-Agent": "GitHubRepositoryAnalytics/1.0",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            if response.status >= 300:
                raise RuntimeError("Email provider rejected the request.")
    except HTTPError as error:
        raise RuntimeError("Email provider rejected the request (HTTP {}).".format(error.code)) from error
    except (URLError, TimeoutError, OSError) as error:
        raise RuntimeError("Could not connect to the email provider.") from error
