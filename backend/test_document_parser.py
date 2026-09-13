from pathlib import Path

from app.tools.document_parser import parse_document


BASE_DIR = Path(__file__).resolve().parent


def print_result(title: str, result: dict):
    print("=" * 50)
    print(title)
    print("=" * 50)
    print("SUCCESS:")
    print(result["success"])
    print("SUMMARY:")
    print(result["summary"])
    print("DATA:")
    print(result["data"])
    print()


# ---------------------------------------------------------
# Test 1: Missing file
# ---------------------------------------------------------

missing_file = BASE_DIR / "does_not_exist.pdf"

result = parse_document(str(missing_file))

print_result(
    "MISSING FILE TEST",
    result,
)


# ---------------------------------------------------------
# Test 2: Unsupported file type
# ---------------------------------------------------------

unsupported_file = BASE_DIR / "sample.docx"

unsupported_file.write_text(
    "This file is intentionally used to test unsupported formats.",
    encoding="utf-8",
)

result = parse_document(str(unsupported_file))

print_result(
    "UNSUPPORTED FILE TEST",
    result,
)


# ---------------------------------------------------------
# Test 3: TXT document
# ---------------------------------------------------------

test_txt = BASE_DIR / "test_document_sample.txt"

test_txt.write_text(
    """
College Examination Form Notice

Last Date: 20 September 2026

Required Documents:
1. Student ID
2. Bonafide Certificate
3. Recent Photograph

Action:
Submit the examination form before the deadline.

Consequence:
Late submission may not be accepted.
""".strip(),
    encoding="utf-8",
)

result = parse_document(str(test_txt))

print_result(
    "TEXT DOCUMENT TEST",
    result,
)


# ---------------------------------------------------------
# Test 4: PDF document
# ---------------------------------------------------------

test_pdf = BASE_DIR / "sample_notice.pdf"

result = parse_document(str(test_pdf))

print_result(
    "PDF DOCUMENT TEST",
    result,
)