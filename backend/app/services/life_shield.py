from typing import Any, Dict, List, Optional
import re


# BhashaLife application-level risk bands.
RISK_BANDS = (
    (0, 24, "LOW"),
    (25, 49, "MODERATE"),
    (50, 74, "HIGH"),
    (75, 100, "CRITICAL"),
)


def _risk_level(score: int) -> str:
    score = max(0, min(100, int(score)))
    for low, high, label in RISK_BANDS:
        if low <= score <= high:
            return label
    return "LOW"


def _has_any(text: str, terms: List[str]) -> bool:
    return any(term in text for term in terms)


def assess_risk(
    text: str,
    rag_results: Optional[List[Dict[str, Any]]] = None,
    intent: Optional[str] = None,
    retrieved_knowledge: Optional[List[Dict[str, Any]]] = None,
    url_analysis: Optional[Dict[str, Any]] = None,
    document_insights: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Explainable, application-level risk triage.

    Important design rule:
    document/application guidance must not inherit banking/scam advice
    merely because generic words such as "account", "verify", "submit",
    or "application" appear in a notice.

    This is a risk indicator, not a scientifically validated probability
    or a prediction of future harm.
    """
    text = (text or "").strip()
    lower = text.lower()
    rag_results = rag_results or retrieved_knowledge or []
    url_analysis = url_analysis or {}
    document_insights = document_insights or {}

    # ---------------------------------------------------------------
    # Domain/context detection
    # ---------------------------------------------------------------
    financial = _has_any(
        lower,
        [
            "bank", "banking", "otp", "cvv", "pin", "password",
            "upi", "transaction", "payment", "credit card",
            "debit card", "account blocked", "account will be blocked",
        ],
    )

    credential_request = _has_any(
        lower,
        [
            "otp", "cvv", "pin", "password", "passcode",
            "enter your credentials", "share your otp",
            "share otp", "verification code",
        ],
    )

    urgency = _has_any(
        lower,
        [
            "urgent", "urgently", "immediately", "right now",
            "today", "within minutes", "last chance",
            "will be blocked", "will be suspended", "act now",
            "account will be closed",
        ],
    )

    suspicious_request = _has_any(
        lower,
        [
            "verify your account", "confirm your account",
            "claim reward", "refund", "kyc", "unblock",
            "click this link", "click the link", "login here",
            "send otp", "share otp",
        ],
    )

    external_link = bool(
        re.search(r"https?://", lower)
    ) or bool(url_analysis.get("url"))

    url_red_flags = len(
        url_analysis.get("indicators", []) or []
    ) + len(
        url_analysis.get("suspicious_terms", []) or []
    )

    unauthorized = _has_any(
        lower,
        [
            "unauthorized transaction",
            "unknown transaction",
            "money deducted",
            "money was deducted",
            "someone transferred",
            "i did not make this transaction",
        ],
    )

    # Threat detection deliberately requires threat-like combinations,
    # not isolated words such as "dead" in casual conversation.
    threat_direct = _has_any(
        lower,
        [
            "i will hurt you",
            "i'll hurt you",
            "i will kill you",
            "i'll kill you",
            "i will attack you",
            "i'll attack you",
            "dekh lunga",
            "maar dunga",
            "marunga",
            "tujhe maar",
            "hurt you",
            "kill you",
            "attack you",
            "threaten you",
        ],
    )

    threat_context = _has_any(
        lower,
        [
            "threat", "threatening", "intimidat",
            "physical harm", "come outside", "meet me outside",
        ],
    )

    # Explicit document intent is a strong de-escalating/domain signal.
    is_document = (
        intent == "document_guidance"
        or bool(document_insights)
    )

    # ---------------------------------------------------------------
    # Base score
    # ---------------------------------------------------------------
    score = 0
    factors: List[str] = []
    consequences: List[str] = []
    what_to_do: List[str] = []
    what_not_to_do: List[str] = []

    if is_document:
        # Official notices are not safety threats by default.
        score = 5

        if document_insights.get("deadline"):
            factors.append("A stated deadline is present")
        if document_insights.get("required_documents"):
            factors.append("Required documents are listed")
        if document_insights.get("consequence"):
            factors.append("The document states a consequence for missing the requirement")

        if document_insights.get("consequence"):
            consequences.append(
                "Missing the stated requirement may result in the consequence described in the notice."
            )

        what_to_do.extend(
            [
                "Review the listed requirements.",
                "Complete the required action before the stated deadline, where possible.",
            ]
        )
        what_not_to_do.append(
            "Do not assume an alternative document is accepted unless the issuing authority confirms it."
        )

    elif threat_direct or threat_context:
        score = 52

        if threat_direct:
            score += 14
            factors.append("Direct threat-like language detected")
        if threat_context:
            score += 8
            factors.append("Potential intimidation or escalation context detected")

        consequences.extend(
            [
                "The conflict could escalate if the situation is handled impulsively.",
                "A real-world safety concern may exist depending on the context.",
            ]
        )
        what_to_do.extend(
            [
                "Avoid confronting or meeting the sender alone.",
                "Preserve relevant messages, screenshots, and timestamps.",
                "Tell a trusted person if the situation is escalating.",
            ]
        )
        what_not_to_do.extend(
            [
                "Do not threaten the sender back.",
                "Do not arrange a confrontation.",
            ]
        )

    else:
        # Financial / digital safety signals.
        if financial:
            score += 20
            factors.append("Financial or banking context detected")

        if credential_request:
            score += 30
            factors.append("Request for sensitive credentials or verification information detected")

        if urgency:
            score += 18
            factors.append("Urgency or pressure language detected")

        if suspicious_request:
            score += 16
            factors.append("Potential social-engineering or suspicious-request language detected")

        if external_link:
            score += 12
            factors.append("External link or potentially risky online action detected")

        if url_red_flags:
            score += min(15, url_red_flags * 5)
            factors.append("URL contains potentially suspicious structural indicators")

        if unauthorized:
            score += 30
            factors.append("Possible unauthorized financial activity reported")

        # Strong combined pattern.
        if financial and (credential_request or suspicious_request) and urgency and external_link:
            score += 12
            factors.append("Financial context combined with urgency and an external link")

        # Do not let generic RAG retrieval create risk by itself.
        safety_sources = len(rag_results)
        if safety_sources and financial:
            score += min(5, safety_sources)
            factors.append(f"{safety_sources} relevant safety knowledge source(s) retrieved")

        if credential_request or external_link or suspicious_request:
            consequences.extend(
                [
                    "Credentials or sensitive information could be exposed if the request is fraudulent.",
                ]
            )
            what_to_do.extend(
                [
                    "Verify the request through the institution's official channel.",
                    "Pause before taking the requested action.",
                ]
            )
            what_not_to_do.append(
                "Do not enter sensitive information through an unexpected link."
            )

        if unauthorized:
            consequences.append(
                "Unauthorized financial activity may continue if the issue is not reported promptly."
            )
            what_to_do.append(
                "Contact the relevant bank or service provider through a trusted official channel."
            )

    score = max(0, min(100, int(score)))
    level = _risk_level(score)

    # Make the scale behavior explicit and stable.
    confidence = {
        "LOW": 0.72,
        "MODERATE": 0.78,
        "HIGH": 0.86,
        "CRITICAL": 0.92,
    }[level]

    # Keep consequences uncertainty-aware and deduplicated.
    consequences = list(dict.fromkeys(consequences))
    what_to_do = list(dict.fromkeys(what_to_do))[:5]
    what_not_to_do = list(dict.fromkeys(what_not_to_do))[:5]
    factors = list(dict.fromkeys(factors))[:7]

    return {
        "risk_score": score,
        "risk_level": level,
        "risk_factors": factors,
        "consequences": consequences,
        "protective_actions": what_to_do + what_not_to_do,
        "what_to_do": what_to_do,
        "what_not_to_do": what_not_to_do,
        "confidence": confidence,
    }
