"""Step 1: Extract - raw CSV ko Pandas DataFrame me padhna."""
import pandas as pd


def extract(path: str) -> pd.DataFrame:
    # Kaggle Superstore CSV latin-1 encoded hoti hai, isliye fallback rakha hai
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="latin-1")

    print(f"[extract] {path} se {df.shape[0]} rows, {df.shape[1]} columns padhe")
    print("[extract] df.info():")
    df.info()
    print("[extract] df.head():")
    print(df.head())
    return df
