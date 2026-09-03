'''
AIM OF THE SCRIPT:
1. To convert the GDLET zip files to parquet files
2. To remove the raw zip files after processing
3. To perform the processing in-stream without saving intermediate CSV files to disk
4. To select required columns and perform aggregation to compute volume-weighted average tone
5. GDLET raw files are stored in data/raw/GDLET_ZIP
6. Target parquet files are stored in data/interim/GDELT
7. The required files can be downloaded from http://data.gdeltproject.org/events/index.html
'''
import zipfile
import pandas as pd
from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR
from pathlib import Path
import pyarrow.parquet as pq

# Set up raw zip input path and processed parquet output path
zip_folder_path = Path(r"C:\Users\gunja\OneDrive\Documents\ACTIVE PROJECTS\conflict_pred\data\raw\GDLET_ZIP")
processed_folder_path = Path(r"C:\Users\gunja\OneDrive\Documents\ACTIVE PROJECTS\conflict_pred\data\interim\GDELT")
processed_folder_path.mkdir(parents=True, exist_ok=True)

all_zip_files = list(zip_folder_path.glob("*.zip"))

if not all_zip_files:
    print(f"No ZIP files found in {zip_folder_path}")
    raise SystemExit(0)

# Column mapping configuration
SELECTED_COLS = [0, 1, 3, 7, 12, 17, 22, 28, 30, 33, 34]  # I used google gemini to find these column indices since the original file didn't have any column header.
COLUMN_NAMES = [
    "statement_id",
    "timestamp",
    "year",
    "country_a",
    "source_type",
    "country_b",
    "target_type",
    "event_root_code",
    "goldstein_scale",
    "num_articles",
    "avg_tone",
]

# Process ZIP files sequentially in-stream
for zip_file in all_zip_files:
    print(f"Processing ZIP: {zip_file.name}...")

    # Read CSV directly from memory stream (bypasses saving intermediate CSV to disk)
    with zipfile.ZipFile(zip_file, "r") as z:
        csv_filename = z.namelist()[0]
        with z.open(csv_filename) as f:
            df = pd.read_csv(
                f,
                sep="\t",
                header=None,
                usecols=SELECTED_COLS,
                names=COLUMN_NAMES,
                low_memory=False,
            )

    # Filter out rows missing essential grouping keys
    df = df.dropna(subset=["year", "country_a", "country_b", "event_root_code"])

    # Vectorized weighted calculation
    df["weighted_tone_num"] = df["num_articles"] * df["avg_tone"]

    df_grouped = (
        df.groupby(["year", "country_a", "country_b", "event_root_code"])
        .agg(
            sum_weighted_tone=("weighted_tone_num", "sum"),
            sum_articles=("num_articles", "sum"),
            mean_goldstein=("goldstein_scale", "mean"),
        )
        .reset_index()
    )

    # Compute final volume-weighted average tone
    df_grouped["weighted_avg_tone"] = (
        df_grouped["sum_weighted_tone"] / df_grouped["sum_articles"]
    )
    df_grouped = df_grouped.drop(
        columns=["sum_weighted_tone", "sum_articles"]
    )

    # Save output directly to compressed Parquet format
    parquet_path = processed_folder_path / f"{zip_file.stem}.parquet"
    df_grouped.to_parquet(parquet_path, engine="pyarrow", index=False)
    print(f"Saved: {parquet_path.name}")

    # Remove raw ZIP file after processing completes
    zip_file.unlink()
    print(f"Deleted raw ZIP file: {zip_file.name}\n")

print("Pipeline complete: All ZIP files converted to Parquet and raw archives removed.")