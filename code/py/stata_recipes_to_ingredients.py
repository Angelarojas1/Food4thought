# -*- coding: utf-8 -*-
"""
Create unique raw ingredient list from recipe dataset.

Uses:
- listofingredients_eng when available and parseable
- otherwise falls back to listofingredients

Output:
    unique_raw_ingredients.csv
"""

import pandas as pd
import ast
import re
from pathlib import Path


# ------------------------------------------------------------------
# FILE PATHS
# ------------------------------------------------------------------

stata_file = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\recipe_all_countries_web.dta"
)

output_csv = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\unique_raw_ingredients.csv"
)


# ------------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------------

INGREDIENT_COL_ENG = "listofingredients_eng"
INGREDIENT_COL_RAW = "listofingredients"
COUNTRY_COL = "country"


# ------------------------------------------------------------------
# FUNCTION TO PARSE INGREDIENT LISTS
# ------------------------------------------------------------------

def parse_ingredient_list(x):
    """
    Converts string representation of Python list into actual list.
    Example:
        "['1 onion', '2 carrots']"
        -> ['1 onion', '2 carrots']
    """

    if pd.isna(x):
        return []

    if isinstance(x, list):
        return x

    x = str(x).strip()

    try:
        parsed = ast.literal_eval(x)

        if isinstance(parsed, list):
            return parsed

    except Exception:
        pass

    return []


def clean_raw_ingredient(x):
    """Trim and normalize whitespace."""
    x = str(x).strip()
    x = re.sub(r"\s+", " ", x)
    return x


# ------------------------------------------------------------------
# LOAD STATA FILE
# ------------------------------------------------------------------

df = pd.read_stata(stata_file)

for col in [INGREDIENT_COL_ENG, INGREDIENT_COL_RAW]:
    if col not in df.columns:
        raise ValueError(f"Could not find column: {col}")


# ------------------------------------------------------------------
# CREATE COMBINED INGREDIENT SOURCE
# ------------------------------------------------------------------

df["ingredient_source"] = df[INGREDIENT_COL_ENG]

# fallback if English variable is missing
mask_missing_eng = df["ingredient_source"].isna()

df.loc[mask_missing_eng, "ingredient_source"] = df.loc[
    mask_missing_eng,
    INGREDIENT_COL_RAW
]

# fallback if English variable exists but parses to empty list
parsed_lengths = df["ingredient_source"].apply(parse_ingredient_list).apply(len)
mask_empty_parse = parsed_lengths.eq(0)

df.loc[mask_empty_parse, "ingredient_source"] = df.loc[
    mask_empty_parse,
    INGREDIENT_COL_RAW
]

# final parsed list
df["parsed_ingredients"] = df["ingredient_source"].apply(parse_ingredient_list)
df["n_parsed_ingredients"] = df["parsed_ingredients"].apply(len)


# ------------------------------------------------------------------
# EXTRACT ALL INGREDIENT STRINGS
# ------------------------------------------------------------------

all_ingredients = []

for ingredients in df["parsed_ingredients"]:

    for ing in ingredients:

        ing = clean_raw_ingredient(ing)

        if ing != "":
            all_ingredients.append(ing)


# ------------------------------------------------------------------
# UNIQUE INGREDIENTS
# ------------------------------------------------------------------

unique_ingredients = sorted(set(all_ingredients))


# ------------------------------------------------------------------
# SAVE
# ------------------------------------------------------------------

out = pd.DataFrame({
    "raw_ingredient": unique_ingredients
})

output_csv.parent.mkdir(parents=True, exist_ok=True)
out.to_csv(output_csv, index=False, encoding="utf-8-sig")


# ------------------------------------------------------------------
# DIAGNOSTICS
# ------------------------------------------------------------------

print(f"Saved {len(unique_ingredients):,} unique ingredient strings")
print(output_csv)

print("\nRows using fallback raw ingredient list:")
print(mask_empty_parse.sum())

print("\nTotal ingredient mentions:")
print(len(all_ingredients))

if COUNTRY_COL in df.columns:
    print("\nUnique countries in full dataset:")
    print(df[COUNTRY_COL].nunique())

    country_parse_check = (
        df
        .groupby(COUNTRY_COL)["n_parsed_ingredients"]
        .agg(["count", "sum", "mean"])
        .sort_values("sum")
    )

    print("\nCountries with lowest parsed ingredient totals:")
    print(country_parse_check.head(20).to_string())

    zero_countries = country_parse_check[country_parse_check["sum"] == 0]

    print("\nCountries with zero parsed ingredients:")
    if len(zero_countries) == 0:
        print("None")
    else:
        print(zero_countries.to_string())