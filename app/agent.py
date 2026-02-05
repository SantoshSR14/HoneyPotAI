from app.gemini_client import gemini_generate

DETAILS_MAPPING = {
    "bankAccounts": "bank account",
    "upiIds": "UPI ID",
    "phoneNumbers": "phone number",
    "phishingLinks": "link",
    "suspiciousKeywords": "reason"
}

def has_any_intelligence(session):
    intel = session.get("intelligence", {})
    return any(len(v) > 0 for v in intel.values())

def should_end_conversation(session):
    """
    END if:
    - 7 or more total messages
    - At least ONE intelligence item extracted
    """
    return (
        len(session.get("messages", [])) >= 7
        and has_any_intelligence(session)
    )

def agent_reply(session):
    history = session.get("messages", [])
    total_messages = len(history)

    # Build recent conversation
    convo = ""
    for m in history[-6:]:
        convo += f"{m['sender'].upper()}: {m['text']}\n"

    # -------- Decide Agent Phase --------
    if total_messages < 3:
        system_prompt = """
You are a normal person responding casually.
Keep replies short and natural.
"""

    elif should_end_conversation(session):
        system_prompt = """
End the conversation naturally.
Sound distracted or unsure.
Do not ask any more questions.
"""

    else:
        # Ask ONLY ONE soft follow-up, not all details
        system_prompt = """
Ask one simple follow-up question.
Keep it vague and human.
Do not ask for sensitive details explicitly.
"""

    # -------- Prompt Gemini --------
    prompt = f"""
Reply only in English.

{system_prompt}

IMPORTANT RULES:
- Never accuse the sender
- Never mention scams, police, or fraud
- Behave like a real human

Conversation:
{convo}

Reply as USER:
"""

    reply = gemini_generate(prompt)
    return reply.strip()[:250] if reply else "Okay."
