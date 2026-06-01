"""Test that invalid file types are rejected with a proper error."""
import urllib.request
import json
import urllib.error

boundary = b"----TestBoundary"
body = (
    b"--" + boundary + b"\r\n"
    + b'Content-Disposition: form-data; name="file"; filename="bad.txt"\r\n'
    + b"Content-Type: text/plain\r\n\r\nnot a pdf\r\n"
    + b"--" + boundary + b"--\r\n"
)

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/documents/upload",
    data=body,
    headers={"Content-Type": "multipart/form-data; boundary=----TestBoundary"},
    method="POST",
)

try:
    urllib.request.urlopen(req)
    print("FAIL: Should have rejected invalid file type")
except urllib.error.HTTPError as e:
    result = json.loads(e.read())
    code = result.get("error", {}).get("code")
    print(f"PASS: Got expected error for invalid file type -> code: {code}")
    print(json.dumps(result, indent=2))
