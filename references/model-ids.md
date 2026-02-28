# JETNET Model ID Reference

Every aircraft model in JETNET has a numeric ID called **AMODID**. When calling endpoints like
`getRegNumber`, `BulkAircraftExport`, or `getFlightActivity`, you pass these IDs in the
`modlist` array to filter by aircraft type.

```json
{
  "modlist": [278, 288]  // G550 + G450
}
```

An empty `modlist: []` means **no model filter** (all models returned).

> **Machine-readable files**: [`model-id-table.json`](model-id-table.json) and [`model-id-table.csv`](model-id-table.csv)
> contain the same data in JSON and CSV formats.

> **Quick search**: Run `python scripts/model_search.py "G550"` to find model IDs from your terminal.

---

## Table of Contents

- [Business Jet](#business-jet) (268 models)
- [Turboprop](#turboprop) (186 models)
- [Jet Airliner](#jet-airliner) (252 models)
- [Turbine](#turbine) (127 models)
- [Piston](#piston) (39 models)
- [Common Lookup Examples](#common-lookup-examples)
- [Combining Filters](#combining-filters)

---

## Business Jet

| AMODID | Make | Model | ICAO | Weight Class | Size Category | Fleet |
|-------:|------|-------|------|-------------|---------------|------:|
| 1305 | AIRBUS | ACJ TWOTWENTY | A322 | Heavy | Airline Business Jet | 5 |
| 644 | AIRBUS | ACJ318 | A318 | Heavy | Airline Business Jet | 20 |
| 22 | AIRBUS | ACJ319 | A319 | Heavy | Airline Business Jet | 73 |
| 1220 | AIRBUS | ACJ319neo | A19N | Heavy | Airline Business Jet | 7 |
| 1133 | AIRBUS | ACJ320 | A20N | Heavy | Airline Business Jet | 18 |
| 1218 | AIRBUS | ACJ320neo | A20N | Heavy | Airline Business Jet | 8 |
| 1174 | AIRBUS | ACJ330 | A30N | Heavy | Airline Business Jet | 4 |
| 23 | ASTRA | 1125 | ASTR | Medium | Mid-Size Jet | 23 |
| 24 | ASTRA | 1125SP | ASTR | Medium | Mid-Size Jet | 48 |
| 25 | ASTRA | 1125SPX | ASTR | Medium | Mid-Size Jet | 59 |
| 26 | BEECHJET | 400 | BE40 | Light | Light Jet | 64 |
| 27 | BEECHJET | 400A | BE40 | Light | Light Jet | 308 |
| 28 | BOEING | BBJ | B737 | Heavy | Airline Business Jet | 132 |
| 1270 | BOEING | BBJ MAX 7 | B37M | Heavy | Airline Business Jet | 1 |
| 1271 | BOEING | BBJ MAX 8 | B38M | Heavy | Airline Business Jet | 9 |
| 1272 | BOEING | BBJ MAX 9 | B39M | Heavy | Airline Business Jet | 2 |
| 266 | BOEING | BBJ2 | B738 | Heavy | Airline Business Jet | 26 |
| 655 | BOEING | BBJ3 | B739 | Heavy | Airline Business Jet | 7 |
| 1263 | BOEING | BBJ747-8 | B748 | Heavy | Airline Business Jet | 4 |
| 1261 | BOEING | BBJ787-8 | B788 | Heavy | Airline Business Jet | 2 |
| 1262 | BOEING | BBJ787-9 | B789 | Heavy | Airline Business Jet | 1 |
| 272 | CHALLENGER | 300 | CL30 | Heavy | Super Mid-Size Jet | 457 |
| 1188 | CHALLENGER | 350 | CL35 | Heavy | Super Mid-Size Jet | 421 |
| 1317 | CHALLENGER | 3500 | CL35 | Heavy | Super Mid-Size Jet | 194 |
| 29 | CHALLENGER | 600 | CL60 | Heavy | Large Jet | 85 |
| 30 | CHALLENGER | 601-1A | CL60 | Heavy | Large Jet | 66 |
| 31 | CHALLENGER | 601-3A | CL60 | Heavy | Large Jet | 134 |
| 32 | CHALLENGER | 601-3R | CL60 | Heavy | Large Jet | 60 |
| 33 | CHALLENGER | 604 | CL60 | Heavy | Large Jet | 365 |
| 630 | CHALLENGER | 605 | CL60 | Heavy | Large Jet | 288 |
| 1217 | CHALLENGER | 650 | CL60 | Heavy | Large Jet | 184 |
| 273 | CHALLENGER | 800 | CRJ2 | Heavy | Large Jet | 9 |
| 624 | CHALLENGER | 850 | CRJ2 | Heavy | Large Jet | 76 |
| 625 | CHALLENGER | 870 | CRJ7 | Heavy | Large Jet | 10 |
| 1253 | CIRRUS | VISION SF50 | SF50 | Very Light Jet | Personal Jet | 92 |
| 1284 | CIRRUS | VISION SF50 G2 | SF50 | Very Light Jet | Personal Jet | 187 |
| 1307 | CIRRUS | VISION SF50 G2+ | SF50 | Very Light Jet | Personal Jet | 504 |
| 34 | CITATION | 500 | C500 | Light | Very Light Jet | 349 |
| 35 | CITATION | 525 | C525 | Light | Very Light Jet | 359 |
| 1325 | CITATION | ASCEND | C56X | Medium | Super Light Jet | 9 |
| 36 | CITATION | BRAVO | C55B | Light | Light Jet | 336 |
| 37 | CITATION | CJ1 | C525 | Light | Very Light Jet | 198 |
| 295 | CITATION | CJ1+ | C525 | Light | Very Light Jet | 102 |
| 38 | CITATION | CJ2 | C25A | Light | Very Light Jet | 243 |
| 296 | CITATION | CJ2+ | C25A | Light | Very Light Jet | 226 |
| 279 | CITATION | CJ3 | C25B | Light | Light Jet | 415 |
| 1194 | CITATION | CJ3+ | C25B | Light | Light Jet | 322 |
| 651 | CITATION | CJ4 | C25C | Light | Light Jet | 345 |
| 1304 | CITATION | CJ4 GEN2 | C25C | Light | Light Jet | 148 |
| 39 | CITATION | ENCORE | C560 | Light | Light Jet | 168 |
| 641 | CITATION | ENCORE+ | C560 | Light | Light Jet | 66 |
| 40 | CITATION | EXCEL | C56X | Light | Super Light Jet | 371 |
| 41 | CITATION | I | C500 | Light | Very Light Jet | 27 |
| 42 | CITATION | I/SP | C501 | Light | Very Light Jet | 315 |
| 43 | CITATION | II | C550 | Light | Light Jet | 607 |
| 44 | CITATION | II/SP | C551 | Light | Light Jet | 83 |
| 45 | CITATION | III | C650 | Medium | Mid-Size Jet | 203 |
| 1167 | CITATION | LATITUDE | C68A | Medium | Mid-Size Jet | 468 |
| 1229 | CITATION | LONGITUDE | C700 | Medium | Super Mid-Size Jet | 165 |
| 1166 | CITATION | M2 | C25M | Light | Light Jet | 309 |
| 1313 | CITATION | M2 GEN 2 | C25M | Light | Light Jet | 102 |
| 299 | CITATION | MUSTANG | C510 | Very Light Jet | Very Light Jet | 479 |
| 46 | CITATION | S/II | C550 | Light | Light Jet | 159 |
| 270 | CITATION | SOVEREIGN | C680 | Medium | Mid-Size Jet | 350 |
| 1191 | CITATION | SOVEREIGN+ | C680 | Medium | Mid-Size Jet | 100 |
| 47 | CITATION | ULTRA | C560 | Light | Light Jet | 279 |
| 48 | CITATION | V | C560 | Light | Light Jet | 262 |
| 49 | CITATION | VI | C650 | Medium | Mid-Size Jet | 38 |
| 50 | CITATION | VII | C650 | Medium | Mid-Size Jet | 119 |
| 51 | CITATION | X | C750 | Heavy | Super Mid-Size Jet | 315 |
| 1200 | CITATION | X+ | C750 | Heavy | Super Mid-Size Jet | 32 |
| 287 | CITATION | XLS | C56X | Medium | Super Light Jet | 330 |
| 1314 | CITATION | XLS GEN 2 | C56X | Medium | Super Light Jet | 60 |
| 652 | CITATION | XLS+ | C56X | Medium | Super Light Jet | 320 |
| 53 | DIAMOND | I | MU30 | Light | Light Jet | 5 |
| 54 | DIAMOND | IA | MU30 | Light | Light Jet | 86 |
| 55 | DIAMOND | II | MU30 | Light | Light Jet | 1 |
| 281 | DORNIER | ENVOY 3 | J328 | Medium | Commercial Jet Airliner | 11 |
| 1163 | ECLIPSE | 550 | EA50 | Very Light Jet | Very Light Jet | 36 |
| 633 | ECLIPSE | EA500 | EA50 | Very Light Jet | Very Light Jet | 270 |
| 686 | EMBRAER | LEGACY 450 | E545 | Heavy | Mid-Size Jet | 22 |
| 687 | EMBRAER | LEGACY 500 | E550 | Heavy | Super Mid-Size Jet | 86 |
| 269 | EMBRAER | LEGACY 600 | E35L | Heavy | Large Jet | 177 |
| 688 | EMBRAER | LEGACY 650 | E35L | Heavy | Large Jet | 97 |
| 1258 | EMBRAER | LEGACY 650E | E35L | Heavy | Large Jet | 14 |
| 645 | EMBRAER | LEGACY SHUTTLE | E35L | Heavy | Large Jet | 18 |
| 661 | EMBRAER | LINEAGE 1000 | E190 | Heavy | Airline Business Jet | 19 |
| 1274 | EMBRAER | LINEAGE 1000E | E190 | Heavy | Airline Business Jet | 12 |
| 654 | EMBRAER | PHENOM 100 | E50P | Light | Very Light Jet | 307 |
| 1255 | EMBRAER | PHENOM 100E | E50P | Light | Very Light Jet | 49 |
| 1256 | EMBRAER | PHENOM 100EV | E50P | Light | Very Light Jet | 71 |
| 1327 | EMBRAER | PHENOM 100EX | E50P | Light | Very Light Jet | 20 |
| 660 | EMBRAER | PHENOM 300 | E55P | Light | Light Jet | 540 |
| 1259 | EMBRAER | PHENOM 300E | E55P | Light | Light Jet | 378 |
| 1279 | EMBRAER | PRAETOR 500 | E545 | Heavy | Mid-Size Jet | 168 |
| 1280 | EMBRAER | PRAETOR 600 | E550 | Heavy | Super Mid-Size Jet | 149 |
| 56 | FALCON | 10 | FA10 | Light | Light Jet | 189 |
| 57 | FALCON | 100 | FA10 | Light | Light Jet | 37 |
| 58 | FALCON | 200 | FA20 | Medium | Super Mid-Size Jet | 33 |
| 59 | FALCON | 2000 | FA20 | Heavy | Large Jet | 231 |
| 634 | FALCON | 2000DX | F2TH | Heavy | Large Jet | 4 |
| 259 | FALCON | 2000EX | F2TH | Heavy | Large Jet | 26 |
| 674 | FALCON | 2000EX EASy | F2TH | Heavy | Large Jet | 90 |
| 656 | FALCON | 2000LX | F2TH | Heavy | Large Jet | 146 |
| 1190 | FALCON | 2000LXS | F2TH | Heavy | Large Jet | 156 |
| 1149 | FALCON | 2000S | F2TH | Heavy | Large Jet | 48 |
| 60 | FALCON | 20C | FA20 | Medium | Super Mid-Size Jet | 157 |
| 61 | FALCON | 20C-5 | FA20 | Medium | Super Mid-Size Jet | 22 |
| 62 | FALCON | 20D | FA20 | Medium | Super Mid-Size Jet | 50 |
| 63 | FALCON | 20D-5 | FA20 | Medium | Super Mid-Size Jet | 5 |
| 64 | FALCON | 20E | FA20 | Medium | Super Mid-Size Jet | 46 |
| 65 | FALCON | 20E-5 | FA20 | Medium | Super Mid-Size Jet | 15 |
| 66 | FALCON | 20F | FA20 | Medium | Super Mid-Size Jet | 101 |
| 67 | FALCON | 20F-5 | FA20 | Medium | Super Mid-Size Jet | 80 |
| 68 | FALCON | 20G | FA20 | Medium | Super Mid-Size Jet | 6 |
| 69 | FALCON | 50 | FA50 | Heavy | Super Mid-Size Jet | 238 |
| 1291 | FALCON | 50-4 | FA50 | Heavy | Super Mid-Size Jet | 5 |
| 292 | FALCON | 50-40 | FA50 | Heavy | Super Mid-Size Jet | 8 |
| 70 | FALCON | 50EX | FA50 | Heavy | Super Mid-Size Jet | 101 |
| 1278 | FALCON | 6X | FA6X | Heavy | Large Long-Range Jet | 23 |
| 297 | FALCON | 7X | FA7X | Heavy | Large Long-Range Jet | 300 |
| 1213 | FALCON | 8X | FA8X | Heavy | Large Ultra Long-Range Jet | 117 |
| 71 | FALCON | 900 | F900 | Heavy | Large Long-Range Jet | 177 |
| 73 | FALCON | 900C | F900 | Heavy | Large Long-Range Jet | 25 |
| 606 | FALCON | 900DX | F900 | Heavy | Large Long-Range Jet | 24 |
| 74 | FALCON | 900EX | F900 | Heavy | Large Long-Range Jet | 118 |
| 673 | FALCON | 900EX EASy | F900 | Heavy | Large Long-Range Jet | 122 |
| 681 | FALCON | 900LX | F900 | Heavy | Large Long-Range Jet | 95 |
| 286 | GLOBAL | 5000 | GL5T | Heavy | Large Long-Range Jet | 238 |
| 1275 | GLOBAL | 5500 | GL5T | Heavy | Large Long-Range Jet | 52 |
| 1148 | GLOBAL | 6000 | GLEX | Heavy | Large Ultra Long-Range Jet | 338 |
| 1276 | GLOBAL | 6500 | GLEX | Heavy | Large Ultra Long-Range Jet | 139 |
| 1161 | GLOBAL | 7500 | GL7T | Heavy | Large Ultra Long-Range Jet | 249 |
| 1162 | GLOBAL | 8000 | GL7T | Heavy | Large Ultra Long-Range Jet | 3 |
| 76 | GLOBAL | EXPRESS | GLEX | Heavy | Large Ultra Long-Range Jet | 150 |
| 298 | GLOBAL | EXPRESS XRS | GLEX | Heavy | Large Ultra Long-Range Jet | 163 |
| 77 | GULFSTREAM | G-II | GLF2 | Heavy | Large Jet | 214 |
| 78 | GULFSTREAM | G-IIB | GLF2 | Heavy | Large Jet | 42 |
| 79 | GULFSTREAM | G-III | GLF3 | Heavy | Large Jet | 202 |
| 81 | GULFSTREAM | G-IV | GLF4 | Heavy | Large Long-Range Jet | 197 |
| 275 | GULFSTREAM | G-IV (G300) | GLF4 | Heavy | Large Jet | 13 |
| 276 | GULFSTREAM | G-IV (G400) | GLF4 | Heavy | Large Long-Range Jet | 23 |
| 82 | GULFSTREAM | G-IVSP | GLF4 | Heavy | Large Long-Range Jet | 303 |
| 83 | GULFSTREAM | G-V | GLF5 | Heavy | Large Long-Range Jet | 193 |
| 262 | GULFSTREAM | G100 | ASTR | Medium | Mid-Size Jet | 22 |
| 274 | GULFSTREAM | G150 | G150 | Medium | Mid-Size Jet | 126 |
| 75 | GULFSTREAM | G200 | GALX | Heavy | Super Mid-Size Jet | 250 |
| 666 | GULFSTREAM | G280 | G280 | Heavy | Super Mid-Size Jet | 326 |
| 294 | GULFSTREAM | G350 | GLF4 | Heavy | Large Jet | 11 |
| 1320 | GULFSTREAM | G400 | GA4C | Heavy | Large Long-Range Jet | 5 |
| 288 | GULFSTREAM | G450 | GLF4 | Heavy | Large Long-Range Jet | 355 |
| 1209 | GULFSTREAM | G500 | GA5C | Heavy | Large Long-Range Jet | 227 |
| 278 | GULFSTREAM | G550 | GLF5 | Heavy | Large Ultra Long-Range Jet | 622 |
| 1210 | GULFSTREAM | G600 | GA6C | Heavy | Large Ultra Long-Range Jet | 242 |
| 663 | GULFSTREAM | G650 | GLF6 | Heavy | Large Ultra Long-Range Jet | 151 |
| 1211 | GULFSTREAM | G650ER | GLF6 | Heavy | Large Ultra Long-Range Jet | 447 |
| 1290 | GULFSTREAM | G700 | GA7C | Heavy | Large Ultra Long-Range Jet | 139 |
| 1310 | GULFSTREAM | G800 | GA8C | Heavy | Large Ultra Long-Range Jet | 51 |
| 277 | GULFSTREAM | GV-SP (G500) | GLF5 | Heavy | Large Ultra Long-Range Jet | 9 |
| 84 | HAWKER | 1000A | H25C | Medium | Mid-Size Jet | 45 |
| 85 | HAWKER | 1000B | H25C | Medium | Mid-Size Jet | 7 |
| 86 | HAWKER | 125-1A | H25A | Medium | Mid-Size Jet | 60 |
| 87 | HAWKER | 125-1AS | H25A | Medium | Mid-Size Jet | 13 |
| 88 | HAWKER | 125-1B | H25A | Medium | Mid-Size Jet | 34 |
| 89 | HAWKER | 125-3A | H25A | Medium | Mid-Size Jet | 11 |
| 90 | HAWKER | 125-3A/RA | H25A | Medium | Mid-Size Jet | 15 |
| 91 | HAWKER | 125-3A/RAS | H25A | Medium | Mid-Size Jet | 4 |
| 92 | HAWKER | 125-3AS | H25A | Medium | Mid-Size Jet | 6 |
| 93 | HAWKER | 125-3B | H25A | Medium | Mid-Size Jet | 20 |
| 94 | HAWKER | 125-3B/RA | H25A | Medium | Mid-Size Jet | 7 |
| 95 | HAWKER | 125-3B/RAS | H25A | Medium | Mid-Size Jet | 1 |
| 96 | HAWKER | 125-3BS | H25A | Medium | Mid-Size Jet | 1 |
| 97 | HAWKER | 125-400A | H25A | Medium | Mid-Size Jet | 30 |
| 98 | HAWKER | 125-400AS | H25A | Medium | Mid-Size Jet | 56 |
| 99 | HAWKER | 125-400B | H25A | Medium | Mid-Size Jet | 27 |
| 100 | HAWKER | 125-400BS | H25A | Medium | Mid-Size Jet | 3 |
| 101 | HAWKER | 125-600A | H25A | Medium | Mid-Size Jet | 41 |
| 102 | HAWKER | 125-600AS | H25A | Medium | Mid-Size Jet | 14 |
| 103 | HAWKER | 125-600B | H25A | Medium | Mid-Size Jet | 17 |
| 104 | HAWKER | 125-600BS | H25A | Medium | Mid-Size Jet | 1 |
| 105 | HAWKER | 125-700A | H25B | Medium | Mid-Size Jet | 182 |
| 106 | HAWKER | 125-700B | H25B | Medium | Mid-Size Jet | 33 |
| 257 | HAWKER | 4000 | HA4T | Heavy | Super Mid-Size Jet | 79 |
| 284 | HAWKER | 400XP | BE40 | Light | Light Jet | 222 |
| 1247 | HAWKER | 400XPR | BE4W | Light | Light Jet | 6 |
| 643 | HAWKER | 750 | H25B | Medium | Super Light Jet | 48 |
| 107 | HAWKER | 800A | H25B | Medium | Mid-Size Jet | 238 |
| 109 | HAWKER | 800B | H25B | Medium | Mid-Size Jet | 54 |
| 110 | HAWKER | 800XP | H25B | Medium | Mid-Size Jet | 425 |
| 607 | HAWKER | 800XPI | H25B | Medium | Mid-Size Jet | 51 |
| 628 | HAWKER | 850XP | H25B | Medium | Mid-Size Jet | 101 |
| 642 | HAWKER | 900XP | H25B | Medium | Mid-Size Jet | 185 |
| 1277 | HONDAJET | ELITE | HDJT | Light | Very Light Jet | 67 |
| 1319 | HONDAJET | ELITE II | HDJT | Light | Very Light Jet | 69 |
| 1308 | HONDAJET | ELITE S | HDJT | Light | Very Light Jet | 42 |
| 677 | HONDAJET | HA-420 | HDJT | Light | Very Light Jet | 120 |
| 111 | JET COMMANDER | 1121 | JCOM | Light | Mid-Size Jet | 112 |
| 112 | JET COMMANDER | 1121A | JCOM | Light | Mid-Size Jet | 4 |
| 113 | JET COMMANDER | 1121B | JCOM | Light | Mid-Size Jet | 33 |
| 114 | JETSTAR | 6 | L29A | Heavy | Mid-Size Jet | 51 |
| 115 | JETSTAR | 731 | L29B | Heavy | Mid-Size Jet | 61 |
| 116 | JETSTAR | 8 | L29A | Heavy | Mid-Size Jet | 52 |
| 117 | JETSTAR | II | L29B | Heavy | Mid-Size Jet | 40 |
| 118 | LEARJET | 23 | LJ23 | Light | Light Jet | 94 |
| 119 | LEARJET | 24 | LJ24 | Light | Light Jet | 81 |
| 120 | LEARJET | 24A | LJ24 | Light | Light Jet | 13 |
| 121 | LEARJET | 24B | LJ24 | Light | Light Jet | 49 |
| 122 | LEARJET | 24D | LJ24 | Light | Light Jet | 99 |
| 123 | LEARJET | 24E | LJ24 | Light | Light Jet | 17 |
| 124 | LEARJET | 24F | LJ24 | Light | Light Jet | 12 |
| 125 | LEARJET | 25 | LJ25 | Light | Light Jet | 63 |
| 126 | LEARJET | 25B | LJ25 | Light | Light Jet | 112 |
| 127 | LEARJET | 25C | LJ25 | Light | Light Jet | 25 |
| 128 | LEARJET | 25D | LJ25 | Light | Light Jet | 164 |
| 129 | LEARJET | 25G | LJ25 | Light | Light Jet | 4 |
| 130 | LEARJET | 28 | LJ28 | Light | Light Jet | 5 |
| 131 | LEARJET | 29 | LJ28 | Light | Light Jet | 4 |
| 132 | LEARJET | 31 | LJ31 | Light | Light Jet | 38 |
| 133 | LEARJET | 31A | LJ31 | Light | Light Jet | 208 |
| 134 | LEARJET | 35 | LJ35 | Light | Light Jet | 66 |
| 135 | LEARJET | 35A | LJ35 | Light | Light Jet | 607 |
| 136 | LEARJET | 36 | LJ35 | Light | Light Jet | 17 |
| 137 | LEARJET | 36A | LJ35 | Light | Light Jet | 46 |
| 283 | LEARJET | 40 | LJ40 | Medium | Light Jet | 37 |
| 636 | LEARJET | 40XR | LJ40 | Medium | Light Jet | 95 |
| 138 | LEARJET | 45 | LJ45 | Medium | Light Jet | 246 |
| 293 | LEARJET | 45XR | LJ45 | Medium | Light Jet | 208 |
| 139 | LEARJET | 55 | LJ55 | Light | Mid-Size Jet | 124 |
| 140 | LEARJET | 55B | LJ55 | Medium | Mid-Size Jet | 8 |
| 141 | LEARJET | 55C | LJ55 | Medium | Mid-Size Jet | 15 |
| 142 | LEARJET | 60 | LJ60 | Medium | Mid-Size Jet | 315 |
| 635 | LEARJET | 60XR | LJ60 | Medium | Mid-Size Jet | 115 |
| 1164 | LEARJET | 70 | LJ70 | Medium | Light Jet | 14 |
| 1165 | LEARJET | 75 | LJ75 | Medium | Super Light Jet | 137 |
| 1287 | LEARJET | 75 LIBERTY | LJ75 | Medium | Super Light Jet | 18 |
| 1186 | NEXTANT | 400XT | BE4W | Light | Light Jet | 27 |
| 1214 | NEXTANT | 400XTi | BE4W | Light | Light Jet | 39 |
| 1199 | PILATUS | PC-24 | PC24 | Light | Light Jet | 347 |
| 143 | PREMIER | I | PRM1 | Light | Very Light Jet | 132 |
| 627 | PREMIER | IA | PRM1 | Light | Very Light Jet | 163 |
| 144 | SABRELINER | 40 | SBR1 | Light | Light Jet | 73 |
| 145 | SABRELINER | 40A | SBR1 | Light | Light Jet | 40 |
| 146 | SABRELINER | 40EL | SBR1 | Light | Light Jet | 14 |
| 147 | SABRELINER | 40EX | SBR1 | Light | Light Jet | 4 |
| 148 | SABRELINER | 40R | SBR1 | Light | Light Jet | 4 |
| 149 | SABRELINER | 40SE | SBR1 | Light | Light Jet | 2 |
| 150 | SABRELINER | 50 | SBR1 | Light | Light Jet | 1 |
| 151 | SABRELINER | 60 | SBR1 | Medium | Light Jet | 79 |
| 152 | SABRELINER | 60A | SBR1 | Medium | Light Jet | 4 |
| 153 | SABRELINER | 60AELXM | SBR1 | Medium | Light Jet | 1 |
| 154 | SABRELINER | 60EL | SBR1 | Medium | Light Jet | 8 |
| 155 | SABRELINER | 60ELXM | SBR1 | Medium | Light Jet | 37 |
| 156 | SABRELINER | 60EX | SBR1 | Medium | Light Jet | 6 |
| 157 | SABRELINER | 60SC | SBR1 | Medium | Light Jet | 3 |
| 158 | SABRELINER | 60SCEL | SBR1 | Medium | Light Jet | 2 |
| 159 | SABRELINER | 60SCELXM | SBR1 | Medium | Light Jet | 3 |
| 160 | SABRELINER | 60SCEX | SBR1 | Medium | Light Jet | 1 |
| 161 | SABRELINER | 65 | SBR1 | Medium | Light Jet | 77 |
| 162 | SABRELINER | 75 | SBR2 | Medium | Light Jet | 8 |
| 163 | SABRELINER | 80 | SBR2 | Medium | Light Jet | 60 |
| 164 | SABRELINER | 80A | SBR2 | Medium | Light Jet | 4 |
| 165 | SABRELINER | 80SC | SBR2 | Medium | Mid-Size Jet | 9 |
| 1157 | SUKHOI | SBJ | SSBJ | Heavy | Airline Business Jet | 15 |
| 683 | SYBERJET | SJ30-2 | SJ30 | Light | Light Jet | 10 |
| 168 | WESTWIND | 1 | WW24 | Medium | Mid-Size Jet | 115 |
| 169 | WESTWIND | 1123 | WW23 | Medium | Mid-Size Jet | 31 |
| 170 | WESTWIND | 1124 | WW24 | Medium | Mid-Size Jet | 58 |
| 171 | WESTWIND | 2 | WW24 | Medium | Mid-Size Jet | 89 |

---

## Turboprop

| AMODID | Make | Model | ICAO | Weight Class | Size Category | Fleet |
|-------:|------|-------|------|-------------|---------------|------:|
| 691 | ATR | ATR 42-300 | AT43 | Medium | Commercial Turboprop Airliner | 230 |
| 692 | ATR | ATR 42-300F | AT43 | Medium | Commercial Turboprop Airliner | 54 |
| 693 | ATR | ATR 42-400 | AT44 | Medium | Commercial Turboprop Airliner | 5 |
| 694 | ATR | ATR 42-500 | AT45 | Medium | Commercial Turboprop Airliner | 128 |
| 1108 | ATR | ATR 42-600 | AT46 | Medium | Commercial Turboprop Airliner | 107 |
| 695 | ATR | ATR 72-200 | AT72 | Medium | Commercial Turboprop Airliner | 133 |
| 697 | ATR | ATR 72-200F | AT72 | Medium | Commercial Turboprop Airliner | 55 |
| 696 | ATR | ATR 72-500 | AT75 | Medium | Commercial Turboprop Airliner | 342 |
| 1235 | ATR | ATR 72-500F | AT75 | Medium | Commercial Turboprop Airliner | 19 |
| 1105 | ATR | ATR 72-600 | AT76 | Medium | Commercial Turboprop Airliner | 802 |
| 1228 | ATR | ATR 72-600 Combi | AT76 | Medium | Commercial Turboprop Airliner | 2 |
| 1260 | ATR | ATR 72-600F | AT76 | Medium | Commercial Turboprop Airliner | 30 |
| 1205 | AVANTI | EVO | P180 | Light | Multi-Engine Turbo-Prop | 17 |
| 631 | AVANTI | II | P180 | Light | Multi-Engine Turbo-Prop | 129 |
| 179 | AVANTI | P180 | P180 | Light | Multi-Engine Turbo-Prop | 104 |
| 768 | BAE | ATP | ATP | Medium | Commercial Turboprop Airliner | 43 |
| 769 | BAE | ATP(F) | ATP | Medium | Commercial Turboprop Airliner | 20 |
| 772 | BEECH | 1900C | B190 | Medium | Commercial Turboprop Airliner | 74 |
| 773 | BEECH | 1900C-1 | B190 | Medium | Commercial Turboprop Airliner | 171 |
| 774 | BEECH | 1900D | B190 | Medium | Commercial Turboprop Airliner | 437 |
| 775 | BEECH | 99 | BE99 | Medium | Commercial Turboprop Airliner | 93 |
| 776 | BEECH | 99A | BE99 | Medium | Commercial Turboprop Airliner | 44 |
| 777 | BEECH | B99 | BE99 | Medium | Commercial Turboprop Airliner | 16 |
| 779 | BEECH | C99 | BE99 | Medium | Commercial Turboprop Airliner | 76 |
| 1306 | BEECHCRAFT | DENALI | BE22 | Light | Single-Engine Turbo-Prop | 3 |
| 897 | BOMBARDIER | DHC-8-100 | DH8A | Medium | Commercial Turboprop Airliner | 290 |
| 1244 | BOMBARDIER | DHC-8-100PF | DH8A | Medium | Commercial Turboprop Airliner | 4 |
| 898 | BOMBARDIER | DHC-8-200 | DH8B | Medium | Commercial Turboprop Airliner | 21 |
| 899 | BOMBARDIER | DHC-8-300 | DH8C | Medium | Commercial Turboprop Airliner | 118 |
| 901 | BOMBARDIER | DHC-8-Q100 | DH8A | Medium | Commercial Turboprop Airliner | 5 |
| 902 | BOMBARDIER | DHC-8-Q200 | DH8B | Medium | Commercial Turboprop Airliner | 84 |
| 903 | BOMBARDIER | DHC-8-Q200 COMBI | DH8B | Medium | Commercial Turboprop Airliner | 1 |
| 904 | BOMBARDIER | DHC-8-Q300 | DH8C | Medium | Commercial Turboprop Airliner | 135 |
| 1231 | BOMBARDIER | DHC-8-Q400 Combi | DH8D | Medium | Commercial Turboprop Airliner | 6 |
| 1184 | BOMBARDIER | DHC-8-Q400PF | DH8D | Medium | Commercial Turboprop Airliner | 5 |
| 180 | CARAVAN | 208 | C208 | Light | Single-Engine Turbo-Prop | 611 |
| 181 | CARAVAN | 208B | C208 | Light | Single-Engine Turbo-Prop | 1,753 |
| 1170 | CARAVAN | 208B EX | C208 | Light | Single-Engine Turbo-Prop | 884 |
| 1266 | CESSNA | SKYCOURIER 408 | C408 | Light | Commercial Turboprop Airliner | 59 |
| 183 | CHEYENNE | 400 | PAY4 | Heavy | Multi-Engine Turbo-Prop | 43 |
| 184 | CHEYENNE | I | PAY1 | Light | Multi-Engine Turbo-Prop | 198 |
| 185 | CHEYENNE | IA | PAY1 | Light | Multi-Engine Turbo-Prop | 17 |
| 186 | CHEYENNE | II | PAY2 | Light | Multi-Engine Turbo-Prop | 525 |
| 187 | CHEYENNE | III | PAY3 | Medium | Multi-Engine Turbo-Prop | 89 |
| 188 | CHEYENNE | IIIA | PAY3 | Medium | Multi-Engine Turbo-Prop | 60 |
| 189 | CHEYENNE | IIXL | PAY2 | Light | Multi-Engine Turbo-Prop | 82 |
| 190 | CONQUEST | I | C425 | Light | Multi-Engine Turbo-Prop | 236 |
| 191 | CONQUEST | II | C441 | Light | Multi-Engine Turbo-Prop | 363 |
| 905 | DE HAVILLAND | DASH 8-400 | DH8D | Medium | Commercial Turboprop Airliner | 649 |
| 884 | DE HAVILLAND | DHC-2T | DH2T | Light | Commercial Turboprop Airliner | 69 |
| 885 | DE HAVILLAND | DHC-3T | DH3T | Light | Commercial Turboprop Airliner | 106 |
| 890 | DE HAVILLAND | DHC-6-100 | DHC6 | Medium | Commercial Turboprop Airliner | 102 |
| 891 | DE HAVILLAND | DHC-6-200 | DHC6 | Medium | Commercial Turboprop Airliner | 114 |
| 892 | DE HAVILLAND | DHC-6-300 | DHC6 | Medium | Commercial Turboprop Airliner | 608 |
| 1326 | DE HAVILLAND | DHC-6-CLASSIC 300-G | DHC6 | Medium | Airliner Turbo-Prop Converted | 4 |
| 893 | DE HAVILLAND | DHC-7-102 | DHC7 | Medium | Commercial Turboprop Airliner | 86 |
| 894 | DE HAVILLAND | DHC-7-103 | DHC7 | Medium | Commercial Turboprop Airliner | 15 |
| 895 | DE HAVILLAND | DHC-7-110 | DHC7 | Medium | Commercial Turboprop Airliner | 4 |
| 907 | DORNIER | 228-100 | D228 | Medium | Commercial Turboprop Airliner | 12 |
| 908 | DORNIER | 228-101 | D228 | Medium | Commercial Turboprop Airliner | 17 |
| 909 | DORNIER | 228-200 | D228 | Medium | Commercial Turboprop Airliner | 13 |
| 910 | DORNIER | 228-201 | D228 | Medium | Commercial Turboprop Airliner | 53 |
| 911 | DORNIER | 228-202 | D228 | Medium | Commercial Turboprop Airliner | 73 |
| 912 | DORNIER | 228-212 | D228 | Medium | Commercial Turboprop Airliner | 60 |
| 913 | DORNIER | 328 | D328 | Medium | Commercial Turboprop Airliner | 111 |
| 1135 | DORNIER | Do 228NG | D228 | Medium | Commercial Turboprop Airliner | 17 |
| 930 | EMBRAER | EMB-120 | E120 | Medium | Commercial Turboprop Airliner | 346 |
| 931 | EMBRAER | EMB-120QC | E120 | Medium | Commercial Turboprop Airliner | 3 |
| 1298 | EPIC | E1000 | EPIC | Light | Single-Engine Turbo-Prop | 13 |
| 1332 | EPIC | E1000 AX | EPIC | Light | Very Light Jet | 18 |
| 1309 | EPIC | E1000 GX | EPIC | Light | Single-Engine Turbo-Prop | 84 |
| 945 | FOKKER | 50 | F50 | Medium | Commercial Turboprop Airliner | 207 |
| 192 | GULFSTREAM | G-I | G159 | Heavy | Multi-Engine Turbo-Prop | 200 |
| 263 | JETSTREAM | 31 | JS31 | Heavy | Commercial Turboprop Airliner | 219 |
| 264 | JETSTREAM | 32 | JS32 | Heavy | Commercial Turboprop Airliner | 162 |
| 265 | JETSTREAM | 41 | JS41 | Heavy | Commercial Turboprop Airliner | 104 |
| 193 | KING AIR | 100 | BE10 | Medium | Multi-Engine Turbo-Prop | 89 |
| 194 | KING AIR | 200 | BE20 | Heavy | Multi-Engine Turbo-Prop | 833 |
| 195 | KING AIR | 200C | BE20 | Heavy | Multi-Engine Turbo-Prop | 35 |
| 197 | KING AIR | 200T | BE20 | Heavy | Multi-Engine Turbo-Prop | 21 |
| 1132 | KING AIR | 250 | BE20 | Heavy | Multi-Engine Turbo-Prop | 274 |
| 1303 | KING AIR | 260 | BE20 | Heavy | Multi-Engine Turbo-Prop | 91 |
| 198 | KING AIR | 300 | BE30 | Heavy | Multi-Engine Turbo-Prop | 225 |
| 199 | KING AIR | 300LW | BE30 | Heavy | Multi-Engine Turbo-Prop | 22 |
| 200 | KING AIR | 350 | B350 | Heavy | Multi-Engine Turbo-Prop | 685 |
| 261 | KING AIR | 350C | B350 | Heavy | Multi-Engine Turbo-Prop | 96 |
| 1250 | KING AIR | 350ER | B350 | Heavy | Multi-Engine Turbo-Prop | 46 |
| 682 | KING AIR | 350i | B350 | Heavy | Multi-Engine Turbo-Prop | 482 |
| 1251 | KING AIR | 350iER | B350 | Heavy | Multi-Engine Turbo-Prop | 16 |
| 1301 | KING AIR | 360 | B350 | Heavy | Multi-Engine Turbo-Prop | 119 |
| 1329 | KING AIR | 360C | B350 | Heavy | Multi-Engine Turbo-Prop | 35 |
| 1302 | KING AIR | 360ER | B350 | Heavy | Multi-Engine Turbo-Prop | 14 |
| 201 | KING AIR | 90 | BE9L | Light | Multi-Engine Turbo-Prop | 111 |
| 202 | KING AIR | A/B90 | BE9L | Light | Multi-Engine Turbo-Prop | 23 |
| 203 | KING AIR | A100 | BE10 | Medium | Multi-Engine Turbo-Prop | 157 |
| 204 | KING AIR | A200 | BE20 | Heavy | Multi-Engine Turbo-Prop | 241 |
| 205 | KING AIR | A90 | BE9L | Light | Multi-Engine Turbo-Prop | 186 |
| 282 | KING AIR | A90-1 | BE9L | Light | Multi-Engine Turbo-Prop | 126 |
| 206 | KING AIR | B100 | BE10 | Medium | Multi-Engine Turbo-Prop | 137 |
| 207 | KING AIR | B200 | BE20 | Heavy | Multi-Engine Turbo-Prop | 1,143 |
| 208 | KING AIR | B200C | BE20 | Heavy | Multi-Engine Turbo-Prop | 126 |
| 1239 | KING AIR | B200CGT | BE20 | Heavy | Multi-Engine Turbo-Prop | 9 |
| 196 | KING AIR | B200CT | BE20 | Heavy | Multi-Engine Turbo-Prop | 9 |
| 649 | KING AIR | B200GT | BE20 | Heavy | Multi-Engine Turbo-Prop | 119 |
| 209 | KING AIR | B200SE | BE20 | Heavy | Multi-Engine Turbo-Prop | 5 |
| 210 | KING AIR | B200T | BE20 | Heavy | Multi-Engine Turbo-Prop | 25 |
| 211 | KING AIR | B90 | BE9L | Light | Multi-Engine Turbo-Prop | 183 |
| 212 | KING AIR | C90 | BE9L | Light | Multi-Engine Turbo-Prop | 516 |
| 213 | KING AIR | C90-1 | BE9L | Light | Multi-Engine Turbo-Prop | 46 |
| 214 | KING AIR | C90A | BE9L | Medium | Multi-Engine Turbo-Prop | 234 |
| 215 | KING AIR | C90B | BE9L | Medium | Multi-Engine Turbo-Prop | 437 |
| 623 | KING AIR | C90GT | BE9L | Medium | Multi-Engine Turbo-Prop | 98 |
| 653 | KING AIR | C90GTi | BE9L | Medium | Multi-Engine Turbo-Prop | 125 |
| 680 | KING AIR | C90GTx | BE9L | Medium | Multi-Engine Turbo-Prop | 202 |
| 216 | KING AIR | C90SE | BE9L | Medium | Multi-Engine Turbo-Prop | 16 |
| 217 | KING AIR | E90 | BE9L | Medium | Multi-Engine Turbo-Prop | 347 |
| 218 | KING AIR | F90 | BE9T | Medium | Multi-Engine Turbo-Prop | 203 |
| 219 | KING AIR | F90-1 | BE9T | Medium | Multi-Engine Turbo-Prop | 33 |
| 1110 | KODIAK | 100 | K100 | Light | Single-Engine Turbo-Prop | 130 |
| 1324 | KODIAK | 100 SERIES I | K100 | Light | Single-Engine Turbo-Prop | 116 |
| 1322 | KODIAK | 100 SERIES II | K100 | Light | Single-Engine Turbo-Prop | 45 |
| 1323 | KODIAK | 100 SERIES III | K100 | Light | Single-Engine Turbo-Prop | 77 |
| 1318 | KODIAK | 900 | K900 | Light | Single-Engine Turbo-Prop | 29 |
| 220 | MERLIN | 300 | SW3 | Heavy | Multi-Engine Turbo-Prop | 10 |
| 221 | MERLIN | IIA | SW2 | Light | Multi-Engine Turbo-Prop | 35 |
| 222 | MERLIN | IIB | SW2 | Light | Multi-Engine Turbo-Prop | 88 |
| 223 | MERLIN | III | SW3 | Heavy | Multi-Engine Turbo-Prop | 49 |
| 224 | MERLIN | IIIA | SW3 | Heavy | Multi-Engine Turbo-Prop | 42 |
| 225 | MERLIN | IIIB | SW3 | Heavy | Multi-Engine Turbo-Prop | 72 |
| 226 | MERLIN | IIIC | SW3 | Heavy | Multi-Engine Turbo-Prop | 28 |
| 227 | MERLIN | IV | SW4 | Heavy | Multi-Engine Turbo-Prop | 19 |
| 228 | MERLIN | IV-A | SW4 | Heavy | Multi-Engine Turbo-Prop | 37 |
| 229 | MERLIN | IV-C | SW4 | Heavy | Multi-Engine Turbo-Prop | 41 |
| 230 | MITSUBISHI | MARQUISE | MU2 | Medium | Multi-Engine Turbo-Prop | 139 |
| 231 | MITSUBISHI | MU-2A | MU2 | Light | Multi-Engine Turbo-Prop | 3 |
| 232 | MITSUBISHI | MU-2B | MU2 | Light | Multi-Engine Turbo-Prop | 34 |
| 233 | MITSUBISHI | MU-2C | MU2 | Light | Multi-Engine Turbo-Prop | 20 |
| 234 | MITSUBISHI | MU-2D | MU2 | Light | Multi-Engine Turbo-Prop | 19 |
| 235 | MITSUBISHI | MU-2F | MU2 | Light | Multi-Engine Turbo-Prop | 96 |
| 236 | MITSUBISHI | MU-2G | MU2 | Medium | Multi-Engine Turbo-Prop | 46 |
| 237 | MITSUBISHI | MU-2J | MU2 | Medium | Multi-Engine Turbo-Prop | 112 |
| 238 | MITSUBISHI | MU-2K | MU2 | Light | Multi-Engine Turbo-Prop | 75 |
| 239 | MITSUBISHI | MU-2L | MU2 | Medium | Multi-Engine Turbo-Prop | 33 |
| 240 | MITSUBISHI | MU-2M | MU2 | Medium | Multi-Engine Turbo-Prop | 26 |
| 241 | MITSUBISHI | MU-2N | MU2 | Medium | Multi-Engine Turbo-Prop | 39 |
| 242 | MITSUBISHI | MU-2P | MU2 | Medium | Multi-Engine Turbo-Prop | 40 |
| 243 | MITSUBISHI | MU-2S | MU2 | Light | Multi-Engine Turbo-Prop | 27 |
| 244 | MITSUBISHI | SOLITAIRE | MU2 | Medium | Multi-Engine Turbo-Prop | 57 |
| 1223 | NEXTANT | G90XT | BE9L | Medium | Multi-Engine Turbo-Prop | 1 |
| 659 | PILATUS | PC-12 NG | PC12 | Light | Single-Engine Turbo-Prop | 942 |
| 1294 | PILATUS | PC-12 NGX | PC12 | Light | Single-Engine Turbo-Prop | 476 |
| 1333 | PILATUS | PC-12 PRO | PC12 | Light | Single-Engine Turbo-Prop | 52 |
| 245 | PILATUS | PC-12/45 | PC12 | Light | Single-Engine Turbo-Prop | 585 |
| 1173 | PILATUS | PC-12/47 | PC12 | Light | Single-Engine Turbo-Prop | 205 |
| 1049 | PILATUS | PC-6/B2-H4 | PC6T | Light | Single-Engine Turbo-Prop | 113 |
| 1216 | PIPER | M500 | P46T | Light | Single-Engine Turbo-Prop | 147 |
| 1225 | PIPER | M600 | M600 | Light | Single-Engine Turbo-Prop | 99 |
| 1300 | PIPER | M600 SLS | M600 | Light | Single-Engine Turbo-Prop | 196 |
| 1330 | PIPER | M700 FURY | M700 | Light | Single-Engine Turbo-Prop | 94 |
| 617 | PIPER | MALIBU JETPROP | PA46 | Light | Single-Engine Turbo-Prop | 315 |
| 256 | PIPER | MERIDIAN | P46T | Light | Single-Engine Turbo-Prop | 578 |
| 1055 | SAAB | 2000 | SB20 | Medium | Commercial Turboprop Airliner | 63 |
| 1058 | SAAB | 340A | SF34 | Medium | Commercial Turboprop Airliner | 145 |
| 1120 | SAAB | 340AF | SF34 | Medium | Commercial Turboprop Airliner | 14 |
| 1056 | SAAB | 340B | SF34 | Medium | Commercial Turboprop Airliner | 209 |
| 1057 | SAAB | 340B PLUS | SF34 | Medium | Commercial Turboprop Airliner | 88 |
| 289 | SOCATA | TBM-700A | TBM7 | Light | Single-Engine Turbo-Prop | 126 |
| 290 | SOCATA | TBM-700B | TBM7 | Light | Single-Engine Turbo-Prop | 96 |
| 291 | SOCATA | TBM-700C1 | TBM7 | Light | Single-Engine Turbo-Prop | 5 |
| 280 | SOCATA | TBM-700C2 | TBM7 | Light | Single-Engine Turbo-Prop | 99 |
| 632 | SOCATA | TBM-850 | TBM8 | Light | Single-Engine Turbo-Prop | 338 |
| 1193 | SOCATA | TBM-900 | TBM9 | Light | Single-Engine Turbo-Prop | 114 |
| 1249 | SOCATA | TBM-910 | TBM9 | Light | Single-Engine Turbo-Prop | 71 |
| 1238 | SOCATA | TBM-930 | TBM9 | Light | Single-Engine Turbo-Prop | 96 |
| 1283 | SOCATA | TBM-940 | TBM9 | Light | Single-Engine Turbo-Prop | 148 |
| 1312 | SOCATA | TBM-960 | TBM9 | Light | Single-Engine Turbo-Prop | 194 |
| 247 | STARSHIP | 2000 | STAR | Heavy | Multi-Engine Turbo-Prop | 21 |
| 248 | STARSHIP | 2000A | STAR | Heavy | Multi-Engine Turbo-Prop | 32 |
| 249 | TURBO COMMANDER | 1000 | AC95 | Medium | Multi-Engine Turbo-Prop | 113 |
| 250 | TURBO COMMANDER | 690 | AC90 | Medium | Multi-Engine Turbo-Prop | 80 |
| 251 | TURBO COMMANDER | 690A | AC90 | Medium | Multi-Engine Turbo-Prop | 245 |
| 252 | TURBO COMMANDER | 690B | AC90 | Medium | Multi-Engine Turbo-Prop | 217 |
| 253 | TURBO COMMANDER | 840 | AC90 | Medium | Multi-Engine Turbo-Prop | 121 |
| 254 | TURBO COMMANDER | 900 | AC90 | Medium | Multi-Engine Turbo-Prop | 39 |
| 255 | TURBO COMMANDER | 980 | AC95 | Medium | Multi-Engine Turbo-Prop | 85 |
| 1103 | VIKING | DHC-6-400 TWIN OTTER | DHC6 | Medium | Commercial Turboprop Airliner | 154 |

---

## Jet Airliner

| AMODID | Make | Model | ICAO | Weight Class | Size Category | Fleet |
|-------:|------|-------|------|-------------|---------------|------:|
| 1126 | AIRBUS | A220-100 | BCS1 | Heavy | Commercial Jet Airliner | 106 |
| 1125 | AIRBUS | A220-300 | BCS3 | Heavy | Commercial Jet Airliner | 624 |
| 698 | AIRBUS | A300B2K-200 | A30B | Heavy | Commercial Jet Airliner | 25 |
| 699 | AIRBUS | A300B4-100 | A30B | Heavy | Commercial Jet Airliner | 36 |
| 700 | AIRBUS | A300B4-100(F) | A30B | Heavy | Commercial Jet Airliner | 8 |
| 701 | AIRBUS | A300B4-200 | A30B | Heavy | Commercial Jet Airliner | 79 |
| 702 | AIRBUS | A300B4-200(F) | A30B | Heavy | Commercial Jet Airliner | 67 |
| 703 | AIRBUS | A300B4-600 | A306 | Heavy | Commercial Jet Airliner | 30 |
| 704 | AIRBUS | A300B4-600(F) | A306 | Heavy | Commercial Jet Airliner | 8 |
| 705 | AIRBUS | A300B4-600R | A306 | Heavy | Commercial Jet Airliner | 97 |
| 706 | AIRBUS | A300B4-600R(F) | A306 | Heavy | Commercial Jet Airliner | 67 |
| 707 | AIRBUS | A300C4-200 | A30B | Heavy | Commercial Jet Airliner | 1 |
| 708 | AIRBUS | A300C4-200(F) | A30B | Heavy | Commercial Jet Airliner | 2 |
| 709 | AIRBUS | A300C4-600 | A306 | Heavy | Commercial Jet Airliner | 4 |
| 710 | AIRBUS | A300C4-600R(F) | A306 | Heavy | Commercial Jet Airliner | 2 |
| 711 | AIRBUS | A300F4-600R | A306 | Heavy | Commercial Jet Airliner | 104 |
| 712 | AIRBUS | A310-200 | A310 | Heavy | Commercial Jet Airliner | 36 |
| 713 | AIRBUS | A310-200F | A310 | Heavy | Commercial Jet Airliner | 49 |
| 714 | AIRBUS | A310-300 | A310 | Heavy | Commercial Jet Airliner | 135 |
| 715 | AIRBUS | A310-300F | A310 | Heavy | Commercial Jet Airliner | 34 |
| 716 | AIRBUS | A318 | A318 | Heavy | Commercial Jet Airliner | 60 |
| 717 | AIRBUS | A319 | A319 | Heavy | Commercial Jet Airliner | 1,430 |
| 718 | AIRBUS | A319LR | A319 | Heavy | Commercial Jet Airliner | 8 |
| 1156 | AIRBUS | A319neo | A19N | Heavy | Commercial Jet Airliner | 53 |
| 719 | AIRBUS | A320-100 | A320 | Heavy | Commercial Jet Airliner | 21 |
| 720 | AIRBUS | A320-200 | A320 | Heavy | Commercial Jet Airliner | 4,901 |
| 1316 | AIRBUS | A320-200P2F | A320 | Heavy | Commercial Jet Airliner | 7 |
| 1140 | AIRBUS | A320neo | A20N | Heavy | Commercial Jet Airliner | 4,315 |
| 721 | AIRBUS | A321-100 | A321 | Heavy | Commercial Jet Airliner | 79 |
| 722 | AIRBUS | A321-200 | A321 | Heavy | Commercial Jet Airliner | 1,680 |
| 1286 | AIRBUS | A321-200P2F | A321 | Heavy | Commercial Jet Airliner | 69 |
| 1285 | AIRBUS | A321-200PCF | A321 | Heavy | Commercial Jet Airliner | 10 |
| 1299 | AIRBUS | A321-200SDF | A321 | Heavy | Commercial Jet Airliner | 1 |
| 1215 | AIRBUS | A321LR | A321 | Heavy | Commercial Jet Airliner | 174 |
| 1288 | AIRBUS | A321XLR | A321 | Heavy | Commercial Jet Airliner | 94 |
| 1147 | AIRBUS | A321neo | A21N | Heavy | Commercial Jet Airliner | 2,772 |
| 723 | AIRBUS | A330-200 | A332 | Heavy | Commercial Jet Airliner | 616 |
| 1104 | AIRBUS | A330-200F | A330 | Heavy | Commercial Jet Airliner | 40 |
| 1242 | AIRBUS | A330-200P2F | A330 | Heavy | Commercial Jet Airliner | 23 |
| 724 | AIRBUS | A330-300 | A333 | Heavy | Commercial Jet Airliner | 756 |
| 1222 | AIRBUS | A330-300 Regional | A333 | Heavy | Commercial Jet Airliner | 20 |
| 1243 | AIRBUS | A330-300P2F | A333 | Heavy | Commercial Jet Airliner | 45 |
| 1202 | AIRBUS | A330-800neo | A338 | Heavy | Commercial Jet Airliner | 15 |
| 1203 | AIRBUS | A330-900neo | A339 | Heavy | Commercial Jet Airliner | 341 |
| 725 | AIRBUS | A340-200 | A342 | Heavy | Commercial Jet Airliner | 28 |
| 726 | AIRBUS | A340-300 | A343 | Heavy | Commercial Jet Airliner | 54 |
| 727 | AIRBUS | A340-300E | A343 | Heavy | Commercial Jet Airliner | 12 |
| 728 | AIRBUS | A340-300X | A343 | Heavy | Commercial Jet Airliner | 153 |
| 729 | AIRBUS | A340-500 | A345 | Heavy | Commercial Jet Airliner | 34 |
| 730 | AIRBUS | A340-600 | A346 | Heavy | Commercial Jet Airliner | 99 |
| 1101 | AIRBUS | A350-1000 | A35K | Heavy | Commercial Jet Airliner | 154 |
| 732 | AIRBUS | A350-900 | A359 | Heavy | Commercial Jet Airliner | 817 |
| 1227 | AIRBUS | A350-900ULR | A359 | Heavy | Commercial Jet Airliner | 8 |
| 733 | AIRBUS | A380-800 | A388 | Heavy | Commercial Jet Airliner | 262 |
| 762 | AVRO | RJ-100 | RJ1H | Heavy | Commercial Jet Airliner | 71 |
| 672 | AVRO | RJ-70 | RJ70 | Heavy | Commercial Jet Airliner | 12 |
| 763 | AVRO | RJ-85 | RJ85 | Heavy | Commercial Jet Airliner | 87 |
| 6 | BAE | 146-100 | B461 | Heavy | Commercial Jet Airliner | 32 |
| 764 | BAE | 146-100QC | B461 | Medium | Commercial Jet Airliner | 1 |
| 668 | BAE | 146-200 | B462 | Heavy | Commercial Jet Airliner | 98 |
| 765 | BAE | 146-200QC | B462 | Medium | Commercial Jet Airliner | 5 |
| 766 | BAE | 146-200QT | B462 | Medium | Commercial Jet Airliner | 13 |
| 669 | BAE | 146-300 | B463 | Heavy | Commercial Jet Airliner | 61 |
| 767 | BAE | 146-300QT | B463 | Medium | Commercial Jet Airliner | 10 |
| 782 | BOEING | 707-120 | B701 | Heavy | Commercial Jet Airliner | 22 |
| 301 | BOEING | 707-120B | B710 | Heavy | Commercial Jet Airliner | 117 |
| 784 | BOEING | 707-120B(F) | B701 | Heavy | Commercial Jet Airliner | 2 |
| 785 | BOEING | 707-220 | B702 | Heavy | Commercial Jet Airliner | 4 |
| 786 | BOEING | 707-220(F) | B702 | Heavy | Commercial Jet Airliner | 1 |
| 302 | BOEING | 707-320 | B703 | Heavy | Commercial Jet Airliner | 69 |
| 787 | BOEING | 707-320(F) | B703 | Heavy | Commercial Jet Airliner | 2 |
| 788 | BOEING | 707-320B | B703 | Heavy | Commercial Jet Airliner | 171 |
| 789 | BOEING | 707-320C | B703 | Heavy | Commercial Jet Airliner | 335 |
| 790 | BOEING | 707-420 | B704 | Heavy | Commercial Jet Airliner | 36 |
| 791 | BOEING | 717-200 | B712 | Heavy | Commercial Jet Airliner | 155 |
| 307 | BOEING | 727-100 | B721 | Heavy | Commercial Jet Airliner | 307 |
| 810 | BOEING | 727-100C | B721 | Heavy | Commercial Jet Airliner | 106 |
| 811 | BOEING | 727-100C(TAY) | B721 | Heavy | Commercial Jet Airliner | 51 |
| 799 | BOEING | 727-100F | B722 | Heavy | Commercial Jet Airliner | 104 |
| 308 | BOEING | 727-200 | B722 | Heavy | Commercial Jet Airliner | 248 |
| 801 | BOEING | 727-200 ADVANCED | B722 | Heavy | Commercial Jet Airliner | 632 |
| 800 | BOEING | 727-200(F) | B722 | Heavy | Commercial Jet Airliner | 64 |
| 803 | BOEING | 727-200A RE | B722 | Heavy | Commercial Jet Airliner | 16 |
| 804 | BOEING | 727-200A(COMBI) | B722 | Heavy | Commercial Jet Airliner | 1 |
| 805 | BOEING | 727-200A(F) | B722 | Heavy | Commercial Jet Airliner | 267 |
| 806 | BOEING | 727-200A(F)RE | B722 | Heavy | Commercial Jet Airliner | 1 |
| 802 | BOEING | 727-200A(RE) | B722 | Heavy | Commercial Jet Airliner | 6 |
| 807 | BOEING | 727-200A-F RE | B722 | Heavy | Commercial Jet Airliner | 6 |
| 809 | BOEING | 727-200F ADVANCED | B722 | Heavy | Commercial Jet Airliner | 4 |
| 808 | BOEING | 727-200F(RE) | B722 | Heavy | Commercial Jet Airliner | 11 |
| 1254 | BOEING | 737 MAX 10 | B3XM | Heavy | Commercial Jet Airliner | 474 |
| 1206 | BOEING | 737 MAX 200 | B38M | Heavy | Commercial Jet Airliner | 331 |
| 1158 | BOEING | 737 MAX 7 | B37M | Heavy | Commercial Jet Airliner | 64 |
| 1151 | BOEING | 737 MAX 8 | B38M | Heavy | Commercial Jet Airliner | 2,919 |
| 1159 | BOEING | 737 MAX 9 | B39M | Heavy | Commercial Jet Airliner | 384 |
| 310 | BOEING | 737-100 | B731 | Heavy | Commercial Jet Airliner | 30 |
| 311 | BOEING | 737-200 | B732 | Heavy | Commercial Jet Airliner | 224 |
| 814 | BOEING | 737-200 ADVANCED | B732 | Heavy | Commercial Jet Airliner | 761 |
| 816 | BOEING | 737-200C | B732 | Heavy | Commercial Jet Airliner | 25 |
| 817 | BOEING | 737-200C ADVANCED | B732 | Heavy | Commercial Jet Airliner | 76 |
| 813 | BOEING | 737-200F | B732 | Heavy | Commercial Jet Airliner | 2 |
| 815 | BOEING | 737-200F ADVANCED | B732 | Heavy | Commercial Jet Airliner | 20 |
| 312 | BOEING | 737-300 | B733 | Heavy | Commercial Jet Airliner | 940 |
| 1122 | BOEING | 737-300BDSF | B733 | Heavy | Commercial Jet Airliner | 13 |
| 818 | BOEING | 737-300F | B733 | Heavy | Commercial Jet Airliner | 94 |
| 1176 | BOEING | 737-300PTF | B733 | Heavy | Commercial Jet Airliner | 2 |
| 819 | BOEING | 737-300QC | B733 | Heavy | Commercial Jet Airliner | 35 |
| 1192 | BOEING | 737-300SF | B733 | Heavy | Commercial Jet Airliner | 29 |
| 313 | BOEING | 737-400 | B734 | Heavy | Commercial Jet Airliner | 293 |
| 1106 | BOEING | 737-400 COMBI | B734 | Heavy | Commercial Jet Airliner | 7 |
| 1121 | BOEING | 737-400BDSF | B734 | Heavy | Commercial Jet Airliner | 5 |
| 1177 | BOEING | 737-400F | B734 | Heavy | Commercial Jet Airliner | 30 |
| 1100 | BOEING | 737-400SF | B734 | Heavy | Commercial Jet Airliner | 152 |
| 314 | BOEING | 737-500 | B735 | Heavy | Commercial Jet Airliner | 389 |
| 820 | BOEING | 737-600 | B736 | Heavy | Commercial Jet Airliner | 69 |
| 316 | BOEING | 737-700 | B737 | Heavy | Commercial Jet Airliner | 1,109 |
| 1232 | BOEING | 737-700BDSF | B37M | Heavy | Commercial Jet Airliner | 7 |
| 821 | BOEING | 737-700C | B737 | Heavy | Commercial Jet Airliner | 13 |
| 822 | BOEING | 737-700ER | B737 | Heavy | Commercial Jet Airliner | 2 |
| 1245 | BOEING | 737-700FC | B37M | Heavy | Commercial Jet Airliner | 2 |
| 823 | BOEING | 737-800 | B738 | Heavy | Commercial Jet Airliner | 4,911 |
| 1234 | BOEING | 737-800BCF | B38M | Heavy | Commercial Jet Airliner | 172 |
| 1292 | BOEING | 737-800BDSF | B38M | Heavy | Commercial Jet Airliner | 14 |
| 1240 | BOEING | 737-800SF | B38M | Heavy | Commercial Jet Airliner | 82 |
| 824 | BOEING | 737-900 | B739 | Heavy | Commercial Jet Airliner | 52 |
| 825 | BOEING | 737-900ER | B739 | Heavy | Commercial Jet Airliner | 537 |
| 826 | BOEING | 747-100 | B741 | Heavy | Commercial Jet Airliner | 117 |
| 828 | BOEING | 747-100 COMBI | B741 | Heavy | Commercial Jet Airliner | 5 |
| 829 | BOEING | 747-100B | B741 | Heavy | Commercial Jet Airliner | 12 |
| 830 | BOEING | 747-100BSR SUD | B741 | Heavy | Commercial Jet Airliner | 2 |
| 827 | BOEING | 747-100F | B741 | Heavy | Commercial Jet Airliner | 46 |
| 831 | BOEING | 747-200B | B742 | Heavy | Commercial Jet Airliner | 182 |
| 832 | BOEING | 747-200BSF | B742 | Heavy | Commercial Jet Airliner | 79 |
| 834 | BOEING | 747-200BSUD | B742 | Heavy | Commercial Jet Airliner | 3 |
| 836 | BOEING | 747-200BSUD F | B742 | Heavy | Commercial Jet Airliner | 2 |
| 837 | BOEING | 747-200C | B742 | Heavy | Commercial Jet Airliner | 13 |
| 838 | BOEING | 747-200F | B742 | Heavy | Commercial Jet Airliner | 73 |
| 833 | BOEING | 747-200M | B742 | Heavy | Commercial Jet Airliner | 28 |
| 835 | BOEING | 747-200MSUD | B742 | Heavy | Commercial Jet Airliner | 7 |
| 321 | BOEING | 747-300 | B743 | Heavy | Commercial Jet Airliner | 60 |
| 839 | BOEING | 747-300F | B743 | Heavy | Commercial Jet Airliner | 7 |
| 840 | BOEING | 747-300M | B743 | Heavy | Commercial Jet Airliner | 14 |
| 322 | BOEING | 747-400 | B744 | Heavy | Commercial Jet Airliner | 376 |
| 846 | BOEING | 747-400BCF | B744 | Heavy | Commercial Jet Airliner | 64 |
| 1169 | BOEING | 747-400BDSF | B744 | Heavy | Commercial Jet Airliner | 11 |
| 842 | BOEING | 747-400D | B744 | Heavy | Commercial Jet Airliner | 19 |
| 843 | BOEING | 747-400ER | B744 | Heavy | Commercial Jet Airliner | 9 |
| 844 | BOEING | 747-400ERF | B744 | Heavy | Commercial Jet Airliner | 40 |
| 845 | BOEING | 747-400F | B744 | Heavy | Commercial Jet Airliner | 126 |
| 841 | BOEING | 747-400M | B744 | Heavy | Commercial Jet Airliner | 46 |
| 847 | BOEING | 747-8F | B748 | Heavy | Commercial Jet Airliner | 122 |
| 1099 | BOEING | 747-8I | B748 | Heavy | Commercial Jet Airliner | 43 |
| 324 | BOEING | 747SP | B74S | Heavy | Commercial Jet Airliner | 45 |
| 1130 | BOEING | 747SRSF | B74S | Heavy | Commercial Jet Airliner | 1 |
| 326 | BOEING | 757-200 | B752 | Heavy | Commercial Jet Airliner | 606 |
| 848 | BOEING | 757-200M | B752 | Heavy | Commercial Jet Airliner | 3 |
| 850 | BOEING | 757-200PCF | B752 | Heavy | Commercial Jet Airliner | 185 |
| 851 | BOEING | 757-200PF | B752 | Heavy | Commercial Jet Airliner | 80 |
| 1168 | BOEING | 757-200SF | B752 | Heavy | Commercial Jet Airliner | 121 |
| 852 | BOEING | 757-300 | B753 | Heavy | Commercial Jet Airliner | 55 |
| 328 | BOEING | 767-200 | B762 | Heavy | Commercial Jet Airliner | 59 |
| 854 | BOEING | 767-200ER | B762 | Heavy | Commercial Jet Airliner | 134 |
| 855 | BOEING | 767-200ER(F) | B762 | Heavy | Commercial Jet Airliner | 11 |
| 853 | BOEING | 767-200SF | B762 | Heavy | Commercial Jet Airliner | 35 |
| 329 | BOEING | 767-300 | B763 | Heavy | Commercial Jet Airliner | 101 |
| 1112 | BOEING | 767-300BCF | B763 | Heavy | Commercial Jet Airliner | 243 |
| 856 | BOEING | 767-300ER | B763 | Heavy | Commercial Jet Airliner | 344 |
| 858 | BOEING | 767-300F | B763 | Heavy | Commercial Jet Airliner | 284 |
| 859 | BOEING | 767-400ER | B764 | Heavy | Commercial Jet Airliner | 38 |
| 860 | BOEING | 777-200 | B772 | Heavy | Commercial Jet Airliner | 80 |
| 332 | BOEING | 777-200ER | B772 | Heavy | Commercial Jet Airliner | 429 |
| 861 | BOEING | 777-200LR | B77L | Heavy | Commercial Jet Airliner | 61 |
| 780 | BOEING | 777-200LRF | B772 | Heavy | Commercial Jet Airliner | 325 |
| 862 | BOEING | 777-300 | B773 | Heavy | Commercial Jet Airliner | 60 |
| 863 | BOEING | 777-300ER | B77W | Heavy | Commercial Jet Airliner | 837 |
| 1293 | BOEING | 777-300ERSF | B77W | Heavy | Commercial Jet Airliner | 11 |
| 1187 | BOEING | 777-8X | B778 | Heavy | Commercial Jet Airliner | 53 |
| 1185 | BOEING | 777-9X | B779 | Heavy | Commercial Jet Airliner | 266 |
| 1178 | BOEING | 787-10 | B78X | Heavy | Commercial Jet Airliner | 278 |
| 864 | BOEING | 787-8 | B788 | Heavy | Commercial Jet Airliner | 522 |
| 865 | BOEING | 787-9 | B789 | Heavy | Commercial Jet Airliner | 920 |
| 868 | BOMBARDIER | CRJ100 | CRJ1 | Medium | Commercial Jet Airliner | 192 |
| 1198 | BOMBARDIER | CRJ100(PF) | CRJ1 | Medium | Commercial Jet Airliner | 2 |
| 1111 | BOMBARDIER | CRJ1000 | CRJX | Medium | Commercial Jet Airliner | 64 |
| 869 | BOMBARDIER | CRJ200 | CRJ2 | Medium | Commercial Jet Airliner | 720 |
| 1109 | BOMBARDIER | CRJ200(PF) | CRJ2 | Medium | Commercial Jet Airliner | 11 |
| 1212 | BOMBARDIER | CRJ200SF | CRJ2 | Medium | Commercial Jet Airliner | 27 |
| 870 | BOMBARDIER | CRJ440 | CRJ2 | Medium | Commercial Jet Airliner | 67 |
| 1289 | BOMBARDIER | CRJ550 | CRJ7 | Medium | Commercial Jet Airliner | 62 |
| 871 | BOMBARDIER | CRJ700 | CRJ7 | Medium | Commercial Jet Airliner | 269 |
| 872 | BOMBARDIER | CRJ900 | CRJ9 | Medium | Commercial Jet Airliner | 499 |
| 1116 | COMAC | ARJ21-700 | AJ27 | Medium | Commercial Jet Airliner | 571 |
| 1128 | COMAC | C919 | C919 | Heavy | Commercial Jet Airliner | 570 |
| 914 | DORNIER | 328JET | J328 | Medium | Commercial Jet Airliner | 102 |
| 1179 | EMBRAER | E190-E2 | E290 | Medium | Commercial Jet Airliner | 101 |
| 1180 | EMBRAER | E195-E2 | E295 | Medium | Commercial Jet Airliner | 220 |
| 919 | EMBRAER | ERJ 170-100 | E170 | Medium | Commercial Jet Airliner | 200 |
| 920 | EMBRAER | ERJ 170-200 | E75L | Medium | Commercial Jet Airliner | 925 |
| 921 | EMBRAER | ERJ 190-100 | E190 | Medium | Commercial Jet Airliner | 568 |
| 922 | EMBRAER | ERJ 190-200 | E195 | Medium | Commercial Jet Airliner | 173 |
| 915 | EMBRAER | ERJ-135 | E135 | Medium | Commercial Jet Airliner | 117 |
| 916 | EMBRAER | ERJ-140 | E135 | Medium | Commercial Jet Airliner | 74 |
| 917 | EMBRAER | ERJ-145 | E145 | Medium | Commercial Jet Airliner | 623 |
| 918 | EMBRAER | ERJ-145XR | E45X | Medium | Commercial Jet Airliner | 104 |
| 16 | FOKKER | 100 | F100 | Heavy | Commercial Jet Airliner | 279 |
| 689 | FOKKER | 70 | F70 | Medium | Commercial Jet Airliner | 48 |
| 1131 | IRKUT | MC-21-300 | MC23 | Heavy | Commercial Jet Airliner | 171 |
| 994 | MCDONNELL DOUGLAS | DC-10-10 (F) | DC10 | Heavy | Commercial Jet Airliner | 63 |
| 995 | MCDONNELL DOUGLAS | DC-10-10CF | DC10 | Heavy | Commercial Jet Airliner | 9 |
| 996 | MCDONNELL DOUGLAS | DC-10-30 | DC10 | Heavy | Commercial Jet Airliner | 117 |
| 997 | MCDONNELL DOUGLAS | DC-10-30(F) | DC10 | Heavy | Commercial Jet Airliner | 37 |
| 998 | MCDONNELL DOUGLAS | DC-10-30CF | DC10 | Heavy | Commercial Jet Airliner | 24 |
| 999 | MCDONNELL DOUGLAS | DC-10-30ER | DC10 | Heavy | Commercial Jet Airliner | 11 |
| 1000 | MCDONNELL DOUGLAS | DC-10-30F | DC10 | Heavy | Commercial Jet Airliner | 10 |
| 1001 | MCDONNELL DOUGLAS | DC-10-40(F) | DC10 | Heavy | Commercial Jet Airliner | 7 |
| 1002 | MCDONNELL DOUGLAS | DC-8-62(F) | DC86 | Heavy | Commercial Jet Airliner | 25 |
| 1003 | MCDONNELL DOUGLAS | DC-8-62AF | DC86 | Heavy | Commercial Jet Airliner | 5 |
| 1004 | MCDONNELL DOUGLAS | DC-8-62CF | DC86 | Heavy | Commercial Jet Airliner | 8 |
| 1171 | MCDONNELL DOUGLAS | DC-8-62H | DC86 | Heavy | Commercial Jet Airliner | 2 |
| 1005 | MCDONNELL DOUGLAS | DC-8-63(F) | DC86 | Heavy | Commercial Jet Airliner | 18 |
| 1006 | MCDONNELL DOUGLAS | DC-8-63CF | DC86 | Heavy | Commercial Jet Airliner | 14 |
| 1007 | MCDONNELL DOUGLAS | DC-8-63PF | DC86 | Heavy | Commercial Jet Airliner | 2 |
| 1008 | MCDONNELL DOUGLAS | DC-8-71(F) | DC87 | Heavy | Commercial Jet Airliner | 53 |
| 1172 | MCDONNELL DOUGLAS | DC-8-72 | DC87 | Heavy | Commercial Jet Airliner | 3 |
| 1009 | MCDONNELL DOUGLAS | DC-8-72CF | DC87 | Heavy | Commercial Jet Airliner | 3 |
| 1010 | MCDONNELL DOUGLAS | DC-8-73(F) | DC87 | Heavy | Commercial Jet Airliner | 9 |
| 1011 | MCDONNELL DOUGLAS | DC-8-73AF | DC87 | Heavy | Commercial Jet Airliner | 7 |
| 1012 | MCDONNELL DOUGLAS | DC-8-73CF | DC87 | Heavy | Commercial Jet Airliner | 33 |
| 1013 | MCDONNELL DOUGLAS | DC-8F-54 | DC85 | Heavy | Commercial Jet Airliner | 51 |
| 1014 | MCDONNELL DOUGLAS | DC-9-10 | DC91 | Heavy | Commercial Jet Airliner | 101 |
| 1015 | MCDONNELL DOUGLAS | DC-9-15RC | DC91 | Heavy | Commercial Jet Airliner | 21 |
| 1016 | MCDONNELL DOUGLAS | DC-9-20 | DC92 | Heavy | Commercial Jet Airliner | 9 |
| 1017 | MCDONNELL DOUGLAS | DC-9-30 | DC93 | Heavy | Commercial Jet Airliner | 547 |
| 1019 | MCDONNELL DOUGLAS | DC-9-30AF | DC93 | Heavy | Commercial Jet Airliner | 6 |
| 1018 | MCDONNELL DOUGLAS | DC-9-30CF | DC93 | Heavy | Commercial Jet Airliner | 15 |
| 1020 | MCDONNELL DOUGLAS | DC-9-30RC | DC93 | Heavy | Commercial Jet Airliner | 14 |
| 1021 | MCDONNELL DOUGLAS | DC-9-40 | DC94 | Heavy | Commercial Jet Airliner | 71 |
| 1022 | MCDONNELL DOUGLAS | DC-9-50 | DC95 | Heavy | Commercial Jet Airliner | 96 |
| 616 | MCDONNELL DOUGLAS | MD-11 | MD11 | Heavy | Commercial Jet Airliner | 21 |
| 1028 | MCDONNELL DOUGLAS | MD-11BCF | MD11 | Heavy | Commercial Jet Airliner | 124 |
| 1029 | MCDONNELL DOUGLAS | MD-11F | MD11 | Heavy | Commercial Jet Airliner | 55 |
| 1023 | MCDONNELL DOUGLAS | MD-81 | MD81 | Heavy | Commercial Jet Airliner | 73 |
| 1024 | MCDONNELL DOUGLAS | MD-82 | MD82 | Heavy | Commercial Jet Airliner | 575 |
| 1175 | MCDONNELL DOUGLAS | MD-82SF | MD82 | Heavy | Commercial Jet Airliner | 7 |
| 1025 | MCDONNELL DOUGLAS | MD-83 | MD83 | Heavy | Commercial Jet Airliner | 289 |
| 1201 | MCDONNELL DOUGLAS | MD-83SF | MD83 | Heavy | Commercial Jet Airliner | 16 |
| 1026 | MCDONNELL DOUGLAS | MD-87 | MD87 | Heavy | Commercial Jet Airliner | 76 |
| 1027 | MCDONNELL DOUGLAS | MD-88 | MD88 | Heavy | Commercial Jet Airliner | 158 |
| 1030 | MCDONNELL DOUGLAS | MD-90-30 | MD90 | Heavy | Commercial Jet Airliner | 117 |
| 1113 | MITSUBISHI | SPACEJET M90 | MRJ9 | Medium | Commercial Jet Airliner | 167 |
| 1123 | SUKHOI | SUPERJET 100 | SU95 | Heavy | Commercial Jet Airliner | 299 |
| 1182 | SUKHOI | SUPERJET 100LR | SU95 | Heavy | Commercial Jet Airliner | 66 |

---

## Turbine

| AMODID | Make | Model | ICAO | Weight Class | Size Category | Fleet |
|-------:|------|-------|------|-------------|---------------|------:|
| 365 | AGUSTA/WESTLAND | A109A | A109 | Light | Twin-Engine Helicopter | 105 |
| 611 | AGUSTA/WESTLAND | A109A MK II | A109 | Light | Twin-Engine Helicopter | 126 |
| 366 | AGUSTA/WESTLAND | A109C | A109 | Light | Twin-Engine Helicopter | 71 |
| 367 | AGUSTA/WESTLAND | A109K2 | A109 | Light | Twin-Engine Helicopter | 38 |
| 604 | AGUSTA/WESTLAND | A109S GRAND | A109 | Medium | Twin-Engine Helicopter | 181 |
| 369 | AGUSTA/WESTLAND | A119 KOALA | A119 | Light | Single-Engine Helicopter | 98 |
| 647 | AGUSTA/WESTLAND | A119KE | A119 | Light | Single-Engine Helicopter | 109 |
| 1145 | AIRBUS | AS-332C1E SUPER PUMA | AS32 | Heavy | Twin-Engine Helicopter | 5 |
| 1230 | AIRBUS | AS-332L1E SUPER PUMA | AS32 | Heavy | Twin-Engine Helicopter | 5 |
| 570 | AIRBUS | AS-350B-2 ECUREUIL | AS50 | Light | Single-Engine Helicopter | 1,379 |
| 637 | AIRBUS | AS-355NP ECUREUIL II | AS55 | Light | Twin-Engine Helicopter | 65 |
| 576 | AIRBUS | AS-365N-3 DAUPHIN 2 | AS65 | Medium | Twin-Engine Helicopter | 230 |
| 1143 | AIRBUS | EC-135P2+ | EC35 | Medium | Twin-Engine Helicopter | 402 |
| 1142 | AIRBUS | EC-135T2+ | EC35 | Medium | Twin-Engine Helicopter | 226 |
| 594 | AIRBUS | EC-145 | EC45 | Medium | Twin-Engine Helicopter | 890 |
| 459 | AIRBUS | H120 | EC20 | Light | Single-Engine Helicopter | 699 |
| 1146 | AIRBUS | H125 | AS50 | Light | Single-Engine Helicopter | 1,472 |
| 1160 | AIRBUS | H130 | EC30 | Light | Single-Engine Helicopter | 442 |
| 1208 | AIRBUS | H135 | EC35 | Medium | Twin-Engine Helicopter | 315 |
| 1141 | AIRBUS | H145 | EC45 | Medium | Twin-Engine Helicopter | 611 |
| 612 | AIRBUS | H155 | EC55 | Medium | Twin-Engine Helicopter | 156 |
| 1226 | AIRBUS | H160 | H160 | Heavy | Twin-Engine Helicopter | 41 |
| 684 | AIRBUS | H175 | EC75 | Heavy | Twin-Engine Helicopter | 54 |
| 605 | AIRBUS | H225 | EC25 | Heavy | Twin-Engine Helicopter | 190 |
| 400 | BELL | 204B | UH1 | Medium | Single-Engine Helicopter | 54 |
| 413 | BELL | 205A-1 | UH1 | Medium | Single-Engine Helicopter | 199 |
| 418 | BELL | 206A JETRANGER | B06 | Light | Single-Engine Helicopter | 157 |
| 422 | BELL | 206B JETRANGER II | B06 | Light | Single-Engine Helicopter | 1,737 |
| 423 | BELL | 206B-3 JETRANGER III | B06 | Light | Single-Engine Helicopter | 2,533 |
| 425 | BELL | 206L LONGRANGER | B06 | Light | Single-Engine Helicopter | 170 |
| 426 | BELL | 206L-1 LONGRANGER II | B06 | Light | Single-Engine Helicopter | 632 |
| 427 | BELL | 206L-3 LONGRANGER | B06 | Light | Single-Engine Helicopter | 610 |
| 428 | BELL | 206L-4 LONGRANGER IV | B06 | Light | Single-Engine Helicopter | 487 |
| 446 | BELL | 206LT TWINRANGER | B06T | Light | Twin-Engine Helicopter | 7 |
| 603 | BELL | 210 | UH1 | Medium | Single-Engine Helicopter | 4 |
| 431 | BELL | 212 | B212 | Medium | Twin-Engine Helicopter | 662 |
| 435 | BELL | 214B BIGLIFTER | B214 | Medium | Single-Engine Helicopter | 63 |
| 436 | BELL | 214ST | BSTP | Heavy | Twin-Engine Helicopter | 55 |
| 437 | BELL | 222A | B222 | Medium | Twin-Engine Helicopter | 80 |
| 438 | BELL | 222B | B222 | Medium | Twin-Engine Helicopter | 26 |
| 440 | BELL | 222SP | B222 | Medium | Twin-Engine Helicopter | 10 |
| 439 | BELL | 222UT | B222 | Medium | Twin-Engine Helicopter | 72 |
| 441 | BELL | 230 | B230 | Medium | Twin-Engine Helicopter | 38 |
| 444 | BELL | 407 | B407 | Light | Single-Engine Helicopter | 1,161 |
| 1137 | BELL | 407GX | B407 | Light | Single-Engine Helicopter | 267 |
| 1219 | BELL | 407GXP | B407 | Light | Single-Engine Helicopter | 189 |
| 1273 | BELL | 407GXi | B407 | Light | Single-Engine Helicopter | 371 |
| 432 | BELL | 412 | B412 | Medium | Twin-Engine Helicopter | 149 |
| 583 | BELL | 412EP | B412 | Medium | Twin-Engine Helicopter | 610 |
| 1189 | BELL | 412EPI | B412 | Medium | Twin-Engine Helicopter | 53 |
| 1311 | BELL | 412EPX | B412 | Medium | Twin-Engine Helicopter | 44 |
| 582 | BELL | 412HP | B412 | Medium | Twin-Engine Helicopter | 71 |
| 581 | BELL | 412SP | B412 | Medium | Twin-Engine Helicopter | 41 |
| 445 | BELL | 427 | B427 | Medium | Twin-Engine Helicopter | 87 |
| 646 | BELL | 429 GLOBALRANGER | B429 | Medium | Twin-Engine Helicopter | 551 |
| 442 | BELL | 430 | B430 | Medium | Twin-Engine Helicopter | 129 |
| 1196 | BELL | 505 JET RANGER X | B505 | Light | Single-Engine Helicopter | 648 |
| 1195 | BELL | 525 RELENTLESS | B525 | Heavy | Twin-Engine Helicopter | 9 |
| 420 | BELL/AGUSTA | AB-206A JETRANGER | B06 | Light | Single-Engine Helicopter | 53 |
| 421 | BELL/AGUSTA | AB-206B JETRANGER II | B06 | Light | Single-Engine Helicopter | 147 |
| 613 | BELL/AGUSTA | AB-206B-3 JETRANGER | B06 | Light | Single-Engine Helicopter | 108 |
| 430 | BELL/AGUSTA | AB-412 | B412 | Medium | Twin-Engine Helicopter | 35 |
| 580 | BELL/AGUSTA | AB-412EP | B412 | Medium | Twin-Engine Helicopter | 18 |
| 614 | BELL/AGUSTA | AB-412HP | B412 | Medium | Twin-Engine Helicopter | 6 |
| 615 | BELL/AGUSTA | AB-412SP | B412 | Medium | Twin-Engine Helicopter | 22 |
| 469 | ENSTROM | 480 | EN48 | Light | Single-Engine Helicopter | 38 |
| 590 | ENSTROM | 480B | EN48 | Light | Single-Engine Helicopter | 219 |
| 350 | EUROCOPTER | AS-332L SUPER PUMA | AS32 | Heavy | Twin-Engine Helicopter | 77 |
| 567 | EUROCOPTER | AS-332L1 SUPER PUMA | AS32 | Heavy | Twin-Engine Helicopter | 78 |
| 568 | EUROCOPTER | AS-332L2 SUPER PUMA | AS32 | Heavy | Twin-Engine Helicopter | 53 |
| 355 | EUROCOPTER | AS-350B ECUREUIL | AS50 | Light | Single-Engine Helicopter | 447 |
| 569 | EUROCOPTER | AS-350B-1 ECUREUIL | AS50 | Light | Single-Engine Helicopter | 63 |
| 571 | EUROCOPTER | AS-350B-3 ECUREUIL | AS50 | Light | Single-Engine Helicopter | 1,130 |
| 618 | EUROCOPTER | AS-350BA ECUREUIL | AS50 | Light | Single-Engine Helicopter | 594 |
| 357 | EUROCOPTER | AS-350D ASTAR | AS50 | Light | Single-Engine Helicopter | 128 |
| 619 | EUROCOPTER | AS-355E ECUREUIL II | AS55 | Light | Twin-Engine Helicopter | 2 |
| 358 | EUROCOPTER | AS-355F ECUREUIL II | AS55 | Light | Twin-Engine Helicopter | 157 |
| 620 | EUROCOPTER | AS-355F-1 ECUREUIL | AS55 | Light | Twin-Engine Helicopter | 89 |
| 621 | EUROCOPTER | AS-355F-2 ECUREUIL | AS55 | Light | Twin-Engine Helicopter | 181 |
| 360 | EUROCOPTER | AS-355N ECUREUIL II | AS55 | Light | Twin-Engine Helicopter | 176 |
| 362 | EUROCOPTER | AS-365C DAUPHIN 2 | A65C | Medium | Twin-Engine Helicopter | 73 |
| 363 | EUROCOPTER | AS-365N DAUPHIN 2 | AS65 | Medium | Twin-Engine Helicopter | 132 |
| 573 | EUROCOPTER | AS-365N-1 DAUPHIN 2 | AS65 | Medium | Twin-Engine Helicopter | 45 |
| 575 | EUROCOPTER | AS-365N-2 DAUPHIN 2 | AS65 | Medium | Twin-Engine Helicopter | 136 |
| 591 | EUROCOPTER | BK-117A-1 | EC45 | Medium | Twin-Engine Helicopter | 70 |
| 507 | EUROCOPTER | BK-117B-1 | EC45 | Medium | Twin-Engine Helicopter | 68 |
| 608 | EUROCOPTER | BK-117B-2 | EC45 | Medium | Twin-Engine Helicopter | 80 |
| 508 | EUROCOPTER | BK-117C-1 | EC45 | Medium | Twin-Engine Helicopter | 57 |
| 572 | EUROCOPTER | EC-130B-4 ECUREUIL | EC30 | Light | Single-Engine Helicopter | 449 |
| 586 | EUROCOPTER | EC-135P1 | EC35 | Medium | Twin-Engine Helicopter | 43 |
| 587 | EUROCOPTER | EC-135P2 | EC35 | Medium | Twin-Engine Helicopter | 151 |
| 588 | EUROCOPTER | EC-135T1 | EC35 | Medium | Twin-Engine Helicopter | 99 |
| 589 | EUROCOPTER | EC-135T2 | EC35 | Medium | Twin-Engine Helicopter | 149 |
| 577 | EUROCOPTER | EC-155B | EC55 | Medium | Twin-Engine Helicopter | 32 |
| 340 | EUROCOPTER | SA-315B LAMA | LAMA | Light | Single-Engine Helicopter | 327 |
| 337 | EUROCOPTER | SA-316B ALOUETTE III | ALO3 | Light | Single-Engine Helicopter | 329 |
| 336 | EUROCOPTER | SA-318C ALOUETTE II | ALO2 | Light | Single-Engine Helicopter | 177 |
| 339 | EUROCOPTER | SA-319B ALOUETTE III | ALO3 | Light | Single-Engine Helicopter | 77 |
| 593 | EUROCOPTER/KAWASAKI | BK-117A-1 | EC45 | Medium | Twin-Engine Helicopter | 9 |
| 592 | EUROCOPTER/KAWASAKI | BK-117B | EC45 | Medium | Twin-Engine Helicopter | 97 |
| 648 | EUROCOPTER/KAWASAKI | BK-117C-1 | EC45 | Medium | Twin-Engine Helicopter | 12 |
| 368 | LEONARDO | A109E POWER | A109 | Medium | Twin-Engine Helicopter | 460 |
| 1134 | LEONARDO | A109SP GRANDNEW | A109 | Medium | Twin-Engine Helicopter | 262 |
| 1321 | LEONARDO | AW09 |  | Light | Twin-Engine Helicopter | 5 |
| 1236 | LEONARDO | AW109 TREKKER | A109 | Medium | Twin-Engine Helicopter | 51 |
| 1204 | LEONARDO | AW119Kx | A119 | Light | Single-Engine Helicopter | 284 |
| 408 | LEONARDO | AW139 | A139 | Heavy | Twin-Engine Helicopter | 1,326 |
| 1139 | LEONARDO | AW169 | A169 | Medium | Twin-Engine Helicopter | 177 |
| 1155 | LEONARDO | AW189 | A189 | Heavy | Twin-Engine Helicopter | 145 |
| 1257 | LEONARDO | AW189K | A189 | Heavy | Twin-Engine Helicopter | 2 |
| 490 | MD | MD 500E | H500 | Light | Single-Engine Helicopter | 429 |
| 492 | MD | MD 520N | MD52 | Light | Single-Engine Helicopter | 112 |
| 491 | MD | MD 530F | H500 | Light | Single-Engine Helicopter | 289 |
| 494 | MD | MD 600N | MD60 | Light | Single-Engine Helicopter | 83 |
| 496 | MD | MD EXPLORER | XPLR | Medium | Twin-Engine Helicopter | 137 |
| 650 | ROBINSON | R66 | R66 | Light | Single-Engine Helicopter | 1,505 |
| 495 | SCHWEIZER | 330 | S330 | Light | Single-Engine Helicopter | 20 |
| 407 | SCHWEIZER | S-333 | S330 | Light | Single-Engine Helicopter | 58 |
| 533 | SIKORSKY | S-76A | S76 | Medium | Twin-Engine Helicopter | 205 |
| 536 | SIKORSKY | S-76A+ | S76 | Medium | Twin-Engine Helicopter | 45 |
| 598 | SIKORSKY | S-76A++ | S76 | Medium | Twin-Engine Helicopter | 43 |
| 534 | SIKORSKY | S-76B | S76 | Medium | Twin-Engine Helicopter | 92 |
| 535 | SIKORSKY | S-76C | S76 | Medium | Twin-Engine Helicopter | 32 |
| 537 | SIKORSKY | S-76C+ | S76 | Medium | Twin-Engine Helicopter | 153 |
| 599 | SIKORSKY | S-76C++ | S76 | Medium | Twin-Engine Helicopter | 219 |
| 610 | SIKORSKY | S-76D | S76 | Medium | Twin-Engine Helicopter | 88 |
| 538 | SIKORSKY | S-92A | S92 | Heavy | Twin-Engine Helicopter | 340 |

---

## Piston

| AMODID | Make | Model | ICAO | Weight Class | Size Category | Fleet |
|-------:|------|-------|------|-------------|---------------|------:|
| 172 | BARON | 58 | BE58 | Light | Multi-Engine Piston | 2,124 |
| 173 | BARON | 58P | B58T | Light | Multi-Engine Piston | 494 |
| 174 | BARON | 58TC | B58T | Light | Multi-Engine Piston | 151 |
| 622 | BARON | G58 | BE58 | Light | Multi-Engine Piston | 421 |
| 1267 | CESSNA | 414 | C414 | Light | Multi-Engine Piston | 330 |
| 1268 | CESSNA | 414A | C414 | Light | Multi-Engine Piston | 445 |
| 175 | CESSNA | 421 | C421 | Light | Multi-Engine Piston | 200 |
| 176 | CESSNA | 421A | C421 | Light | Multi-Engine Piston | 157 |
| 177 | CESSNA | 421B | C421 | Light | Multi-Engine Piston | 699 |
| 267 | CESSNA | 421C | C421 | Light | Multi-Engine Piston | 863 |
| 1241 | DIAMOND AIRCRAFT | DA62 | DA62 | Light | Multi-Engine Piston | 477 |
| 465 | ENSTROM | 280 SHARK | EN28 | Light | Single-Engine Helicopter | 16 |
| 466 | ENSTROM | 280C SHARK | EN28 | Light | Single-Engine Helicopter | 201 |
| 467 | ENSTROM | 280F SHARK | EN28 | Light | Single-Engine Helicopter | 19 |
| 468 | ENSTROM | 280FX SHARK | EN28 | Light | Single-Engine Helicopter | 171 |
| 460 | ENSTROM | F-28 | EN28 | Light | Single-Engine Helicopter | 10 |
| 461 | ENSTROM | F-28A | EN28 | Light | Single-Engine Helicopter | 290 |
| 462 | ENSTROM | F-28C | EN28 | Light | Single-Engine Helicopter | 130 |
| 463 | ENSTROM | F-28C-2 | EN28 | Light | Single-Engine Helicopter | 48 |
| 464 | ENSTROM | F28F FALCON | EN28 | Light | Single-Engine Helicopter | 128 |
| 1252 | ENSTROM | TH-180 | EN18 | Light | Single-Engine Helicopter | 3 |
| 1224 | PIPER | M350 | PA46 | Light | Single-Engine Piston | 221 |
| 678 | PIPER | MALIBU | PA46 | Light | Single-Engine Piston | 357 |
| 667 | PIPER | MATRIX | PA46 | Light | Single-Engine Piston | 214 |
| 676 | PIPER | MIRAGE | PA46 | Light | Single-Engine Piston | 581 |
| 511 | ROBINSON | R22 | R22 | Light | Single-Engine Helicopter | 192 |
| 512 | ROBINSON | R22 ALPHA | R22 | Light | Single-Engine Helicopter | 146 |
| 513 | ROBINSON | R22 BETA | R22 | Light | Single-Engine Helicopter | 1,889 |
| 601 | ROBINSON | R22 BETA II | R22 | Light | Single-Engine Helicopter | 2,278 |
| 596 | ROBINSON | R22 HP | R22 | Light | Single-Engine Helicopter | 157 |
| 516 | ROBINSON | R22 MARINER | R22 | Light | Single-Engine Helicopter | 183 |
| 406 | ROBINSON | R22 MARINER II | R22 | Light | Single-Engine Helicopter | 58 |
| 514 | ROBINSON | R44 ASTRO | R44 | Light | Single-Engine Helicopter | 754 |
| 1233 | ROBINSON | R44 CADET | R44 | Light | Single-Engine Helicopter | 110 |
| 602 | ROBINSON | R44 RAVEN I | R44 | Light | Single-Engine Helicopter | 2,036 |
| 515 | ROBINSON | R44 RAVEN II | R44 | Light | Single-Engine Helicopter | 4,893 |
| 481 | SCHWEIZER | 300CB | H269 | Light | Single-Engine Helicopter | 127 |
| 482 | SCHWEIZER | S-300C | H269 | Light | Single-Engine Helicopter | 739 |
| 370 | SCHWEIZER | S-300CBI | H269 | Light | Single-Engine Helicopter | 239 |

---

## Common Lookup Examples

| I want... | modlist | Notes |
|-----------|---------|-------|
| All Gulfstream G550s | `[278]` | GV-SP (G500) is AMODID 277 — different model |
| Gulfstream G650 + G650ER | `[663, 1211]` | Two separate model IDs |
| All Gulfstream large-cabin | `[278, 288, 294, 663, 1211, 83, 82, 81, 79, 275, 276, 1209, 1210, 1290, 1310]` | G-III through G800 |
| All Citation CJ3 variants | `[279, 1194]` | CJ3 and CJ3+ |
| Citation Latitude only | `[1167]` |  |
| All Falcon 900 variants | `[63, 64, 65, 66]` | 900, 900B, 900C, 900EX — check table for exact IDs |
| All King Air 350 variants | `[142, 143, 145, 1192]` | 350, 350C, 350ER, 350i — check table |
| All Boeing 737 MAX | `check Jet Airliner table` | Multiple variants: MAX 7, MAX 8, MAX 9, MAX 10 |
| Bell 407 only | `[100]` |  |
| All Robinson helicopters | `[847, 848, 849, 850, 851]` | R22, R44, R44-II, R66, R66 Turbine — check table |

---

## Combining Filters

The `modlist` parameter works alongside other request fields:

```json
{
  "modlist": [278, 288],
  "forsale": "true",
  "countrylist": ["United States"]
}
```

Common combinations:

| Filter | Field | Example |
|--------|-------|---------|
| Models for sale | `forsale: "true"` | Gulfstream G550s currently listed |
| Models by country | `countrylist: ["United States"]` | US-registered Citation Latitudes |
| Models by year range | `yearstart / yearend` | 2015+ Challenger 350s |
| Models by lifecycle | `lifecycle: ["Active"]` | Active-only King Air 350s |
| All models (no filter) | `modlist: []` | Returns every aircraft type |

