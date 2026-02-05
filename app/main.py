from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time

from app.agent import agent_reply
from app.session_store import get_or_create_session
from app.callback import send_guvi_callback

API_KEY = "YOUR_SECRET_API_KEY"
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
    # ---- API KEY CHECK ----
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # ---- SESSION ----
    session = get_or_create_session(req.sessionId)

    # ---- SAFETY INIT (CRITICAL) ----
    session.setdefault("messages", [])
    session.setdefault("scamDetected", False)
    session.setdefault("finalSent", False)
    session.setdefault("intelligence", {
        "bankAccounts": [],
        "upiIds": [],
        "phishingLinks": [],
        "phoneNumbers": [],
        "suspiciousKeywords": []
    })

    # ---- MERGE HISTORY ONCE ----
    if not session["messages"] and req.conversationHistory:
        for msg in req.conversationHistory:
            session["messages"].append({
                "sender": msg.sender,
                "text": msg.text,
                "timestamp": msg.timestamp
            })

    # ---- APPEND INCOMING MESSAGE ----
    session["messages"].append({
        "sender": req.message.sender,
        "text": req.message.text,
        "timestamp": req.message.timestamp
    })

    # ---- AGENT REPLY ----
    reply = agent_reply(session)

    # ---- FAILSAFE (NO 500s) ----
    if not reply:
        reply = "Can you explain more?"

    # ---- APPEND AGENT MESSAGE ----
    session["messages"].append({
        "sender": "user",
        "text": reply,
        "timestamp": int(time.time() * 1000)
    })

    # ---- FINAL GUVI CALLBACK (ONCE ONLY) ----
    if (
        not session["finalSent"]
        and session["scamDetected"] is True
        and len(session["messages"]) >= MAX_MESSAGES
        and any(session["intelligence"].values())
    ):
        session["finalSent"] = True
        print("🚨 SENDING FINAL GUVI CALLBACK 🚨")
        try:
            send_guvi_callback(session)
        except Exception as e:
            print("❌ GUVI CALLBACK FAILED:", str(e))

    # ---- RESPONSE (HACKATHON FORMAT) ----
    return {
        "status": "success",
        "reply": reply
    }
