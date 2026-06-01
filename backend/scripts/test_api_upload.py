"""Quick API test to verify the upload endpoint returns real OCR data."""
import urllib.request
import json
from pathlib import Path

pdf_bytes = Path("data/test/sample_rental.pdf").read_bytes()
boundary = b"----WebKitFormBoundary7MA4YWxkTrZu0gW"
body = (
    b"--" + boundary + b"\r\n"
    + b'Content-Disposition: form-data; name="file"; filename="sample_rental.pdf"\r\n'
    + b"Content-Type: application/pdf\r\n\r\n"
    + pdf_bytes
    + b"\r\n--" + boundary + b"--\r\n"
)

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/documents/upload",
    data=body,
    headers={"Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW"},
    method="POST",
)

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print("UPLOAD RESPONSE:")
        print(json.dumps(result, indent=2))
        status = result.get("extraction_status")
        pages = result.get("num_pages", 0)
        doc_type = result.get("metadata", {}).get("document_type")
        print(f"\nextraction_status: {status}")
        print(f"num_pages: {pages}")
        print(f"document_type: {doc_type}")
        if status == "completed" and pages > 0:
            print("\nTEST PASSED - Upload returned real OCR results!")
        else:
            print("\nTEST FAILED - Unexpected response")
except urllib.error.HTTPError as e:
    body_text = e.read().decode()
    print(f"HTTP {e.code}: {body_text}")
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    traceback.print_exc()
