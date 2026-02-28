# Contacts

Contacts represent **people** in the JETNET ecosystem — chief pilots, directors of aviation, CEOs, dispatchers, and other decision-makers tied to aircraft and companies. A contact is a **relationship hub** connecting companies, aircraft, and listings, not just a person record.

## Endpoints

| Endpoint | Method | URL Pattern | Purpose |
|----------|--------|-------------|---------|
| getContact | GET | `/api/Contact/getContact/{id}/{apiToken}` | Full contact record |
| getContactList | POST | `/api/Contact/getContactList/{apiToken}` | Search contacts |
| getContactListPaged | POST | `/api/Contact/getContactListPaged/{apiToken}/{pagesize}/{page}` | Paginated contact search |
| getIdentification | GET | `/api/Contact/getIdentification/{id}/{apiToken}` | Identification-only record |
| getPhonenumbers | GET | `/api/Contact/getPhonenumbers/{id}/{apiToken}` | Phone numbers for a contact |
| getOtherlistings | GET | `/api/Contact/getOtherlistings/{id}/{apiToken}` | Alternate company/contact associations |
| getContAircraftRelationships | GET | `/api/Contact/getContAircraftRelationships/{id}/{apiToken}` | Aircraft relationships for a contact |

## Recommended Workflow

```
1. getContactList / getContactListPaged  →  search by name, company, aircraft
2. getIdentification                     →  lightweight verify before hydrating
3. getContact                            →  full profile (includes nested sub-records)
4. getContAircraftRelationships          →  aircraft linkage
5. getPhonenumbers                       →  communication data
6. getOtherlistings                      →  extended cross-company relationships
```

## Endpoint Details

### getContact

Returns a complete contact object including identification, phone numbers, and aircraft relationships when available.

```
GET /api/Contact/getContact/{contactId}/{apiToken}
```

**Response:**

```json
{
  "responsestatus": "SUCCESS",
  "contact": {
    "identification": {
      "contactid": 343,
      "companyid": 215,
      "firstname": "William",
      "lastname": "Butler",
      "title": "President",
      "email": null
    },
    "phonenumbers": null,
    "aircraftrelationships": []
  }
}
```

**Response key:** `contact` (object with nested `identification`, `phonenumbers`, `aircraftrelationships`)

### getContactList

Search contacts by name, company, aircraft, or other criteria. Returns a non-paginated result set.

```
POST /api/Contact/getContactList/{apiToken}
```

**Request body** (`ContListOptions`):

| Field | Type | Description |
|-------|------|-------------|
| `aircraftid` | array | Filter by aircraft IDs |
| `companyid` | integer | Filter by company ID |
| `companyname` | string | Filter by company name |
| `firstname` | string | Filter by first name |
| `lastname` | string | Filter by last name |
| `title` | string | Filter by title |
| `email` | string | Filter by email |
| `actiondate` | string | Changed-since date (MM/DD/YYYY) |
| `enddate` | string | Changed-before date (MM/DD/YYYY) |
| `phonenumber` | string | Filter by phone number |
| `contactchanges` | string | Filter by change type |
| `contlist` | array | Specific contact IDs |
| `complist` | array | Specific company IDs |

**Example request:**

```json
{
  "aircraftid": [23453, 241265, 2521],
  "companyname": "",
  "firstname": "",
  "lastname": ""
}
```

**Response key:** `contactlist` (array)

### getContactListPaged

Same search logic as `getContactList` but with pagination for large result sets.

```
POST /api/Contact/getContactListPaged/{apiToken}/{pagesize}/{page}
```

**Path params:** `pagesize` (integer), `page` (integer, 1-based)

**Request body:** Same `ContListOptions` as `getContactList`.

**Response includes:** `currentpage`, `maxpages`, `count`, `contacts[]`

Use this endpoint for data warehouse ingestion, CRM synchronization, and batch exports. See [pagination](pagination.md) for the standard paging pattern.

### getIdentification

Lightweight endpoint returning only identification metadata — useful when you need to verify a contact without pulling the full record.

```
GET /api/Contact/getIdentification/{contactId}/{apiToken}
```

**Returns:** Contact name, title, company ID, email, action date.

### getPhonenumbers

Retrieves phone numbers associated with a contact.

```
GET /api/Contact/getPhonenumbers/{contactId}/{apiToken}
```

**Response:**

```json
{
  "responsestatus": "SUCCESS: NO RESULTS FOUND [PHONE NUMBERS]",
  "count": 0,
  "phonenumbers": null
}
```

**Response key:** `phonenumbers` (array or `null`)

> `"SUCCESS: NO RESULTS FOUND"` is **not an error** — it means the contact has no phone numbers on file. The `phonenumbers` field will be `null`, not `[]`. Always guard before iterating. See [Key Behaviors](#key-behaviors) below.

### getOtherlistings

Returns alternate company/contact associations — discover cross-company affiliations for a contact.

```
GET /api/Contact/getOtherlistings/{contactId}/{apiToken}
```

**Response:**

```json
{
  "responsestatus": "SUCCESS",
  "count": 2,
  "otherlistings": [
    { "companyid": 214, "contactid": 342 }
  ]
}
```

**Response key:** `otherlistings` (array or `null`)

Use this to build relationship expansion graphs and discover contacts that span multiple organizations.

### getContAircraftRelationships

Returns aircraft relationships tied to a contact — which aircraft they are associated with and in what role.

```
GET /api/Contact/getContAircraftRelationships/{contactId}/{apiToken}
```

**Response:**

```json
{
  "responsestatus": "SUCCESS",
  "aircraftrelationships": [
    {
      "aircraftid": 197551,
      "relationtype": "Additional Company/Contact",
      "isoperator": "N",
      "businesstype": "End User"
    }
  ]
}
```

**Response key:** `aircraftrelationships` (array or `null`)

Use `aircraftid` from these results to call aircraft sub-record endpoints (`getAircraft`, `getRelationships`, etc.).

## Key Behaviors

### "SUCCESS: NO RESULTS FOUND" Is Normal

Many contact sub-endpoints return `"SUCCESS: NO RESULTS FOUND [PHONE NUMBERS]"` or similar when the contact exists but has no data for that sub-record. This is **not an error**. Use a prefix/startsWith check:

```python
status = data.get("responsestatus", "")
if status.upper().startswith("SUCCESS"):
    pass  # OK, even if "NO RESULTS FOUND"
elif "ERROR" in status.upper():
    raise ValueError(f"JETNET error: {status}")
```

```javascript
const status = data.responsestatus || "";
if (status.toUpperCase().startsWith("SUCCESS")) {
  // OK, even if "NO RESULTS FOUND"
} else if (status.toUpperCase().includes("ERROR")) {
  throw new Error(`JETNET error: ${status}`);
}
```

### Null Arrays, Not Empty Arrays

Fields like `phonenumbers`, `aircraftrelationships`, and `otherlistings` return `null` when there are no results — **not** an empty array `[]`. Always guard before calling `.map()`, `.forEach()`, or iterating:

```python
phones = data.get("phonenumbers") or []
for phone in phones:
    print(phone)
```

```javascript
const phones = data.phonenumbers ?? [];
phones.forEach((p) => console.log(p));
```

### contactid Is the Join Key

`contactid` is the primary key for all contact sub-record endpoints and the field you use to de-duplicate contacts across multiple aircraft or company records. Store `contactid` (not names) as your foreign key. See [ID System](id-system.md).

## Contact as a Relationship Hub

Contacts connect outward to three entity types:

```
                    ┌─────────────┐
                    │  Companies  │
                    │ (companyid) │
                    └──────▲──────┘
                           │
              ┌────────────┼────────────┐
              │         Contact         │
              │       (contactid)       │
              └────────────┼────────────┘
              │                         │
       ┌──────▼──────┐          ┌───────▼───────┐
       │   Aircraft   │          │   Listings    │
       │ (aircraftid) │          │ (otherlistings│
       └──────────────┘          └───────────────┘
```

- **Companies:** Every contact belongs to a company via `companyid`. Use `getIdentification` to see the primary company, or `getOtherlistings` to find additional affiliations.
- **Aircraft:** Use `getContAircraftRelationships` to find all aircraft linked to a contact. Each relationship includes `relationtype`, `isoperator`, and `businesstype`.
- **Listings:** `getOtherlistings` reveals alternate company/contact associations — the same person may appear under different companies with different `contactid` values.

## Common Use Cases

### CRM Enrichment

```
getContactListPaged (lastname="Smith", title="Chief Pilot")
  → for each contact:
      getContact/{contactid}        → full profile
      getPhonenumbers/{contactid}   → phone data
      getContAircraftRelationships/{contactid} → linked aircraft
```

### Ownership Intelligence

Starting from an aircraft, find decision-makers:

```
getRegNumber/{tailNumber}
  → extract contactid from companyrelationships
  → getContact/{contactid}         → full contact record
  → getOtherlistings/{contactid}   → cross-company links
```

### Incremental Sync

Use `actiondate` in `getContactListPaged` to pull only contacts that changed since your last sync:

```json
{
  "actiondate": "01/15/2025",
  "enddate": ""
}
```

## See Also

- [ID System](id-system.md) — `contactid`, `companyid`, and `aircraftid` explained
- [Response Handling](response-handling.md) — `responsestatus` patterns and schema differences
- [Common Mistakes](common-mistakes.md) — null arrays, "SUCCESS: NO RESULTS FOUND", and other gotchas
- [Pagination](pagination.md) — standard paging pattern for `getContactListPaged`
- [Companies](companies.md) — company endpoints that connect to contacts via `companyid`
