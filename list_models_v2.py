import urllib.request
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("GEMINI_API_KEY not found")
    exit()

# Try v1beta models list
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
        print("Models list:")
        for m in data.get('models', []):
            print(f"- {m['name']}")
except Exception as e:
    print(f"Error: {e}")
