# app/agent.py

import os
from google import genai

DETAILS_LIST = [
    "bank account",
    "upi id",
    "phone number",
    "account details",
    "links"
]

# -----------------------------
# Gemini Client Setup
# -----------------------------
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-1.5-flash"


def agent_reply(session: dict) -> str:
    history = session.get("messages", [])
    collected_details = session.get("collected_details", set())
    total_messages = len(history)

    session.setdefault("agentPhase", "PASSIVE")
    session.setdefault("scamDetected", True)
    session.setdefault(
        "intelligence",
        {
            "bankAccounts": [],
            "upiIds": [],
            "phoneNumbers": [],
            "phishingLinks": [],
            "suspiciousKeywords": []
        }
    )

    # -----------------------------
    # Build conversation context
    # -----------------------------
    convo = ""
    for m in history[-8:]:
        convo += f"{m['sender'].upper()}: {m['text']}\n"

    missing_details = [d for d in DETAILS_LIST if d not in collected_details]

    # -----------------------------
    # Phase decision (UNCHANGED)
    # -----------------------------
    if total_messages >= 20 and collected_details:
        system_prompt = """
You have enough information now.
Politely end the conversation.
Thank them and say you will proceed.
"""
        session["agentPhase"] = "DONE"

    elif missing_details:
        if total_messages < 3:
            system_prompt = """
You are a normal person replying casually.
Do NOT ask for sensitive information yet.
Be natural and calm.
"""
            session["agentPhase"] = "PASSIVE"
        else:
            detail = missing_details[0]
            system_prompt = f"""
You want to understand the situation better.
Casually ask for the {detail}.
Do NOT sound suspicious.
"""
            session["agentPhase"] = "EXTRACTING"

    else:
        system_prompt = """
You have everything you need.
Politely end the conversation.
"""
        session["agentPhase"] = "DONE"

    # -----------------------------
    # Gemini Prompt (LLM CORE)
    # -----------------------------
    prompt = f"""
You are a real human chatting naturally over SMS.
Never reveal you are an AI.
Never accuse the sender.
Never mention scams, police, or security.

SYSTEM INSTRUCTION:
{system_prompt}

Conversation so far:
{convo}

Reply naturally in 1–2 sentences.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        reply = response.text.strip()
    except Exception as e:
        # Hard safety fallback — never crash
        reply = "Okay, can you explain a bit more?"

    # -----------------------------
    # Track collected details (UNCHANGED)
    # -----------------------------
    for d in missing_details:
        if d.lower() in reply.lower():
            collected_details.add(d)

    session["collected_details"] = collected_details

    return reply[:250]
