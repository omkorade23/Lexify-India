"""List available Gemini embedding models"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from google import genai

client = genai.Client(api_key=settings.GEMINI_API_KEY)

print("Available models with embedContent support:")
for m in client.models.list():
    if 'embed' in m.name.lower() or 'embedding' in m.name.lower():
        print(f"  {m.name}")

print("\nAll models (first 30):")
for i, m in enumerate(client.models.list()):
    print(f"  {m.name}")
    if i > 30:
        break
