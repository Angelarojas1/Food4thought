# -*- coding: utf-8 -*-
"""
Created on Tue May 26 17:14:50 2026

@author: stevebc
"""

import pandas as pd
import glob
import os

# Path to the folder containing the CSV files
input_folder = r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\ChatGPT_output\ingredient_batch100"

# Output file path (saved in the same folder)
output_file = os.path.join(input_folder, "ingredient_all.csv")

# Expected columns
expected_columns = ["ingredient", "category", "canonical_ingredient"]

# Find all CSV files in the folder
csv_files = glob.glob(os.path.join(input_folder, "*.csv"))

if not csv_files:
    print("No CSV files found in the specified folder.")
    exit()

print(f"Found {len(csv_files)} CSV file(s).")

all_dfs = []
skipped = []

for file in sorted(csv_files):
    filename = os.path.basename(file)
    try:
        df = pd.read_csv(file)

        # Check column count
        if df.shape[1] != 3:
            print(f"  WARNING: '{filename}' has {df.shape[1]} column(s) — expected 3. Skipping.")
            skipped.append(filename)
            continue

        # Rename columns to the expected names regardless of what they're called
        df.columns = expected_columns

        all_dfs.append(df)
        print(f"  OK: '{filename}' — {len(df)} rows")

    except Exception as e:
        print(f"  ERROR reading '{filename}': {e}")
        skipped.append(filename)

if not all_dfs:
    print("\nNo valid CSV files to concatenate.")
    exit()

# Concatenate all dataframes
combined = pd.concat(all_dfs, ignore_index=True)

# Save to output file
combined.to_csv(output_file, index=False)

print(f"\nDone! {len(all_dfs)} file(s) combined into '{output_file}'")
print(f"Total rows: {len(combined)}")

if skipped:
    print(f"\nSkipped files ({len(skipped)}):")
    for f in skipped:
        print(f"  - {f}")