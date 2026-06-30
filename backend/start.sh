#!/bin/sh
set -e

# Seed legal knowledge on first boot (no-op if collection already populated)
python scripts/seed_legal_knowledge.py || true

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
