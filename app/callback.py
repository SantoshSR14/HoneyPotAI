import requests
from app.config import GUVI_CALLBACK_URL

def send_final_callback(session_id, session_data):
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": len(session_data["messages"]),
        "extractedIntelligence": session_data["intelligence"],
        "agentNotes": "Scammer used urgency and financial threats"
    }
    print("🚨 SENDING FINAL GUVI CALLBACK 🚨")
    print(payload)

    try:
        response = requests.post(
            GUVI_CALLBACK_URL,
            json=payload,
            timeout=5
        )

        print("✅ GUVI RESPONSE STATUS:", response.status_code)
        print("✅ GUVI RESPONSE BODY:", response.text)

    except Exception as e:
        print("❌ GUVI CALLBACK ERROR:", e)


  #  requests.post(GUVI_CALLBACK_URL, json=payload, timeout=5)
