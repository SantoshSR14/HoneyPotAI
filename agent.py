from gemini_client import gemini_generate
def agent_reply(session):
    history = session["messages"]
    phase = session.get("agentPhase", "PASSIVE")

    # Build conversation safely
    convo = ""
    for m in history[-6:]:
        sender = m.get("sender", "user")
        text = m.get("text", "")
        convo += f"{sender.upper()}: {text}\n"

    # -------- PHASE PROMPTS --------

    if phase == "PASSIVE":
        system_prompt = """
You are a normal person. You received a message.
You have to get the details of the message and find out if it's a scam
or a legit message.
Do NOT cooperate yet.
"""
        next_phase = "CONFIRMED_SCAM"

    elif phase == "CONFIRMED_SCAM":
        system_prompt = """
You are not worried. You have to just keep on building 
the converstaion casually as if you have not sensed that it 
is a scam. Ask what needs to be done.
"""
      

        next_phase = "EXTRACTING"

    elif phase == "EXTRACTING":
        system_prompt = """
You are now going to start extarcting the details about the 
scammers. Ask for bank account details, UPI ID, phone number, account details,
and any links if possible based on the context of the message.
In this phase, you shouldn't reveal you know it's a scam. Do 
it casually.
"""
        next_phase = "DONE"

    elif phase == "DONE":
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
- Sound human, emotional, and realistic
- Keep replies short (1–2 sentences)

Conversation:
{convo}

Reply as USER:
"""

    reply = gemini_generate(prompt)

    if reply:
        session["agentPhase"] = next_phase
        return reply.strip()[:250]

    return "Can you explain what this is about?"
