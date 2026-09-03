import duckdb
from pathlib import Path

# 1. Add *.parquet wildcard and convert paths to POSIX format (forward slashes)
input_dir = Path(
    r"C:\Users\gunja\OneDrive\Documents\ACTIVE PROJECTS\conflict_pred\data\interim\GDELT"
)
input_pattern = (input_dir / "*.parquet").as_posix()

output_parquet = Path(
    r"C:\Users\gunja\OneDrive\Documents\ACTIVE PROJECTS\conflict_pred\data\interim\gdelt_filtered.parquet"
).as_posix()

# 2. Construct the SQL query cleanly
query = f"""
WITH filtered_data AS (
    SELECT 
        year || '_' || LEAST(country_a, country_b) || '_' || GREATEST(country_a, country_b) AS dyad,
        year,
        LEAST(country_a, country_b) AS country_a,
        GREATEST(country_a, country_b) AS country_b,
        event_root_code AS event_code,
        mean_goldstein,
        weighted_avg_tone
    FROM '{input_pattern}'
    WHERE country_a != country_b
)
PIVOT filtered_data
ON event_code IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)
USING 
    AVG(weighted_avg_tone) AS 'tone_code_{{}}',
    AVG(mean_goldstein) AS 'goldstein_code_{{}}'
GROUP BY dyad, year, country_a, country_b
ORDER BY year, country_a, country_b
"""

# 3. Execute using standard string formatting to avoid double-escaping braces
copy_sql = f"COPY ({query}) TO '{output_parquet}' (FORMAT PARQUET, COMPRESSION 'ZSTD');"

con = duckdb.connect()
con.execute(copy_sql)
print("Pipeline complete! Flat, clean dataset generated successfully.")