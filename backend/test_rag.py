from app.services.rag import retrieve


queries = [
    "Someone is asking me for my OTP",
    "I clicked a suspicious bank link",
    "There is an unauthorized transaction in my account",
    "Where can I report cyber financial fraud?",
]


for query in queries:
    print("\n==============================")
    print("QUERY:", query)

    result = retrieve(query)

    print("SUCCESS:", result["success"])
    print("SUMMARY:", result["summary"])

    for item in result["data"]["results"]:
        print("\nCHUNK:", item["title"])
        print("SCORE:", item["score"])
        print("MATCHES:", item["matched_terms"])