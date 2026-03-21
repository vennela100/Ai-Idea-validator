import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

try:
    response = model.generate_content("Hello")
    with open('gemini_test_output.txt', 'w') as f:
        f.write(response.text)
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
