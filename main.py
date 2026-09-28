"""Sales Data ETL Pipeline: Extract -> Transform -> Load -> Analyze

Usage:
    python main.py                  # poori pipeline (MySQL chahiye)
    python main.py --skip-db        # sirf extract + transform, clean CSV save hoti hai
    python main.py --input path.csv # apni CSV (jaise Kaggle Superstore) use karo
"""
import argparse
from pathlib import Path

from src.extract import extract
from src.transform import split_tables, transform

BASE_DIR = Path(__file__).resolve().parent
REPORT_TITLES = [
    "Monthly total sales",
    "Top 5 best-selling products",
    "Region-wise revenue",
    "Category-wise sales",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Sales Data ETL Pipeline")
    parser.add_argument("--input", default=BASE_DIR / "data" / "raw_sales.csv")
    parser.add_argument("--skip-db", action="store_true", help="MySQL load aur analysis skip karo")
    args = parser.parse_args()

    print("=== Step 1: Extract ===")
    raw = extract(args.input)

    print("\n=== Step 2: Transform ===")
    clean = transform(raw)
    products, sales = split_tables(clean)
    clean_path = BASE_DIR / "data" / "clean_sales.csv"
    clean.to_csv(clean_path, index=False)
    print(f"[transform] clean data save hua: {clean_path}")

    if args.skip_db:
        print("\n--skip-db diya hai, MySQL steps skip kiye.")
        return

    # MySQL imports yahan, taaki --skip-db bina connector ke bhi chale
    from src.load import analyze, load

    print("\n=== Step 3: Load ===")
    load(products, sales)

    print("\n=== Step 4: Analyze ===")
    for title, result in zip(REPORT_TITLES, analyze()):
        print(f"\n--- {title} ---")
        print(result.to_string(index=False))


if __name__ == "__main__":
    main()
