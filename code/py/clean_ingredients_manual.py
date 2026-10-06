# -*- coding: utf-8 -*-
"""
Clean raw ingredient strings using manually flagged unigram removals.

Reads:
    unique_raw_ingredients.csv
    unigram_frequencies_manual_flags.csv

Outputs:
    unique_raw_ingredients_cleaned_manual.csv
    unique_clean_manual.csv
"""

import pandas as pd
import re
from pathlib import Path


# ------------------------------------------------------------------
# FILE PATHS
# ------------------------------------------------------------------

input_csv = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\unique_raw_ingredients.csv"
)

manual_flags_csv = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\unigram_frequencies_manual_flags_UPDATED.csv"
)

output_dir = input_csv.parent

cleaned_output_csv = output_dir / "unique_raw_ingredients_cleaned_manual.csv"
unique_output_csv = output_dir / "unique_clean_manual.csv"


# ------------------------------------------------------------------
# BASIC CLEANING FUNCTIONS
# ------------------------------------------------------------------

UNICODE_FRACTIONS = "¼½¾⅓⅔⅛⅜⅝⅞"


def normalize_text(x):
    """Lowercase, remove digits, normalize punctuation and whitespace."""
    if pd.isna(x):
        return ""

    x = str(x).lower().strip()
    x = x.replace("–", "-").replace("—", "-")

    # remove unicode fractions
    x = re.sub(f"[{UNICODE_FRACTIONS}]", " ", x)

    # remove digits
    x = re.sub(r"\d+", " ", x)

    # keep letters and whitespace only
    x = re.sub(r"[^a-zA-Z\s]", " ", x)

    # collapse whitespace
    x = re.sub(r"\s+", " ", x).strip()

    return x


def remove_single_letters(x):
    """Remove standalone one-letter tokens."""
    if not isinstance(x, str) or x.strip() == "":
        return ""

    tokens = x.split()
    tokens = [tok for tok in tokens if len(tok) > 1]

    return " ".join(tokens)


def drop_words_from_text(x, drop_words):
    """Drop standalone tokens in drop_words and collapse whitespace."""
    if not isinstance(x, str) or x.strip() == "":
        return ""

    tokens = x.split()
    tokens = [tok for tok in tokens if tok not in drop_words]

    cleaned = " ".join(tokens)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def tokenize(x):
    if not isinstance(x, str) or x.strip() == "":
        return []
    return x.split()


# ------------------------------------------------------------------
# LOAD RAW INGREDIENTS
# ------------------------------------------------------------------

df = pd.read_csv(input_csv)

if "raw_ingredient" not in df.columns:
    raise ValueError("Expected input file to contain column: raw_ingredient")

df["raw_ingredient"] = df["raw_ingredient"].astype(str)


# ------------------------------------------------------------------
# LOAD MANUAL UNIGRAM FLAGS
# ------------------------------------------------------------------

flags = pd.read_csv(manual_flags_csv)

required_cols = {"term", "flag"}
missing_cols = required_cols - set(flags.columns)

if missing_cols:
    raise ValueError(f"Manual flags file is missing columns: {missing_cols}")

flags["term"] = flags["term"].astype(str).str.lower().str.strip()

# flag == 0 means remove
drop_words = set(flags.loc[flags["flag"] == 0, "term"].dropna())

print(f"Loaded {len(drop_words)} manually flagged drop words.")


# ------------------------------------------------------------------
# CLEANING PIPELINE
# ------------------------------------------------------------------

df["clean_lower_digits_removed"] = df["raw_ingredient"].apply(normalize_text)

df["clean_no_single_letters"] = df["clean_lower_digits_removed"].apply(
    remove_single_letters
)

df["clean_manual_flags_removed"] = df["clean_no_single_letters"].apply(
    lambda x: drop_words_from_text(x, drop_words)
)

df["clean_manual_flags_removed"] = (
    df["clean_manual_flags_removed"]
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

df.loc[df["clean_manual_flags_removed"] == "", "clean_manual_flags_removed"] = pd.NA

df["n_tokens_manual_clean"] = df["clean_manual_flags_removed"].apply(
    lambda x: len(tokenize(x))
)

df["n_chars_manual_clean"] = df["clean_manual_flags_removed"].fillna("").str.len()


# ------------------------------------------------------------------
# SAVE FULL TRACEBACK FILE
# ------------------------------------------------------------------

df.to_csv(cleaned_output_csv, index=False, encoding="utf-8-sig")


# ------------------------------------------------------------------
# SAVE UNIQUE CLEANED INGREDIENT LIST WITH COUNTS / RANKS
# ------------------------------------------------------------------

unique_clean_df = (
    df["clean_manual_flags_removed"]
    .dropna()
    .value_counts()
    .rename_axis("clean_manual")
    .reset_index(name="count")
)

unique_clean_df["rank"] = unique_clean_df["count"].rank(
    method="dense",
    ascending=False
).astype(int)

unique_clean_df = unique_clean_df[
    ["rank", "clean_manual", "count"]
]

unique_clean_df.to_csv(unique_output_csv, index=False, encoding="utf-8-sig")


# ------------------------------------------------------------------
# PRINT SUMMARY
# ------------------------------------------------------------------

print("\nDone.")
print(f"Full traceback file saved to: {cleaned_output_csv}")
print(f"Unique cleaned list saved to: {unique_output_csv}")

print(f"\nRaw rows: {len(df):,}")
print(f"Unique cleaned rows: {len(unique_clean_df):,}")

print("\nExample output:")
print(
    df[["raw_ingredient", "clean_no_single_letters", "clean_manual_flags_removed"]]
    .head(20)
    .to_string(index=False)
)