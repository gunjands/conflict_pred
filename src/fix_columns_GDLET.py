from pathlib import Path
import pandas as pd


interim_folder = Path(r"C:\Users\gunja\OneDrive\Documents\ACTIVE PROJECTS\conflict_pred\data\interim\GDELT")
parquet_files = list(interim_folder.glob("*.parquet"))

for p_file in parquet_files:
    print(f"Cleaning types for: {p_file.name}...")

    df = pd.read_parquet(p_file)

    # 1. Force invalid strings ('--', '') to NaN, then drop them
    df["event_root_code"] = pd.to_numeric(
        df["event_root_code"], errors="coerce"
    )
    df = df.dropna(
        subset=["year", "country_a", "country_b", "event_root_code"]
    )

    # 2. Enforce strict type schemas across all columns
    df["year"] = df["year"].astype("int64")
    df["country_a"] = df["country_a"].astype("string")
    df["country_b"] = df["country_b"].astype("string")
    df["event_root_code"] = df["event_root_code"].astype("int32")
    df["mean_goldstein"] = df["mean_goldstein"].astype("float64")
    df["weighted_avg_tone"] = df["weighted_avg_tone"].astype("float64")

    # 3. Overwrite clean file back to disk
    df.to_parquet(p_file, engine="pyarrow", index=False)

print("All interim Parquet files sanitized successfully!")