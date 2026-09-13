import re
from typing import Dict


DEVANAGARI_RANGE = re.compile(r"[\u0900-\u097F]")


MARATHI_WORDS = {
    "मी",
    "मला",
    "माझा",
    "माझी",
    "माझे",
    "काय",
    "कसे",
    "कशी",
    "करू",
    "करायचे",
    "आहे",
    "आहेत",
    "नाही",
    "आला",
    "आली",
    "आले",
    "संदेश",
    "कागदपत्र",
    "अर्ज",
    "महाविद्यालय",
    "शुल्क",
    "मुदत",
    "बँक",
    "खाते",
}

HINDI_WORDS = {
    "मैं",
    "मुझे",
    "मेरा",
    "मेरी",
    "मेरे",
    "क्या",
    "कैसे",
    "कैसी",
    "करूं",
    "करना",
    "है",
    "हैं",
    "नहीं",
    "आया",
    "आई",
    "आए",
    "संदेश",
    "दस्तावेज",
    "आवेदन",
    "कॉलेज",
    "बैंक",
    "खाता",
}

ROMAN_MARATHI_WORDS = {
    "mi",
    "mala",
    "majha",
    "majhi",
    "majhe",
    "maza",
    "maze",
    "kay",
    "kasa",
    "kashi",
    "kasay",
    "karu",
    "karaycha",
    "karaychi",
    "karayche",
    "ahe",
    "aahe",
    "nahi",
    "aala",
    "aali",
    "aale",
    "mala",
    "tumhi",
    "tumcha",
    "tumchi",
    "tumche",
    "apan",
    "aplya",
    "majhyakade",
    "kuthe",
    "kadhi",
    "ka",
    "kaay",
    "sanga",
    "sang",
    "pahije",
    "pahije",
    "shakto",
    "shakte",
    "shakat",
    "karu",
    "ghya",
    "ghene",
    "dya",
    "dyaycha",
}


ROMAN_HINDI_WORDS = {
    "main",
    "mujhe",
    "mera",
    "meri",
    "mere",
    "mujhko",
    "kya",
    "kaise",
    "kaisi",
    "kaisa",
    "karu",
    "karna",
    "karni",
    "karne",
    "hai",
    "hain",
    "nahi",
    "nahin",
    "mila",
    "mujhe",
    "aaya",
    "aayi",
    "aaye",
    "tum",
    "tumhe",
    "tumhara",
    "tumhari",
    "tumhare",
    "apna",
    "apni",
    "apne",
    "kahan",
    "kab",
    "kyun",
    "kyon",
    "batao",
    "bata",
    "chahiye",
    "sakta",
    "sakti",
    "sakte",
    "karna",
    "lo",
    "lena",
    "do",
}


def _words(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z\u0900-\u097F]+", text.lower()))


def detect_language(
    text: str,
    preferred_language: str = "English",
) -> Dict:
    """
    Lightweight multilingual language understanding layer.

    Supports:
    English, Hindi, Marathi and Hinglish/Roman input.

    Handles:
    - Native Hindi/Marathi
    - Roman Hindi
    - Roman Marathi
    - Code-mixed English + Hindi/Marathi
    - Short conversational follow-ups
    """

    text_lower = text.lower().strip()
    words = _words(text)

    devanagari_count = len(
        DEVANAGARI_RANGE.findall(text)
    )

    # ================================================================
    # NATIVE DEVANAGARI
    # ================================================================

    marathi_score = len(
        words & MARATHI_WORDS
    )

    hindi_score = len(
        words & HINDI_WORDS
    )

    if devanagari_count > 0:

        if marathi_score > hindi_score:
            return {
                "language": "Marathi",
                "script": "Devanagari",
                "mode": "native",
                "confidence": min(
                    0.98,
                    0.70 + marathi_score * 0.06,
                ),
            }

        if hindi_score > marathi_score:
            return {
                "language": "Hindi",
                "script": "Devanagari",
                "mode": "native",
                "confidence": min(
                    0.98,
                    0.70 + hindi_score * 0.06,
                ),
            }

    # ================================================================
    # ROMAN MARATHI
    # ================================================================

    # Existing dictionary evidence
    roman_marathi_score = len(
        words & ROMAN_MARATHI_WORDS
    )

    # Strong conversational Marathi markers.
    #
    # These are checked using substring/phrase matching because
    # users frequently type Marathi in many spellings:
    #
    # majhyakade / mazyakade / mazya kade
    # mala / mi / majha / majhi
    # nahi / nahiye
    # kay karu
    # pahije / aahe / ahe / ata
    #

    roman_marathi_markers = [
        "majhyakade",
        "mazyakade",
        "mazhyakade",
        "mazya kade",
        "majha",
        "majhi",
        "majhe",
        "mala",
        "mi",
        "kay karu",
        "kay kara",
        "karu",
        "karnar",
        "kelay",
        "kela",
        "kele",
        "pahije",
        "aahe",
        "ahe",
        "ata",
        "tumcha",
        "tumchi",
        "tumche",
        "tumhala",
        "tumhi",
        "ghya",
        "kara",
        "karaycha",
        "karaychi",
        "karayche",
    ]

    roman_marathi_hits = [
        marker
        for marker in roman_marathi_markers
        if marker in text_lower
    ]

    # Strong Marathi ownership / absence pattern:
    # "Majhyakade college ID nahi"
    strong_marathi_absence = (
        any(
            marker in text_lower
            for marker in [
                "majhyakade",
                "mazyakade",
                "mazhyakade",
                "mazya kade",
                "mala",
            ]
        )
        and any(
            marker in text_lower
            for marker in [
                "nahi",
                "nahiye",
                "nahiyet",
            ]
        )
    )

    # Strong Marathi conversational pattern:
    # "mi kay karu ata?"
    strong_marathi_question = (
        "kay karu" in text_lower
        or "kay kara" in text_lower
    )

    if (
        roman_marathi_score >= 2
        or strong_marathi_absence
        or strong_marathi_question
        or len(roman_marathi_hits) >= 2
    ):
        return {
            "language": "Marathi",
            "script": "Latin",
            "mode": "Roman",
            "confidence": min(
                0.96,
                0.78
                + max(
                    roman_marathi_score,
                    len(roman_marathi_hits),
                ) * 0.05,
            ),
        }

    # ================================================================
    # ROMAN HINDI
    # ================================================================

    roman_hindi_score = len(
        words & ROMAN_HINDI_WORDS
    )

    roman_hindi_markers = [
        "mere paas",
        "mere pass",
        "mujhe",
        "mujhko",
        "mera",
        "meri",
        "mere",
        "humara",
        "hamara",
        "aapka",
        "aapki",
        "aapko",
        "aap",
        "kya karu",
        "kya kare",
        "karna hai",
        "karna",
        "chahiye",
        "abhi",
        "nahi",
        "nahin",
        "hai",
        "hain",
        "tha",
        "thi",
        "the",
    ]

    roman_hindi_hits = [
        marker
        for marker in roman_hindi_markers
        if marker in text_lower
    ]

    strong_hindi_absence = (
        any(
            marker in text_lower
            for marker in [
                "mere paas",
                "mere pass",
                "mujhe",
                "mujhko",
            ]
        )
        and any(
            marker in text_lower
            for marker in [
                "nahi",
                "nahin",
            ]
        )
    )

    strong_hindi_question = (
        "kya karu" in text_lower
        or "kya kare" in text_lower
    )

    if (
        roman_hindi_score >= 2
        or strong_hindi_absence
        or strong_hindi_question
        or len(roman_hindi_hits) >= 3
    ):
        return {
            "language": "Hindi",
            "script": "Latin",
            "mode": "Roman",
            "confidence": min(
                0.96,
                0.78
                + max(
                    roman_hindi_score,
                    len(roman_hindi_hits),
                ) * 0.05,
            ),
        }

    # ================================================================
    # CODE-MIXED ROMAN INPUT
    # ================================================================

    if (
        roman_marathi_score >= 1
        and roman_hindi_score >= 1
    ):
        return {
            "language": "Hinglish / Roman",
            "script": "Latin",
            "mode": "code-mixed",
            "confidence": 0.72,
        }

    # ================================================================
    # PREFERRED LANGUAGE FALLBACK
    # ================================================================

    if preferred_language in {
        "Hindi",
        "Marathi",
    }:
        return {
            "language": preferred_language,
            "script": "Devanagari",
            "mode": "preferred",
            "confidence": 0.55,
        }

    # ================================================================
    # ENGLISH FALLBACK
    # ================================================================

    return {
        "language": "English",
        "script": "Latin",
        "mode": "native",
        "confidence": 0.90,
    }