"""
Synthetic POS & Foot Traffic Data Generator
Shop: Egyptian Clothing Boutique (Cairo)
Regulation: 9 PM mandatory closure — RE-ENFORCED / UPDATED 2026
References: CAPMAS 2025 Retail Report, EFG Hermes Consumer Sector Analysis 2025

Timeline:
  2025 → Pre-regulation baseline (shops open until 11 PM)
  2026 → Post-regulation (9 PM mandatory closure, effective January 2026)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

np.random.seed(42)
random.seed(42)

# ── Constants ────────────────────────────────────────────────────────────────
SHOP_NAME = "Al-Nour Fashion Boutique"
CITY = "Cairo"
REGULATION_HOUR = 21  # 9 PM
START_DATE = datetime(2025, 1, 1)
END_DATE   = datetime(2026, 4, 25)   # up to today (Apr 25 2026)

# Hourly foot-traffic multipliers (pre-regulation baseline, 10 AM–11 PM)
# Source: EFG Hermes Egyptian Retail Survey 2023
HOURLY_TRAFFIC_BASE = {
    10: 0.20, 11: 0.35, 12: 0.50, 13: 0.45,
    14: 0.40, 15: 0.45, 16: 0.60, 17: 0.75,
    18: 0.90, 19: 1.00, 20: 0.95, 21: 0.85,
    22: 0.60, 23: 0.30,
}

# Post-regulation multipliers (9 PM closure enforced from Jan 2024)
HOURLY_TRAFFIC_POST_REG = {
    10: 0.28, 11: 0.45, 12: 0.62, 13: 0.52,
    14: 0.50, 15: 0.58, 16: 0.72, 17: 0.88,
    18: 1.00, 19: 1.05, 20: 0.98,
}

# Day-of-week multipliers (Fri/Sat are weekend in Egypt)
DOW_MULTIPLIERS = {0: 0.70, 1: 0.75, 2: 0.80, 3: 0.85, 4: 0.90, 5: 1.20, 6: 1.10}

# Monthly seasonality (Ramadan boost ~April, Summer slump, Back-to-school Sep)
MONTHLY_MULTIPLIERS = {
    1: 0.85, 2: 0.88, 3: 0.92, 4: 1.25,  # Ramadan
    5: 0.95, 6: 1.05, 7: 0.90, 8: 0.88,
    9: 1.10, 10: 1.00, 11: 1.00, 12: 1.15,
}

# Average transaction value (EGP) by product category
CATEGORIES = {
    "Women's Clothing": {"avg_price": 650, "weight": 0.40},
    "Men's Clothing":   {"avg_price": 580, "weight": 0.30},
    "Children's":       {"avg_price": 320, "weight": 0.15},
    "Accessories":      {"avg_price": 180, "weight": 0.10},
    "Footwear":         {"avg_price": 420, "weight": 0.05},
}

PAYMENT_METHODS = {"Cash": 0.55, "Card": 0.30, "Instapay": 0.15}

# Competitor shops (manual / Google Maps "Busy Hours" proxy)
COMPETITORS = [
    {"name": "Zara - Cairo Festival City", "peak_start": 17, "peak_end": 21},
    {"name": "H&M - Mall of Arabia",       "peak_start": 16, "peak_end": 21},
    {"name": "Local Boutique A",            "peak_start": 18, "peak_end": 22},
    {"name": "Local Boutique B",            "peak_start": 15, "peak_end": 20},
]

# Staffing levels
STAFF_ROLES = ["Cashier", "Sales Associate", "Stock Handler", "Security"]


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_hourly_dist(date: datetime) -> dict:
    """Return hourly traffic distribution for a given date."""
    is_post_reg = date.year == 2024
    base = HOURLY_TRAFFIC_POST_REG if is_post_reg else HOURLY_TRAFFIC_BASE
    return base


def transaction_count(hour_mult, dow_mult, month_mult, noise=0.15) -> int:
    base = 18 * hour_mult * dow_mult * month_mult
    base = max(0, base * (1 + np.random.normal(0, noise)))
    return int(base)


def pick_category():
    cats = list(CATEGORIES.keys())
    weights = [CATEGORIES[c]["weight"] for c in cats]
    return random.choices(cats, weights=weights, k=1)[0]


def pick_payment():
    methods = list(PAYMENT_METHODS.keys())
    weights = list(PAYMENT_METHODS.values())
    return random.choices(methods, weights=weights, k=1)[0]


# ── Main generators ──────────────────────────────────────────────────────────

def generate_pos_data() -> pd.DataFrame:
    records = []
    current = START_DATE
    tx_id = 1

    while current <= END_DATE:
        hourly = get_hourly_dist(current)
        dow_m = DOW_MULTIPLIERS[current.weekday()]
        mon_m = MONTHLY_MULTIPLIERS[current.month]

        for hour, h_mult in hourly.items():
            n_tx = transaction_count(h_mult, dow_m, mon_m)
            for _ in range(n_tx):
                cat = pick_category()
                unit_price = CATEGORIES[cat]["avg_price"]
                qty = random.choices([1, 2, 3], weights=[0.65, 0.25, 0.10])[0]
                discount_pct = random.choices([0, 5, 10, 15, 20],
                                              weights=[0.50, 0.15, 0.20, 0.10, 0.05])[0]
                revenue = unit_price * qty * (1 - discount_pct / 100)
                minute = random.randint(0, 59)
                records.append({
                    "transaction_id": f"TX{tx_id:07d}",
                    "timestamp": current.replace(hour=hour, minute=minute),
                    "date": current.date(),
                    "hour": hour,
                    "day_of_week": current.strftime("%A"),
                    "month": current.month,
                    "year": current.year,
                    "is_post_regulation": current.year == 2026,
                    "is_weekend": current.weekday() in [4, 5],
                    "category": cat,
                    "quantity": qty,
                    "unit_price_egp": unit_price,
                    "discount_pct": discount_pct,
                    "revenue_egp": round(revenue, 2),
                    "payment_method": pick_payment(),
                    "customer_age_group": random.choices(
                        ["18-25", "26-35", "36-45", "46+"],
                        weights=[0.30, 0.35, 0.25, 0.10])[0],
                    "is_return_customer": random.random() < 0.40,
                })
                tx_id += 1
        current += timedelta(days=1)

    return pd.DataFrame(records)


def generate_foot_traffic() -> pd.DataFrame:
    records = []
    current = START_DATE
    while current <= END_DATE:
        hourly = get_hourly_dist(current)
        dow_m = DOW_MULTIPLIERS[current.weekday()]
        mon_m = MONTHLY_MULTIPLIERS[current.month]
        for hour, h_mult in hourly.items():
            visitors = int(25 * h_mult * dow_m * mon_m * (1 + np.random.normal(0, 0.12)))
            records.append({
                "date": current.date(),
                "hour": hour,
                "day_of_week": current.strftime("%A"),
                "month": current.month,
                "year": current.year,
                "is_post_regulation": current.year == 2026,
                "is_weekend": current.weekday() in [4, 5],
                "visitors": max(0, visitors),
                "conversion_rate": round(min(0.95, max(0.1, np.random.normal(0.42, 0.08))), 3),
            })
        current += timedelta(days=1)

    return pd.DataFrame(records)


def generate_staffing() -> pd.DataFrame:
    records = []
    current = START_DATE
    while current <= END_DATE:
        is_weekend = current.weekday() in [4, 5]
        is_post_reg = current.year == 2026
        for shift in ["Morning (10-14)", "Afternoon (14-18)", "Evening (18-21/23)"]:
            if shift == "Evening (18-21/23)":
                end_h = 21 if is_post_reg else 23
                hours = 3 if is_post_reg else 5
            elif shift == "Afternoon (14-18)":
                hours = 4
            else:
                hours = 4
            records.append({
                "date": current.date(),
                "shift": shift,
                "cashiers": 2 if (is_weekend and shift != "Morning (10-14)") else 1,
                "sales_associates": 3 if (is_weekend and shift == "Evening (18-21/23)") else 2,
                "stock_handlers": 1 if shift == "Morning (10-14)" else 0,
                "security": 1,
                "shift_hours": hours,
                "is_weekend": is_weekend,
                "is_post_regulation": is_post_reg,
            })
        current += timedelta(days=1)

    return pd.DataFrame(records)


def generate_competitor_data() -> pd.DataFrame:
    records = []
    current = START_DATE
    while current <= END_DATE:
        for comp in COMPETITORS:
            for hour in range(10, 24):
                is_peak = comp["peak_start"] <= hour <= comp["peak_end"]
                # Post-regulation: competitors also close at 9 PM
                if current.year == 2026 and hour >= 21:
                    activity = 0
                else:
                    base = 0.80 if is_peak else 0.35
                    activity = round(base + np.random.normal(0, 0.08), 3)
                    activity = max(0, min(1, activity))
                records.append({
                    "date": current.date(),
                    "hour": hour,
                    "competitor": comp["name"],
                    "activity_index": activity,
                    "is_peak_hour": is_peak,
                    "year": current.year,
                })
        current += timedelta(days=1)

    return pd.DataFrame(records)


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    out_dir = os.path.dirname(__file__)
    print("Generating POS data (~2 years)…")
    pos = generate_pos_data()
    pos.to_csv(f"{out_dir}/pos_transactions.csv", index=False)
    print(f"  ✓ pos_transactions.csv  ({len(pos):,} rows)")

    print("Generating foot traffic data…")
    ft = generate_foot_traffic()
    ft.to_csv(f"{out_dir}/foot_traffic.csv", index=False)
    print(f"  ✓ foot_traffic.csv  ({len(ft):,} rows)")

    print("Generating staffing data…")
    st = generate_staffing()
    st.to_csv(f"{out_dir}/staffing.csv", index=False)
    print(f"  ✓ staffing.csv  ({len(st):,} rows)")

    print("Generating competitor data…")
    comp = generate_competitor_data()
    comp.to_csv(f"{out_dir}/competitor_activity.csv", index=False)
    print(f"  ✓ competitor_activity.csv  ({len(comp):,} rows)")

    print("\nAll datasets generated successfully.")
