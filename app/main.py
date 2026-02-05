@app.post("/api/honeypot/message")
async def honeypot_message(req: Request):
    try:
        data = await req.json()
        session_id = data.get("sessionId")
        user_message = data.get("text")

        if not session_id or not user_message:
            return {"status": "error", "message": "sessionId and text are required"}

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
        # Catch any error and return as JSON
        print("Internal Server Error:", e)
        return {"status": "error", "message": str(e)}
