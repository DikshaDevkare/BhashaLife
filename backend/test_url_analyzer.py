from app.tools.url_analyzer import analyze_text_for_url


def print_result(title: str, text: str):
    print("=" * 40)
    print(title)
    print("INPUT:")
    print(text)

    result = analyze_text_for_url(text)

    print("\nRESULT:")
    print(result)


print_result(
    "SUSPICIOUS HTTP URL",
    "Your account needs urgent verification: "
    "http://example.com/login/verify",
)

print_result(
    "HTTPS URL",
    "Visit https://example.com for more information.",
)

print_result(
    "NO URL",
    "Someone is asking me for my OTP.",
)