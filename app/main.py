from fastapi import FastAPI, Request
from app.agent import agent_reply, DETAILS_MAPPING
import requests
import os

GUVI_ENDPOINT = os.getenv("GUVI_ENDPOINT", "https://guvi-endpoint.example.com")  # replace with actual

app = FastAPI()
sessions = {}

def send_final_payload_to_guvi(session):
    payload = {
        "sessionId": session["sessionId"],
        "scamDetected": session.get("scamDetected", True),
        "totalMessagesExchanged": len(session["messages"]),
        "extractedIntelligence": session["collected_details"],
        "agentNotes": session.get("agentNotes", "")
    }
    print("→ FINAL GUVI PAYLOAD:", payload)  # debug print
    try:
        requests.post(GUVI_ENDPOINT, json=payload, timeout=5)
    except Exception as e:
        print("Error sending final payload:", e)

@app.post("/api/honeypot/message")
async def honeypot_message(req: Request):
    try:
        data = await req.json()

        session_id = data.get("sessionId")
        message_obj = data.get("message", {})
        user_message = message_obj.get("text")

        if not session_id or not user_message:
            return {"status": "error", "message": "sessionId and text required"}

        # Initialize session if not exists
        if session_id not in sessions:
            sessions[session_id] = {
                "sessionId": session_id,
                "messages": [],
                "agentPhase": "PASSIVE",
                "collected_details": {k: [] for k in DETAILS_MAPPING.keys()},
                "scamDetected": True,
                "agentNotes": ""
            }

        session = sessions[session_id]

        # Append user message
        session["messages"].append({"sender": "user", "text": user_message})

        # Generate agent reply
        agent_text = agent_reply(session)

        # Append agent reply
        session["messages"].append({"sender": "agent", "text": agent_text})

        return {"status": "success", "reply": agent_text}

    except Exception as e:
        print("Internal Server Error:", e)
        return {"status": "error", "message": str(e)}
