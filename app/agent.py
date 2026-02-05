from app.gemini_client import gemini_generate

DETAILS_LIST = ["bank account", "UPI ID", "phone number", "account details", "links"]

def agent_reply(session):
    history = session.get("messages", [])
    collected_details = session.get("collected_details", set())
    total_messages = len(history)
    
    # Build conversation safely (last 6 messages for context)
    convo = ""
    for m in history[-6:]:
        sender = m.get("sender", "user")
        text = m.get("text", "")
        convo += f"{sender.upper()}: {text}\n"

    # Determine missing details
    missing_details = [d for d in DETAILS_LIST if d not in collected_details]

    # -------- Decide Agent Phase --------
    if total_messages > 8 and collected_details:
        # Stop if enough messages and at least one detail collected
        system_prompt = """
Now you have collected enough details. Politely end the conversation.
Thank the sender and say you won't be able to proceed further.
"""
        next_phase = "DONE"

    elif missing_details:
        # Progressive detail extraction: only start asking after 2-3 messages
        if total_messages < 3:
            # Early conversation: stay casual, don't ask details yet
            system_prompt = """
You are a normal person having a casual conversation.
Respond naturally, engage the sender, and keep it short (1-2 sentences).
Do NOT ask for any sensitive details yet.
"""
            next_phase = "PASSIVE"
        else:
            # Ask for the first missing detail in a casual way
            detail_to_ask = missing_details[0]
            system_prompt = f"""
You are now going to collect the {detail_to_ask} from the sender.
Do it casually as part of the conversation. Do NOT mention scams or police.
Keep your reply short (1-2 sentences) and realistic.
"""
            next_phase = "EXTRACTING"
    else:
        # No missing details left, politely end conversation
        system_prompt = """
Now you have done the agent's job. Politely end the conversation.
Thank the sender and say you won't be able to proceed further.
"""
        next_phase = "DONE"

    # -------- Build final prompt --------
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

    reply = gemini_generate(prompt)

    if reply:
        session["agentPhase"] = next_phase

        # Track details if mentioned in reply (simple keyword check)
        for detail in missing_details:
            if detail.lower() in reply.lower():
                collected_details.add(detail)
        session["collected_details"] = collected_details

        return reply.strip()[:250]

    return "Can you explain what this is about?"
