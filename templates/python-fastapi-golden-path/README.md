# JETNET Golden Path — FastAPI Template

1. Copy `.env.example` to `.env` and fill in your JETNET credentials.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `uvicorn main:app --reload`
4. Open `http://localhost:8000/lookup?tail=N12345` in your browser.

Returns a normalized `GoldenPathResult` with aircraft, owner, operator, and flight activity.

See `docs/response-shapes.md` for the full response contract.
See `src/jetnet/session.py` for the session helper used under the hood.
