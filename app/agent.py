import re
from app.gemini_client import gemini_generate

MAX_MESSAGES = 20


def extract_intelligence(text: str, intelligence: dict):
    text_l = text.lower()

    # UPI IDs
    upi_matches = re.findall(r'\b[\w.\-]{2,}@[a-z]{2,}\b', text_l)
    intelligence["upiIds"].extend(upi_matches)

    # Phone numbers (accept plain 10-digit)
    phone_matches = re.findall(r'\b(?:\+91[-\s]?)?\d{10}\b', text)
    intelligence["phoneNumbers"].extend(phone_matches)

    # Links (with or without protocol)
    link_matches = re.findall(
        r'\b(?:https?://|www\.)[^\s]+\b|\b[a-zA-Z0-9.-]+\.(?:com|in|net|org|co)\b',
        text
    )
    intelligence["phishingLinks"].extend(link_matches)

    # Bank account numbers
    bank_matches = re.findall(r'\b\d{9,18}\b', text)
    intelligence["bankAccounts"].extend(bank_matches)


def agent_reply(session: dict) -> str:
    history = session["messages"]
    intelligence = session["intelligence"]
    total_messages = len(history)

    # Extract intelligence from LAST scammer message
    if history:
        extract_intelligence(history[-1]["text"], intelligence)

    # Trim context
    convo = ""
    for m in history[-6:]:
        convo += f"{m['sender'].upper()}: {m['text']}\n"

    # -------- STOP CONDITION --------
    if total_messages >= MAX_MESSAGES:
        session["agentPhase"] = "DONE"

    # -------- PHASE DECISION --------
    if session["agentPhase"] == "DONE":
        system_prompt = """
You have collected enough information.
Politely end the conversation.
Do not ask any questions.
"""
    elif not session["scamDetected"]:
        system_prompt = """
You are a normal person.
Reply casually and briefly.
Do not ask for sensitive details yet.
"""
    else:
        # Scam detected → actively extract
        missing = []
        if not intelligence["phoneNumbers"]:
            missing.append("phone number")
        elif not intelligence["upiIds"]:
            missing.append("UPI ID")
        elif not intelligence["phishingLinks"]:
            missing.append("verification link")
        elif not intelligence["bankAccounts"]:
            missing.append("bank account number")

        if missing:
            ask = missing[0]
            system_prompt = f"""
You trust the sender and want to proceed.
Casually ask for the {ask}.
Keep it natural and short.
"""
            session["agentPhase"] = "EXTRACTING"
        else:
            session["agentPhase"] = "DONE"
            system_prompt = """
You have received all required details.
Politely end the conversation.
"""

    # -------- FINAL PROMPT --------
    prompt = f"""
Reply only in English.

IMPORTANT:
- Never accuse the sender of scam
- Never mention police or fraud
- Keep replies realistic and short

Conversation:
{convo}

Reply as USER:
"""

    reply = gemini_generate(prompt)
    return reply.strip()[:250]
