
import google.generativeai as genai
import os
import json

# The key provided by the user in api.py
API_KEY = "YOUR_GEMINI_API_KEY_HERE"

print(f"Testing Gemini API with key: {API_KEY[:5]}...{API_KEY[-5:]}")

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    print("Sending test prompt...")
    response = model.generate_content(
        "Return a simple JSON object: {'status': 'ok'}",
        generation_config={"response_mime_type": "application/json"}
    )
    
    print(f"Response: {response.text}")
    print("SUCCESS: API is working.")
    
except Exception as e:
    print(f"FAILURE: {e}")
    if hasattr(e, 'response'):
         print(f"Response feedback: {e.response.prompt_feedback}")
