# JETNET Prompt Recipes

Paste these into Cursor, GitHub Copilot Chat, or any AI coding assistant to scaffold
working JETNET integrations fast. Each prompt is self-contained and produces runnable
starter code.

| File | Use case | Primary endpoint |
|---|---|---|
| `01_golden_path_tail_lookup_app.md` | Next.js tail-number lookup UI | getRegNumber |
| `02_fbo_airport_activity_leads.md` | FBO ramp-to-lead enrichment | getRegNumber loop |
| `03_fleet_watchlist_alerts.md` | Fleet change monitoring alerts | getBulkAircraftExportPaged |
| `04_bulk_export_pipeline.md` | Hourly market intelligence feed | getBulkAircraftExportPaged |

## How to use

1. Open the prompt file.
2. Copy the entire contents.
3. Paste into Cursor Composer (Cmd+I), Copilot Chat, or Claude.
4. Fill in the `[PLACEHOLDER]` values for your specific project.
5. Iterate on the generated code.

## Tips

- These prompts reference `src/jetnet/session.py` and `src/jetnet/session.ts` -- make sure those files are in your project.
- For Cursor: paste into Composer with your project open so Cursor can read the session helpers.
- For standalone use: the prompts include the minimal auth pattern inline.
