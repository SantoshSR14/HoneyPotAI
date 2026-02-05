from fastapi import FastAPI
from pydantic import BaseModel
from app.agent import agent_reply
from app.callback import send_guvi_callback

app = FastAPI()

class MessageRequest(BaseModel):
    sessionId: str
    message: str


# In-memory session store (simple & sufficient)
SESSIONS = {}


@app.post("/api/honeypot/message")
def honeypot_message(req: MessageRequest):
    session = SESSIONS.setdefault(req.sessionId, {
        "sessionId": req.sessionId,
        "messages": [],
        "agentPhase": "PASSIVE",
        "scamDetected": False,
        "finalSent": False,
        "intelligence": {
            "upiIds": [],
            "phoneNumbers": [],
            "phishingLinks": [],
            "bankAccounts": [],
            "suspiciousKeywords": []
        }
    })

    # Add user message
    session["messages"].append({
        "sender": "scammer",
        "text": req.message
    })

    # Very basic scam signal (you can improve later)
    if any(k in req.message.lower() for k in ["urgent", "pay", "verify", "blocked"]):
        session["scamDetected"] = True
        session["intelligence"]["suspiciousKeywords"].append("urgent")

    # Generate agent reply
    reply = agent_reply(session)

    # Add agent reply to history
    session["messages"].append({
        "sender": "agent",
        "text": reply
    })

    # 🚨 FINAL GUVI CALLBACK (ONLY ONCE)
    if (
        not session["finalSent"]
        and session["scamDetected"]
        and len(session["messages"]) >= 7
        and any(session["intelligence"].values())
    ):
        session["finalSent"] = True
        send_guvi_callback(session)

    return {"reply": reply}
