import re

def extract_intelligence(text: str, intelligence: dict):
    text_l = text.lower()

    # UPI IDs
    upi_matches = re.findall(r'\b[\w.\-]{2,}@[a-z]{2,}\b', text_l)
    intelligence["upiIds"].extend(upi_matches)

    # Phone numbers (more permissive)
    phone_matches = re.findall(
        r'\b(?:\+91[-\s]?)?\d{10}\b',
        text
    )
    intelligence["phoneNumbers"].extend(phone_matches)

    # Links (with or without protocol)
    link_matches = re.findall(
        r'\b(?:https?://|www\.)[^\s]+\b|\b[a-zA-Z0-9.-]+\.(?:com|in|net|org|co)\b',
        text
    )
    intelligence["phishingLinks"].extend(link_matches)

    # Bank account numbers (loose)
    bank_matches = re.findall(r'\b\d{9,18}\b', text)
    intelligence["bankAccounts"].extend(bank_matches)
