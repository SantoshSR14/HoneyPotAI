import requests
from config import GUVI_CALLBACK_URL

def send_final_callback(session_id, session_data):
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": len(session_data["messages"]),
        "extractedIntelligence": session_data["intelligence"],
        "agentNotes": "Scammer used urgency and financial threats"
    }

    requests.post(GUVI_CALLBACK_URL, json=payload, timeout=5)
