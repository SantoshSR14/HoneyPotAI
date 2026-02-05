# app/session_store.py

sessions = {}

def get_session(session_id: str) -> dict:
    if session_id not in sessions:
        sessions[session_id] = {
            "messages": [],
            "agentPhase": "PASSIVE",
            "scamDetected": False,
            "finalSent": False,   # 🔒 callback lock
            "intelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": []
            }
        }
    return sessions[session_id]
