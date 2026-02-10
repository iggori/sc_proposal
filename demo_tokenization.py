"""
Quick demo showing how PII tokenization works in the MVP

Run this to see the concept in action before running the full Streamlit app.
"""

from gateway import AIGateway
from templates import get_template

print("=" * 70)
print("PII TOKENIZATION CONCEPT DEMONSTRATION")
print("=" * 70)

gateway = AIGateway()

# Use the onboarding document extractor (has PII)
config = get_template('onboarding_document_extractor')

user_input = """Onboarding Document
Name: John Smith
Email: john.smith@email.com
Phone: 555-123-4567
IBAN: DE89370400440532013000
Nationality: German
Risk Assessment: Low risk profile"""

print("\n1️⃣  ORIGINAL INPUT:")
print("-" * 70)
print(user_input)

print("\n\n2️⃣  TOKENIZATION (What gets sent to LLM):")
print("-" * 70)
result = gateway.process('onboarding_doc', user_input, config)
print(result['tokenized_input'])

print("\n\n3️⃣  PII VAULT (Stored mapping):")
print("-" * 70)
for token, original in gateway.pii_vault.items():
    print(f"{token} → {original}")

print("\n\n4️⃣  LLM RESPONSE (With tokens):")
print("-" * 70)
import json
print(json.dumps(result['output'], indent=2))

print("\n\n5️⃣  BACKEND OUTPUT (Detokenized - full PII):")
print("-" * 70)
print(json.dumps(result['backend_output'], indent=2))

print("\n\n6️⃣  UI OUTPUT (Masked for privacy):")
print("-" * 70)
print(json.dumps(result['output'], indent=2))

print("\n\n✅ KEY INSIGHT:")
print("-" * 70)
print("• Tokens preserve ability to use PII in backend systems")
print("• LLM never sees raw PII (compliance ✓)")
print("• UI shows masked version (privacy ✓)")
print("• System can still send emails, update records, etc. (functionality ✓)")

print("\n💡 PRODUCTION:")
print("-" * 70)
print("Current: dict storage (self.pii_vault = {})")
print("Production: Redis/DynamoDB + encryption + TTL + access logs")
print("=" * 70)
