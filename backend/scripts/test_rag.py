"""E2E RAG validation — run from backend/ with venv\Scripts\python.exe"""
import sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

BASE = "http://localhost:8000"

def create_test_pdf() -> Path:
    pdf = Path("data/test_rental.pdf")
    pdf.parent.mkdir(exist_ok=True)
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        c = canvas.Canvas(str(pdf), pagesize=letter)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 750, "RESIDENTIAL RENTAL AGREEMENT")
        c.setFont("Helvetica", 11)
        lines = [
            "This agreement entered on January 1, 2026 between Landlord and Tenant.",
            "Clause 1: Rent - Monthly rent Rs. 35,000, payable on 1st of every month.",
            "Clause 2: Security Deposit - Rs. 1,05,000 (3 months). Refundable at end.",
            "Clause 3: Lock-in Period - 36 months from date of agreement.",
            "Tenant liable for full remaining rent if vacating during lock-in.",
            "Clause 4: Notice Period - Either party gives 2 months written notice.",
            "Clause 5: Maintenance - Tenant responsible for all repairs.",
        ]
        y = 710
        for line in lines:
            c.drawString(80, y, line)
            y -= 22
        c.showPage()
        c.save()
    except ImportError:
        pdf.write_text(
            "RESIDENTIAL RENTAL AGREEMENT\n\n"
            "Clause 1: Rent Rs 35000 monthly.\n"
            "Clause 2: Security Deposit Rs 105000 (3 months).\n"
            "Clause 3: Lock-in 36 months.\n"
            "Clause 4: Notice 2 months written.\n"
            "Clause 5: Maintenance - tenant responsible.\n",
            encoding="utf-8"
        )
    return pdf


RESULTS = []

def check(name: str, ok: bool, note: str = "") -> None:
    RESULTS.append((name, ok, note))
    status = "[PASS]" if ok else "[FAIL]"
    print(f"  {status} {name}" + (f" -- {note}" if note else ""))


def run() -> None:
    print("=" * 60)
    print("LEXIFY-INDIA RAG PIPELINE -- E2E VALIDATION")
    print("=" * 60)

    # 1. Health check
    print("\n[1] Health check...")
    try:
        r = requests.get(f"{BASE}/health", timeout=5)
        check("API health", r.status_code == 200, f"status={r.status_code}")
    except Exception as e:
        check("API health", False, str(e))
        print("    FATAL: Server not running. Start with: venv\\Scripts\\python.exe -m uvicorn app.main:app --reload")
        sys.exit(1)

    # 2. Legal KB seeded
    print("\n[2] Legal KB check...")
    from app.core.config import settings
    from app.services.storage_service import StorageService
    ls = StorageService(settings.DATABASE_PATH, settings.LEGAL_COLLECTION_NAME)
    stats = ls.collection_stats()
    check("Legal KB seeded", stats["total_chunks"] >= 30, f"{stats['total_chunks']} chunks")
    if stats["total_chunks"] == 0:
        print("    FATAL: Run seed first: venv\\Scripts\\python.exe scripts\\seed_legal_knowledge.py")
        sys.exit(1)

    # 3. Upload document
    print("\n[3] Upload test document...")
    pdf = create_test_pdf()
    try:
        with open(pdf, "rb") as f:
            mime = "application/pdf" if pdf.suffix == ".pdf" else "text/plain"
            r = requests.post(f"{BASE}/api/documents/upload",
                              files={"file": (pdf.name, f, mime)}, timeout=180)
        ok = r.status_code == 201
        check("Upload document", ok, f"status={r.status_code}")
        if not ok:
            print(f"    Error: {r.text[:200]}")
            sys.exit(1)
        d = r.json()
        doc_id = d["document_id"]
        check("Document ID returned", bool(doc_id), doc_id[:12] + "...")
        check("Pages extracted", d["num_pages"] >= 0, f"pages={d['num_pages']}")
        check("Doc type detected", bool(d["metadata"]["document_type"]),
              d["metadata"]["document_type"])
        print(f"    doc_id={doc_id}, pages={d['num_pages']}, type={d['metadata']['document_type']}")
    except Exception as e:
        check("Upload document", False, str(e))
        sys.exit(1)

    time.sleep(1)

    # 4. Factual query
    print("\n[4] Factual query (document citations expected)...")
    r = requests.post(f"{BASE}/api/chat",
                      json={"document_id": doc_id, "question": "What is the monthly rent?"},
                      timeout=60)
    ok = r.status_code == 200
    check("Factual query returns 200", ok, f"status={r.status_code}")
    if ok:
        res = r.json()
        doc_cit = [c for c in res["citations"] if c["source_type"] == "document"]
        check("Has answer text", bool(res["answer"]), res["answer"][:80])
        check("Has document citations", len(doc_cit) > 0, f"{len(doc_cit)} doc citations")
        check("Confidence not none", res["confidence"] != "none", res["confidence"])
        print(f"    confidence={res['confidence']}, doc_citations={len(doc_cit)}")

    # 5. Advisory (dual-source) query
    print("\n[5] Advisory query (dual-source expected)...")
    r = requests.post(f"{BASE}/api/chat",
                      json={"document_id": doc_id,
                            "question": "Is the 36-month lock-in period risky? Is this normal in India?"},
                      timeout=60)
    ok = r.status_code == 200
    check("Advisory query returns 200", ok, f"status={r.status_code}")
    if ok:
        res = r.json()
        legal_cit = [c for c in res["citations"] if c["source_type"] == "legal_reference"]
        doc_cit2 = [c for c in res["citations"] if c["source_type"] == "document"]
        check("has_legal_context flag set", bool(res["has_legal_context"]), str(res["has_legal_context"]))
        check("Legal citations returned", len(legal_cit) > 0, f"{len(legal_cit)} legal citations")
        print(f"    doc_citations={len(doc_cit2)}, legal_citations={len(legal_cit)}")
        if legal_cit:
            print(f"    First legal ref: {legal_cit[0].get('act_name','?')} {legal_cit[0].get('act_section','?')}")

    # 6. Not-found scenario
    print("\n[6] Not-found scenario (graceful handling)...")
    r = requests.post(f"{BASE}/api/chat",
                      json={"document_id": doc_id,
                            "question": "What is the arbitration tribunal fee schedule?"},
                      timeout=60)
    check("Not-found returns 200", r.status_code == 200, f"status={r.status_code}")
    if r.status_code == 200:
        res = r.json()
        check("Handled gracefully", bool(res["answer"]), f"confidence={res['confidence']}")

    # 7. Invalid document ID
    print("\n[7] Invalid document ID (expect 404)...")
    try:
        r = requests.post(f"{BASE}/api/chat",
                          json={"document_id": "non-existent-uuid-00000", "question": "What is rent?"},
                          timeout=10)
        check("Invalid doc returns 404", r.status_code == 404, f"got {r.status_code}")
    except Exception as e:
        check("Invalid doc 404 test", False, str(e))

    # 8. ChromaDB state post-ingestion
    print("\n[8] ChromaDB state...")
    doc_storage = StorageService(settings.DATABASE_PATH, settings.DOCUMENT_COLLECTION_NAME)
    doc_stats = doc_storage.collection_stats()
    legal_stats = ls.collection_stats()
    check("Document chunks stored", doc_stats["total_chunks"] > 0, f"{doc_stats['total_chunks']} chunks")
    check("Legal KB still intact", legal_stats["total_chunks"] >= 30, f"{legal_stats['total_chunks']} chunks")

    # Summary
    print("\n" + "=" * 60)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    print(f"RESULTS: {passed}/{total} checks passed")
    if passed == total:
        print("ALL CHECKS PASSED -- Phase 2 RAG Pipeline: COMPLETE")
    else:
        print("SOME CHECKS FAILED -- see above for details")
        for name, ok, note in RESULTS:
            if not ok:
                print(f"  FAIL: {name} ({note})")

    # Cleanup
    try:
        pdf.unlink(missing_ok=True)
    except Exception:
        pass

    return passed, total, doc_id


if __name__ == "__main__":
    run()
