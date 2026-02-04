from gemini_client import gemini_generate

SCAM_KEYWORDS = [
    "blocked", "urgent", "verify", "suspended",
    "upi", "bank", "otp", "click link"
]

def detect_scam(text: str) -> bool:
    rule_match = any(k in text.lower() for k in SCAM_KEYWORDS)

    llm_prompt = f"""
    Is the following message likely a scam?
    Reply only YES or NO.

    Message: "{text}"
    """

    llm_result = gemini_generate(llm_prompt)

    return rule_match or "YES" in llm_result.upper()
