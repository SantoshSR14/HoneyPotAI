import requests

GUVI_ENDPOINT = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

def send_guvi_callback(payload: dict):
    try:
        response = requests.post(
            GUVI_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        print("✅ GUVI RESPONSE STATUS:", response.status_code)
        print("✅ GUVI RESPONSE BODY:", response.text)

        return response.status_code, response.text

    except Exception as e:
        print("❌ GUVI CALLBACK FAILED:", str(e))
        return None, str(e)
