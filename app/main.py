from fastapi import APIRouter, Request
from app.session_store import get_session
from app.agent import agent_reply
from app.intelligence import extract_intelligence
from app.callback import send_guvi_callback

router = APIRouter()

@router.post("/api/honeypot/message")
async def honeypot_message(req: Request):
    body = await req.json()

    session_id = body["sessionId"]
    message = body["message"]

    session = get_session(session_id)

    # -------------------------------
    # 1️⃣ STORE INCOMING MESSAGE
    # -------------------------------
    session["messages"].append({
        "sender": message["sender"],   # scammer
        "text": message["text"],
        "timestamp": message["timestamp"]
    })

    # -------------------------------
    # 2️⃣ SCAM DETECTION (ALREADY WORKING)
    # -------------------------------
    if not session["scamDetected"]:
        if "urgent" in message["text"].lower():
            session["scamDetected"] = True

    # -------------------------------
    # 3️⃣ EXTRACT INTELLIGENCE (REAL DATA)
    # -------------------------------
    extract_intelligence(
        message["text"],
        session["intelligence"]
    )

    # -------------------------------
    # 4️⃣ HARD STOP + GUVI CALLBACK (ONCE)
    # -------------------------------
    if (
        session["scamDetected"]
        and not session.get("finalSent")               # 🔒 LOCK
        and len(session["messages"]) >= 7
        and any(session["intelligence"].values())
    ):
        print("🚨 SENDING FINAL GUVI CALLBACK 🚨")

        payload = {
            "sessionId": session_id,
            "scamDetected": True,
            "totalMessagesExchanged": len(session["messages"]),
            "extractedIntelligence": session["intelligence"],
            "agentNotes": "Scammer used urgency and payment redirection tactics"
        }

        print(payload)

        send_guvi_callback(payload)
        session["finalSent"] = True   # 🔒 VERY IMPORTANT

    # -------------------------------
    # 5️⃣ AGENT REPLY (IF NOT DONE)
    # -------------------------------
    reply = "Okay."

    if not session.get("finalSent"):
        reply = agent_reply(session)

        session["messages"].append({
            "sender": "user",
            "text": reply,
            "timestamp": message["timestamp"]
        })

    # -------------------------------
    # 6️⃣ API RESPONSE
    # -------------------------------
    return {
        "status": "success",
        "reply": reply
    }
