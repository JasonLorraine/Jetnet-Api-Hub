# JETNET API -- Full Endpoint Reference
This file contains every endpoint with its parameters.
Date parameters use `MM/DD/YYYY` format unless noted.

## Admin

### `POST` /api/Admin/APILogin
**Customer APILogin**

**Request body** (`ApiUser`):
- `emailAddress` (string, capital A) -- ApiUser EmailAddress
- `password` (string) -- ApiUser Password

---

### `GET` /api/Admin/getBearerToken
**Get Bearer Token**

---

## Aircraft

### `GET` /api/Aircraft/getAircraft/{id}/{securityToken}
**Get ALL Aircraft data**

**Path params:**
- `id`: Aircraft ID (required)

**Response key:** `aircraft` (object -- composite with nested identification, airframe, engine, apu, avionics, features, interior, exterior, maintenance, leases, pictures, companyrelationships, status)

---

### `GET` /api/Aircraft/getIdentification/{id}/{securityToken}
**Get Aircraft Identification**

**Path params:**
- `id`: Aircraft ID (required)

**Response key:** `identification` (object -- aircraftid, modelid, make, model, sernbr, regnbr, yearmfr, yeardlv, actiondate, pageurl)

---

### `GET` /api/Aircraft/getStatus/{id}/{securityToken}
**Get Aircraft Status**

**Path params:**
- `id`: Aircraft ID (required)

**Response key:** `status` (object)

---

### `GET` /api/Aircraft/getAirframe/{id}/{securityToken}
**Get Aircraft Airframe**

**Path params:**
- `id`: Aircraft ID (required)

**Response key:** `airframe` (object -- aftt, landings, timesasofdate, estaftt)

---

### `GET` /api/Aircraft/getEngine/{id}/{securityToken}
**Get Aircraft Engines**

**Path params:**
- `id`: Aircraft ID (required)

**Response key:** `engine` (object -- maintenanceprogram, model, enginenoiserating; contains `engines[]` sub-array with per-engine sequencenumber, serialnumber, timesincenew, tbo)

---

### `GET` /api/Aircraft/getApu/{id}/{securityToken}
**Get Aircraft APU**

**Path params:**
- `id`: Aircraft ID (required)

**Response key:** `apu` (object or null; responsestatus may be "SUCCESS: NO RESULTS FOUND [APU]")

---

### `GET` /api/Aircraft/getCompanyrelationships/{id}/{securityToken}
**Get Aircraft Company Relationships**

**Path params:**
- `id`: Aircraft ID (required)

**Response key:** `companyrelationships` (array) + `count` -- fields: companyid, name, relationtype, relationseqno, contactid, ownerpercent, fractionexpiresdate, isoperator (string "Y"/"N")

---

### `GET` /api/Aircraft/getMaintenance/{id}/{securityToken}
**Get Aircraft Maintenance**

**Path params:**
- `id`: Aircraft ID (required)

**Response key:** `maintenance` (object)

---

### `GET` /api/Aircraft/getAvionics/{id}/{securityToken}
**Get Aircraft Avionics**

**Path params:**
- `id`: Aircraft ID (required)

**Response key:** `avionics` (array of { name, description }) + `count`

---

### `GET` /api/Aircraft/getFeatures/{id}/{securityToken}
**Get Aircraft Features**

**Path params:**
- `id`: Aircraft ID (required)

**Response key:** `features` (array) + `count`

---

### `GET` /api/Aircraft/getAdditionalEquipment/{id}/{securityToken}
**Get Aircraft Additional Equipment**

**Path params:**
- `id`: Aircraft ID (required)

**Response key:** `additionalequipment` (array of { name, description }) + `count`

---

### `GET` /api/Aircraft/getInterior/{id}/{securityToken}
**Get Aircraft Interior**

**Path params:**
- `id`: Aircraft ID (required)

**Response key:** `interior` (object)

---

### `GET` /api/Aircraft/getExterior/{id}/{securityToken}
**Get Aircraft Exterior**

**Path params:**
- `id`: Aircraft ID (required)

**Response key:** `exterior` (object)

---

### `GET` /api/Aircraft/getLeases/{id}/{securityToken}
**Get Aircraft Leases**

**Path params:**
- `id`: Aircraft ID (required)

**Response key:** `leases` (array or null)

---

### `GET` /api/Aircraft/getFlights/{id}/{securityToken}
**Get Aircraft Flight Summary**

**Path params:**
- `id`: Aircraft ID (required)

**Response key:** `flightsummary` (object/array)

---

### `GET` /api/Aircraft/getPictures/{id}/{securityToken}
**Get Aircraft Pictures**

**Path params:**
- `id`: Aircraft ID (required)

**Response key:** `pictures` (array) + `count`

---

### `GET` /api/Aircraft/getRegNumber/{reg}/{securityToken}
**Get simple aircraft info by tail number**

**Path params:**
- `reg`: Registration Number (required)

**Response key:** `aircraftresult` (object -- flat schema with companyrelation field, not relationtype)

---

### `GET` /api/Aircraft/getHexNumber/{hex}/{securityToken}
**Get simple aircraft info by hexcode number**

**Path params:**
- `hex`: Hexcode Number (required)

**Response key:** `aircraft` (object)

---

### `POST` /api/Aircraft/getAircraftList/{securityToken}
**Get Aircraft List**

**Request body** (`AcListOptions`):
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)
- `sernbr` (string)
- `regnbr` (string)
- `regnbrlist` (array)
- `modelid` (integer)
- `make` (string)
- `makelist` (array)
- `forsale` (string)
- `lifecycle` (eLifeCycle)
- `basestate` (array)
- `basestatename` (array)
- `basecountry` (string)
- `basecountrylist` (array)
- `basecode` (string)
- `actiondate` (string)
- `enddate` (string)
- `companyid` (integer)
- `complist` (array)
- `contactid` (integer)
- `yearmfr` (integer)
- `yeardlv` (integer)
- `aircraftchanges` (string)
- `aclist` (array)
- `modlist` (array)
- `exactMatchReg` (boolean)
- `showHistoricalAcRefs` (boolean)
- `showAwaitingDocsCompanies` (boolean)

---

### `POST` /api/Aircraft/getEventList/{securityToken}
**Get Aircraft Events**

**Request body** (`AcEventsOptions`):
- `aircraftid` (integer)
- `modelid` (integer)
- `make` (string)
- `evcategory` (array)
- `evtype` (array)
- `startdate` (string)
- `enddate` (string)
- `aclist` (array)
- `modlist` (array)

---

### `POST` /api/Aircraft/getEventListPaged/{securityToken}/{pagesize}/{page}
**Get Aircraft Events Paged**

**Path params:**
- `pagesize`: Page Size (required)
- `page`: Page (required)

**Request body** (`AcEventsOptions`):
- `aircraftid` (integer)
- `modelid` (integer)
- `make` (string)
- `evcategory` (array)
- `evtype` (array)
- `startdate` (string)
- `enddate` (string)
- `aclist` (array)
- `modlist` (array)

---

### `POST` /api/Aircraft/getHistoryList/{securityToken}
**Get Aircraft History**

**Request body** (`AcHistoryOptions`):
- `aircraftid` (integer)
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)
- `modelid` (integer)
- `make` (string)
- `companyid` (integer)
- `isnewaircraft` (eYesNoIgnoreFlag)
- `allrelationships` (boolean)
- `transtype` (array)
- `startdate` (string)
- `enddate` (string)
- `aclist` (array)
- `modlist` (array)
- `lastactionstartdate` (string)
- `lastactionenddate` (string)
- `ispreownedtrans` (eYesNoIgnoreFlag)
- `isretailtrans` (eYesNoIgnoreFlag)
- `isinternaltrans` (eYesNoIgnoreFlag)

---

### `POST` /api/Aircraft/getHistoryListPaged/{securityToken}/{pagesize}/{page}
**Get Aircraft History Paged**

**Path params:**
- `pagesize`: Page Size (required)
- `page`: Page (required)

**Request body** (`AcHistoryOptions`):
- `aircraftid` (integer)
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)
- `modelid` (integer)
- `make` (string)
- `companyid` (integer)
- `isnewaircraft` (eYesNoIgnoreFlag)
- `allrelationships` (boolean)
- `transtype` (array)
- `startdate` (string)
- `enddate` (string)
- `aclist` (array)
- `modlist` (array)
- `lastactionstartdate` (string)
- `lastactionenddate` (string)
- `ispreownedtrans` (eYesNoIgnoreFlag)
- `isretailtrans` (eYesNoIgnoreFlag)
- `isinternaltrans` (eYesNoIgnoreFlag)

---

### `POST` /api/Aircraft/getRelationships/{securityToken}
**Get Aircraft Relationships**

**Request body** (`AcRelationshipOptions`):
- `aircraftid` (integer)
- `aclist` (array)
- `modlist` (array)
- `actiondate` (string)
- `showHistoricalAcRefs` (boolean)

---

### `POST` /api/Aircraft/getFlightData/{securityToken}
**Get Aircraft Flight Data**

**Request body** (`AcFlightDataOptions`):
- `aircraftid` (integer)
- `airframetype` (eAirFrameTypes)
- `sernbr` (string)
- `regnbr` (string)
- `maketype` (eMakeTypes)
- `modelid` (integer)
- `make` (string)
- `origin` (string)
- `destination` (string)
- `startdate` (string)
- `enddate` (string)
- `aclist` (array)
- `modlist` (array)
- `lastactionstartdate` (string)
- `lastactionenddate` (string)
- `exactMatchReg` (boolean)

---

### `POST` /api/Aircraft/getFlightDataPaged/{securityToken}/{pagesize}/{page}
**Get Aircraft Flight Data Paged**

**Path params:**
- `pagesize`: Page Size (required)
- `page`: Page (required)

**Request body** (`AcFlightDataOptions`):
- `aircraftid` (integer)
- `airframetype` (eAirFrameTypes)
- `sernbr` (string)
- `regnbr` (string)
- `maketype` (eMakeTypes)
- `modelid` (integer)
- `make` (string)
- `origin` (string)
- `destination` (string)
- `startdate` (string)
- `enddate` (string)
- `aclist` (array)
- `modlist` (array)
- `lastactionstartdate` (string)
- `lastactionenddate` (string)
- `exactMatchReg` (boolean)

---

### `POST` /api/Aircraft/getCondensedOwnerOperators/{securityToken}
**Get Aircraft Condensed Owner / Operators List**

**Request body** (`AcListOptions`):
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)
- `sernbr` (string)
- `regnbr` (string)
- `regnbrlist` (array)
- `modelid` (integer)
- `make` (string)
- `makelist` (array)
- `forsale` (string)
- `lifecycle` (eLifeCycle)
- `basestate` (array)
- `basestatename` (array)
- `basecountry` (string)
- `basecountrylist` (array)
- `basecode` (string)
- `actiondate` (string)
- `enddate` (string)
- `companyid` (integer)
- `complist` (array)
- `contactid` (integer)
- `yearmfr` (integer)
- `yeardlv` (integer)
- `aircraftchanges` (string)
- `aclist` (array)
- `modlist` (array)
- `exactMatchReg` (boolean)
- `showHistoricalAcRefs` (boolean)
- `showAwaitingDocsCompanies` (boolean)

---

### `POST` /api/Aircraft/getCondensedOwnerOperatorsPaged/{securityToken}/{pagesize}/{page}
**Get Aircraft Condensed Owner / Operators List Paged**

**Path params:**
- `pagesize`: Page Size (required)
- `page`: Page (required)

**Request body** (`AcListOptions`):
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)
- `sernbr` (string)
- `regnbr` (string)
- `regnbrlist` (array)
- `modelid` (integer)
- `make` (string)
- `makelist` (array)
- `forsale` (string)
- `lifecycle` (eLifeCycle)
- `basestate` (array)
- `basestatename` (array)
- `basecountry` (string)
- `basecountrylist` (array)
- `basecode` (string)
- `actiondate` (string)
- `enddate` (string)
- `companyid` (integer)
- `complist` (array)
- `contactid` (integer)
- `yearmfr` (integer)
- `yeardlv` (integer)
- `aircraftchanges` (string)
- `aclist` (array)
- `modlist` (array)
- `exactMatchReg` (boolean)
- `showHistoricalAcRefs` (boolean)
- `showAwaitingDocsCompanies` (boolean)

---

### `POST` /api/Aircraft/getCondensedSnapshot/{securityToken}
**Get Aircraft Condensed Owner / Operators Historical Snapshot**

**Request body** (`AcSnapshotOptions`):
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)
- `sernbr` (string)
- `regnbr` (string)
- `regnbrlist` (array)
- `modelid` (integer)
- `make` (string)
- `makelist` (array)
- `lifecycle` (eLifeCycle)
- `basestate` (array)
- `basecountry` (string)
- `basecountrylist` (array)
- `basecode` (string)
- `snapshotdate` (string)
- `yearmfr` (integer)
- `yeardlv` (integer)
- `aclist` (array)
- `modlist` (array)
- `exactMatchReg` (boolean)

---

### `POST` /api/Aircraft/getAcCompanyFractionalReport/{securityToken}
**Get Aircraft Fractional Info**

**Request body** (`AircraftReportOptions`):
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)
- `sernbr` (string)
- `regnbr` (string)
- `regnbrlist` (array)
- `modelid` (integer)
- `make` (string)
- `makelist` (array)
- `forsale` (string)
- `lifecycle` (eLifeCycle)
- `basestate` (array)
- `basestatename` (array)
- `basecountry` (string)
- `basecountrylist` (array)
- `basecode` (string)
- `actiondate` (string)
- `enddate` (string)
- `fractionexpiresdate` (string)
- `companyid` (integer)
- `complist` (array)
- `contactid` (integer)
- `yearmfr` (integer)
- `yeardlv` (integer)
- `aircraftchanges` (string)
- `aclist` (array)
- `modlist` (array)
- `exactMatchReg` (boolean)
- `bustype` (array)
- `relationship` (array)
- `ownertype` (array)

---

### `POST` /api/Aircraft/getAcCompanyFractionalReportPaged/{securityToken}/{pagesize}/{page}
**Get Aircraft Fractional Info Paged**

**Path params:**
- `pagesize`: Page Size (required)
- `page`: Page (required)

**Request body** (`AircraftReportOptions`):
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)
- `sernbr` (string)
- `regnbr` (string)
- `regnbrlist` (array)
- `modelid` (integer)
- `make` (string)
- `makelist` (array)
- `forsale` (string)
- `lifecycle` (eLifeCycle)
- `basestate` (array)
- `basestatename` (array)
- `basecountry` (string)
- `basecountrylist` (array)
- `basecode` (string)
- `actiondate` (string)
- `enddate` (string)
- `fractionexpiresdate` (string)
- `companyid` (integer)
- `complist` (array)
- `contactid` (integer)
- `yearmfr` (integer)
- `yeardlv` (integer)
- `aircraftchanges` (string)
- `aclist` (array)
- `modlist` (array)
- `exactMatchReg` (boolean)
- `bustype` (array)
- `relationship` (array)
- `ownertype` (array)

---

### `POST` /api/Aircraft/getAcSellerPurchaserReport/{securityToken}
**Get Aircraft Seller Purchaser Report**

**Request body** (`AircraftReportOptions`):
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)
- `sernbr` (string)
- `regnbr` (string)
- `regnbrlist` (array)
- `modelid` (integer)
- `make` (string)
- `makelist` (array)
- `forsale` (string)
- `lifecycle` (eLifeCycle)
- `basestate` (array)
- `basestatename` (array)
- `basecountry` (string)
- `basecountrylist` (array)
- `basecode` (string)
- `actiondate` (string)
- `enddate` (string)
- `fractionexpiresdate` (string)
- `companyid` (integer)
- `complist` (array)
- `contactid` (integer)
- `yearmfr` (integer)
- `yeardlv` (integer)
- `aircraftchanges` (string)
- `aclist` (array)
- `modlist` (array)
- `exactMatchReg` (boolean)
- `bustype` (array)
- `relationship` (array)
- `ownertype` (array)

---

### `POST` /api/Aircraft/getAcSellerPurchaserReportPaged/{securityToken}/{pagesize}/{page}
**Get Aircraft Seller Purchaser Report Paged**

**Path params:**
- `pagesize`: Page Size (required)
- `page`: Page (required)

**Request body** (`AircraftReportOptions`):
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)
- `sernbr` (string)
- `regnbr` (string)
- `regnbrlist` (array)
- `modelid` (integer)
- `make` (string)
- `makelist` (array)
- `forsale` (string)
- `lifecycle` (eLifeCycle)
- `basestate` (array)
- `basestatename` (array)
- `basecountry` (string)
- `basecountrylist` (array)
- `basecode` (string)
- `actiondate` (string)
- `enddate` (string)
- `fractionexpiresdate` (string)
- `companyid` (integer)
- `complist` (array)
- `contactid` (integer)
- `yearmfr` (integer)
- `yeardlv` (integer)
- `aircraftchanges` (string)
- `aclist` (array)
- `modlist` (array)
- `exactMatchReg` (boolean)
- `bustype` (array)
- `relationship` (array)
- `ownertype` (array)

---

### `POST` /api/Aircraft/getBulkAircraftExport/{securityToken}
**Get Bulk Export of Aircraft Record Lists**

**Request body** (`AcListOptions`):
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)
- `sernbr` (string)
- `regnbr` (string)
- `regnbrlist` (array)
- `modelid` (integer)
- `make` (string)
- `makelist` (array)
- `forsale` (string)
- `lifecycle` (eLifeCycle)
- `basestate` (array)
- `basestatename` (array)
- `basecountry` (string)
- `basecountrylist` (array)
- `basecode` (string)
- `actiondate` (string)
- `enddate` (string)
- `companyid` (integer)
- `complist` (array)
- `contactid` (integer)
- `yearmfr` (integer)
- `yeardlv` (integer)
- `aircraftchanges` (string)
- `aclist` (array)
- `modlist` (array)
- `exactMatchReg` (boolean)
- `showHistoricalAcRefs` (boolean)
- `showAwaitingDocsCompanies` (boolean)

---

### `POST` /api/Aircraft/getBulkAircraftExportPaged/{securityToken}/{pagesize}/{page}
**Get Bulk Export of Aircraft Record Lists Paged**

**Path params:**
- `pagesize`: Page Size (required)
- `page`: Page (required)

**Request body** (`AcListOptions`):
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)
- `sernbr` (string)
- `regnbr` (string)
- `regnbrlist` (array)
- `modelid` (integer)
- `make` (string)
- `makelist` (array)
- `forsale` (string)
- `lifecycle` (eLifeCycle)
- `basestate` (array)
- `basestatename` (array)
- `basecountry` (string)
- `basecountrylist` (array)
- `basecode` (string)
- `actiondate` (string)
- `enddate` (string)
- `companyid` (integer)
- `complist` (array)
- `contactid` (integer)
- `yearmfr` (integer)
- `yeardlv` (integer)
- `aircraftchanges` (string)
- `aclist` (array)
- `modlist` (array)
- `exactMatchReg` (boolean)
- `showHistoricalAcRefs` (boolean)
- `showAwaitingDocsCompanies` (boolean)

---

### `POST` /api/Aircraft/getAllAircraftObjects/{securityToken}/{pagesize}/{page}
**Get ALL Aircraft Object Data **

**Path params:**
- `pagesize`: Page Size (required)
- `page`: Page (required)

**Request body** (`AcObjectListOptions`):
- `aclist` (array)

---

## Company

### `GET` /api/Company/getCompany/{id}/{securityToken}
**Get ALL Company data**

**Path params:**
- `id`: Company ID (required)

---

### `GET` /api/Company/getIdentification/{id}/{securityToken}
**Get Identification**

**Path params:**
- `id`: Company ID (required)

---

### `GET` /api/Company/getContacts/{id}/{securityToken}
**Get Contacts**

**Path params:**
- `id`: Company ID (required)

---

### `GET` /api/Company/getPhonenumbers/{id}/{securityToken}
**Get Phone Numbers**

**Path params:**
- `id`: Company ID (required)

---

### `GET` /api/Company/getBusinesstypes/{id}/{securityToken}
**Get Business Types**

**Path params:**
- `id`: Company ID (required)

---

### `GET` /api/Company/getAircraftrelationships/{id}/{securityToken}
**Get Aircraft Relationships**

**Path params:**
- `id`: Company ID (required)

---

### `GET` /api/Company/getRelatedcompanies/{id}/{securityToken}
**Get Related Companies**

**Path params:**
- `id`: Company ID (required)

---

### `GET` /api/Company/getCompanyCertifications/{id}/{securityToken}
**Get Company Certifications**

**Path params:**
- `id`: Company ID (required)

---

### `POST` /api/Company/getCompanyList/{securityToken}
**Get Company List**

**Request body** (`CompListOptions`):
- `aircraftid` (array)
- `name` (string)
- `country` (string)
- `city` (string)
- `state` (array)
- `statename` (array)
- `bustype` (array)
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)
- `modelid` (array)
- `make` (array)
- `relationship` (array)
- `isoperator` (string)
- `actiondate` (string)
- `companychanges` (string)
- `website` (string)
- `complist` (array)

---

### `POST` /api/Company/getCompanyListPaged/{securityToken}/{pagesize}/{page}
**Get Company List Paged**

**Path params:**
- `pagesize`: Page Size (required)
- `page`: Page (required)

**Request body** (`CompListOptions`):
- `aircraftid` (array)
- `name` (string)
- `country` (string)
- `city` (string)
- `state` (array)
- `statename` (array)
- `bustype` (array)
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)
- `modelid` (array)
- `make` (array)
- `relationship` (array)
- `isoperator` (string)
- `actiondate` (string)
- `companychanges` (string)
- `website` (string)
- `complist` (array)

---

### `POST` /api/Company/getCompanyHistory/{securityToken}
**Get Company History List**

**Request body** (`CompHistoryOptions`):
- `companyid` (integer)
- `complist` (array)
- `aircraftid` (integer)
- `aclist` (array)
- `transtype` (array)
- `relationship` (array)
- `startdate` (string)
- `enddate` (string)
- `lastactionstartdate` (string)
- `lastactionenddate` (string)
- `isinternaltrans` (eYesNoIgnoreFlag)
- `isoperator` (eYesNoIgnoreFlag)

---

### `POST` /api/Company/getCompanyHistoryPaged/{securityToken}/{pagesize}/{page}
**Get Company History List Paged**

**Path params:**
- `pagesize`: Page Size (required)
- `page`: Page (required)

**Request body** (`CompHistoryOptions`):
- `companyid` (integer)
- `complist` (array)
- `aircraftid` (integer)
- `aclist` (array)
- `transtype` (array)
- `relationship` (array)
- `startdate` (string)
- `enddate` (string)
- `lastactionstartdate` (string)
- `lastactionenddate` (string)
- `isinternaltrans` (eYesNoIgnoreFlag)
- `isoperator` (eYesNoIgnoreFlag)

---

## Contact

### `GET` /api/Contact/getContact/{id}/{securityToken}
**Get ALL Contact**

**Path params:**
- `id`: Contact ID (required)

---

### `GET` /api/Contact/getIdentification/{id}/{securityToken}
**Get Identification**

**Path params:**
- `id`: Contact ID (required)

---

### `GET` /api/Contact/getPhonenumbers/{id}/{securityToken}
**Get Phone Numbers**

**Path params:**
- `id`: Contact ID (required)

---

### `GET` /api/Contact/getContAircraftRelationships/{id}/{securityToken}
**Get Aircraft Relationships**

**Path params:**
- `id`: Contact ID (required)

---

### `GET` /api/Contact/getOtherlistings/{id}/{securityToken}
**Get Other Listings**

**Path params:**
- `id`: Contact ID (required)

---

### `POST` /api/Contact/getContactList/{securityToken}
**Get Contact List**

**Request body** (`ContListOptions`):
- `aircraftid` (array)
- `companyid` (integer)
- `companyname` (string)
- `firstname` (string)
- `lastname` (string)
- `title` (string)
- `email` (string)
- `actiondate` (string)
- `enddate` (string)
- `phonenumber` (string)
- `contactchanges` (string)
- `contlist` (array)
- `complist` (array)

---

### `POST` /api/Contact/getContactListPaged/{securityToken}/{pagesize}/{page}
**Get Contact List**

**Path params:**
- `pagesize`: Page Size (required)
- `page`: Page (required)

**Request body** (`ContListOptions`):
- `aircraftid` (array)
- `companyid` (integer)
- `companyname` (string)
- `firstname` (string)
- `lastname` (string)
- `title` (string)
- `email` (string)
- `actiondate` (string)
- `enddate` (string)
- `phonenumber` (string)
- `contactchanges` (string)
- `contlist` (array)
- `complist` (array)

---

## Model

### `POST` /api/Model/getModelMarketTrends/{securityToken}
**Get Model Market Trends**

**Request body** (`ModelTrendOptions`):
- `modlist` (array)
- `displayRange` (integer)
- `startdate` (string)
- `enddate` (string)
- `productcode` (array)

---

### `POST` /api/Model/getModelOperationCosts/{securityToken}
**Get Model Operation Costs**

**Request body** (`ModelPerformanceOptions`):
- `modlist` (array)
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)
- `make` (string)
- `annualhours` (integer)
- `fuelprice` (integer)

---

### `POST` /api/Model/getModelPerformanceSpecs/{securityToken}
**Get Model Performance Specs**

**Request body** (`ModelPerformanceOptions`):
- `modlist` (array)
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)
- `make` (string)
- `annualhours` (integer)
- `fuelprice` (integer)

---

## Utility

### `GET` /api/Utility/getAccountInfo/{securityToken}
**Get my user account**

---

### `GET` /api/Utility/getProductCodes/{securityToken}
**Get my product codes**

---

### `GET` /api/Utility/getAirframeTypes/{securityToken}
**Get Aircraft Airframes**

---

### `POST` /api/Utility/getMakeTypeList/{securityToken}
**Get Aircraft Make Types**

**Request body** (`AcAirframeOptions`):
- `airframetype` (eAirFrameTypes)

---

### `GET` /api/Utility/getWeightClassTypes/{securityToken}
**Get Aircraft Weight Classes**

---

### `GET` /api/Utility/getAirframeJniqSizes/{securityToken}
**Get Aircraft Jniq Sizes**

---

### `POST` /api/Utility/getAircraftMakeList/{securityToken}
**Get Aircraft Makes**

**Request body** (`AcMakeOptions`):
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)

---

### `POST` /api/Utility/getAircraftModelList/{securityToken}
**Get Aircraft Models**

**Request body** (`AcModelOptions`):
- `airframetype` (eAirFrameTypes)
- `maketype` (eMakeTypes)
- `make` (string)

---

### `GET` /api/Utility/getCompanyBusinessTypes/{securityToken}
**Get Company Business Types**

---

### `GET` /api/Utility/getAircraftCompanyRelationships/{securityToken}
**Get Aircraft Company Relationship Types**

---

### `GET` /api/Utility/getEventCategories/{securityToken}
**Get Aircraft Event Categories**

---

### `POST` /api/Utility/getEventTypes/{securityToken}
**Get Aircraft Event Types**

**Request body** (`AcEventOptions`):
- `eventcategory` (string)

---

### `POST` /api/Utility/getAirportList/{securityToken}
**Get Airport List**

**Request body** (`AirportOptions`):
- `name` (string)
- `city` (string)
- `state` (array)
- `statename` (array)
- `country` (string)
- `iata` (string)
- `icao` (string)
- `faaid` (string)

---

### `POST` /api/Utility/getStateList/{securityToken}
**Get State List**

**Request body** (`CountryOptions`):
- `country` (string)

---

### `GET` /api/Utility/getCountryList/{securityToken}
**Get Country List**

---

### `GET` /api/Utility/getAircraftLifecycleStatus/{securityToken}
**Get Aircraft LifeCycle Types**

---

### `GET` /api/Utility/getAircraftHistoryTransTypes/{securityToken}
**Get Aircraft History Transaction Types**

---
