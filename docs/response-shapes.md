# JETNET Response Shapes -- Normalized Contracts

This document defines three canonical data shapes that normalize JETNET's five raw
response schemas into a consistent interface for UI and pipeline code.

Use these shapes as your application's internal data model. Transform raw JETNET
responses into these shapes at the API boundary -- never spread raw field names
(`owrfname`, `companyrelation`, `contactfirstname`) through your UI components.

---

## Why Normalize?

JETNET returns company/contact data in five different schemas depending on the
endpoint. See the Schema Mapping Quick Reference below for the comparison table.
Normalizing at ingestion means your UI components, CRM mappers, and export jobs
only deal with one shape.

---

## 1. AircraftCard

Canonical aircraft summary. Produced by tail-lookup, aircraft list, and bulk export.

```typescript
interface AircraftCard {
  // Identity
  aircraftId: number
  modelId: number
  tailNumber: string       // regnbr
  serialNumber: string     // sernbr / serialnbr
  make: string             // e.g. "GULFSTREAM"
  model: string            // e.g. "G550"
  yearMfr: number
  yearDelivered: number

  // Classification
  makeType: string         // "BusinessJet" | "Turboprop" | "Piston" | ...
  airframeType: string     // "FixedWing" | "Rotorcraft"
  weightClass: string      // "Light" | "Midsize" | "Heavy" | ...
  categorySize: string     // "Light Jet" | "Large Long-Range Jet" | ...

  // Status
  lifecycle: string        // "InOperation" | "Written Off" | ...
  usage: string            // "Business" | "Charter" | ...
  ownership: string        // "Wholly Owned" | "Fractional" | ...
  forSale: boolean
  askingPrice: string | null  // "Inquire" or dollar string or null
  marketStatus: string | null

  // Home base
  baseIcao: string | null
  baseAirport: string | null
  baseCountry: string | null
  baseContinent: string | null

  // Airframe metrics
  estimatedAFTT: number | null
  estimatedCycles: number | null
  estimatedFlightHours: number | null

  // Relationships (normalized -- see CompanyCard below)
  owner: CompanyCard | null
  operator: CompanyCard | null
  chiefPilot: ContactCard | null
  exclusiveBrokers: CompanyCard[]
  additionalRelations: RelationCard[]
}
```

### Python factory (from getRegNumber / tail lookup)

```python
def aircraft_card_from_regnbr(raw: dict) -> dict:
    ac = raw.get("aircraftresult", raw)
    rels = ac.get("companyrelationships", [])
    owner = next((r for r in rels if r["companyrelation"] == "Owner"), None)
    operator = next((r for r in rels if r["companyrelation"] == "Operator"), None)
    return {
        "aircraftId": ac.get("aircraftid"),
        "modelId": ac.get("modelid"),
        "tailNumber": ac.get("regnbr"),
        "serialNumber": ac.get("serialnbr") or ac.get("sernbr"),
        "make": ac.get("make"),
        "model": ac.get("model"),
        "yearMfr": ac.get("yearmfr"),
        "yearDelivered": ac.get("yeardlv"),
        "makeType": ac.get("maketype"),
        "airframeType": ac.get("airframetype"),
        "weightClass": ac.get("weightclass"),
        "categorySize": ac.get("categorysize"),
        "lifecycle": ac.get("lifecycle"),
        "usage": ac.get("usage"),
        "ownership": ac.get("ownership"),
        "forSale": bool(ac.get("forsale")),
        "askingPrice": None,
        "marketStatus": None,
        "baseIcao": ac.get("baseicao"),
        "baseAirport": ac.get("baseairport"),
        "baseCountry": ac.get("basecountry"),
        "baseContinent": ac.get("basecontinent"),
        "estimatedAFTT": ac.get("estaftt"),
        "estimatedCycles": ac.get("estcycles"),
        "estimatedFlightHours": None,
        "owner": company_card_from_flat(owner) if owner else None,
        "operator": company_card_from_flat(operator) if operator else None,
        "chiefPilot": None,
        "exclusiveBrokers": [],
        "additionalRelations": [],
    }
```

### Python factory (from getBulkAircraftExportPaged -- flat owr*/opr*/chp* schema)

```python
def aircraft_card_from_bulk(raw: dict) -> dict:
    for_sale_raw = raw.get("forsale", "N")
    for_sale = for_sale_raw == "Y" if isinstance(for_sale_raw, str) else bool(for_sale_raw)

    owner = None
    if raw.get("owrcompid"):
        owner = {
            "companyId": raw["owrcompid"],
            "name": raw.get("owrcompanyname"),
            "city": raw.get("owrcity"),
            "state": raw.get("owrstate"),
            "country": raw.get("owrcountry"),
            "phone": raw.get("owrphone1"),
            "email": raw.get("owremail"),
            "contact": {
                "contactId": raw.get("owrcontactid"),
                "firstName": raw.get("owrfname"),
                "lastName": raw.get("owrlname"),
                "title": raw.get("owrtitle"),
                "email": raw.get("owremail"),
                "phone": raw.get("owrphone1"),
            },
        }
    return {
        "aircraftId": raw.get("aircraftid"),
        "modelId": raw.get("modelid"),
        "tailNumber": raw.get("regnbr"),
        "serialNumber": raw.get("sernbr"),
        "make": raw.get("make"),
        "model": raw.get("model"),
        "yearMfr": raw.get("yearmfr"),
        "yearDelivered": raw.get("yeardelivered"),
        "makeType": raw.get("maketype"),
        "airframeType": raw.get("airframetype"),
        "lifecycle": raw.get("lifecycle"),
        "forSale": for_sale,
        "askingPrice": raw.get("asking"),
        "marketStatus": raw.get("status"),
        "estimatedAFTT": raw.get("estaftt"),
        "estimatedCycles": raw.get("estcycles"),
        "estimatedFlightHours": raw.get("estflighthrs"),
        "owner": owner,
        "operator": None,   # map opr* similarly if needed
        "chiefPilot": None, # map chp* if needed
        "exclusiveBrokers": [],
        "additionalRelations": [],
    }
```

---

## 2. CompanyCard

Canonical company + primary contact. Used as a nested shape inside AircraftCard
and as a standalone for CRM upsert operations.

```typescript
interface ContactCard {
  contactId: number | null
  firstName: string | null
  lastName: string | null
  fullName: string          // computed: firstName + ' ' + lastName
  title: string | null
  email: string | null
  phone: string | null      // best available phone
  officePhone: string | null
  mobilePhone: string | null
}

interface CompanyCard {
  companyId: number
  name: string
  address1: string | null
  city: string | null
  state: string | null
  country: string | null
  postCode: string | null
  email: string | null
  phone: string | null      // office phone
  businessType: string | null
  agencyType: string | null
  contact: ContactCard | null
}
```

### Python factory (from getRegNumber flat companyrelationships)

```python
def company_card_from_flat(rel: dict) -> dict:
    """
    Normalize a flat getRegNumber companyrelationships entry.
    Field prefix: company* for company, contact* for contact.
    """
    first = rel.get("contactfirstname") or ""
    last  = rel.get("contactlastname") or ""
    return {
        "companyId":   rel.get("companyid"),
        "name":        rel.get("companyname"),
        "address1":    rel.get("companyaddress1"),
        "city":        rel.get("companycity"),
        "state":       rel.get("companystate") or rel.get("companystateabbr"),
        "country":     rel.get("companycountry"),
        "postCode":    rel.get("companypostcode"),
        "email":       rel.get("companyemail"),
        "phone":       rel.get("companyofficephone"),
        "businessType": rel.get("companybusinesstype"),
        "agencyType":  rel.get("companyagencytype"),
        "contact": {
            "contactId":   rel.get("contactid"),
            "firstName":   first,
            "lastName":    last,
            "fullName":    f"{first} {last}".strip(),
            "title":       rel.get("contacttitle"),
            "email":       rel.get("contactemail"),
            "phone":       rel.get("contactbestphone"),
            "officePhone": rel.get("contactofficephone"),
            "mobilePhone": rel.get("contactmobilephone"),
        },
    }
```

### Python factory (from getRelationships / getHistoryList nested schema)

```python
def company_card_from_nested(rel: dict) -> dict:
    """
    Normalize a nested getRelationships / getHistoryList companyrelationships entry.
    Has sub-objects: rel['company'] and rel['contact'].
    """
    co = rel.get("company") or {}
    ct = rel.get("contact") or {}
    first = ct.get("firstname") or ""
    last  = ct.get("lastname") or ""
    return {
        "companyId":    co.get("companyid") or rel.get("companyid"),
        "name":         co.get("name") or rel.get("name"),
        "address1":     co.get("address1"),
        "city":         co.get("city"),
        "state":        co.get("state"),
        "country":      co.get("country"),
        "postCode":     co.get("postcode"),
        "email":        co.get("email"),
        "phone":        co.get("office"),
        "businessType": rel.get("businesstype"),
        "agencyType":   None,
        "contact": {
            "contactId":   ct.get("contactid") or rel.get("contactid"),
            "firstName":   first,
            "lastName":    last,
            "fullName":    f"{first} {last}".strip(),
            "title":       ct.get("title"),
            "email":       ct.get("email"),
            "phone":       ct.get("office") or ct.get("mobile"),
            "officePhone": ct.get("office"),
            "mobilePhone": ct.get("mobile"),
        },
    }
```

---

## 3. GoldenPathResult

The "golden path" shape: everything a front-end component or CRM trigger needs in
one flat dict. Produced by combining AircraftCard + ownership history + market data.
Designed for the Next.js tail-lookup template and CRM enrichment pipelines.

```typescript
interface GoldenPathResult {
  // Aircraft identity (from AircraftCard)
  aircraftId: number
  tailNumber: string
  make: string
  model: string
  yearMfr: number
  yearDelivered: number
  categorySize: string
  weightClass: string

  // Market status
  forSale: boolean
  askingPrice: string | null
  marketStatus: string | null

  // Current owner + operator (from AircraftCard)
  owner: CompanyCard | null
  operator: CompanyCard | null
  chiefPilot: ContactCard | null

  // Home base
  baseIcao: string | null
  baseAirport: string | null
  baseCountry: string | null

  // Enrichment metadata
  jetnetPageUrl: string | null    // link to JETNET Evolution detail page
  lastUpdated: string | null      // ISO datetime of last JETNET update
  dataSource: string              // always "JETNET"
}
```

### Python factory

```python
def golden_path_result(
    aircraft_card: dict,
    jetnet_page_url: str | None = None,
    last_updated: str | None = None,
) -> dict:
    """
    Produce a GoldenPathResult from a normalized AircraftCard.
    """
    return {
        "aircraftId":    aircraft_card["aircraftId"],
        "tailNumber":    aircraft_card["tailNumber"],
        "make":          aircraft_card["make"],
        "model":         aircraft_card["model"],
        "yearMfr":       aircraft_card["yearMfr"],
        "yearDelivered": aircraft_card["yearDelivered"],
        "categorySize":  aircraft_card.get("categorySize"),
        "weightClass":   aircraft_card.get("weightClass"),
        "forSale":       aircraft_card.get("forSale", False),
        "askingPrice":   aircraft_card.get("askingPrice"),
        "marketStatus":  aircraft_card.get("marketStatus"),
        "owner":         aircraft_card.get("owner"),
        "operator":      aircraft_card.get("operator"),
        "chiefPilot":    aircraft_card.get("chiefPilot"),
        "baseIcao":      aircraft_card.get("baseIcao"),
        "baseAirport":   aircraft_card.get("baseAirport"),
        "baseCountry":   aircraft_card.get("baseCountry"),
        "jetnetPageUrl": jetnet_page_url,
        "lastUpdated":   last_updated,
        "dataSource":    "JETNET",
    }
```

---

## Schema Mapping Quick Reference

| Field in GoldenPathResult | getRegNumber (flat) | getBulkExport (prefixed) | getRelationships (nested) |
|---|---|---|---|
| owner.companyId | `companyid` | `owrcompid` | `company.companyid` |
| owner.name | `companyname` | `owrcompanyname` | `company.name` |
| owner.contact.firstName | `contactfirstname` | `owrfname` | `contact.firstname` |
| owner.contact.lastName | `contactlastname` | `owrlname` | `contact.lastname` |
| owner.contact.title | `contacttitle` | `owrtitle` | `contact.title` |
| owner.contact.email | `contactemail` | `owremail` | `contact.email` |
| owner.contact.phone | `contactbestphone` | `owrphone1` | `contact.office` |
| relation field | `companyrelation` | prefix (`owr*`) | `relationtype` |

---

## TypeScript Utility (Next.js)

```typescript
// lib/normalize.ts

export function companyCardFromFlat(rel: Record<string, unknown>): CompanyCard {
  const first = String(rel['contactfirstname'] ?? '')
  const last = String(rel['contactlastname'] ?? '')
  return {
    companyId: Number(rel['companyid']),
    name: String(rel['companyname'] ?? ''),
    address1: (rel['companyaddress1'] as string) ?? null,
    city: (rel['companycity'] as string) ?? null,
    state: (rel['companystateabbr'] as string) ?? null,
    country: (rel['companycountry'] as string) ?? null,
    postCode: (rel['companypostcode'] as string) ?? null,
    email: (rel['companyemail'] as string) || null,
    phone: (rel['companyofficephone'] as string) ?? null,
    businessType: (rel['companybusinesstype'] as string) ?? null,
    agencyType: (rel['companyagencytype'] as string) ?? null,
    contact: {
      contactId: rel['contactid'] ? Number(rel['contactid']) : null,
      firstName: first || null,
      lastName: last || null,
      fullName: [first, last].filter(Boolean).join(' '),
      title: (rel['contacttitle'] as string) ?? null,
      email: (rel['contactemail'] as string) ?? null,
      phone: (rel['contactbestphone'] as string) ?? null,
      officePhone: (rel['contactofficephone'] as string) ?? null,
      mobilePhone: (rel['contactmobilephone'] as string) ?? null,
    },
  }
}

export function aircraftCardFromRegNbr(raw: Record<string, unknown>): AircraftCard {
  const ac = (raw['aircraftresult'] as Record<string, unknown>) ?? raw
  const rels = (ac['companyrelationships'] as Record<string, unknown>[]) ?? []
  const ownerRel = rels.find(r => r['companyrelation'] === 'Owner') ?? null
  const opRel = rels.find(r => r['companyrelation'] === 'Operator') ?? null
  return {
    aircraftId: Number(ac['aircraftid']),
    modelId: Number(ac['modelid']),
    tailNumber: String(ac['regnbr'] ?? ''),
    serialNumber: String(ac['serialnbr'] ?? ac['sernbr'] ?? ''),
    make: String(ac['make'] ?? ''),
    model: String(ac['model'] ?? ''),
    yearMfr: Number(ac['yearmfr']),
    yearDelivered: Number(ac['yeardlv'] ?? ac['yeardelivered']),
    makeType: String(ac['maketype'] ?? ''),
    airframeType: String(ac['airframetype'] ?? ''),
    weightClass: String(ac['weightclass'] ?? ''),
    categorySize: String(ac['categorysize'] ?? ''),
    lifecycle: String(ac['lifecycle'] ?? ''),
    usage: String(ac['usage'] ?? ''),
    ownership: String(ac['ownership'] ?? ''),
    forSale: Boolean(ac['forsale']),
    askingPrice: null,
    marketStatus: null,
    baseIcao: (ac['baseicao'] as string) ?? null,
    baseAirport: (ac['baseairport'] as string) ?? null,
    baseCountry: (ac['basecountry'] as string) ?? null,
    baseContinent: (ac['basecontinent'] as string) ?? null,
    estimatedAFTT: ac['estaftt'] != null ? Number(ac['estaftt']) : null,
    estimatedCycles: ac['estcycles'] != null ? Number(ac['estcycles']) : null,
    estimatedFlightHours: null,
    owner: ownerRel ? companyCardFromFlat(ownerRel) : null,
    operator: opRel ? companyCardFromFlat(opRel) : null,
    chiefPilot: null,
    exclusiveBrokers: [],
    additionalRelations: [],
  }
}
```
