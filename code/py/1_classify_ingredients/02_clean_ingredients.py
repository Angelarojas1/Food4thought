# -*- coding: utf-8 -*-
"""
Created on Wed May 20 12:32:00 2026

@author: stevebc
"""

# -*- coding: utf-8 -*-
"""
Clean unique raw ingredient strings and create unigram/bigram frequency lists.

Input:
    unique_raw_ingredients.csv

Outputs:
    unique_raw_ingredients_cleaned_step1.csv
    unigram_frequencies.csv
    bigram_frequencies.csv
"""

import pandas as pd
import re
from collections import Counter
from pathlib import Path


# ------------------------------------------------------------------
# FILE PATHS
# ------------------------------------------------------------------

input_csv = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\unique_raw_ingredients.csv"
)

output_dir = input_csv.parent

cleaned_output_csv = output_dir / "unique_raw_ingredients_cleaned_step1.csv"
unigram_output_csv = output_dir / "unigram_frequencies.csv"
bigram_output_csv = output_dir / "bigram_frequencies.csv"


# ------------------------------------------------------------------
# BASIC CLEANING FUNCTIONS
# ------------------------------------------------------------------

UNICODE_FRACTIONS = "¼½¾⅓⅔⅛⅜⅝⅞"


def normalize_text(x):
    """Lowercase and standardize spacing/punctuation."""
    if pd.isna(x):
        return ""

    x = str(x).lower().strip()

    # normalize common unicode dashes
    x = x.replace("–", "-").replace("—", "-")

    # remove unicode fractions
    x = re.sub(f"[{UNICODE_FRACTIONS}]", " ", x)

    # remove digits
    x = re.sub(r"\d+", " ", x)

    # replace punctuation with spaces
    # keep letters only, but allow apostrophes to disappear cleanly
    x = re.sub(r"[^a-zA-Z\s]", " ", x)

    # collapse whitespace
    x = re.sub(r"\s+", " ", x).strip()

    return x


def remove_single_letters(x):
    """
    Remove standalone one-letter tokens.
    Example:
        'g bell peppers' -> 'bell peppers'
    """
    tokens = x.split()
    tokens = [tok for tok in tokens if len(tok) > 1]
    return " ".join(tokens)


def tokenize(x):
    """Simple whitespace tokenizer."""
    if not isinstance(x, str) or x.strip() == "":
        return []
    return x.split()


def get_bigrams(tokens):
    return list(zip(tokens[:-1], tokens[1:]))


# ------------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------------

df = pd.read_csv(input_csv)

if "raw_ingredient" not in df.columns:
    raise ValueError("Expected a column named 'raw_ingredient'.")

df["raw_ingredient"] = df["raw_ingredient"].astype(str)


# ------------------------------------------------------------------
# STEPWISE CLEANING
# ------------------------------------------------------------------

df["clean_lower_digits_removed"] = df["raw_ingredient"].apply(normalize_text)

df["clean_no_single_letters"] = df["clean_lower_digits_removed"].apply(
    remove_single_letters
)

df["n_tokens"] = df["clean_no_single_letters"].apply(lambda x: len(tokenize(x)))
df["n_chars"] = df["clean_no_single_letters"].str.len()


# ------------------------------------------------------------------
# CREATE UNIGRAM AND BIGRAM FREQUENCIES
# ------------------------------------------------------------------

unigram_counter = Counter()
bigram_counter = Counter()

for text in df["clean_no_single_letters"]:
    tokens = tokenize(text)

    unigram_counter.update(tokens)

    bigrams = [" ".join(bg) for bg in get_bigrams(tokens)]
    bigram_counter.update(bigrams)


unigrams = (
    pd.DataFrame(unigram_counter.items(), columns=["term", "count"])
    .sort_values("count", ascending=False)
    .reset_index(drop=True)
)

bigrams = (
    pd.DataFrame(bigram_counter.items(), columns=["term", "count"])
    .sort_values("count", ascending=False)
    .reset_index(drop=True)
)


# ------------------------------------------------------------------
# SAVE OUTPUTS
# ------------------------------------------------------------------

unigrams.to_csv(unigram_output_csv, index=False)
bigrams.to_csv(bigram_output_csv, index=False)

print("Done.")
print(f"Unigram frequency file saved to: {unigram_output_csv}")
print(f"Bigram frequency file saved to: {bigram_output_csv}")

print("\nTop 30 unigrams:")
print(unigrams.head(30).to_string(index=False))

print("\nTop 30 bigrams:")
print(bigrams.head(30).to_string(index=False))



DROP_WORDS = {

    # ------------------------------------------------------------------
    # FUNCTION WORDS
    # ------------------------------------------------------------------

    "of", "or", "and", "for", "the", "to", "in",
    "with", "from", "as", "if", "you", "it",
    "about", "some", "one", "two",

    # ------------------------------------------------------------------
    # UNITS / MEASURES
    # ------------------------------------------------------------------

    "grams", "gram", "gr", "kg", "ml", "dl", "lb",
    "cup", "cups",
    "tablespoon", "tablespoons",
    "teaspoon", "teaspoons",
    "tbsp", "tsp",
    "spoon", "spoons",
    "glass", "liter",
    "pcs", "pc",
    "cm",
    "pack", "bag",
    "piece", "pieces",
    "slice", "slices",
    "bunch",
    "pinch",
    "handful",
    "head",
    "size",

    # ------------------------------------------------------------------
    # PREPARATION / COOKING WORDS
    # ------------------------------------------------------------------

    "chopped", "grated", "cut", "ground",
    "sliced", "peeled", "diced", "minced",
    "boiled", "cooked", "smoked", "frozen",
    "crushed", "roasted", "fried",
    "canned",
    "freshly",
    "powdered",

    # ------------------------------------------------------------------
    # DESCRIPTORS / MODIFIERS
    # ------------------------------------------------------------------

    "fresh", "dry", "dried",
    "large", "small", "medium",
  #  "red", "green", "yellow", "brown",
  #  "sweet", "hot", "cold", "dark",
    "whole", "mixed",
    "moderate",
    "little",
    "optional",
    "possibly",
    "desired",
    "half",
    "approx",

    # ------------------------------------------------------------------
    # RECIPE / INSTRUCTION WORDS
    # ------------------------------------------------------------------

    "taste",
    "optional",
    "desired",
    "cooking",
    "frying",

    # ------------------------------------------------------------------
    # TOKENS THAT OFTEN CREATE NOISE
    # ------------------------------------------------------------------

    "powder",
    "liquid",
    "cubes",
    "cube",
    "fillet",
    "breast",
    "zest",
 #   "leaves",
 #   "leaf",
 #   "seeds",
 #   "seed",

    # ------------------------------------------------------------------
    # FOREIGN / MISC UNIT-LIKE TOKENS
    # ------------------------------------------------------------------

    "el",

}


def drop_words_from_text(x, drop_words):
    """
    Drop standalone tokens that appear in DROP_WORDS.
    Then collapse whitespace so:
        'liters of cream' -> 'cream'
    """
    if not isinstance(x, str) or x.strip() == "":
        return ""

    tokens = x.split()
    tokens = [tok for tok in tokens if tok not in drop_words]

    cleaned = " ".join(tokens)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned

df["clean_after_drop_words"] = df["clean_no_single_letters"].apply(
    lambda x: drop_words_from_text(x, DROP_WORDS)
)

df["n_tokens_after_drop"] = df["clean_after_drop_words"].apply(
    lambda x: len(tokenize(x))
)

df["n_chars_after_drop"] = df["clean_after_drop_words"].str.len()

df.to_csv(cleaned_output_csv, index=False)

print("Done.")
print(f"Cleaned ingredient file saved to: {cleaned_output_csv}")



# ------------------------------------------------------------------
# CREATE FREQUENCIES AFTER DROP-WORD CLEANING
# ------------------------------------------------------------------

unigram_after_counter = Counter()
bigram_after_counter = Counter()

for text in df["clean_after_drop_words"]:
    tokens = tokenize(text)

    unigram_after_counter.update(tokens)

    bigrams = [" ".join(bg) for bg in get_bigrams(tokens)]
    bigram_after_counter.update(bigrams)


unigrams_after = (
    pd.DataFrame(unigram_after_counter.items(), columns=["term", "count"])
    .sort_values("count", ascending=False)
    .reset_index(drop=True)
)

bigrams_after = (
    pd.DataFrame(bigram_after_counter.items(), columns=["term", "count"])
    .sort_values("count", ascending=False)
    .reset_index(drop=True)
)

unigrams_after.to_csv(output_dir / "unigram_frequencies_after_drop.csv", index=False)
bigrams_after.to_csv(output_dir / "bigram_frequencies_after_drop.csv", index=False)

print("\nTop 100 unigrams after drop-word cleaning:")
print(unigrams_after.head(100).to_string(index=False))

print("\nTop 100 bigrams after drop-word cleaning:")
print(bigrams_after.head(100).to_string(index=False))

MORE_DROP_WORDS = {

    # --------------------------------------------------------------
    # REMAINING FUNCTION / STRUCTURE WORDS
    # --------------------------------------------------------------

    "be",
    "is",
    "on",
    "at",
    "use",
    "used",
    "without",
    "more",
    "other",
    "also",
    "like",
    "your",
    "not",

    # --------------------------------------------------------------
    # REMAINING PROCESS / PREPARATION WORDS
    # --------------------------------------------------------------

    "finely",
    "thinly",
    "washed",
    "cleaned",
    "drained",
    "melted",
    "whipped",
    "shredded",
    "halved",
    "pickled",
    "salted",
    "soaked",

    "ripe",
    "raw",
    "warm",
    "soft",
    "smooth",
    "thick",
    "hard",
    "young",
    "lukewarm",

    # --------------------------------------------------------------
    # SIZE / FORM / SHAPE
    # --------------------------------------------------------------

    "strips",
    "thin",
    "coarse",
    "coarsely",
    "sized",
    "long",

    # --------------------------------------------------------------
    # QUANTITY / CONTAINER WORDS
    # --------------------------------------------------------------

    "liters",
    "milliliters",
    "package",
    "packet",
    "jar",
    "bowl",
    "glasses",
    "drops",
    "scoops",
    "units",

    "pound",
    "kilo",
    "dkg",
    "dag",
    "dcl",
    "cc",
    "tl",

    # --------------------------------------------------------------
    # RECIPE / META WORDS
    # --------------------------------------------------------------

    "ingredients",
    "ingredient",
    "garnish",
    "decoration",
    "needed",
    "choice",
    "preferably",
    "amount",
    "type",
    "undefined",

    # --------------------------------------------------------------
    # GENERIC FOOD-STRUCTURE WORDS
    # --------------------------------------------------------------

    "mix",
    "filling",

    # --------------------------------------------------------------
    # POSSIBLY REMOVE DEPENDING ON GOAL
    # --------------------------------------------------------------
    # keep if you care about cooking distinctions

    # "broth",
    # "stock",
    # "paste",
    # "soup",
    # "spice",
    # "spices",
    # "seasoning",

}


# ------------------------------------------------------------------
# COMBINE DROP WORD LISTS
# ------------------------------------------------------------------

FINAL_DROP_WORDS = DROP_WORDS.union(MORE_DROP_WORDS)

FINAL_EXTRA_DROP_WORDS = {
    "into",
    "then",
    "depending",
    "alternatively",
    "possible",
    "possibly",
    "similar",
    "etc",
    "just",
    "enough",
    "want",
    "wants",
    "have",
    "don",
    "include",
    "choose",
    "there",
    "are",
    "will",
    "can",
    "may",
    "add",
    "removed",
    "divide",
    "divided",
    "portions",
    "rings",
    "circles",
    "julienne",
    "dice",
    "brunoise",
    "work",
    "surface",
    "working",
    "decorate",
    "brushing",
    "boil",
    "until",
    
    
    # additional ones
    "de",
    "three",
    "sheets",
    "ready",
    "plain",
    "good",
    "appropriate",
    "instant",
    "well",
    "ones",
    "bottle",
    "roughly",
    "according",
    "necessary",
    "quarter",
    "cl",
    "any",
    "free",
    "that",
    "mashed",
    "roast",
    "big",
    "ripe",
    "pitted",
    "scoop",
    "more",
    "natural",
    "old",
    "part",
    "but",
    "only",
    "thinly",
    "without",
    "mild",
    "thin",
    "cans",
    "tl",
    "toasted",
    "melted",
    "kl",
    "full",
    "meter",
    "round",
    "amount",
    "warm",
    "packs",
    "soft",
    "made",
    "be",
    "gm",
    "liters",
    "clean",
    "package",
    "condensed",
    "washed",
    "granulated",
    "pickled",
    "spoonful",
    "jar",
    "mix",
    "also",
    "on",
    "ingredients",
    "type",
    "inch",
    "lukewarm",
    "your",
    "cook",
    "semi",
    "per",
    "other",
    "used",
    "undefined",
    "dash",
    "is",
    "room",
    "serving",
    "kilogram",
    "less",
    "box",
    "maestro",
    "at",
    "low",
    "sized",
    "smooth",
    "fry",
    "needed"
    
    
}

FINAL_DROP_WORDS = FINAL_DROP_WORDS.union(FINAL_EXTRA_DROP_WORDS)


# ------------------------------------------------------------------
# FINAL CLEANING PASS
# ------------------------------------------------------------------

df["clean_final"] = df["clean_after_drop_words"].apply(
    lambda x: drop_words_from_text(x, FINAL_DROP_WORDS)
)

# collapse whitespace again just to be safe
df["clean_final"] = (
    df["clean_final"]
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

# remove empty strings
df.loc[df["clean_final"] == "", "clean_final"] = pd.NA


# ------------------------------------------------------------------
# OPTIONAL: CREATE FINAL UNIQUE INGREDIENT LIST
# ------------------------------------------------------------------

final_unique = (
    df["clean_final"]
    .dropna()
    .drop_duplicates()
    .sort_values()
)

final_unique_df = pd.DataFrame({
    "clean_final": final_unique
})

final_unique_output = output_dir / "unique_clean_final.csv"

final_unique_df.to_csv(final_unique_output, index=False)


# ------------------------------------------------------------------
# SAVE UPDATED CLEANED DATASET
# ------------------------------------------------------------------

df.to_csv(cleaned_output_csv, index=False)

print("\nFinal cleaned variable created:")
print("clean_final")

print(f"\nFinal unique ingredient list saved to:")
print(final_unique_output)