# app/session_store.py

sessions = {}


def get_or_create_session(session_id: str):
    if session_id not in sessions:
        sessions[session_id] = {
            "sessionId": session_id,
            "messages": [],
            "scamDetected": False,
            "intelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": []
            },
            "agentNotes": "",
            "finalSent": False
        }
    return sessions[session_id]
