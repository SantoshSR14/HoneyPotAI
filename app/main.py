from fastapi import FastAPI, Header, HTTPException
from app.models import HoneypotRequest, HoneypotResponse
from app.config import API_KEY
from app.scam_detector import detect_scam
from fastapi import FastAPI, Request
from app.agent import agent_reply
from app.intelligence import extract_intelligence
from app.session_store import get_session
from app.callback import send_final_callback

app = FastAPI()

# Simple in-memory session store (for demo)
sessions = {}

@app.post("/", response_model=HoneypotResponse)
def honeypot(
    req: HoneypotRequest,
    x_api_key: str = Header(..., alias="x-api-key")  # ✅ FIX
):
    # 🔐 API Key validation
    print("ENV API KEY:", repr(API_KEY))
@app.post("/api/honeypot/message")
async def honeypot_message(req: Request):
    data = await req.json()
    session_id = data.get("sessionId")
    user_message = data.get("text")

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
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

    # 📦 Session handling
    session = get_session(req.sessionId)
    session = sessions[session_id]

    # Store incoming message
    session["messages"].append(req.message.dict())
    # Append user message to history
    session["messages"].append({"sender": "user", "text": user_message})

    # Extract intelligence
    extract_intelligence(req.message.text, session["intelligence"])
    # Generate agent reply
    agent_text = agent_reply(session)

    # Detect scam (once)
    if not session["scamDetected"]:
        session["scamDetected"] = detect_scam(req.message.text)
    # Append agent reply to history
    session["messages"].append({"sender": "agent", "text": agent_text})

    # Agent reply
    reply = agent_reply(session)

    # Store agent reply
    session["messages"].append({
        "sender": "user",
        "text": reply,
        "timestamp": req.message.timestamp
    })

    # Debug logs (safe)
    print("\n--- CONVERSATION HISTORY ---")
    for m in session["messages"]:
        print(f"{m['sender']}: {m['text']}")
    print("----------------------------\n")

    # 📤 Final callback (mandatory for GUVI)
    if session["scamDetected"] and len(session["messages"]) >= 15:
        send_final_callback(req.sessionId, session)

    return HoneypotResponse(
        status="success",
        reply=reply
    )
    return {"status": "success", "reply": agent_text}
