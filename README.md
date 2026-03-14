# Kenexai Talent Analytics Platform Backend

This is the FastAPI backend for the Kenexai platform, structured using the "src layout" for scalability and clean code.

## Structure

```
APIs/
├── src/
│   └── app/
│       ├── api/          # Route handlers
│       ├── core/         # Core config & DB
│       ├── models/       # SQLAlchemy models
│       ├── schemas/       # Pydantic models
│       └── main.py       # Entrypoint
```

## Detailed Guide

For full instructions on local setup, Docker deployment, and API testing, see the [Running and Testing Guide](file:///C:/Users/mgkuv/.gemini/antigravity/brain/1320ee2d-3641-472f-934f-e10754f14b60/run_and_test.md).

## Quick Setup

1. **Navigate to the API folder**: `cd APIs`
2. Create a virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the app: `$env:PYTHONPATH="src"; uvicorn app.main:app --reload`
