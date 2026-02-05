from app.gemini_client import gemini_generate

def agent_reply(session: dict) -> str:
    # ---------------------------
    # SESSION STATE
    # ---------------------------
    history = session.setdefault("messages", [])
    phase = session.setdefault("agentPhase", "PASSIVE")

    intelligence = session.setdefault("intelligence", {
        "upiIds": [],
        "phoneNumbers": [],
        "phishingLinks": [],
        "bankAccounts": [],
        "suspiciousKeywords": []
    })

    scam_detected = session.get("scamDetected", False)

    # ---------------------------
    # HELPER CHECKS
    # ---------------------------
    intelligence_found = any(len(v) > 0 for v in intelligence.values())
    total_messages = len(history)

    # 🔴 HARD STOP CONDITION
    if total_messages >= 7 and intelligence_found:
        session["agentPhase"] = "DONE"

    # ---------------------------
    # BUILD CONTEXT (LAST 6 MSGS)
    # ---------------------------
    convo = ""
    for m in history[-6:]:
        sender = m.get("sender", "user")
        convo += f"{sender.upper()}: {m.get('text','')}\n"

    # ---------------------------
    # WHAT IS STILL MISSING
    # ---------------------------
    missing_items = []
    if not intelligence["upiIds"]:
        missing_items.append("UPI ID")
    if not intelligence["phoneNumbers"]:
        missing_items.append("phone number")
    if not intelligence["phishingLinks"]:
        missing_items.append("verification link")
    if not intelligence["bankAccounts"]:
        missing_items.append("bank account details")

    if missing_items:
        missing_prompt = "Casually try to ask for: " + ", ".join(missing_items) + "."
    else:
        missing_prompt = "You have collected enough information. End the conversation."

    # ---------------------------
    # PHASE LOGIC (EXPLICIT)
    # ---------------------------
    if session["agentPhase"] == "PASSIVE":
        system_prompt = """
You are a normal person who just received a message.
You are unsure if it is genuine.
Ask for clarification casually.
Do not provide any details.
"""
        if scam_detected:
            session["agentPhase"] = "CONFIRMED_SCAM"

    elif session["agentPhase"] == "CONFIRMED_SCAM":
        system_prompt = """
You are slightly concerned but calm.
Continue the conversation naturally.
Ask what needs to be done.
"""
        if total_messages >= 4:
            session["agentPhase"] = "EXTRACTING"

    elif session["agentPhase"] == "EXTRACTING":
        system_prompt = f"""
Continue chatting naturally.
Casually ask for ONE detail needed to proceed.
Do not ask multiple questions.
{missing_prompt}
"""

    elif session["agentPhase"] == "DONE":
        system_prompt = """
Politely end the conversation.
Say you will check later or handle it.
Do not ask any questions.
"""

    # ---------------------------
    # FINAL PROMPT
    # ---------------------------
    prompt = f"""
Reply only in English.

{system_prompt}

IMPORTANT:
- Never accuse the sender
- Never mention scam, police, or fraud
- Behave like a real human

Conversation:
{convo}

Reply as USER:
"""

    reply = gemini_generate(prompt)
    return reply.strip()[:250] if reply else "Okay."
