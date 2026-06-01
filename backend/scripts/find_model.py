"""Find which Gemini model still has generateContent quota"""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from google import genai

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Models to try (in order of preference)
candidates = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash-001",
    "gemini-1.5-flash",
    "gemini-2.5-pro",
]

for model in candidates:
    try:
        resp = client.models.generate_content(
            model=model,
            contents="Reply with exactly one word: hello",
        )
        print(f"OK  {model}: {resp.text.strip()[:30]}")
        break  # Use first working model
    except Exception as e:
        err = str(e)[:120]
        print(f"ERR {model}: {err}")
    time.sleep(1)
