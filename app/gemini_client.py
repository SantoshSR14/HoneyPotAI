from app.config import GEMINI_API_KEY
from functools import lru_cache

@lru_cache(maxsize=1)
def _get_client():
    from google import genai
    return genai.Client(api_key=GEMINI_API_KEY)

def gemini_generate(prompt: str) -> str:
    try:
        if not GEMINI_API_KEY:
            return "I don't understand. Can you explain?"

        client = _get_client()

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        if not response or not response.text:
            return "Sorry, can you repeat that?"

        return response.text.strip()

    except Exception as e:
        print("GEMINI ERROR:", e)
        return "I'm not sure what you mean."
