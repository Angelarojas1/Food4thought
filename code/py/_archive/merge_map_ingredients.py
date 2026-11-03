# -*- coding: utf-8 -*-
"""
Created on Wed May 20 15:23:01 2026

@author: stevebc
"""

# -*- coding: utf-8 -*-

import pandas as pd

# ------------------------------------------------------------------
# FILE PATHS
# ------------------------------------------------------------------

ingredients_path = r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\unique_raw_ingredients_cleaned_manual.csv"

categories_path = r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\ChatGPT_output\categories_iter1.csv"

other_manual_path = r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\ChatGPT_output\other_match_manual.csv"

output_path = r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\unique_raw_ingredients_cleaned_manual_with_categories.csv"


# ------------------------------------------------------------------
# LOAD FILES
# ------------------------------------------------------------------

ingredients = pd.read_csv(ingredients_path)
categories = pd.read_csv(categories_path)
other_manual = pd.read_csv(other_manual_path)


# ------------------------------------------------------------------
# BASIC CLEANING OF MERGE KEYS
# ------------------------------------------------------------------

ingredients["clean_manual_flags_removed"] = (
    ingredients["clean_manual_flags_removed"]
    .astype(str)
    .str.strip()
)

categories["clean_manual"] = (
    categories["clean_manual"]
    .astype(str)
    .str.strip()
)

other_manual["clean_manual"] = (
    other_manual["clean_manual"]
    .astype(str)
    .str.strip()
)


# ------------------------------------------------------------------
# FIRST MERGE: CHATGPT CATEGORY OUTPUT
# ------------------------------------------------------------------

df = ingredients.merge(
    categories,
    left_on="clean_manual_flags_removed",
    right_on="clean_manual",
    how="left",
    validate="many_to_one"
)

df = df.rename(columns={
    "broad_category": "broad_category_iter1"
})


# ------------------------------------------------------------------
# SECOND MERGE: MANUAL REPLACEMENTS FOR OTHER
# ------------------------------------------------------------------

other_manual = other_manual.rename(columns={
    "broad_category": "broad_category_manual_other"
})

df = df.merge(
    other_manual[["clean_manual", "broad_category_manual_other"]],
    left_on="clean_manual_flags_removed",
    right_on="clean_manual",
    how="left",
    validate="many_to_one",
    suffixes=("", "_manual")
)


# ------------------------------------------------------------------
# FINAL CATEGORY
# ------------------------------------------------------------------

df["broad_category_final"] = df["broad_category_iter1"]

mask_replace_other = (
    df["broad_category_iter1"].eq("other")
    & df["broad_category_manual_other"].notna()
)

df.loc[mask_replace_other, "broad_category_final"] = df.loc[
    mask_replace_other, "broad_category_manual_other"
]


# ------------------------------------------------------------------
# OPTIONAL DIAGNOSTICS
# ------------------------------------------------------------------

print("\nCategory counts, initial:")
print(df["broad_category_iter1"].value_counts(dropna=False).to_string())

print("\nCategory counts, final:")
print(df["broad_category_final"].value_counts(dropna=False).to_string())

print("\nNumber of 'other' replaced manually:")
print(mask_replace_other.sum())


# ------------------------------------------------------------------
# SAVE
# ------------------------------------------------------------------

df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"\nSaved to: {output_path}")


