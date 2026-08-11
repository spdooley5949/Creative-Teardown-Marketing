"""Run this once after pasting your API key into .env, to confirm it works."""
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
key = os.getenv("ANTHROPIC_API_KEY")

if not key:
    print("No key found. Open the .env file, paste your key after ANTHROPIC_API_KEY=, save, and run this again.")
    raise SystemExit(1)

print(f"Key loaded (ends with ...{key[-4:]}). Testing the connection to Claude...")

client = Anthropic(api_key=key)
resp = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=20,
    messages=[{"role": "user", "content": "Reply with the single word: working"}],
)
print("Claude replied:", resp.content[0].text.strip())
print("Your key works. You are ready to build.")
