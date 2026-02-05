from app.gemini_client import gemini_generate

DETAILS_LIST = ["bank account", "UPI ID", "phone number", "account details", "links"]

def agent_reply(session):
    history = session.get("messages", [])
    total_messages = len(history)

    # 🔹 Use a SET to track collected details
    collected_details = session.setdefault("collected_details", set())

    # -------- BUILD CONTEXT (LAST 6 MESSAGES) --------
    convo = ""
    for m in history[-6:]:
        sender = m.get("sender", "user")
        text = m.get("text", "")
        convo += f"{sender.upper()}: {text}\n"

    # -------- DETECT DETAILS FROM USER MESSAGES --------
    # IMPORTANT: extraction happens from USER replies, not agent replies
    for m in history:
        if m.get("sender") == "scammer":  # scammer is the one giving details
            text = m.get("text", "").lower()
            for detail in DETAILS_LIST:
                if detail.lower() in text:
                    collected_details.add(detail)

    session["collected_details"] = collected_details

    # -------- STOP CONDITION (YOUR RULE) --------
    if total_messages >= 7 and collected_details:
        system_prompt = """
Now you have collected enough details.
Politely end the conversation.
Sound cooperative and natural.
Do NOT ask any more questions.
"""
        session["agentPhase"] = "DONE"

    else:
        # -------- DETERMINE MISSING DETAILS --------
        missing_details = [d for d in DETAILS_LIST if d not in collected_details]

        # -------- PHASE LOGIC --------
        if total_messages < 3:
            # Early conversation
            system_prompt = """
You are a normal person having a casual conversation.
Respond naturally and ask what this is about.
Do NOT ask for any sensitive details yet.
"""
            session["agentPhase"] = "PASSIVE"

        else:
            # Start extracting ONE detail at a time
            detail_to_ask = missing_details[0] if missing_details else "details"
            system_prompt = f"""
You are slightly confused but cooperative.
Casually ask about the {detail_to_ask}.
Do not sound suspicious.
Ask only ONE question.
"""
            session["agentPhase"] = "EXTRACTING"

    # -------- FINAL PROMPT --------
    prompt = f"""
Reply only in English.

{system_prompt}

IMPORTANT RULES:
- Never accuse the sender
- Never mention scam, police, or fraud
- Keep replies short, human, and realistic

Conversation:
{convo}

Reply as USER:
"""

    reply = gemini_generate(prompt)

    return reply.strip()[:250] if reply else "Okay."
