import re

def extract_intelligence(text: str, intelligence: dict):
    text_l = text.lower()

    # UPI IDs
    upi_matches = re.findall(r'\b[\w.\-]{2,}@[a-z]{2,}\b', text_l)
    intelligence["upiIds"].extend(upi_matches)

    # Phone numbers (India-focused)
    phone_matches = re.findall(r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b', text)
    intelligence["phoneNumbers"].extend(phone_matches)

    # Links
    link_matches = re.findall(r'https?://[^\s]+', text)
    intelligence["phishingLinks"].extend(link_matches)

    # Bank account (very loose on purpose)
    bank_matches = re.findall(r'\b\d{9,18}\b', text)
    intelligence["bankAccounts"].extend(bank_matches)

    # Keywords
    for k in ["urgent", "verify", "blocked", "suspended"]:
        if k in text_l and k not in intelligence["suspiciousKeywords"]:
            intelligence["suspiciousKeywords"].append(k)
