from app.services.bhasha_shield import detect_language


tests = [
    "I received a suspicious bank message.",
    "मुझे एक संदिग्ध बैंक संदेश मिला।",
    "मला एक संशयास्पद बँक संदेश आला.",
    "mujhe OTP share karna chahiye kya?",
    "mi kay karu?",
]


for text in tests:
    result = detect_language(text)

    print("\nINPUT:", text)
    print("RESULT:", result)