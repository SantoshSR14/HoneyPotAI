import re
from typing import Dict, Any

MAX_MESSAGES = 20


def agent_reply(session: Dict[str, Any]) -> str:
    """
    Scam honeypot agent.
    - Keeps scammer engaged
    - Extracts intelligence
    - Never crashes
    """

    # -----------------------------
    # HARD INITIALIZATION (CRITICAL)
    # -----------------------------

    session.setdefault("agentPhase", "ENGAGE")
    session.setdefault("scamDetected", False)

    session.setdefault("intelligence", {
        "bankAccounts": [],
        "upiIds": [],
        "phishingLinks": [],
        "phoneNumbers": [],
        "suspiciousKeywords": []
    })

    messages = session.get("messages", [])
    last_message = messages[-1]["text"] if messages else ""
    text_l = last_message.lower()

    intelligence = session["intelligence"]

    # -----------------------------
    # INTELLIGENCE EXTRACTION
    # -----------------------------

    # UPI IDs (example@upi, name@okaxis, etc.)
    upi_matches = re.findall(r'\b[\w.\-]{2,}@[a-z]{2,}\b', text_l)
    intelligence["upiIds"].extend(upi_matches)

    # Phone numbers (India)
    phone_matches = re.findall(r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b', last_message)
    intelligence["phoneNumbers"].extend(phone_matches)

    # URLs (https, http, www, bare domains)
    link_matches = re.findall(
        r'(https?://[^\s]+|www\.[^\s]+|\b[a-zA-Z0-9-]+\.(com|in|net|org)\b)',
        last_message
    )
    intelligence["phishingLinks"].extend(
        [m[0] if isinstance(m, tuple) else m for m in link_matches]
    )

    # Bank account numbers (loose on purpose)
    bank_matches = re.findall(r'\b\d{9,18}\b', last_message)
    intelligence["bankAccounts"].extend(bank_matches)

    # Suspicious keywords
    keywords = ["urgent", "emergency", "help", "transfer", "surgery", "hospital"]
    for k in keywords:
        if k in text_l:
            intelligence["suspiciousKeywords"].append(k)

    # -----------------------------
    # SCAM DETECTION HEURISTIC
    # -----------------------------

    if (
        intelligence["upiIds"]
        or intelligence["phoneNumbers"]
        or intelligence["phishingLinks"]
        or intelligence["bankAccounts"]
    ):
        session["scamDetected"] = True

    # -----------------------------
    # PHASE TRANSITION
    # -----------------------------

    if len(messages) >= MAX_MESSAGES:
        session["agentPhase"] = "DONE"

    # -----------------------------
    # AGENT RESPONSE LOGIC
    # -----------------------------

    if session["agentPhase"] == "DONE":
        return "I am trying to arrange funds. Please wait."

    # Keep scammer talking
    if "money" in text_l or "need" in text_l:
        return "I want to help. Can you tell me where to send the money?"

    if "upi" in text_l or "account" in text_l:
        return "Please share the full details so I don’t make a mistake."

    if "urgent" in text_l:
        return "I understand. I am arranging it now."

    return "Can you explain your situation a bit more?"
