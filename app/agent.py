import requests
from app.gemini_client import gemini_generate

# Define the intelligence fields
DETAILS_MAPPING = {
    "bankAccounts": "bank account",
    "upiIds": "UPI ID",
    "phoneNumbers": "phone number",
    "phishingLinks": "links",
    "suspiciousKeywords": "suspicious keyword"
}

GUVI_ENDPOINT = "https://guvi-endpoint.example/api/report"  # replace with actual endpoint

def agent_reply(session):
    """
    Progressive and rule-based agent reply generator
    """
    history = session.get("messages", [])
    total_messages = len(history)

    # Initialize intelligence collection if not present
    if "collected_details" not in session:
        session["collected_details"] = {k: [] for k in DETAILS_MAPPING.keys()}

    collected_details = session["collected_details"]

    # Build conversation context (last 6 messages)
    convo = ""
    for m in history[-6:]:
        convo += f"{m.get('sender','user').upper()}: {m.get('text','')}\n"

    # Determine missing details
    missing_details = [k for k, v in DETAILS_MAPPING.items() if not collected_details[k]]

    # -------- Decide Agent Phase --------
    if total_messages < 3:
        # Early conversation: stay casual
        phase = "PASSIVE"
        system_prompt = """
You are a normal person having a casual conversation.
Respond naturally, engage the sender, and keep it short (1–2 sentences).
Do NOT ask for any sensitive details yet.
"""
    elif missing_details:
        # Progressive detail extraction: ask one missing detail at a time
        phase = "EXTRACTING"
        detail_key = missing_details[0]
        detail_name = DETAILS_MAPPING[detail_key]
        system_prompt = f"""
You are going to collect the {detail_name} from the sender.
Do it casually as part of the conversation. Do NOT mention scams or police.
Keep your reply short (1–2 sentences) and realistic.
"""
    else:
        # No missing details left, polite ending
        phase = "DONE"
        system_prompt = """
Now you have done your job. Politely end the conversation.
Thank the sender and say you won't be able to proceed further.
"""
    
    # -------- Build final prompt for Gemini --------
    prompt = f"""
Reply only in English.

{system_prompt}

IMPORTANT RULES:
- Never accuse the sender of scam
- Never mention police, cybercrime, or fraud
- Keep replies short, human, and realistic

Conversation:
{convo}

Reply as USER:
"""

    # Generate agent reply
    reply = gemini_generate(prompt)

    # -------- Extract details from reply (simple keyword check) --------
    if reply:
        # Try to detect detail mentions (basic)
        for key, name in DETAILS_MAPPING.items():
            if name.lower() in reply.lower() and reply not in collected_details[key]:
                collected_details[key].append(reply.strip())

        session["collected_details"] = collected_details
        session["agentPhase"] = phase

    # -------- Check if final payload should be sent --------
    if should_send_final_payload(session):
    final_payload = build_final_payload(session)
    print("→ FINAL GUVI PAYLOAD:", final_payload)  # << this is what GUVI will receive
    try:
        requests.post(GUVI_ENDPOINT, json=final_payload, timeout=5)
    except Exception as e:
        print("Error sending final payload:", e)
    session["agentPhase"] = "DONE"


    return reply.strip()[:250] if reply else "Can you explain what this is about?"


# -------- Helper functions --------

def should_send_final_payload(session):
    """
    Send final payload only if:
    1. Scam detected
    2. Sufficient engagement (>=8 messages)
    3. At least one detail collected
    """
    enough_messages = len(session.get("messages", [])) >= 8
    has_details = any(session.get("collected_details", {}).values())
    scam_confirmed = session.get("scamDetected", False)
    return scam_confirmed and enough_messages and has_details


def build_final_payload(session):
    """
    Construct GUVI endpoint payload
    """
    collected = session.get("collected_details", {})
    payload = {
        "sessionId": session.get("sessionId", ""),
        "scamDetected": session.get("scamDetected", False),
        "totalMessagesExchanged": len(session.get("messages", [])),
        "extractedIntelligence": {
            "bankAccounts": collected.get("bankAccounts", []),
            "upiIds": collected.get("upiIds", []),
            "phishingLinks": collected.get("phishingLinks", []),
            "phoneNumbers": collected.get("phoneNumbers", []),
            "suspiciousKeywords": collected.get("suspiciousKeywords", [])
        },
        "agentNotes": session.get("agentNotes", "")
    }
    return payload
