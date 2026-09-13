from pathlib import Path

import re

from typing import Any, Dict, List


# ==============================================================
# KNOWLEDGE BASE LOCATION
# ==============================================================

# Project structure:
#
# BhashaShield/
# ├── knowledge/
# │   ├── banking_safety.md
# │   └── document_guidance.md
# │
# └── backend/
#     └── app/
#         └── services/
#
# Therefore, parents[3] points to the project root.

PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]

KNOWLEDGE_DIR = (
    PROJECT_ROOT / "knowledge"
)


# ==============================================================
# STOPWORDS
# ==============================================================

# Common words that do not provide useful retrieval evidence.

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "being",
    "by",
    "can",
    "could",
    "did",
    "do",
    "does",
    "for",
    "from",
    "had",
    "has",
    "have",
    "he",
    "her",
    "here",
    "him",
    "his",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "me",
    "my",
    "of",
    "on",
    "or",
    "our",
    "she",
    "so",
    "someone",
    "that",
    "the",
    "their",
    "them",
    "there",
    "these",
    "they",
    "this",
    "those",
    "to",
    "up",
    "us",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "will",
    "with",
    "would",
    "you",
    "your",

    # Technical / URL terms
    "http",
    "https",
    "www",
    "com",
    "org",
    "source",
    "use",
    "using",
    "not",
}


# ==============================================================
# TOKENIZATION
# ==============================================================

def _tokenize(
    text: str,
) -> set[str]:
    """
    Convert text into meaningful retrieval tokens.

    URLs are normalized so that protocol/domain fragments
    do not become strong retrieval signals.
    """

    text = text.lower()

    # Remove URL protocols.
    text = re.sub(
        r"https?://",
        " ",
        text,
    )

    # Remove common URL punctuation.
    text = re.sub(
        r"[./:_?=&%#\-]",
        " ",
        text,
    )

    # Extract English + Devanagari tokens.
    tokens = re.findall(
        r"[a-zA-Z0-9\u0900-\u097F]+",
        text,
    )

    return {
        token
        for token in tokens
        if token not in STOPWORDS
        and len(token) > 1
    }


# ==============================================================
# CHUNKING
# ==============================================================

def _split_markdown_sections(
    content: str,
) -> List[Dict[str, str]]:
    """
    Split a Markdown knowledge file into useful sections.

    Supports both:

    1. Explicit chunks:
       ## Chunk: OTP Safety

    2. Normal Markdown headings:
       ## Official Notice Guidance

    3. A file without section headings:
       entire file becomes one chunk.
    """

    content = content.strip()

    if not content:
        return []

    # ----------------------------------------------------------
    # Explicit ## Chunk: format
    # ----------------------------------------------------------

    if re.search(
        r"(?im)^##\s+Chunk\s*:",
        content,
    ):

        sections = re.split(
            r"(?im)^##\s+Chunk\s*:\s*",
            content,
        )

        chunks = []

        for section in sections:

            section = section.strip()

            if not section:
                continue

            lines = section.splitlines()

            title = lines[0].strip()

            body = "\n".join(
                lines[1:]
            ).strip()

            if not body:
                body = title

            chunks.append(
                {
                    "title": title,
                    "content": body,
                }
            )

        return chunks

    # ----------------------------------------------------------
    # Normal Markdown ## headings
    # ----------------------------------------------------------

    if re.search(
        r"(?im)^##\s+",
        content,
    ):

        sections = re.split(
            r"(?im)^##\s+",
            content,
        )

        chunks = []

        for section in sections:

            section = section.strip()

            if not section:
                continue

            lines = section.splitlines()

            title = lines[0].strip()

            body = "\n".join(
                lines[1:]
            ).strip()

            if not body:
                body = title

            chunks.append(
                {
                    "title": title,
                    "content": body,
                }
            )

        return chunks

    # ----------------------------------------------------------
    # No headings
    # ----------------------------------------------------------

    lines = content.splitlines()

    title = lines[0].strip()

    body = "\n".join(
        lines[1:]
    ).strip()

    if not body:
        body = title

    return [
        {
            "title": title,
            "content": body,
        }
    ]


# ==============================================================
# LOAD KNOWLEDGE
# ==============================================================

def _load_chunks() -> List[Dict[str, str]]:
    """
    Load trusted knowledge-base chunks from Markdown files.

    README.md is intentionally excluded because it contains
    project documentation rather than trusted domain knowledge.
    """

    chunks: List[Dict[str, str]] = []

    if not KNOWLEDGE_DIR.exists():
        return chunks

    # Sort files to make retrieval order deterministic.
    for file_path in sorted(
        KNOWLEDGE_DIR.glob("*.md")
    ):

        # ------------------------------------------------------
        # Never treat README as domain knowledge.
        # ------------------------------------------------------

        if file_path.name.lower() == "readme.md":
            continue

        try:

            content = file_path.read_text(
                encoding="utf-8"
            )

        except Exception:
            continue

        sections = (
            _split_markdown_sections(
                content
            )
        )

        for section in sections:

            title = section[
                "title"
            ].strip()

            body = section[
                "content"
            ].strip()

            if not title and not body:
                continue

            chunks.append(
                {
                    "title": title,
                    "content": body,
                    "source_file": (
                        file_path.name
                    ),
                }
            )

    return chunks


# ==============================================================
# SCORE CHUNK
# ==============================================================

def _score_chunk(
    query_tokens: set[str],
    chunk: Dict[str, str],
) -> Dict[str, Any]:
    """
    Score one knowledge chunk.

    Scoring:

    Title match  = 3 points
    Body match   = 1 point

    Additional domain-specific boosts are applied when the
    knowledge title strongly matches the user's intent.
    """

    title_tokens = _tokenize(
        chunk["title"]
    )

    content_tokens = _tokenize(
        chunk["content"]
    )

    title_overlap = (
        query_tokens.intersection(
            title_tokens
        )
    )

    content_overlap = (
        query_tokens.intersection(
            content_tokens
        )
    )

    # ----------------------------------------------------------
    # Base score
    # ----------------------------------------------------------

    score = (
        len(title_overlap) * 3
        + len(content_overlap)
    )

    # ----------------------------------------------------------
    # Domain-specific relevance boosts
    # ----------------------------------------------------------

    query_lower = " ".join(
        sorted(query_tokens)
    )

    title_lower = chunk[
        "title"
    ].lower()

    # Document-related query.
    document_terms = {
        "document",
        "documents",
        "notice",
        "deadline",
        "application",
        "submission",
        "submit",
        "requirement",
        "requirements",
        "certificate",
        "form",
    }

    # Safety-related query.
    safety_terms = {
        "otp",
        "scam",
        "fraud",
        "phishing",
        "bank",
        "transaction",
        "password",
        "cvv",
        "pin",
        "kyc",
        "payment",
    }

    query_has_document_terms = bool(
        query_tokens.intersection(
            document_terms
        )
    )

    query_has_safety_terms = bool(
        query_tokens.intersection(
            safety_terms
        )
    )

    title_has_document_terms = bool(
        _tokenize(title_lower).intersection(
            document_terms
        )
    )

    title_has_safety_terms = bool(
        _tokenize(title_lower).intersection(
            safety_terms
        )
    )

    if (
        query_has_document_terms
        and title_has_document_terms
    ):

        score += 5

    if (
        query_has_safety_terms
        and title_has_safety_terms
    ):

        score += 5

    # ----------------------------------------------------------
    # Source-specific relevance
    # ----------------------------------------------------------

    source_file = (
        chunk.get(
            "source_file",
            "",
        )
        .lower()
    )

    if (
        query_has_document_terms
        and "document_guidance"
        in source_file
    ):

        score += 8

    if (
        query_has_safety_terms
        and "banking_safety"
        in source_file
    ):

        score += 8

    # ----------------------------------------------------------
    # Matched terms
    # ----------------------------------------------------------

    matched_terms = sorted(
        title_overlap.union(
            content_overlap
        )
    )

    return {
        **chunk,
        "score": score,
        "matched_terms": matched_terms,
    }


# ==============================================================
# RETRIEVE
# ==============================================================

def retrieve(
    query: str,
    top_k: int = 3,
) -> Dict[str, Any]:
    """
    Retrieve the most relevant trusted knowledge chunks.

    Retrieval is lightweight and explainable.

    It uses:
        - meaningful token matching
        - title weighting
        - domain relevance
        - trusted source weighting
    """

    # ----------------------------------------------------------
    # Query validation
    # ----------------------------------------------------------

    query_tokens = _tokenize(
        query
    )

    if not query_tokens:

        return {
            "success": False,
            "tool_name": "safety_rag",
            "summary": (
                "No meaningful retrieval "
                "terms were found."
            ),
            "data": {
                "results": [],
            },
        }

    # ----------------------------------------------------------
    # Load knowledge
    # ----------------------------------------------------------

    chunks = _load_chunks()

    if not chunks:

        return {
            "success": False,
            "tool_name": "safety_rag",
            "summary": (
                "No knowledge-base documents "
                "were found."
            ),
            "data": {
                "results": [],
            },
        }

    # ----------------------------------------------------------
    # Score chunks
    # ----------------------------------------------------------

    scored_chunks: List[
        Dict[str, Any]
    ] = []

    for chunk in chunks:

        scored = _score_chunk(
            query_tokens,
            chunk,
        )

        if scored["score"] > 0:

            scored_chunks.append(
                scored
            )

    # ----------------------------------------------------------
    # Sort
    # ----------------------------------------------------------

    scored_chunks.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    # ----------------------------------------------------------
    # Top results
    # ----------------------------------------------------------

    results = scored_chunks[
        :top_k
    ]

    # ----------------------------------------------------------
    # Response
    # ----------------------------------------------------------

    return {
        "success": bool(results),
        "tool_name": "safety_rag",
        "summary": (
            f"Retrieved {len(results)} "
            "relevant knowledge chunks."
            if results
            else
            "No relevant knowledge was found."
        ),
        "data": {
            "results": results,
        },
    }