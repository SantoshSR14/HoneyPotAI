from fastapi import FastAPI, Header, HTTPException
from app.models import HoneypotRequest, HoneypotResponse
from app.config import API_KEY
from app.scam_detector import detect_scam
from app.agent import agent_reply
from app.intelligence import extract_intelligence
from app.session_store import get_session
from app.callback import send_final_callback

app = FastAPI()

@app.post("/api/honeypot/message", response_model=HoneypotResponse)
async def honeypot_message(
    req: HoneypotRequest,
    x_api_key: str = Header(..., alias="x-api-key")
):
    # 🔐 API Key validation
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    session = get_session(req.sessionId)

    # 🧠 Load conversation history (SPEC COMPLIANT)
    if req.conversationHistory:
        session["messages"] = [
            {"sender": m.sender, "text": m.text, "timestamp": m.timestamp}
            for m in req.conversationHistory
        ]

    # ➕ Add latest message
    session["messages"].append({
        "sender": req.message.sender,
        "text": req.message.text,
        "timestamp": req.message.timestamp
    })

    # 🔍 Scam detection (only once)
    if not session["scamDetected"]:
        session["scamDetected"] = detect_scam(req.message.text)
        session["agentActive"] = session["scamDetected"]

    # 🤖 Agent only activates after scam detected
    if session["agentActive"]:
        extract_intelligence(req.message.text, session["intelligence"])
        reply = agent_reply(session)
    else:
        reply = "Okay."

    # 🧾 Store agent reply as USER (persona)
    session["messages"].append({
        "sender": "user",
        "text": reply,
        "timestamp": req.message.timestamp
    })

    # ✅ Engagement completion logic (INTELLIGENT, NOT COUNT-BASED)
    if (
        session["scamDetected"]
        and len(session["messages"]) >= 10
        and any(session["intelligence"].values())
    ):
        session["engagementComplete"] = True

    # 📤 Mandatory GUVI callback
    if session["engagementComplete"]:
        send_final_callback(req.sessionId, session)
        session["agentNotes"] = "Scammer used urgency and payment redirection tactics"

    return HoneypotResponse(
        status="success",
        reply=reply
    )
