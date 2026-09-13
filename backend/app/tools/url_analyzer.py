import re
from typing import Any, Dict
from urllib.parse import urlparse

import httpx


URL_PATTERN = re.compile(
    r"https?://[^\s<>\"]+",
    re.IGNORECASE,
)


SUSPICIOUS_TERMS = {
    "login",
    "verify",
    "verification",
    "secure",
    "update",
    "account",
    "confirm",
    "otp",
    "kyc",
    "refund",
    "reward",
    "prize",
    "urgent",
}


SHORTENER_DOMAINS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "is.gd",
    "cutt.ly",
    "shorturl.at",
}


def extract_url(text: str) -> str | None:
    match = URL_PATTERN.search(text)

    if not match:
        return None

    return match.group(0).rstrip(".,!?;:)")


def analyze_url(url: str) -> Dict[str, Any]:
    if not url:
        return {
            "success": False,
            "tool_name": "url_analyzer",
            "summary": "No URL was provided.",
            "data": {},
        }

    try:
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            return {
                "success": False,
                "tool_name": "url_analyzer",
                "summary": "The URL uses an unsupported scheme.",
                "data": {
                    "url": url,
                    "scheme": parsed.scheme,
                },
            }

        hostname = (parsed.hostname or "").lower()

        if not hostname:
            return {
                "success": False,
                "tool_name": "url_analyzer",
                "summary": "The URL does not contain a valid hostname.",
                "data": {
                    "url": url,
                },
            }

        indicators = []

        if parsed.scheme != "https":
            indicators.append("URL does not use HTTPS.")

        if "@" in parsed.netloc:
            indicators.append("URL contains an @ symbol in the network location.")

        if hostname in SHORTENER_DOMAINS:
            indicators.append("URL uses a known URL-shortening service.")

        suspicious_term_matches = [
            term
            for term in SUSPICIOUS_TERMS
            if term in url.lower()
        ]

        if suspicious_term_matches:
            indicators.append(
                "URL contains terms commonly associated with account or "
                "verification requests."
            )

        if hostname.count(".") >= 3:
            indicators.append(
                "URL contains an unusually deep subdomain structure."
            )

        http_status = None
        final_url = None
        request_error = None

        try:
            with httpx.Client(
                timeout=5.0,
                follow_redirects=True,
                headers={
                    "User-Agent": "BhashaLifeAI-URL-Analyzer/1.0"
                },
            ) as client:
                response = client.head(url)

                http_status = response.status_code
                final_url = str(response.url)

        except Exception as error:
            request_error = str(error)

        if final_url and final_url != url:
            indicators.append(
                "The URL redirected to a different address."
            )

        if indicators:
            assessment = "Suspicious indicators detected."
        else:
            assessment = (
                "No obvious structural red flags were detected, "
                "but this does not establish that the URL is safe."
            )

        return {
            "success": True,
            "tool_name": "url_analyzer",
            "summary": assessment,
            "data": {
                "url": url,
                "scheme": parsed.scheme,
                "hostname": hostname,
                "path": parsed.path,
                "query_present": bool(parsed.query),
                "https": parsed.scheme == "https",
                "suspicious_terms": suspicious_term_matches,
                "indicators": indicators,
                "http_status": http_status,
                "final_url": final_url,
                "request_error": request_error,
                "verified_safe": False,
            },
        }

    except Exception as error:
        return {
            "success": False,
            "tool_name": "url_analyzer",
            "summary": "URL analysis failed.",
            "data": {
                "url": url,
                "error": str(error),
            },
        }


def analyze_text_for_url(text: str) -> Dict[str, Any]:
    url = extract_url(text)

    if not url:
        return {
            "success": False,
            "tool_name": "url_analyzer",
            "summary": "No URL was found in the provided text.",
            "data": {
                "url": None,
            },
        }

    return analyze_url(url)