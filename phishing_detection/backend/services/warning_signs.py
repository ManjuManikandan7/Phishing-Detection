"""Rule-based warning sign extraction (supports UI regardless of model)."""

import re
from urllib.parse import urlparse

from schemas import WarningSign

URL_PATTERN = re.compile(
    r"https?://[^\s]+|www\.[^\s]+|[a-z0-9-]+\.(?:com|net|org|xyz|top|click|ru|tk|ml|ga|cf|gq|pw|info|biz|online|site|live|shop)(?:/[^\s]*)?",
    re.IGNORECASE,
)

URGENCY = re.compile(
    r"\b(urgent|immediately|act now|limited time|expires|within \d+\s*(hours?|minutes?|days?)|last chance|verify now|suspend|locked|unusual activity)\b",
    re.IGNORECASE,
)
CREDENTIALS = re.compile(
    r"\b(password|otp|one[- ]time|verification code|pin code|login credentials|confirm your account|verify your account|update your (?:password|details))\b",
    re.IGNORECASE,
)
REWARD = re.compile(
    r"\b(free diamonds?|free coins?|free skins?|claim (?:your )?(?:reward|prize|gift)|won (?:a )?prize|congratulations|you(?:'ve| have) won|bonus (?:coins?|diamonds?|gems?))\b",
    re.IGNORECASE,
)
SUSPICIOUS_DOMAIN_HINTS = re.compile(
    r"(bit\.ly|tinyurl|t\.co|goo\.gl|login-secure|account-verify|support-team|paypal-secure|amazon-security)",
    re.IGNORECASE,
)


def _looks_suspicious_url(url: str) -> bool:
    try:
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        parsed = urlparse(url)
        host = (parsed.netloc or "").lower()
        if SUSPICIOUS_DOMAIN_HINTS.search(host + (parsed.path or "")):
            return True
        if host.count("-") >= 2:
            return True
        if re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", host):
            return True
        return False
    except Exception:
        return True


def extract_warning_signs(message: str) -> list[WarningSign]:
    signs: list[WarningSign] = []
    lower = message.lower()

    urls = URL_PATTERN.findall(message)
    suspicious_urls = [u for u in urls if _looks_suspicious_url(u)]
    if urls:
        sev = "high" if suspicious_urls else "medium"
        signs.append(
            WarningSign(
                category="links",
                description=f"Contains {len(urls)} link(s)" + ("; some look suspicious." if suspicious_urls else "."),
                severity=sev,
            )
        )

    if URGENCY.search(message):
        signs.append(
            WarningSign(
                category="urgency",
                description="Uses urgent or threatening language to pressure quick action.",
                severity="high",
            )
        )

    if CREDENTIALS.search(message):
        signs.append(
            WarningSign(
                category="credentials",
                description="Asks for passwords, OTPs, or account verification.",
                severity="high",
            )
        )

    if REWARD.search(message):
        signs.append(
            WarningSign(
                category="gaming_reward",
                description="Promises free in-game currency, skins, or prizes (common in gaming scams).",
                severity="medium" if not CREDENTIALS.search(message) else "high",
            )
        )

    if re.search(r"\b(click here|tap here|follow this link)\b", lower):
        signs.append(
            WarningSign(
                category="call_to_action",
                description="Directs you to click a link without clear official context.",
                severity="medium",
            )
        )

    return signs
