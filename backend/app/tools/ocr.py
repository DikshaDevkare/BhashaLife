from pathlib import Path
from typing import Any, Dict

from PIL import Image
import pytesseract


def extract_text_from_image(file_path: str) -> Dict[str, Any]:
    """
    Extract text from an image using OCR.

    Returns a structured result so the agent can
    evaluate whether the tool succeeded.
    """

    path = Path(file_path)

    if not path.exists():
        return {
            "success": False,
            "tool_name": "ocr",
            "summary": "Image file was not found.",
            "data": {},
        }

    try:
        image = Image.open(path)

        text = pytesseract.image_to_string(image).strip()

        if not text:
            return {
                "success": False,
                "tool_name": "ocr",
                "summary": "No readable text was detected in the image.",
                "data": {
                    "text": "",
                },
            }

        return {
            "success": True,
            "tool_name": "ocr",
            "summary": "Text successfully extracted from image.",
            "data": {
                "text": text,
            },
        }

    except Exception as error:
        return {
            "success": False,
            "tool_name": "ocr",
            "summary": "OCR processing failed.",
            "data": {
                "error": str(error),
            },
        }