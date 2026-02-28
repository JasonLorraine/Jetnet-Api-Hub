"""
model_search.py -- Search the JETNET model-ID reference table.

Finds models matching a search term against make, model, and ICAO type.
Results include the AMODID (the integer you pass in `modlist`).

Usage:
    python scripts/model_search.py "G550"
    python scripts/model_search.py "citation"
    python scripts/model_search.py "GLF5"
    python scripts/model_search.py           # interactive mode
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TABLE_PATH = os.path.join(SCRIPT_DIR, "..", "references", "model-id-table.json")


def load_table():
    with open(TABLE_PATH) as f:
        return json.load(f)


def search(term, table):
    term = term.lower().strip()
    results = []
    for m in table:
        haystack = f"{m['make']} {m['model']} {m['icaotype']}".lower()
        if term in haystack:
            results.append(m)
    results.sort(key=lambda m: (-m["fleetCount"],))
    return results


def format_results(results):
    if not results:
        return "  No matches found."
    lines = []
    lines.append(f"  {'AMODID':>6}  {'MAKE':<20} {'MODEL':<22} {'ICAO':<6} {'TYPE':<14} {'FLEET':>6}")
    lines.append(f"  {'------':>6}  {'----':<20} {'-----':<22} {'----':<6} {'----':<14} {'-----':>6}")
    for m in results:
        lines.append(
            f"  {m['amodid']:>6}  {m['make']:<20} {m['model']:<22} {m['icaotype']:<6} {m['maketype']:<14} {m['fleetCount']:>6}"
        )
    lines.append(f"\n  {len(results)} model(s) found.  modlist: [{', '.join(str(m['amodid']) for m in results)}]")
    return "\n".join(lines)


def interactive(table):
    print("JETNET Model Search (type 'q' to quit)\n")
    while True:
        try:
            term = input("Search: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not term or term.lower() == "q":
            break
        results = search(term, table)
        print(format_results(results))
        print()


def self_test(table):
    print("Running self-test...\n")
    tests = [
        ("G550", 278, True),
        ("citation", None, True),
        ("GLF5", None, True),
        ("KING AIR", None, True),
        ("xyznonexistent", None, False),
    ]
    passed = 0
    for term, expect_amodid, expect_results in tests:
        results = search(term, table)
        has_results = len(results) > 0
        if has_results != expect_results:
            print(f"  FAIL: '{term}' expected results={expect_results}, got {has_results}")
            continue
        if expect_amodid and not any(m["amodid"] == expect_amodid for m in results):
            print(f"  FAIL: '{term}' expected AMODID {expect_amodid} in results")
            continue
        print(f"  PASS: '{term}' -> {len(results)} result(s)")
        passed += 1
    print(f"\n{passed}/{len(tests)} tests passed.")
    return passed == len(tests)


if __name__ == "__main__":
    table = load_table()
    if len(sys.argv) > 1:
        term = " ".join(sys.argv[1:])
        if term == "--self-test":
            ok = self_test(table)
            sys.exit(0 if ok else 1)
        results = search(term, table)
        print(format_results(results))
    else:
        interactive(table)
