from fastapi import FastAPI, Header, HTTPException
from requests import session
from models import HoneypotRequest, HoneypotResponse
from config import API_KEY
from scam_detector import detect_scam
from agent import agent_reply
from intelligence import extract_intelligence
from session_store import get_session
from callback import send_final_callback

app = FastAPI()

@app.post("/api/honeypot", response_model=HoneypotResponse)
def honeypot(req: HoneypotRequest, x_api_key: str = Header(...)):


    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    session = get_session(req.sessionId)

    session["messages"].append(req.message.dict())

    extract_intelligence(req.message.text, session["intelligence"])

    if not session["scamDetected"]:
        session["scamDetected"] = detect_scam(req.message.text)
    reply = agent_reply(session)

    #reply = agent_reply(session["messages"])

    session["messages"].append({
        "sender": "user",
        "text": reply,
        "timestamp": req.message.timestamp
    })
    print("\n--- CONVERSATION HISTORY ---")
    for m in session["messages"]:
        print(f"{m['sender']}: {m['text']}")
        print("----------------------------\n")

    # Finalize after enough engagement
    if session["scamDetected"] and len(session["messages"]) >= 15:
        send_final_callback(req.sessionId, session)

    return HoneypotResponse(
        status="success",
        reply=reply
    )
