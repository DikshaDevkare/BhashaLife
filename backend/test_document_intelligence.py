from app.services.document_intelligence import (
    extract_document_intelligence,
)


text = """
COLLEGE EXAMINATION FORM NOTICE

Last Date: 20 September 2026

Required Documents:
1. Student ID
2. Bonafide Certificate
3. Recent Photograph

Action:
Submit the examination form before the deadline.

Consequence:
Late submission may not be accepted.
"""


result = extract_document_intelligence(text)

print("\nDOCUMENT INTELLIGENCE TEST")
print("=" * 50)

print("SUCCESS:")
print(result["success"])

print("\nSUMMARY:")
print(result["summary"])

print("\nDATA:")

data = result["data"]

print("\nSituation:")
print(data["situation"])

print("\nDeadline:")
print(data["deadline"])

print("\nRequired Documents:")
for item in data["required_documents"]:
    print("-", item)

print("\nAction:")
print(data["action"])

print("\nConsequence:")
print(data["consequence"])

print("\nImportant Only:")
for item in data["important_items"]:
    print("-", item)

print("\nAction Plan:")
for item in data["action_plan"]:
    print("-", item)