import argparse
import pandas as pd
from pathlib import Path
import sys

def main():
    parser = argparse.ArgumentParser(description="Check a COVID dataset (CSV or Excel).")
    parser.add_argument("--path", type=str, default="data/owid-covid-data.csv", help="Path to dataset")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"❌ File not found: {path}")
        sys.exit(1)

    if path.suffix.lower() in [".csv", ".txt"]:
        df = pd.read_csv(path)
    elif path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(path)
    else:
        print(f"❌ Unsupported file type: {path.suffix}")
        sys.exit(1)

    print("\n✅ Loaded file:", path)
    print("Shape:", df.shape)

    print("\nColumns:")
    for i, c in enumerate(df.columns, 1):
        print(f"{i:>2}. {c}")

    # Guess useful columns
    date_cols = [c for c in df.columns if "date" in c.lower()]
    death_cols = [c for c in df.columns if "death" in c.lower()]
    location_cols = [c for c in df.columns if c.lower() in ["location","continent","iso_code"]]

    print("\nDate columns:", date_cols)
    print("Death columns:", death_cols)
    print("Location columns:", location_cols)

    print("\nSample rows:")
    print(df.head(5))

if __name__ == "__main__":
    main()
