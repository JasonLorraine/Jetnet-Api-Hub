# JETNET Tail Lookup — Next.js Template

1. `cp .env.example .env.local` and fill in your JETNET credentials
2. `npm install`
3. `npm run dev`
4. Open `http://localhost:3000`
5. Enter a tail number (e.g. `N123AB`) and click **Lookup**

Uses the session helper pattern from `src/jetnet/session.js`.
Returns a normalized `GoldenPathResult` shape (see `docs/response-shapes.md`).
