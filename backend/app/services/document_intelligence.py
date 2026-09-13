import re
from typing import Any, Dict, List, Optional


MONTH_PATTERN = (
    r"(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December)"
)

DATE_PATTERNS = [
    rf"\b\d{{1,2}}\s+{MONTH_PATTERN}\s+\d{{4}}\b",
    rf"\b{MONTH_PATTERN}\s+\d{{1,2}},?\s+\d{{4}}\b",
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
    r"\b\d{1,2}\s+[A-Za-z]+\s+\d{2,4}\b",
]


def _first_date(text: str) -> Optional[str]:
    """
    Find the first date-like value in text.
    """
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(0).strip()

    return None


def _clean_line(line: str) -> str:
    """
    Clean numbering and common bullet characters.
    """
    line = line.strip()

    line = re.sub(
        r"^\s*(?:\d+[\.\):]|[-•●▪◦])\s*",
        "",
        line,
    )

    return line.strip()


def _extract_section(
    text: str,
    headings: List[str],
) -> Optional[str]:
    heading_pattern = "|".join(re.escape(h) for h in headings)
    stop_pattern = (
        r"action|instruction|consequence|warning|result|"
        r"submission|important|note|deadline|last\s+date|due\s+date|"
        r"next\s+step|procedure"
    )
    pattern = rf"(?:^|\n)\s*(?:{heading_pattern})\s*[:\-]?\s*(.*?)(?=\n\s*(?:{stop_pattern})\s*[:\-]|\Z)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else None


def _extract_list_items(section_text: str) -> List[str]:
    """
    Convert a requirement section into individual items.
    """

    items: List[str] = []

    for raw_line in section_text.splitlines():
        line = _clean_line(raw_line)

        if not line:
            continue

        # Ignore obvious section headings.
        if re.fullmatch(
            r"(action|instruction|consequence|warning|"
            r"deadline|last date|due date|submission)",
            line,
            re.IGNORECASE,
        ):
            continue

        items.append(line)

    return list(dict.fromkeys(items))


def _extract_inline_requirements(text: str) -> List[str]:
    """
    Detect requirements even when the document does not contain
    a 'Required Documents:' heading.
    """

    requirements: List[str] = []

    patterns = [
        r"(?:applicants?|students?|users?)\s+"
        r"(?:are\s+)?required\s+to\s+"
        r"(?:submit|provide|attach|upload)\s+(.+?)(?:\.|\n|$)",

        r"(?:please|kindly)\s+"
        r"(?:submit|provide|attach|upload)\s+(.+?)(?:\.|\n|$)",

        r"(?:must|should)\s+"
        r"(?:submit|provide|attach|upload)\s+(.+?)(?:\.|\n|$)",
    ]

    for pattern in patterns:
        matches = re.finditer(
            pattern,
            text,
            re.IGNORECASE,
        )

        for match in matches:
            value = match.group(1).strip()

            if value:
                requirements.append(value)

    return list(dict.fromkeys(requirements))


def _extract_action(text: str) -> Optional[str]:
    """
    Detect the main action the user is expected to take.
    """

    # First prefer explicit labelled sections.
    labelled_patterns = [
        r"(?:action|instruction|next\s+step|"
        r"submission|procedure)\s*[:\-]\s*(.+)",
    ]

    for pattern in labelled_patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            value = match.group(1).strip()
            value = value.split("\n")[0].strip()

            if value:
                return value

    # Then detect natural-language instructions.
    natural_patterns = [
        r"(?:applicants?|students?|users?)\s+"
        r"(?:must|should|need\s+to|are\s+required\s+to)\s+"
        r"(.+?)(?:\.|\n|$)",

        r"(?:please|kindly)\s+"
        r"(.+?)(?:\.|\n|$)",

        r"(?:you\s+must|you\s+should|you\s+need\s+to)\s+"
        r"(.+?)(?:\.|\n|$)",
    ]

    for pattern in natural_patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            value = match.group(1).strip()

            if value:
                return value

    return None


def _extract_consequence(text: str) -> Optional[str]:
    """
    Detect explicit and natural-language consequences.
    """

    labelled_patterns = [
        r"(?:consequence|warning|result|penalty|"
        r"important\s+note)\s*[:\-]\s*(.+)",
    ]

    for pattern in labelled_patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            value = match.group(1).strip()
            value = value.split("\n")[0].strip()

            if value:
                return value

    natural_patterns = [
        r"((?:late|failure|failing|missing|not\s+submitting)"
        r".{0,120}"
        r"(?:may|will|could|might|result|accepted|considered)"
        r".{0,150})",

        r"((?:applications?|submissions?)"
        r".{0,100}"
        r"(?:after|beyond|past)"
        r".{0,100}"
        r"(?:will|may|might|could)"
        r".{0,150})",
    ]

    for pattern in natural_patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL,
        )

        if match:
            value = match.group(1).strip()
            value = re.sub(r"\s+", " ", value)

            if value:
                return value

    return None


def _extract_deadline(text: str) -> Optional[str]:
    """
    Detect deadlines from labelled and natural-language statements.
    """

    labelled_patterns = [
        r"(?:last\s+date|deadline|due\s+date|"
        r"closing\s+date|submission\s+deadline)"
        r"\s*[:\-]?\s*("
        + "|".join(DATE_PATTERNS)
        + r")",
    ]

    for pattern in labelled_patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            return match.group(1).strip()

    natural_patterns = [
        r"(?:submit|apply|applications?|registration|"
        r"form|submission)"
        r".{0,100}?"
        r"(?:by|before|no later than|until|on)"
        r"\s*("
        + "|".join(DATE_PATTERNS)
        + r")",

        r"(?:deadline|closes?|ends?|expires?)"
        r".{0,50}?"
        r"("
        + "|".join(DATE_PATTERNS)
        + r")",
    ]

    for pattern in natural_patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL,
        )

        if match:
            return match.group(1).strip()

    return _first_date(text)


def _detect_situation(text: str) -> str:
    """
    Classify the general document situation.
    """

    lower_text = text.lower()

    if (
        "examination" in lower_text
        and "form" in lower_text
    ):
        return "College examination form submission notice"

    if any(
        word in lower_text
        for word in [
            "exam",
            "examination",
            "admit card",
            "hall ticket",
        ]
    ):
        return "Education or examination-related document"

    if any(
        word in lower_text
        for word in [
            "application",
            "applicant",
            "apply",
            "registration",
        ]
    ):
        return "Application or registration-related document"

    if any(
        word in lower_text
        for word in [
            "fee",
            "bill",
            "payment",
            "invoice",
            "amount due",
        ]
    ):
        return "Bill or payment-related document"

    if any(
        word in lower_text
        for word in [
            "bank",
            "account",
            "transaction",
            "otp",
            "kyc",
        ]
    ):
        return "Financial or banking-related document"

    if any(
        word in lower_text
        for word in [
            "notice",
            "notification",
            "circular",
            "announcement",
        ]
    ):
        return "Official notice requiring review"

    return "Uploaded document requiring review"


def extract_document_intelligence(
    text: str,
) -> Dict[str, Any]:

    if not text or not text.strip():
        return {
            "success": False,
            "summary": "No document text available.",
            "data": {},
        }

    clean_text = text.strip()

    # ======================================================
    # DEADLINE
    # ======================================================

    deadline = _extract_deadline(clean_text)

    # ======================================================
    # REQUIRED DOCUMENTS
    # ======================================================

    required_documents: List[str] = []

    required_section = _extract_section(
        clean_text,
        [
            "required documents",
            "documents required",
            "documents to submit",
            "documents to be submitted",
            "documents needed",
            "required certificates",
            "required proofs",
        ],
    )

    if required_section:
        required_documents.extend(
            _extract_list_items(required_section)
        )

    # Natural-language requirements.
    required_documents.extend(
        _extract_inline_requirements(clean_text)
    )

    required_documents = list(
        dict.fromkeys(required_documents)
    )

    # ======================================================
    # ACTION
    # ======================================================

    action = _extract_action(clean_text)

    # ======================================================
    # CONSEQUENCE
    # ======================================================

    consequence = _extract_consequence(clean_text)

    # ======================================================
    # DOCUMENT TYPE / SITUATION
    # ======================================================

    situation = _detect_situation(clean_text)

    # ======================================================
    # IMPORTANT ONLY
    # ======================================================

    important_items: List[str] = []

    if deadline:
        important_items.append(
            f"Deadline: {deadline}"
        )

    if required_documents:
        important_items.append(
            "Required: "
            + ", ".join(required_documents)
        )

    if action:
        important_items.append(
            f"Action: {action}"
        )

    if consequence:
        important_items.append(
            f"Consequence: {consequence}"
        )

    # ======================================================
    # ACTION PLAN
    # ======================================================

    action_plan: List[str] = []

    if required_documents:
        for document in required_documents:
            action_plan.append(
                f"Collect {document}."
            )

    if action:
        action_plan.append(action)

    if deadline:
        action_plan.append(
            f"Complete the required action "
            f"before {deadline}."
        )

    if not action_plan:
        action_plan.append(
            "Review the document carefully "
            "and identify the required next step."
        )

    action_plan = list(
        dict.fromkeys(action_plan)
    )

    # ======================================================
    # CONFIDENCE / EVIDENCE
    # ======================================================

    evidence_count = sum(
        value is not None
        for value in [
            deadline,
            action,
            consequence,
        ]
    )

    if required_documents:
        evidence_count += 1

    if evidence_count >= 3:
        intelligence_confidence = 0.90
    elif evidence_count == 2:
        intelligence_confidence = 0.80
    elif evidence_count == 1:
        intelligence_confidence = 0.65
    else:
        intelligence_confidence = 0.40

    # ======================================================
    # RESULT
    # ======================================================

    return {
        "success": True,
        "summary": (
            "Document intelligence extracted "
            "successfully."
        ),
        "data": {
            "situation": situation,
            "deadline": deadline,
            "required_documents": required_documents,
            "action": action,
            "consequence": consequence,
            "important_items": important_items,
            "action_plan": action_plan,
            "confidence": intelligence_confidence,
        },
    }