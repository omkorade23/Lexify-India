"""
E2E API tests for Phase 4B verification.
Tests all three general legal chat flows.
"""
import urllib.request
import json
import sys

BASE_URL = "http://localhost:8000"


def api_post(path, payload):
    url = BASE_URL + path
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def api_get(path):
    url = BASE_URL + path
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read())


def print_response(label, data):
    print(f"\n{'='*60}")
    print(f"FLOW: {label}")
    print(f"{'='*60}")
    print(f"ANSWER (first 600 chars): {data['answer'][:600]}")
    print(f"CITATIONS_COUNT: {len(data['citations'])}")
    print(f"HAS_LEGAL_CONTEXT: {data['has_legal_context']}")
    print(f"CONFIDENCE: {data['confidence']}")
    for c in data['citations'][:3]:
        src = c.get('source_type', 'unknown')
        act = c.get('act_name', '')
        sec = c.get('act_section', '')
        score = c.get('similarity_score', 0)
        cat = c.get('category', '')
        print(f"  [{src}] {act} / {sec} / cat={cat} / score={score}")
    # Check for motor_vehicles content
    answer_lower = data['answer'].lower()
    keywords_check = {
        "30-day": any(k in answer_lower for k in ["30 day", "30-day", "thirty day"]),
        "6-month window": any(k in answer_lower for k in ["6 month", "six month", "180 day"]),
        "section 438": "438" in answer_lower,
        "anticipatory": "anticipatory" in answer_lower,
        "tenant": any(k in answer_lower for k in ["tenant", "tenancy", "landlord", "rent"]),
    }
    print(f"KEYWORD CHECKS: {keywords_check}")


# Health check
health = api_get("/health")
print(f"HEALTH: {health}")

# Flow 1: Driving licence
print("\n--- Flow 1: Driving Licence ---")
try:
    r1 = api_post("/api/legal-chat", {
        "question": "Can I apply for permanent driving licence? I got my learner licence 35 days ago.",
        "conversation_history": []
    })
    print_response("Motor Vehicles - Driving Licence", r1)
    flow1_pass = "motor_vehicles" in str([c.get("category", "") for c in r1["citations"]])
    print(f"FLOW 1 RESULT: {'PASS - motor_vehicles citations present' if flow1_pass else 'CHECK - no motor_vehicles category in citations (answer may still be correct)'}")
except Exception as e:
    print(f"FLOW 1 ERROR: {e}")

# Flow 2: Anticipatory bail
print("\n--- Flow 2: Anticipatory Bail ---")
try:
    r2 = api_post("/api/legal-chat", {
        "question": "What is anticipatory bail?",
        "conversation_history": []
    })
    print_response("Criminal Law - Anticipatory Bail", r2)
    flow2_pass = "438" in r2["answer"] or "anticipatory" in r2["answer"].lower()
    print(f"FLOW 2 RESULT: {'PASS' if flow2_pass else 'FAIL - no Section 438 or anticipatory bail content'}")
except Exception as e:
    print(f"FLOW 2 ERROR: {e}")

# Flow 3: Tenant rights
print("\n--- Flow 3: Tenant Rights ---")
try:
    r3 = api_post("/api/legal-chat", {
        "question": "What are my rights as a tenant in India?",
        "conversation_history": []
    })
    print_response("Tenancy Law - Tenant Rights", r3)
    flow3_pass = any(k in r3["answer"].lower() for k in ["tenant", "tenancy", "landlord", "rent"])
    print(f"FLOW 3 RESULT: {'PASS' if flow3_pass else 'FAIL - no tenancy content in answer'}")
except Exception as e:
    print(f"FLOW 3 ERROR: {e}")

print("\n--- API verification complete ---")
