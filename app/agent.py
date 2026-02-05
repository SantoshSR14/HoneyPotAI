from app.gemini_client import gemini_generate

def agent_reply(session: dict) -> str:
    history = session["messages"]
    phase = session.get("agentPhase", "PASSIVE")
    intelligence = session.get("intelligence", {})

    # -------- BUILD CONTEXT (LAST 6 MESSAGES) --------
    convo = ""
    for m in history[-6:]:
        sender = m.get("sender", "user")
        text = m.get("text", "")
        convo += f"{sender.upper()}: {text}\n"

    # -------- PHASE PROMPTS --------

    if phase == "PASSIVE":
        system_prompt = """
You are a normal person who just received a message.
You are unsure if it is genuine or not.
Ask for clarification naturally without cooperating.
"""
        # RULE: Move only if scam detected elsewhere
        if session.get("scamDetected"):
            session["agentPhase"] = "CONFIRMED_SCAM"

    elif phase == "CONFIRMED_SCAM":
        system_prompt = """
You are slightly concerned but not alarmed.
Continue the conversation casually.
Ask what needs to be done and why.
"""
        # RULE: Move after enough engagement
        if len(history) >= 4:
            session["agentPhase"] = "EXTRACTING"

    elif phase == "EXTRACTING":
        system_prompt = """
You are continuing the conversation naturally.
Casually ask for details such as:
- UPI ID
- bank details
- phone number
- any verification links
Do not sound suspicious or defensive.
"""
        # RULE: Move only if intelligence found
        if any([
            intelligence.get("upiIds"),
            intelligence.get("phoneNumbers"),
            intelligence.get("phishingLinks"),
            intelligence.get("bankAccounts")
        ]):
            session["agentPhase"] = "DONE"

    elif phase == "DONE":
        system_prompt = """
Politely end the conversation.
Thank the sender and say you will take care of it later.
Do not continue asking questions.
"""


    prompt = f"""
Reply only in English.

{system_prompt}

IMPORTANT RULES:
- Never accuse the sender of scam
- Never mention police, cybercrime, fraud, or investigation
- Sound human, emotional, and realistic
- Keep replies short (1–2 sentences)

Conversation:
{convo}

Reply as USER:
"""

    reply = gemini_generate(prompt)

    return reply.strip()[:250] if reply else "Can you explain a bit more?"
