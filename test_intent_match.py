msg = "Ürün satmak istiyorum"
msg_lower = msg.lower()

listing_keywords = ["ilan ver", "ilan vereceğim", "satmak istiyorum", "satacağım", "satış yap"]

print(f"Message: '{msg_lower}'")
print(f"\nChecking keywords:")
for keyword in listing_keywords:
    if keyword in msg_lower:
        print(f"✅ MATCH: '{keyword}'")
    else:
        print(f"❌ NO: '{keyword}'")

result = any(keyword in msg_lower for keyword in listing_keywords)
print(f"\nFinal result: {result}")
