# Start Here

New to the JETNET API? Pick your path and get running in minutes.

---

## What You Need

- A JETNET API account (email + password)
- Base URL: `https://customer.jetnetconnect.com`
- Environment variables set: `JETNET_EMAIL`, `JETNET_PASSWORD`

## How Auth Works

1. POST credentials to `/api/Admin/APILogin` (field is `emailAddress` with a capital A)
2. Response gives you two tokens: `bearerToken` and `apiToken`
3. Every call after login: `bearerToken` in the `Authorization` header, `apiToken` in the URL path
4. Tokens expire after 60 minutes
5. Validate your session with `/api/Admin/getAccountInfo/{apiToken}` before long workflows
6. On `INVALID SECURITY TOKEN`: re-login once and retry. Never loop.

## HTTP 200 Does Not Mean Success

JETNET returns HTTP 200 even for errors. Always check `responsestatus` in the JSON body:

```
if responsestatus starts with "ERROR" → it failed, even though HTTP said 200
```

---

## Choose Your Path

> **New to APIs?** Start with the [Junior Dev Guide](docs/junior-dev-guide.md) -- it teaches only the 4 endpoints that matter, with copy-paste examples and the 5 mistakes every new developer hits.

### Path A: "I want a demo UI in 5 minutes"

You want to see a working app, type in a tail number, and get results.

1. Go to [`templates/nextjs-tail-lookup/`](templates/nextjs-tail-lookup/)
2. Copy `.env.example` to `.env.local`, fill in your credentials
3. `npm install && npm run dev`
4. Open `http://localhost:3000`, enter a tail number

That's it. You have a working aircraft lookup app.

**Also available:** [`templates/python-fastapi-golden-path/`](templates/python-fastapi-golden-path/) if you prefer Python.

---

### Path B: "I want bulk/export data"

You want to sync fleet data, export history, or build analytics pipelines.

1. Read the [Pagination Guide](docs/pagination.md) (1-based pages, `maxpages` loop)
2. Look at [`examples/python/07_bulk_export.py`](examples/python/07_bulk_export.py) for the pattern
3. Use [`scripts/paginate.py`](scripts/paginate.py) to handle pagination automatically
4. For a full pipeline prompt, paste [`prompts/04_bulk_export_pipeline.md`](prompts/04_bulk_export_pipeline.md) into your IDE agent

Key gotcha: `getBulkAircraftExportPaged` returns `maxpages: 0` for single-page results. Use `max(maxpages, 1)`.

---

### Path C: "I want CRM enrichment"

You want to enrich contacts, generate leads, or monitor ownership changes.

1. For FBO/airport leads: paste [`prompts/02_fbo_airport_activity_leads.md`](prompts/02_fbo_airport_activity_leads.md) into your IDE agent
2. For fleet watchlist/alerts: paste [`prompts/03_fleet_watchlist_alerts.md`](prompts/03_fleet_watchlist_alerts.md) into your IDE agent
3. Use the [`templates/python-fastapi-golden-path/`](templates/python-fastapi-golden-path/) as your backend starting point
4. See [`snippets/ownership.md`](snippets/ownership.md) for quick copy-paste relationship lookups

---

### Path D: "I'm building an AI agent / code agent"

> **Want zero-code MCP instead?** Skip to [Path E](#path-e-i-want-zero-code-ai-agent-access-mcp) below.

You want to give an AI agent (Cursor, Copilot, custom GPT, LangChain, CrewAI, or your own) the ability to call the JETNET API.

**Quickest path:** Feed [`llms.txt`](llms.txt) into your agent's context window. It contains every rule, gotcha, enum value, and response key in ~150 lines. For agents with large context windows, use [`llms-full.txt`](llms-full.txt) (~3100 lines, all docs).

1. **Feed your agent the rules:** Copy [`src/jetnet/session.py`](src/jetnet/session.py) (Python) or [`src/jetnet/session.ts`](src/jetnet/session.ts) (TypeScript) into your agent's context -- it handles auth, token refresh, and error normalization automatically
2. **Give it the model reference:** Load [`references/model-id-table.json`](references/model-id-table.json) so your agent can resolve aircraft makes/models to the correct `modlist` IDs (872 models across 67 makes)
3. **Use the prompt recipes:** Paste any of the [`prompts/`](prompts/) into your agent as system instructions -- they are self-contained with API call sequences, error rules, and response shapes
4. **Validate with evals:** Use [`evals/evals.json`](evals/evals.json) to test that your agent handles JETNET responses correctly
5. **Normalize responses:** Use the contracts in [`docs/response-shapes.md`](docs/response-shapes.md) to ensure your agent outputs consistent shapes (AircraftCard, CompanyCard, GoldenPathResult)

**Key files for agent context windows:**

| File | Purpose | Size |
|------|---------|------|
| [`llms.txt`](llms.txt) | Single-file AI reference (all rules + gotchas + enums) | ~150 lines |
| [`llms-full.txt`](llms-full.txt) | Complete reference (all docs concatenated) | ~3100 lines |
| [`src/jetnet/session.py`](src/jetnet/session.py) | Auth + session management (drop into agent) | ~240 lines |
| [`references/model-id-table.json`](references/model-id-table.json) | Model ID lookup (agent can resolve "G550" → modlist: [278]) | 872 entries |
| [`docs/response-shapes.md`](docs/response-shapes.md) | Response contracts for structured output | ~440 lines |
| [`docs/common-mistakes.md`](docs/common-mistakes.md) | Guardrails to prevent agent errors | ~170 lines |
| [`evals/evals.json`](evals/evals.json) | Test cases for agent validation | 3 cases |
| [`prompts/`](prompts/) | 4 ready-to-use system prompts | ~200 lines each |

**Quick agent setup pattern:**

```python
context = open("llms.txt").read()
model_ids = json.load(open("references/model-id-table.json"))

system_prompt = open("prompts/01_golden_path_tail_lookup_app.md").read()
```

---

### Path E: "I want zero-code AI agent access (MCP)"

You want to connect Claude Desktop, Cursor, or any MCP-compatible AI directly to JETNET. No integration code needed -- the AI calls JETNET tools natively.

**Start here:** [`mcp/README.md`](mcp/README.md)

**What you'll get in 5 minutes:**
1. Install: `pip install mcp httpx pydantic`
2. Configure your MCP client (Claude Desktop, Cursor, etc.)
3. Ask: "Look up N650GD and show me who owns it"
4. Done. The AI handles auth, token refresh, pagination, and formatting.

**Best for:** Business users who want data without writing code, developers using AI-assisted coding tools, and automation pipelines where LLMs orchestrate workflows.

---

## Session Helpers

We provide production-ready session modules that handle login, token refresh, and validation automatically:

- **Python:** [`src/jetnet/session.py`](src/jetnet/session.py)
- **TypeScript:** [`src/jetnet/session.ts`](src/jetnet/session.ts)

These use `/api/Admin/getAccountInfo` as a lightweight health check to validate your token before long workflows, and auto re-login once if the token has expired.

---

## Where to Go Next

| Resource | When to use it |
|----------|---------------|
| [Authentication Guide](docs/authentication.md) | Deep dive into tokens, refresh, retry |
| [Response Shapes](docs/response-shapes.md) | Normalized objects for your UI (AircraftCard, CompanyCard, etc.) |
| [Common Mistakes](docs/common-mistakes.md) | Save yourself hours of debugging |
| [Prompts](prompts/) | Paste into Cursor/Copilot to generate working apps |
| [Model ID Lookup](references/model-ids.md) | Find the right `modlist` IDs for any aircraft make/model |
| [Evals](evals/evals.json) | Test cases for validating AI agent responses |
| [MCP Server](mcp/README.md) | Zero-code AI agent access to JETNET (Claude, Cursor, Copilot) |
| [Full Endpoint Reference](references/endpoints.md) | Every endpoint with all parameters |
