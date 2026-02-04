import google.generativeai as genai

genai.configure(api_key="AIzaSyANiB51tLqSirWfQ_mONdBOoh_4y3e0Rbg")

model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content("Say hello like a human")

print(response.text)
