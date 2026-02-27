"""
JETNET API -- Model Market Trends (Valuation Context)

Demonstrates how to use getModelMarketTrends to retrieve market trend
data for aircraft models, useful for valuation context and market analysis.

Required environment variables:
    JETNET_EMAIL    -- Your JETNET account email
    JETNET_PASSWORD -- Your JETNET account password
"""

import os
import sys
import requests
from datetime import datetime, timedelta

BASE = "https://customer.jetnetconnect.com"


def login(email, password):
    r = requests.post(
        f"{BASE}/api/Admin/APILogin",
        json={"emailAddress": email, "password": password},
    )
    r.raise_for_status()
    data = r.json()
    return data["bearerToken"], data["apiToken"]


def api(method, path, bearer, token, body=None):
    url = f"{BASE}{path}".replace("{apiToken}", token)
    headers = {
        "Authorization": f"Bearer {bearer}",
        "Content-Type": "application/json",
    }
    r = requests.request(method, url, headers=headers, json=body)
    r.raise_for_status()
    result = r.json()
    if "ERROR" in str(result.get("responsestatus", "")).upper():
        raise ValueError(f"JETNET error: {result['responsestatus']}")
    return result


def fmt_date(d):
    return d.strftime("%m/%d/%Y")


def get_market_trends(bearer, token, model_ids, months=24):
    """Get market trends for given model IDs over a time range.

    Args:
        model_ids: List of JETNET model IDs (e.g., [145] for G550)
        months: Number of months of data to retrieve
    """
    start_date = datetime.now() - timedelta(days=months * 30)
    body = {
        "modlist": model_ids,
        "displayRange": months,
        "startdate": fmt_date(start_date),
        "productcode": ["None"],
    }
    return api("POST", "/api/Model/getModelMarketTrends/{apiToken}", bearer, token, body)


def main():
    email = os.environ.get("JETNET_EMAIL")
    password = os.environ.get("JETNET_PASSWORD")
    if not email or not password:
        print("Set JETNET_EMAIL and JETNET_PASSWORD environment variables.")
        sys.exit(1)

    bearer, token = login(email, password)

    model_ids = [145, 634]
    print(f"Fetching 24-month market trends for model IDs: {model_ids}")
    print(f"(e.g., G550 = 145, G600 = 634)\n")

    result = get_market_trends(bearer, token, model_ids, months=24)

    trends = result.get("modelmarkettrends", result.get("markettrends", []))

    if not trends:
        print("No trend data returned. Check model IDs.")
        print(f"Response keys: {list(result.keys())}")
        return

    print(f"{'Month':12s}  {'For Sale':>10s}  {'Avg Ask Price':>15s}  {'Avg Days on Mkt':>16s}")
    print("-" * 60)

    for entry in trends[:12]:
        month = entry.get("month", entry.get("trendmonth", "N/A"))
        for_sale = entry.get("aircraft_for_sale_count", entry.get("forsalecount", "N/A"))
        avg_price = entry.get("avg_asking_price", entry.get("avgaskingprice", ""))
        days = entry.get("avg_daysonmarket", entry.get("avgdaysonmarket", ""))

        price_str = f"${avg_price:,.0f}" if isinstance(avg_price, (int, float)) and avg_price else str(avg_price)
        days_str = f"{days:.0f}" if isinstance(days, (int, float)) else str(days)

        print(f"{str(month):12s}  {str(for_sale):>10s}  {price_str:>15s}  {days_str:>16s}")

    if len(trends) > 12:
        print(f"\n  ... and {len(trends) - 12} more months of data.")

    print("\n--- 60-Month Deep Dive (for valuation) ---\n")
    result_60 = get_market_trends(bearer, token, [145], months=60)
    trends_60 = result_60.get("modelmarkettrends", result_60.get("markettrends", []))

    if trends_60:
        prices = [
            t.get("avg_asking_price", t.get("avgaskingprice", 0))
            for t in trends_60
            if t.get("avg_asking_price", t.get("avgaskingprice"))
        ]
        if prices:
            print(f"  Model ID 145 -- 60-month price range:")
            print(f"    High:    ${max(prices):,.0f}")
            print(f"    Low:     ${min(prices):,.0f}")
            print(f"    Current: ${prices[-1]:,.0f}")
            if len(prices) >= 2:
                change = ((prices[-1] - prices[0]) / prices[0]) * 100
                print(f"    Change:  {change:+.1f}%")


if __name__ == "__main__":
    main()
