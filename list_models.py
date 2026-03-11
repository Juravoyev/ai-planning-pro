import urllib.request
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("API key not found")
    exit()

# Try listing models with v1
url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"

try:
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
        print("Available models:")
        for model in data.get('models', []):
            print(f"- {model['name']} (supported methods: {model.get('supportedGenerationMethods', [])})")
except Exception as e:
    print(f"Error listing models: {e}")
    if hasattr(e, 'read'):
        print(e.read().decode())
