# JETNET API Prompts

Pre-built prompts for AI coding assistants (Cursor, Copilot, ChatGPT, Claude, etc.).

## How to use

1. Pick a prompt that matches your use case
2. Copy the entire file contents
3. Paste into your AI coding assistant as a new conversation
4. Set your environment variables (`JETNET_EMAIL`, `JETNET_PASSWORD`, `JETNET_BASE_URL`)
5. Let the AI build the app

## Available prompts

| File | Use case |
|------|----------|
| `01_golden_path_tail_lookup_app.md` | Enter a tail number, get a full aircraft profile with owner/operator and flight activity |
| `02_fbo_airport_activity_leads.md` | Airport-based flight activity for FBO lead generation and ramp contact targeting |
| `03_fleet_watchlist_alerts.md` | Monitor a fleet by model, alert on ownership changes |
| `04_bulk_export_pipeline.md` | Bulk aircraft export with pagination and incremental sync |

## Prompt structure

Every prompt follows the same standard sections:

- **App goal** — what the app does in one sentence
- **UI screens** — what the user sees
- **API workflow** — ordered sequence of JETNET API calls
- **Response shaping contract** — normalized output shape for the frontend
- **Auth/session rules** — must use session helpers + `/getAccountInfo` validation
- **Error rules** — responsestatus handling, retry logic
- **Definition of done** — acceptance criteria checklist
- **Do not do** — common mistakes to avoid

## Dependencies

All prompts reference the session helpers in `src/jetnet/session.py` (Python) and `src/jetnet/session.js` (JavaScript). These handle login, token refresh, `/getAccountInfo` validation, and error normalization automatically.
