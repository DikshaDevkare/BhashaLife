from app.services.life_shield import assess_risk


tests = [
    "Someone is asking me for my OTP to verify my bank account urgently.",
    "I received a suspicious message with a link.",
    "There is an unauthorized transaction in my account.",
    "I received a normal college announcement.",
]


for text in tests:
    result = assess_risk(text)

    print("\n================================")
    print("INPUT:")
    print(text)

    print("\nRISK SCORE:")
    print(result["risk_score"])

    print("RISK LEVEL:")
    print(result["risk_level"])

    print("\nRISK FACTORS:")
    for factor in result["risk_factors"]:
        print("-", factor)

    print("\nCONSEQUENCES:")
    for consequence in result["consequences"]:
        print("-", consequence)

    print("\nPROTECTIVE ACTIONS:")
    for action in result["protective_actions"]:
        print("-", action)

    print("\nCONFIDENCE:")
    print(result["confidence"])