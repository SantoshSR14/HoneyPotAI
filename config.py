import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HONEYPOT_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
