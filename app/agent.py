from app.gemini_client import gemini_generate

def agent_reply(session: dict) -> str:
    history = session["messages"]
    phase = session.get("agentPhase", "PASSIVE")
    intelligence = session.setdefault("intelligence", {
        "upiIds": [],
        "phoneNumbers": [],
        "phishingLinks": [],
        "bankAccounts": [],
        "suspiciousKeywords": []
    })

    # -------- BUILD CONTEXT (LAST 6 MESSAGES) --------
    convo = ""
    for m in history[-6:]:
        sender = m.get("sender", "user")
        text = m.get("text", "")
        convo += f"{sender.upper()}: {text}\n"

    # -------- CHECK INTELLIGENCE --------
    intelligence_found = any([
        intelligence.get("upiIds"),
        intelligence.get("phoneNumbers"),
        intelligence.get("phishingLinks"),
        intelligence.get("bankAccounts")
    ])

    # -------- BUILD MEMORY-AWARE PROMPT --------
    missing_items = []
    if not intelligence.get("upiIds"):
        missing_items.append("UPI ID")
    if not intelligence.get("phoneNumbers"):
        missing_items.append("phone number")
    if not intelligence.get("phishingLinks"):
        missing_items.append("any verification link")
    if not intelligence.get("bankAccounts"):
        missing_items.append("bank account details")

    if missing_items:
        missing_prompt = (
            "Casually try to ask for: " + ", ".join(missing_items) + "."
        )
    else:
        missing_prompt = "You have collected all possible intelligence. Politely end the conversation."

    # -------- PHASE LOGIC --------

    if phase == "PASSIVE":
        system_prompt = """
You are a normal person who just received a message.
You are unsure if it is genuine.
Ask for clarification casually without cooperating.
"""
        if session.get("scamDetected"):
            session["agentPhase"] = "CONFIRMED_SCAM"

    elif phase == "CONFIRMED_SCAM":
        system_prompt = """
You are slightly concerned but calm.
Continue the conversation naturally.
"""
        if len(history) >= 4:
            session["agentPhase"] = "EXTRACTING"

    elif phase == "EXTRACTING":
        system_prompt = f"""
Continue chatting naturally.
{missing_prompt}
"""
        # HARD STOP CONDITION
        if intelligence_found and len(history) > 8:
            session["agentPhase"] = "DONE"

    elif phase == "DONE":
        system_prompt = """
Politely end the conversation.
Thank the sender and say you will handle it later.
Do not ask any more questions.
"""

    # -------- FINAL PROMPT --------
    prompt = f"""
Reply only in English.

{system_prompt}

IMPORTANT RULES:
- Never accuse the sender of scam
- Never mention police, cybercrime, or fraud
- Sound human, emotional, and realistic
- Keep replies short (1–2 sentences)

Conversation:
{convo}

Reply as USER:
"""

    reply = gemini_generate(prompt)

    return reply.strip()[:250] if reply else "Can you explain a bit more?"
