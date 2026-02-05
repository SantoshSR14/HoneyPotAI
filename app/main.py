from fastapi import FastAPI, Request
from app.agent import agent_reply

app = FastAPI()

# Simple in-memory session store (for demo)
sessions = {}

@app.post("/")
async def honeypot_message(req: Request):
    data = await req.json()
    session_id = data.get("sessionId")
    user_message = data.get("text")

    # Initialize session if first message
    if session_id not in sessions:
        sessions[session_id] = {
            "sessionId": session_id,
            "messages": [],
            "agentPhase": "PASSIVE",
            "collected_details": {},
            "scamDetected": True,  # or set based on your detection logic
            "agentNotes": ""
        }

    session = sessions[session_id]

    # Append user message to history
    session["messages"].append({"sender": "user", "text": user_message})

    # Generate agent reply
    agent_text = agent_reply(session)

    # Append agent reply to history
    session["messages"].append({"sender": "agent", "text": agent_text})

    return {"status": "success", "reply": agent_text}
