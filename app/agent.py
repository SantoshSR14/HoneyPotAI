from app.gemini_client import gemini_generate

# -------------------------------
# Helper checks
# -------------------------------

def has_any_intelligence(session):
    intel = session.get("intelligence", {})
    return any(len(v) > 0 for v in intel.values())


def should_end_conversation(session):
    return (
        len(session.get("messages", [])) >= 7
        and has_any_intelligence(session)
    )


# -------------------------------
# Main agent logic
# -------------------------------

def agent_reply(session):
    messages = session.get("messages", [])
    scam_detected = session.get("scamDetected", False)

    # Build last few messages as context
    convo = ""
    for m in messages[-6:]:
        convo += f"{m['sender'].upper()}: {m['text']}\n"

    # -------------------------------
    # PHASE 3: ENDING
    # -------------------------------
    if should_end_conversation(session):
        system_prompt = """
End the conversation naturally.
Sound distracted, unsure, or busy.
Do NOT ask any questions.
Do NOT request any details.
"""
        prompt = f"""
Reply only in English.

{system_prompt}

Conversation:
{convo}

Reply as USER:
"""
        return gemini_generate(prompt).strip()[:200]

    # -------------------------------
    # PHASE 2: EXTRACTION
    # (only AFTER scam is detected)
    # -------------------------------
    if scam_detected:
        system_prompt = """
You suspect something is wrong.
Casually ask for ONE small clarification that may reveal details.
Do NOT ask multiple questions.
Do NOT sound official or threatening.
"""
        prompt = f"""
Reply only in English.

{system_prompt}

Conversation:
{convo}

Reply as USER:
"""
        return gemini_generate(prompt).strip()[:200]

    # -------------------------------
    # PHASE 1: PASSIVE
    # (before scam detection)
    # -------------------------------
    system_prompt = """
You are a normal person.
Respond casually and keep the conversation going.
Ask neutral questions only.
"""
    prompt = f"""
Reply only in English.

{system_prompt}

Conversation:
{convo}

Reply as USER:
"""
    return gemini_generate(prompt).strip()[:200]
