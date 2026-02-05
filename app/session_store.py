# session_store.py
sessions = {}

def get_session(session_id):
    return sessions.setdefault(session_id, {
        "sessionId": session_id,
        "messages": [],
        "intelligence": {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        },
        "scamDetected": False,
        "agentActive": False,
        "engagementComplete": False,
        "agentNotes": ""
    })
