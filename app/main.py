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
    # 🔐 API key check
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    session_id = req.sessionId
    session = get_session(session_id)

    # 🧠 Store user message
    session["messages"].append({
        "sender": "user",
        "text": req.message.text,
        "timestamp": req.message.timestamp
    })

    # 🔍 Extract intelligence
    extract_intelligence(req.message.text, session["intelligence"])

    # 🕵️ Scam detection (only once)
    if not session["scamDetected"]:
        session["scamDetected"] = detect_scam(req.message.text)

    # 🤖 Agent reply
    reply = agent_reply(session)

    # 🧾 Store agent reply
    session["messages"].append({
        "sender": "agent",
        "text": reply,
        "timestamp": req.message.timestamp
    })

    # 📤 Final callback to GUVI
    if session["scamDetected"] and len(session["messages"]) >= 15:
        send_final_callback(session_id, session)

    return HoneypotResponse(
        status="success",
        reply=reply
    )
