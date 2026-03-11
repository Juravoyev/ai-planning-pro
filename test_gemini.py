import urllib.request
import json
import os
import sys
from dotenv import load_dotenv

print("Script started...")

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key found: {bool(api_key)}")

if not api_key:
    sys.exit("Error: GEMINI_API_KEY not found in .env")

# Try v1 with 1.5-flash
url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"

payload = json.dumps({
    "contents": [{
        "parts": [{
            "text": "Salom"
        }]
    }]
}).encode("utf-8")

print(f"Requesting: {url}")

req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"Status: {resp.status}")
        data = json.loads(resp.read())
        print("Response received!")
        print(data['candidates'][0]['content']['parts'][0]['text'])
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(e.read().decode())
except Exception as e:
    print(f"General Error: {e}")
