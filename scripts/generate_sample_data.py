"""Kaggle Superstore jaisa messy sample CSV banata hai (Kaggle download ke bina test karne ke liye).

Jaan-boojh ke daali gayi gandagi: duplicate rows, missing values, mixed date formats,
extra spaces, inconsistent casing, negative quantity aur galat values.
"""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 1000

PRODUCTS = [
    ("FUR-CH-10001", "Office Chair Deluxe", "Furniture", 180.0),
    ("FUR-TA-10002", "Conference Table", "Furniture", 520.0),
    ("FUR-BO-10003", "Wooden Bookcase", "Furniture", 240.0),
    ("OFF-PA-10004", "Copy Paper A4 (500 sheets)", "Office Supplies", 12.5),
    ("OFF-BI-10005", "Ring Binder Set", "Office Supplies", 18.0),
    ("OFF-ST-10006", "Storage Box", "Office Supplies", 35.0),
    ("OFF-PE-10007", "Gel Pens (Pack of 10)", "Office Supplies", 6.5),
    ("TEC-PH-10008", "Smartphone X2", "Technology", 650.0),
    ("TEC-AC-10009", "Wireless Mouse", "Technology", 25.0),
    ("TEC-MA-10010", "Laser Printer", "Technology", 310.0),
    ("TEC-CO-10011", "Laptop Pro 14", "Technology", 1200.0),
    ("TEC-AC-10012", "USB-C Hub", "Technology", 45.0),
]
REGIONS = ["East", "West", "Central", "South"]

rows = []
dates = pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 730, N), unit="D")
for i in range(N):
    pid, name, cat, base = PRODUCTS[rng.integers(len(PRODUCTS))]
    qty = int(rng.integers(1, 10))
    price = round(base * rng.uniform(0.85, 1.15), 2)
    d = dates[i]
    # Mixed date formats
    date_str = [d.strftime("%m/%d/%Y"), d.strftime("%Y-%m-%d"), d.strftime("%d-%b-%Y")][i % 3]
    rows.append({
        "Row ID": i + 1,
        "Order ID": f"CA-{d.year}-{100000 + i // 2}",
        "Order Date": date_str,
        "Region": REGIONS[rng.integers(len(REGIONS))],
        "Product ID": pid,
        "Category": cat,
        "Product Name": name,
        "Sales": round(qty * price, 2),
        "Quantity": qty,
    })

df = pd.DataFrame(rows).astype(object)

# Inconsistent text: spaces aur casing
for idx in rng.choice(N, 60, replace=False):
    df.at[idx, "Region"] = f"  {str(df.at[idx, 'Region']).lower()} "
for idx in rng.choice(N, 30, replace=False):
    df.at[idx, "Category"] = str(df.at[idx, "Category"]).upper()

# Missing values
for col, count in [("Region", 25), ("Category", 15), ("Order Date", 10), ("Quantity", 8), ("Product ID", 5)]:
    df.loc[rng.choice(N, count, replace=False), col] = np.nan

# Invalid values
df.loc[rng.choice(N, 12, replace=False), "Quantity"] = -2   # negative quantity
df.loc[rng.choice(N, 6, replace=False), "Sales"] = -150.0   # negative price
df.loc[rng.choice(N, 4, replace=False), "Order Date"] = "not a date"

# Duplicate rows (Row ID bhi same, taaki exact duplicates hon)
df = pd.concat([df, df.sample(40, random_state=1)]).sample(frac=1, random_state=2)

out = Path(__file__).resolve().parent.parent / "data" / "raw_sales.csv"
df.to_csv(out, index=False)
print(f"{len(df)} rows likhe: {out}")
