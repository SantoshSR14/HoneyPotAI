import re

def extract_intelligence(text, intel):
    intel["upiIds"] += re.findall(r'\b[\w.-]+@upi\b', text)
    intel["phoneNumbers"] += re.findall(r'\+91\d{10}', text)
    intel["phishingLinks"] += re.findall(r'https?://\S+', text)

    for k in ["urgent", "verify", "blocked", "suspended"]:
        if k in text.lower():
            intel["suspiciousKeywords"].append(k)
