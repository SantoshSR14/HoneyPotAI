from fastapi import FastAPI, Request
from app.session_store import get_session
from app.agent import agent_reply
from app.intelligence import extract_intelligence
from app.callback import send_guvi_callback

app = FastAPI()   # 🔴 THIS WAS MISSING


@app.post("/api/honeypot/message")
async def honeypot_message(req: Request):
    body = await req.json()

    session_id = body["sessionId"]
    message = body["message"]

    session = get_session(session_id)

    # 1️⃣ Store incoming message (from scammer)
    session["messages"].append({
        "sender": message["sender"],
        "text": message["text"],
        "timestamp": message["timestamp"]
    })

    # 2️⃣ Scam detection (simple trigger, already works)
    if not session["scamDetected"]:
        if "urgent" in message["text"].lower():
            session["scamDetected"] = True

    # 3️⃣ Extract intelligence from scammer text
    extract_intelligence(
        message["text"],
        session["intelligence"]
    )

    # 4️⃣ HARD STOP + GUVI CALLBACK (ONCE)
    if (
        session["scamDetected"]
        and not session["finalSent"]
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

        session["finalSent"] = True

    # 5️⃣ Agent reply (only if not finished)
    reply = "Okay."

    if not session["finalSent"]:
        reply = agent_reply(session)

        session["messages"].append({
            "sender": "user",
            "text": reply,
            "timestamp": message["timestamp"]
        })

    return {
        "status": "success",
        "reply": reply
    }
