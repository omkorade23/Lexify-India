"""
Step 4: Live API retrieval test for /api/legal-chat
Run from backend/ with: venv\Scripts\python.exe scripts\test_legal_chat_api.py
"""
import sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import requests
except ImportError:
    print("pip install requests")
    sys.exit(1)

BASE = "http://localhost:8000"

# Wait for server
for attempt in range(12):
    try:
        r = requests.get(f"{BASE}/health", timeout=3)
        if r.status_code == 200:
            print(f"Server UP: {r.json()}")
            break
    except Exception:
        pass
    print(f"  Waiting for server... ({attempt+1}/12)")
    time.sleep(3)
else:
    print("Server did not start in time.")
    sys.exit(1)

# Step 4 test query
question = "Can I apply for permanent driving licence now? I got my learner licence 35 days ago."
payload = {"question": question, "conversation_history": []}

print(f"\n{'='*70}")
print("STEP 4: LIVE API TEST — /api/legal-chat")
print(f"{'='*70}")
print(f"Question: {question}")

try:
    resp = requests.post(f"{BASE}/api/legal-chat", json=payload, timeout=60)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print("\nFull Response:")
    print(json.dumps(data, indent=2))
    
    # Validation checks
    print(f"\n{'='*70}")
    print("VALIDATION CHECKS")
    print(f"{'='*70}")
    
    confidence = data.get("confidence", "")
    check1 = confidence != "none"
    print(f"[{'PASS' if check1 else 'FAIL'}] confidence != 'none': '{confidence}'")
    
    citations = data.get("citations", [])
    driving_ids = {"motor_vehicles_001", "motor_vehicles_002"}
    driving_cits = [c for c in citations if c.get("chunk_id") in driving_ids]
    check2 = len(driving_cits) > 0
    print(f"[{'PASS' if check2 else 'FAIL'}] citations contain motor_vehicles_001 or _002: {len(driving_cits)} found")
    for c in driving_cits:
        print(f"    chunk_id={c.get('chunk_id')} score={c.get('similarity_score')}")
    
    answer = data.get("answer", "").lower()
    check3 = "30" in answer or "thirty" in answer or "30-day" in answer or "6 month" in answer or "six month" in answer or "180 day" in answer or "wait" in answer or "minimum" in answer
    print(f"[{'PASS' if check3 else 'FAIL'}] answer mentions 30-day/6-month window: {check3}")
    print(f"    Answer preview: {data.get('answer','')[:200]}")
    
    all_pass = check1 and check2 and check3
    print(f"\n{'='*70}")
    print(f"RESULT: {'ALL CHECKS PASSED' if all_pass else 'SOME CHECKS FAILED'}")
    print(f"{'='*70}")
    
except Exception as e:
    print(f"Request failed: {e}")
    sys.exit(1)
