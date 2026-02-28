# JETNET MCP Server — AI Agent Integration

> **The first aviation data API with native AI agent support.**
> Let Claude, Cursor, Copilot, and any MCP-compatible agent query JETNET data
> with natural language. No code required on the user's side.

---

## What is MCP?

The **Model Context Protocol** (MCP) is an open standard created by Anthropic that lets
AI agents call external tools directly. Instead of a developer writing API integration
code, the AI agent reads the tool definitions, understands the parameters, and makes
the calls itself.

**Before MCP:** Developer reads docs → writes code → tests → deploys → user gets data.
**With MCP:** User asks Claude "What G650s are for sale?" → Claude calls JETNET → user gets data.

This makes JETNET accessible to:
- **Vibe coders** who build by talking to AI instead of writing code
- **Business users** who ask questions in natural language through Claude Desktop
- **AI agents** in Cursor, Copilot, Windsurf, and any MCP client
- **Automation pipelines** where LLMs orchestrate multi-step data workflows

---

## Quick Start

### Option A: Claude Desktop (Local — stdio)

1. **Install dependencies:**
   ```bash
   pip install mcp httpx pydantic
   ```

2. **Configure Claude Desktop** — add to your `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "jetnet": {
         "command": "python",
         "args": ["/path/to/jetnet_mcp.py"],
         "env": {
           "JETNET_EMAIL": "your_email@example.com",
           "JETNET_PASSWORD": "your_password"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop.** You'll see the JETNET tools available in the tool picker.

4. **Try it:** Ask Claude *"Look up tail number N650GD and show me who owns it."*

### Option B: Cursor / Copilot (Local — stdio)

1. **Install:** `pip install mcp httpx pydantic`

2. **Add to your project's `.cursor/mcp.json`:**
   ```json
   {
     "mcpServers": {
       "jetnet": {
         "command": "python",
         "args": ["./jetnet_mcp.py"],
         "env": {
           "JETNET_EMAIL": "your_email@example.com",
           "JETNET_PASSWORD": "your_password"
         }
       }
     }
   }
   ```

3. **In Cursor**, ask: *"Find all Challenger 350s for sale and show me market trends for the last 2 years."*

### Option C: Remote Server (Streamable HTTP — multi-client)

For shared deployments, CI/CD pipelines, or multi-user environments:

```bash
TRANSPORT=http \
PORT=8000 \
JETNET_EMAIL=your_email@example.com \
JETNET_PASSWORD=your_password \
python jetnet_mcp.py
```

Then point any MCP client at `http://your-server:8000/mcp`.

---

## Available Tools

The MCP server exposes **8 tools** that cover the most common JETNET workflows.
Each tool handles authentication, token refresh, pagination, and error handling
automatically — the AI agent just calls the tool with the right parameters.

### Core Tools

| Tool | What It Does | Key Parameters |
|------|-------------|----------------|
| `jetnet_golden_path` | **Complete aircraft profile** — tail lookup + owner/operator + pictures in one call. The recommended starting point. | `registration` |
| `jetnet_lookup_aircraft` | Look up a single aircraft by tail/registration number. Returns `aircraftid` needed by all other tools. | `registration` |
| `jetnet_get_relationships` | Get owner, operator, manager, trustee relationships for an aircraft. | `aircraftid` |
| `jetnet_get_flight_data` | Flight activity within a date range: departure/arrival airports, dates, utilization. | `aircraftid`, `start_date`, `end_date` |

### Search & Analysis Tools

| Tool | What It Does | Key Parameters |
|------|-------------|----------------|
| `jetnet_search_fleet` | Search the fleet database by model, make, for-sale status, country. Find inventory and listings. | `modlist`, `for_sale`, `country` |
| `jetnet_get_history` | Transaction history: sales, deliveries, registrations within a date range. | `modlist` or `aclist`, date range |
| `jetnet_get_market_trends` | Market analytics: for-sale count, avg asking price, days on market over time. | `modelid`, date range |

### Utility Tools

| Tool | What It Does | Key Parameters |
|------|-------------|----------------|
| `jetnet_search_models` | Find JETNET model IDs (AMODID) by name, make, or ICAO code. Use these IDs in `modlist`. | `query` (e.g., "G550") |

---

## The Golden Path via MCP

The **Golden Path** is the most common JETNET workflow: start with a tail number,
get a complete aircraft profile. The `jetnet_golden_path` tool executes this entire
workflow in a single call:

```
User: "Tell me everything about N650GD"

Claude calls: jetnet_golden_path(registration="N650GD")

Claude responds with:
  - Aircraft specs (make, model, serial, year, lifecycle status)
  - Owner/Operator (company name, location, relationship type)
  - Pictures (URLs to aircraft photos)
```

For more granular control, agents can call the individual tools:

```
1. jetnet_lookup_aircraft(registration="N650GD")     → aircraftid = 211461
2. jetnet_get_relationships(aircraftid=211461)        → owner, operator details
3. jetnet_get_flight_data(aircraftid=211461, ...)     → flight history
4. jetnet_get_history(aclist=[211461], ...)            → transaction history
```

---

## Example Conversations

### Aircraft Research
> **User:** "Look up VP-BDJ and tell me who owns it, when it was manufactured,
> and if it's for sale."
>
> **Claude:** *calls `jetnet_golden_path(registration="VP-BDJ")`*

### Market Analysis
> **User:** "How many G650s are for sale right now? What's the average asking price
> trend over the last 3 years?"
>
> **Claude:** *calls `jetnet_search_models(query="G650")` → gets AMODID=278*
> *then calls `jetnet_search_fleet(modlist=[278], for_sale="true")`*
> *then calls `jetnet_get_market_trends(modelid=278, start_date="01/01/2023", end_date="02/27/2026")`*

### Fleet Intelligence
> **User:** "Find all Challenger 350s based in Canada."
>
> **Claude:** *calls `jetnet_search_models(query="Challenger 350")` → AMODID=634*
> *then calls `jetnet_search_fleet(modlist=[634], country="Canada")`*

### Transaction Diligence
> **User:** "Show me all G550 transactions in 2024."
>
> **Claude:** *calls `jetnet_get_history(modlist=[145], start_date="01/01/2024", end_date="12/31/2024")`*

### Flight Activity
> **User:** "Where has N1KE been flying in the last 6 months?"
>
> **Claude:** *calls `jetnet_lookup_aircraft(registration="N1KE")` → aircraftid*
> *then calls `jetnet_get_flight_data(aircraftid=..., start_date="08/27/2025", end_date="02/27/2026")`*

---

## Architecture

```
+---------------------+     MCP Protocol      +------------------+
|                     |    (stdio or HTTP)     |                  |
|  Claude Desktop     |<---------------------->|  jetnet_mcp.py   |
|  Cursor / Copilot   |    Tool calls &        |                  |
|  Any MCP Client     |    Responses           |  - Auth/refresh  |
|                     |                        |  - Pagination    |
+---------------------+                        |  - Error handling|
                                               |  - Formatting    |
                                               +--------+---------+
                                                        | HTTPS
                                                        v
                                               +------------------+
                                               | JETNET API       |
                                               | customer.        |
                                               | jetnetconnect.com|
                                               +------------------+
```

### What the MCP server handles for you:
- **Authentication**: Logs in with `emailAddress` (capital A — the #1 gotcha)
- **Token lifecycle**: Proactive refresh at 50 minutes, auto re-login on `INVALID SECURITY TOKEN`
- **apiToken placement**: Always in the URL path, never in headers or body
- **Pagination**: Automatically fetches all pages for paged endpoints
- **Response status checks**: HTTP 200 doesn't mean success — always checks `responsestatus`
- **Date formatting**: Validates `MM/DD/YYYY` with leading zeros
- **Error messages**: Actionable guidance when things go wrong

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JETNET_EMAIL` | Yes | — | Your JETNET login email |
| `JETNET_PASSWORD` | Yes | — | Your JETNET password |
| `JETNET_BASE_URL` | No | `https://customer.jetnetconnect.com` | API base URL |
| `TRANSPORT` | No | `stdio` | Transport: `stdio` (local) or `http` (remote) |
| `PORT` | No | `8000` | HTTP port (only used when TRANSPORT=http) |

### Security Best Practices

- **Never commit credentials** to source control. Use environment variables or a secrets manager.
- **Use stdio transport** for single-user, local setups (Claude Desktop, Cursor). Credentials stay on your machine.
- **Use HTTP transport** only behind a VPN or with additional authentication for shared/remote deployments.
- **Token rotation**: JETNET tokens expire at 60 minutes. The MCP server refreshes proactively at 50 minutes. No action needed from the user.

---

## Extending the Server

### Adding New Tools

To add a tool, follow this pattern:

```python
from pydantic import BaseModel, Field

class MyNewInput(BaseModel):
    """Input description."""
    param: str = Field(..., description="What this param does")

@mcp.tool(
    name="jetnet_my_new_tool",
    annotations={
        "title": "Human-Readable Title",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def jetnet_my_new_tool(params: MyNewInput, ctx=None) -> str:
    """Comprehensive description. Include what it does, what it returns,
    and when to use it vs other tools."""
    session = _get_session(ctx)
    data = await session.request("GET", "/api/...")
    return json.dumps(data, indent=2)
```

### Common JETNET Endpoints Not Yet Exposed

These endpoints could be added as tools following the same pattern:

| Endpoint | Use Case | Priority |
|----------|----------|----------|
| `getCondensedSnapshot` | Fleet snapshot at a point in time | High |
| `getCompanyList` | Search companies by name/type | Medium |
| `getContactList` | Search contacts | Medium |
| `getModelPerformanceSpecs` | Aircraft specs (range, speed, cabin) | Medium |
| `getModelOperationCosts` | Annual operating costs | Medium |
| `getAirportList` | Airport reference data | Low |
| `getBulkAircraftExportPaged` | Bulk data sync (Tier B — not for interactive) | Low |

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `Missing JETNET credentials` | Env vars not set | Set `JETNET_EMAIL` and `JETNET_PASSWORD` |
| `JETNET API error: ERROR: INVALID SECURITY TOKEN` | Token expired + auto-retry failed | Check credentials are correct. Server auto-retries once. |
| `No aircraft found` | Bad tail number or trailing whitespace | Verify the registration. The tool auto-strips whitespace and uppercases. |
| `No models found` | Search too specific | Try broader terms: "Gulfstream" instead of "G-550" |
| `Response truncated` | Result exceeds 50K chars | Use filters to narrow results, or request `json` format and process programmatically |
| Tool not appearing in Claude | Config file error | Verify `claude_desktop_config.json` path and restart Claude Desktop |
| `Connection refused` on HTTP | Wrong port or not running | Verify `TRANSPORT=http` and check the port |

---

## Common Model IDs (Quick Reference)

| Aircraft | AMODID | ICAO |
|----------|--------|------|
| Gulfstream G550 | 145 | GLF5 |
| Gulfstream G650/ER | 278 | GLF6 |
| Bombardier Challenger 350 | 634 | CL35 |
| Bombardier Global 7500 | 753 | GL7T |
| Dassault Falcon 8X | 704 | FA8X |
| Dassault Falcon 900LX | 318 | F900 |
| Cessna Citation XLS+ | 326 | C56X |
| Cessna Citation Latitude | 680 | C68A |
| Beechcraft King Air 350 | 255 | B350 |
| Embraer Praetor 600 | 780 | E545 |

Use `jetnet_search_models(query="...")` for the complete list of 872+ models.

---

## File Placement in the Repo

```
jetnet-api-docs/
├── mcp/
│   ├── README.md              ← This file
│   ├── jetnet_mcp.py          ← Python MCP server (stdio + HTTP)
│   ├── requirements.txt       ← mcp, httpx, pydantic
│   └── claude_desktop_config.example.json
├── ...existing files...
```

---

## What This Unlocks

With the MCP server in place, JETNET becomes **the first aviation data API that
AI agents can use natively**. Here's what that means in practice:

1. **Zero-code access**: Business users ask questions in natural language. No integration needed.
2. **AI-assisted development**: Developers in Cursor say "build me a fleet dashboard for G650s" and the AI writes the code AND queries the data to test it.
3. **Multi-step workflows**: An AI agent can chain tools — look up a tail → check ownership → pull flight data → get market comps — in a single conversation.
4. **Competitive moat**: No other aviation data provider offers this. FlightAware, Cirium, and Amstat require traditional API integrations.

---

## License

MIT — same as the parent repository.
