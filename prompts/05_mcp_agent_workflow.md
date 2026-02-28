# Prompt 05: MCP Agent Workflow -- Natural Language Aviation Intelligence

## Use Case
Build an AI-powered aviation research assistant that uses JETNET's MCP server
to answer complex, multi-step questions about aircraft, fleet composition,
ownership, and market trends -- all through natural language.

## Prerequisites
- JETNET MCP server running (see `mcp/README.md`)
- Claude Desktop, Cursor, or any MCP-compatible client
- JETNET_EMAIL and JETNET_PASSWORD configured

## Example Queries to Test

### Single-Step
- "Look up tail number N650GD"
- "What G650s are for sale?"
- "Find the model ID for Citation Latitude"
- "Check if my JETNET connection is working"
- "Get the specs for a Challenger 350"

### Multi-Step (agent chains tools automatically)
- "Look up VP-BDJ, show me who owns it, and pull their flight activity for the last 6 months"
- "How many Challenger 350s are for sale in Canada? What's the average asking price trend over 3 years?"
- "Find all G550 transactions in 2024 and summarize the market activity"
- "Compare the for-sale inventory of G650 vs Global 7500 over the last 2 years"
- "Get a fleet snapshot of all G650s as of January 2020, then compare to January 2025"

### Complex Research
- "I'm evaluating a 2018 G650ER for purchase. Pull the aircraft profile, check
  the transaction history for comparable sales, and show me market trends for the
  model over the last 3 years. What should I expect to pay?"
- "Build me a report on the Challenger 350 fleet: total in operation, how many
  for sale, average days on market, and top 5 countries by fleet size."
- "Compare the performance specs of the G650 vs Global 7500 vs Falcon 8X.
  Which has the best range? Which has the largest cabin?"

## How It Works
The MCP server exposes 11 tools. The AI agent reads the tool descriptions,
understands what parameters each tool needs, and chains them together to answer
complex questions. The agent handles:
- Finding model IDs via `jetnet_search_models` before calling fleet/history tools
- Extracting `aircraftid` from lookups before calling relationship/flight tools
- Formatting dates as MM/DD/YYYY with leading zeros
- Choosing markdown vs json format based on context
- Verifying connection health with `jetnet_health_check` when errors occur

## Available Tools

| Tool | Purpose |
|------|---------|
| `jetnet_golden_path` | Complete aircraft profile in one call |
| `jetnet_lookup_aircraft` | Tail number lookup, returns aircraftid |
| `jetnet_get_relationships` | Owner/operator/manager relationships |
| `jetnet_get_flight_data` | Flight activity within a date range |
| `jetnet_search_fleet` | Search by model, for-sale, country |
| `jetnet_get_history` | Transaction history (sales, deliveries) |
| `jetnet_get_market_trends` | Pricing, days-on-market, inventory over time |
| `jetnet_search_models` | Find model IDs (AMODID) by name/ICAO |
| `jetnet_get_snapshot` | Fleet snapshot at a point in time |
| `jetnet_get_model_specs` | Performance specs: range, speed, cabin, payload |
| `jetnet_health_check` | Verify JETNET connection is working |

## Guardrails Built Into the MCP Server
All JETNET guardrails are enforced automatically:
- `emailAddress` with capital A
- `apiToken` in URL path only
- `responsestatus` checked on every response
- Token refresh at 50 minutes, auto-retry on INVALID SECURITY TOKEN
- `transtype: ["None"]` for all transaction types
- Date validation (MM/DD/YYYY with leading zeros)
