import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')

if not api_key or api_key == 'your-google-api-key-here':
    print("SKIPPED: Please set GOOGLE_API_KEY in .env to run this test.")
else:
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents="Hello"
        )
        with open('gemini_test_output.txt', 'w') as f:
            f.write(response.text)
        print("SUCCESS")
    except Exception as e:
        print(f"ERROR: {e}")
