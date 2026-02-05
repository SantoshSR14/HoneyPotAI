from app.gemini_client import gemini_generate

# What intelligence we may extract
DETAILS_MAPPING = {
    "bankAccounts": "bank account",
    "upiIds": "UPI ID",
    "phoneNumbers": "phone number",
    "phishingLinks": "link",
    "suspiciousKeywords": "reason"
}

def should_end_conversation(session):
    """
    End conversation if:
    - At least 7 messages exchanged
    - At least one intelligence item collected
    """
    messages_count = len(session.get("messages", []))
    intel = session.get("collected_details", {})

    has_any_intel = any(len(v) > 0 for v in intel.values())
    return messages_count >= 7 and has_any_intel


def agent_reply(session):
    history = session.get("messages", [])
    total_messages = len(history)

    # Initialize collected_details if missing
    if "collected_details" not in session:
        session["collected_details"] = {k: [] for k in DETAILS_MAPPING.keys()}

    collected_details = session["collected_details"]

    # Build recent conversation context
    convo = ""
    for m in history[-6:]:
        convo += f"{m['sender'].upper()}: {m['text']}\n"

    # Determine missing details
    missing_details = [
        k for k in DETAILS_MAPPING
        if not collected_details.get(k)
    ]

    # -------- Decide Agent Phase --------
    if total_messages < 3:
        # Early casual replies
        phase = "PASSIVE"
        system_prompt = """
You are a normal person responding casually.
Keep replies short and natural.
Do not ask sensitive questions yet.
"""

    elif should_end_conversation(session):
        # Stop probing and disengage
        phase = "DONE"
        system_prompt = """
End the conversation naturally.
Sound distracted or unsure.
Do not ask any more questions.
"""

    elif missing_details:
        # Ask for just ONE missing detail
        phase = "EXTRACTING"
        detail_name = DETAILS_MAPPING[missing_details[0]]
        system_prompt = f"""
Casually ask about the {detail_name}.
Do not sound suspicious.
Keep it short and realistic.
"""

    else:
        phase = "DONE"
        system_prompt = """
End the conversation naturally.
"""

    # -------- Final prompt to Gemini --------
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

    # Update session phase
    session["agentPhase"] = phase

    return reply.strip()[:250] if reply else "Okay."
