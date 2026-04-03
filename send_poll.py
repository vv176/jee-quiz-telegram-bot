import anthropic
import requests
import json
import random
import os
import sys

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL_ID = os.environ["TELEGRAM_CHANNEL_ID"]
CLAUDE_API_KEY = os.environ["CLAUDE_API_KEY"]

subject = random.choice(["Physics", "Chemistry", "Mathematics"])

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

prompt = f"""Generate a JEE Main/Advanced level multiple-choice question on {subject}.

Return ONLY a valid JSON object with this exact structure (no markdown, no extra text):
{{
  "question": "[{subject}] The question text here",
  "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
  "correct_option_id": 0,
  "explanation": "Brief explanation of why this answer is correct (1-2 sentences)"
}}

Rules:
- Question must be genuinely challenging, JEE Main/Advanced standard
- Question text must be under 300 characters total (including the subject tag)
- Each option must be under 100 characters
- correct_option_id is 0-indexed (0, 1, 2, or 3)
- Vary the correct answer position, don't always use 0
- Return ONLY the JSON object, nothing else"""

print(f"Generating {subject} question...")

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
)

raw = message.content[0].text.strip()

# Strip markdown code block if present
if raw.startswith("```"):
    raw = raw.split("```")[1]
    if raw.startswith("json"):
        raw = raw[4:]
    raw = raw.strip()

data = json.loads(raw)

print(f"Question: {data['question']}")
print(f"Options: {data['options']}")
print(f"Correct: {data['correct_option_id']}")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPoll"
payload = {
    "chat_id": CHANNEL_ID,
    "question": data["question"],
    "options": data["options"],
    "type": "quiz",
    "correct_option_id": data["correct_option_id"],
    "is_anonymous": True,
    "explanation": data["explanation"]
}

response = requests.post(url, json=payload)
result = response.json()

if result.get("ok"):
    print("SUCCESS: Poll posted to Telegram channel!")
else:
    print(f"ERROR posting to Telegram: {result.get('description')}")
    sys.exit(1)
