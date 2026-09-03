#Downloading data from the GDELT project for the specified date range and saving it to the designated output directory.
import os
import urllib.request
import pandas as pd


output_dir = r"C:\Users\gunja\OneDrive\Documents\ACTIVE PROJECTS\conflict_pred\data\raw\GDLET_ZIP"  # Or absolute: r"C:\your\folder\path"


# Generate valid calendar daily dates from 2015-04-10 to 2021-12-31
dates = pd.date_range(start="2015-04-10", end="2021-12-31", freq="D")
base_url = "http://data.gdeltproject.org/events/"

for dt in dates:
    date_str = dt.strftime("%Y%m%d")
    filename = f"{date_str}.export.CSV.zip"
    url = f"{base_url}{filename}"

    # 3. Create full destination filepath
    file_path = os.path.join(output_dir, filename)

    # 4. Check existence and save to the target filepath
    if not os.path.exists(file_path):
        print(f"Downloading {filename} to {output_dir}...")
        try:
            urllib.request.urlretrieve(url, file_path)
        except Exception as e:
            print(f"Failed to download {filename}: {e}")