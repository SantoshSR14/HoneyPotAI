from app.gemini_client import gemini_generate

def agent_reply(session: dict) -> str:
    history = session["messages"]
    phase = session.get("agentPhase", "PASSIVE")
    intelligence = session.get("intelligence", {})

    # -------- BUILD CONTEXT --------
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

    # -------- PHASE LOGIC --------

    if phase == "PASSIVE":
        system_prompt = """
You are a normal person who just received a message.
You are unsure if it is genuine.
Ask for clarification casually.
"""
        if session.get("scamDetected"):
            session["agentPhase"] = "CONFIRMED_SCAM"

    elif phase == "CONFIRMED_SCAM":
        system_prompt = """
You are slightly concerned but calm.
Continue the conversation and ask what needs to be done.
"""
        if len(history) >= 4:
            session["agentPhase"] = "EXTRACTING"

    elif phase == "EXTRACTING":
        # 🚨 HARD STOP CONDITION
        if intelligence_found and len(history) > 8:
            session["agentPhase"] = "DONE"

        system_prompt = """
Continue chatting naturally.
Casually ask for any details needed to proceed,
such as UPI ID, phone number, or verification link.
"""

    elif phase == "DONE":
        system_prompt = """
Politely end the conversation.
Thank the sender and say you will handle it later.
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
