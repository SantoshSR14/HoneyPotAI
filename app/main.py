from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
from app.config import API_KEY
from app.agent import agent_reply
from app.session_store import get_or_create_session
from app.callback import send_guvi_callback

#API_KEY = "sk_test_123456789"
MAX_MESSAGES = 20

app = FastAPI()


# -----------------------------
# Request Models (Hackathon Spec)
# -----------------------------

class Message(BaseModel):
    sender: str
    text: str
    timestamp: int


class MessageRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: Optional[List[Message]] = []
    metadata: Optional[Dict[str, Any]] = {}


# -----------------------------
# API Endpoint
# -----------------------------

@app.post("/api/honeypot/message")
def honeypot_message(
    req: MessageRequest,
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    session = get_or_create_session(req.sessionId)

    # -----------------------------
    # Merge conversation history (only once)
    # -----------------------------
    if not session["messages"] and req.conversationHistory:
        for msg in req.conversationHistory:
            session["messages"].append({
                "sender": msg.sender,
                "text": msg.text,
                "timestamp": msg.timestamp
            })

    # -----------------------------
    # Append latest incoming message
    # -----------------------------
    session["messages"].append({
        "sender": req.message.sender,
        "text": req.message.text,
        "timestamp": req.message.timestamp
    })

    # -----------------------------
    # Call AI Agent (NO logic change)
    # -----------------------------
    reply = agent_reply(session)

    # -----------------------------
    # Append agent reply
    # -----------------------------
    session["messages"].append({
        "sender": "user",
        "text": reply,
        "timestamp": int(time.time() * 1000)
    })

    # -----------------------------
    # Final GUVI Callback Condition
    # -----------------------------
    if (
        not session.get("finalSent")
        and session.get("scamDetected") is True
        and len(session["messages"]) >= MAX_MESSAGES
        and any(session["intelligence"].values())
    ):
        session["finalSent"] = True
        print("🚨 SENDING FINAL GUVI CALLBACK 🚨")
        send_guvi_callback(session)

    # -----------------------------
    # API Response (Hackathon format)
    # -----------------------------
    return {
        "status": "success",
        "reply": reply
    }
