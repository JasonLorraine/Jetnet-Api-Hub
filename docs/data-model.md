# JETNET Data Model: Aircraft, Companies, and Contacts

How aircraft, companies, and contacts connect through relationships -- and how to traverse the graph to build complete intelligence profiles.

---

## Core Entities

JETNET's relational model revolves around four primary identifiers:

| Entity | Primary Key | Description |
|--------|-------------|-------------|
| Aircraft | `aircraftid` | Unique aircraft identifier (stable, never changes) |
| Company | `companyid` | Unique company identifier |
| Contact | `contactid` | Unique individual/person identifier |
| Relationship | Derived / Join | Defines how Aircraft ↔ Company ↔ Contact connect |

These IDs are stable and should always be stored in downstream systems. See [ID System](id-system.md) for details.

---

## The Entity Graph

Relationships are graph-based, not linear:

```
Aircraft (aircraftid)
       ↕
Company (companyid)
       ↕
Contact (contactid)
```

Each link has a **relationship type** attached to it. One aircraft can have multiple companies. One company can have multiple aircraft. One company can have many contacts. This is a graph, not a table.

---

## Aircraft ↔ Company (`aircraftid` → `companyid`)

This defines ownership and operational structure.

### Common Relationship Types

| Relationship Type | Meaning |
|-------------------|---------|
| Owner | Legal registered owner |
| Operator | Company operating the aircraft |
| Manager | Management company |
| Lessee | Leasing entity |
| Fractional Owner | Shared ownership participant |
| Parent Company | Corporate hierarchy link |

### How to Retrieve

1. Look up aircraft by registration → get `aircraftid`
2. Call `getRelationships` with the `aircraftid`
3. Extract: `companyid`, relationship type, `isoperator` flag

```
GET /api/Aircraft/getRegNumber/{regnbr}/{apiToken}     → aircraftid
POST /api/Aircraft/getRelationships/{apiToken}          → companyrelationships[]
GET /api/Company/getCompany/{companyid}/{apiToken}      → company profile
```

**Response key:** `companyrelationships` — an array where each entry has `companyid`, `companyname`, `relationtype`, and `isoperator` ("Y"/"N" as a string).

> **Gotcha:** `isoperator` is a string `"Y"` or `"N"`, not a boolean. See [Common Mistakes](common-mistakes.md).

---

## Company ↔ Contact (`companyid` → `contactid`)

This defines who works at or represents a company.

### Common Contact Roles

| Role | Meaning |
|------|---------|
| Executive | C-level leadership |
| Chief Pilot | Operational authority |
| Director of Maintenance | Maintenance authority |
| Aviation Manager | Aircraft oversight |
| Broker | Sales contact |
| Fleet Manager | Asset oversight |

### How to Retrieve

1. Get company via `companyid`
2. Call company-contact relationship endpoint
3. Extract: `contactid`, title, department

Then call the contact endpoint with `contactid` for the full profile.

```
POST /api/Contact/getContactListPaged/{apiToken}/{pagesize}/{pagenumber}
     → contactlist[]
GET /api/Contact/getContact/{contactid}/{apiToken}
     → full contact profile
```

**Response keys:** `contactlist` (from getContactListPaged), `contactIdentification` (from getIdentification).

> **Gotcha:** Contact search uses `getContactListPaged` → response key `contactlist`. Company search uses `getCompanyListPaged` → response key `companylist`. These are different from `getContactList` → `contacts` and `getCompanyList` → `companies`. See [Pagination](pagination.md).

---

## Aircraft ↔ Contact (Indirect Link)

There is no direct Aircraft → Contact join. The path is always:

```
Aircraft → Company → Contact
```

Example: Aircraft `aircraftid` 123 → Operator `companyid` 456 → Chief Pilot `contactid` 789. That Chief Pilot is operationally responsible for the aircraft.

For direct aircraft-contact relationships, use `getContAircraftRelationships` (see [Contacts](contacts.md)).

---

## Full Golden Path: Building the Complete Picture

### Step 1: Start with Aircraft

Input: `regnbr` (tail number) or `serialnbr`

```
GET /api/Aircraft/getRegNumber/{regnbr}/{apiToken}
```

Output: `aircraftid`, make, model, serial number, year manufactured, lifecycle status.

### Step 2: Get All Aircraft Relationships

```
POST /api/Aircraft/getRelationships/{apiToken}
Body: { "aclist": [aircraftid] }
```

Output: Array of company relationships with types.

Store as:
```json
[
  { "companyid": 456, "relationtype": "Owner" },
  { "companyid": 789, "relationtype": "Operator" }
]
```

### Step 3: Hydrate Company Records

For each `companyid`:

```
GET /api/Company/getCompany/{companyid}/{apiToken}
```

Output: Company name, location, segment, fleet size.

### Step 4: Get Contacts Per Company

For each `companyid`:

```
POST /api/Contact/getContactListPaged/{apiToken}/{pagesize}/{pagenumber}
Body: { "companyid": companyid }
```

Output: Contacts associated with that company, with titles and roles.

### Step 5: Build the Network Object

```json
{
  "aircraft": {
    "aircraftid": 123,
    "regnbr": "N650GD",
    "make": "Gulfstream",
    "model": "G650"
  },
  "companies": [
    {
      "companyid": 456,
      "companyname": "XYZ Holdings",
      "relationtype": "Owner",
      "contacts": [
        {
          "contactid": 789,
          "name": "John Smith",
          "title": "CEO"
        }
      ]
    }
  ]
}
```

This object represents the full ecosystem around that aircraft.

---

## Hierarchical Considerations

Companies may have parent-child relationships:

```
Holding Company (companyid: 100)
    ↓
Operating Entity (companyid: 200)
    ↓
Aircraft (aircraftid: 300)
```

To build accurate intelligence:

- Always check parent company via `getRelatedcompanies`
- Store both child `companyid` and parent `companyid`
- Do not assume operator = ultimate owner

---

## Time Sensitivity

Relationships can be current, historical, or pending.

Important fields:

- `startdate`
- `enddate`
- `iscurrent`

**For CRM use cases:** Filter to current relationships only.

**For transaction intelligence:** Include historical relationships to track ownership changes over time. See [History](history.md).

---

## Best Practices

### Always Store IDs

Never store names as foreign keys. Use `aircraftid`, `companyid`, and `contactid`.

Registration numbers change (re-registration). Company names change (mergers). IDs are permanent.

### Normalize Relationship Types

Create an internal enum map:

```
OWNER
OPERATOR
MANAGER
LESSEE
FRACTIONAL_OWNER
```

Avoid relying on raw string comparisons.

### Expect Many-to-Many

- One aircraft can have multiple companies (owner ≠ operator ≠ manager)
- One company can have multiple aircraft (fleet)
- One company can have many contacts (staff)

---

## Advanced Use Cases

### Lead Targeting

Find all aircraft operated by a company → find all decision-makers at that company → map contacts to fleet.

### Watchlist Monitoring

Monitor aircraft relationship changes, new operator assignments, and contact additions at operator companies using `getBulkAircraftExportPaged` with `aircraftchanges=true`. See [Bulk Export](bulk-export.md).

### M&A Intelligence

Detect aircraft moving between related `companyid` values, parent company restructuring, and contact changes at holding companies using [History](history.md) endpoints.

---

## Common Mistakes

| Mistake | Why It's Wrong | Fix |
|---------|---------------|-----|
| Assuming registration number is permanent | Aircraft get re-registered | Always use `aircraftid` |
| Assuming owner = operator | Often different entities | Check `relationtype` and `isoperator` |
| Not filtering historical relationships | Leads to outdated CRM data | Filter by `iscurrent` |
| Storing company names as keys | Names change | Use `companyid` |
| Treating contacts as standalone | Contacts are always tied to companies | Always join `contactid` → `companyid` |

---

## Related Docs

- [ID System](id-system.md) — Primary keys and how they connect
- [Aircraft](aircraft.md) — Full aircraft endpoint reference including `getRelationships`
- [Companies](companies.md) — Company lookup, search, and relationship endpoints
- [Contacts](contacts.md) — Contact lookup, search, and aircraft relationship endpoints
- [Common Mistakes](common-mistakes.md) — Every known gotcha
