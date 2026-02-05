from app.gemini_client import gemini_generate

# Define possible details to collect
DETAILS_LIST = ["bank account", "UPI ID", "phone number", "account details", "links"]

def agent_reply(session):
    history = session.get("messages", [])
    collected_details = session.get("collected_details", set())
    
    # Build conversation safely (last 6 messages for context)
    convo = ""
    for m in history[-6:]:
        sender = m.get("sender", "user")
        text = m.get("text", "")
        convo += f"{sender.upper()}: {text}\n"

    # Count total messages
    total_messages = len(history)

    # Determine which details are still missing
    missing_details = [d for d in DETAILS_LIST if d not in collected_details]

    # -------- DECIDE AGENT PHASE --------
    if total_messages > 8 and collected_details:
        # Stop if enough messages and at least one detail is collected
        system_prompt = """
Now you have collected enough details. Politely end the conversation.
Thank the sender and say you won't be able to proceed further.
"""
        next_phase = "DONE"

    elif missing_details:
        # Extract remaining details one by one
        # Ask only about one missing detail at a time
        detail_to_ask = missing_details[0]
        system_prompt = f"""
You are now going to collect the {detail_to_ask} from the sender.
Do it casually as part of the conversation. Do NOT mention scams or police.
Sound human, emotional, and realistic. Keep reply short (1–2 sentences).
"""
        next_phase = "EXTRACTING"

    else:
        # No missing details left, politely end conversation
        system_prompt = """
Now you have done the agent's job. Politely end the conversation.
Thank the sender and say you won't be able to proceed further.
"""
        next_phase = "DONE"

    # -------- FINAL PROMPT --------
    prompt = f"""
Reply only in English.

{system_prompt}

IMPORTANT RULES:
- Never accuse the sender of scam
- Never mention police, cybercrime, or fraud
- Keep replies short and realistic

Conversation:
{convo}

Reply as USER:
"""

    reply = gemini_generate(prompt)

    if reply:
        session["agentPhase"] = next_phase

        # Try to detect if a detail was given in reply (very simple keyword check)
        for detail in missing_details:
            if detail.lower() in reply.lower():
                collected_details.add(detail)
        session["collected_details"] = collected_details

        return reply.strip()[:250]

    return "Can you explain what this is about?"
