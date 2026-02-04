from config import GEMINI_API_KEY

def gemini_generate(prompt: str) -> str:
    try:
        from google import genai

        if not GEMINI_API_KEY:
            return "I don't understand. Can you explain?"

        # ✅ NEW SDK: create client
        client = genai.Client(api_key=GEMINI_API_KEY)

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
