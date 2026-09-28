"""Step 2: Transform - data clean karna aur naye columns banana."""
import re

import numpy as np
import pandas as pd

# In columns ke bina row bekaar hai -> aisi rows drop hongi
REQUIRED_COLUMNS = ["order_id", "order_date", "product_id", "quantity"]

# Baaki columns me missing values ke liye defaults
DEFAULTS = {
    "region": "Unknown",
    "category": "Unknown",
    "product_name": "Unknown Product",
}


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """'Order Date' -> 'order_date', 'Sub-Category' -> 'sub_category'."""
    df = df.copy()
    df.columns = [
        re.sub(r"[^0-9a-z]+", "_", col.strip().lower()).strip("_") for col in df.columns
    ]
    return df


def clean_text(df: pd.DataFrame) -> pd.DataFrame:
    """Extra spaces hatana aur region/category ki casing consistent karna."""
    df = df.copy()
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].str.strip().replace("", np.nan)
    for col in ["region", "category"]:
        if col in df.columns:
            df[col] = df[col].str.title()
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    start_rows = len(df)
    df = standardize_columns(df)
    df = clean_text(df)

    # 1. Duplicates hatana
    df = df.drop_duplicates()
    print(f"[transform] duplicates hataye: {start_rows - len(df)}")

    # 2. Numbers ko numeric banana (galat values -> NaN)
    for col in ["quantity", "sales", "unit_price", "price"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 3. Date format fix karna (mixed formats handle hote hain, galat date -> NaT)
    df["order_date"] = pd.to_datetime(df["order_date"], format="mixed", errors="coerce")

    # 4. Missing values: zaroori columns wali rows drop, baaki me defaults
    before = len(df)
    df = df.dropna(subset=REQUIRED_COLUMNS)
    print(f"[transform] zaroori values missing wali rows hatayi: {before - len(df)}")
    df = df.fillna({col: val for col, val in DEFAULTS.items() if col in df.columns})

    # 5. unit_price nikaalna. Superstore me sirf line total 'sales' hota hai,
    #    to unit_price = sales / quantity
    if "unit_price" not in df.columns:
        if "price" in df.columns:
            df["unit_price"] = df["price"]
        else:
            df["unit_price"] = np.where(df["quantity"] > 0, df["sales"] / df["quantity"], np.nan)

    # 6. Invalid data filter: negative / zero quantity ya price
    before = len(df)
    df = df[(df["quantity"] > 0) & (df["unit_price"] > 0)]
    print(f"[transform] invalid quantity/price wali rows hatayi: {before - len(df)}")

    # 7. Naye columns: revenue, year, month
    df = df.assign(
        quantity=df["quantity"].astype(int),
        unit_price=np.round(df["unit_price"], 2),
    )
    df["revenue"] = np.round(df["quantity"] * df["unit_price"], 2)
    df["order_year"] = df["order_date"].dt.year
    df["order_month"] = df["order_date"].dt.month

    df = df.reset_index(drop=True)
    print(f"[transform] {start_rows} raw rows -> {len(df)} clean rows")
    return df


def split_tables(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Clean data ko products aur sales tables me todna."""
    # Superstore me ek product_id ke kabhi-kabhi 2 naam hote hain -> ek hi rakho,
    # aur 'Unknown' default wali entry ko last priority do
    products = (
        df[["product_id", "product_name", "category"]]
        .sort_values("category", key=lambda c: c.eq("Unknown"), kind="stable")
        .drop_duplicates(subset="product_id", keep="first")
        .reset_index(drop=True)
    )
    sales = df[
        ["order_id", "order_date", "product_id", "region", "quantity", "unit_price", "revenue"]
    ].rename(columns={"unit_price": "price"})
    sales = sales.assign(order_date=sales["order_date"].dt.date)
    return products, sales
