import requests
import json
import os

BASE_URL = "http://localhost:8000"

print("--- Flow 4: Upload ---")
file_path = "test_lease.pdf"
with open(file_path, "rb") as f:
    resp = requests.post(f"{BASE_URL}/api/documents/upload", files={"file": f})
    data = resp.json()
    
print("Upload response:", data)
doc_id = data.get("document_id")
print("Document ID:", doc_id)

print("\n--- Flow 5: Document Chat ---")
chat_payload = {
    "document_id": doc_id,
    "question": "What is the rent?",
    "conversation_history": []
}
chat_resp = requests.post(f"{BASE_URL}/api/chat", json=chat_payload)
chat_data = chat_resp.json()
print("Chat answer:", chat_data.get("answer"))
print("Citations:", len(chat_data.get("citations", [])))
