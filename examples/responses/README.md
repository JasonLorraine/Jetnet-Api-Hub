# Examples -- Known-Good Request/Response Pairs

Each file contains a real or representative request body, the actual response
structure, and inline notes on field names, gotchas, and response keys.

| File | Endpoint | Tier | Key gotcha |
|------|----------|------|------------|
| `tail-lookup.json` | getRegNumber | A | `aircraftresult` key, flat `companyrelation` |
| `relationships-single.json` | getRelationships (single) | A | Nested `company/contact`, `relationtype` |
| `relationships-bulk.json` | getRelationships (bulk aclist) | B | `aircraftcount` vs `count` |
| `aircraft-list.json` | getAircraftList | A | Not paged, string booleans |
| `history-paged.json` | getHistoryListPaged | B | 1-based page, `maxpages`, nested structure |
| `flight-data-paged.json` | getFlightDataPaged | A/B | Dynamic dates, `flightdata` key |
| `event-list-paged.json` | getEventListPaged | B | Strict enums, use `[]` to get all |
| `condensed-owner-operators.json` | getCondensedOwnerOperators | A | `aircraftowneroperators` key, `actiondate` sync |
| `bulk-export-paged.json` | getBulkAircraftExportPaged | B | Always paged, `actiondate` for incremental |
| `model-market-trends.json` | getModelMarketTrends | B | `modelMarketTrends` camelCase M |
| `model-performance-specs.json` | getModelPerformanceSpecs | A | Multi-model comparison via `modlist` |
| `fractional-owner-report.json` | getAcCompanyFractionalReportPaged | B | `aircraftcompfractionalrefs` key; one row per relation; filter `fractionPercentOwned != "0.00"` for actual owners |
| `fbo-contact-lookup.json` | getRegNumber (FBO ramp workflow) | A | Flat `companyrelation` schema; filter `contacttitle` for Chief Pilot / Dir of Aviation / Scheduler |
| `bulk-export-hourly.json` | getBulkAircraftExportPaged (hourly poll) | B | `maxpages: 0` quirk; datetime actiondate; flat `owr*`/`opr*`/`chp*` prefixed schema; `forsale: "Y"/"N"` |
| `history-transaction-search.json` | getHistoryListPaged (comps/sale search) | B | `transtype` categories vs response strings; `transretail`; Seller/Purchaser/Broker relation types; `maxpages: 0` on small sets |
