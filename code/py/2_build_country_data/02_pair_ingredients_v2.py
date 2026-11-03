
# ============================================================
# IMPROVED INGREDIENT-PAIR PIPELINE
#
# Produces the outputs of both original scripts:
#   1. recipes_pairs.dta
#   2. recipes_pairs_spices.dta
#
# Preserves:
# - Original denominator definitions.
# - Ordered pairs: A-B and B-A.
# - Unique-recipe counts for each pair.
# - Original output structure for each analysis.
#
# Improves:
# - Measurement and quantity removal.
# - Separation of combined ingredient entries.
# - Ingredient-name standardization.
# - Ingredient deduplication within each recipe.
# ============================================================

import ast
import html
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

import pandas as pd


# ============================================================
# 1. FILE PATHS AND EXPORT SETTING
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if not (PROJECT_ROOT  / "data").is_dir():
    PROJECT_ROOT  = Path.home() / "Dropbox" / "food4thought" / "analysis23"


INPUT_PATH = (
    PROJECT_ROOT
    / "data/coded/recipes/recipe_all_countries_web.dta"
)

SPICES_FILE1 = (
    PROJECT_ROOT
    / "data/raw/roster_spices/roster_spices_edited.xlsx"
)

SPICES_FILE2 = (
    PROJECT_ROOT
    / "data/raw/roster_spices/spices.xlsx"
)

OUTPUT_ALL = (
    PROJECT_ROOT
    / "data/coded/recipes/recipes_pairs.dta"
)

OUTPUT_SPICES = (
    PROJECT_ROOT
    / "data/coded/recipes/recipes_pairs_spices.dta"
)

# Set to True to overwrite the two original output files.
SAVE_OUTPUTS = True


# ============================================================
# 2. CLEANING RULES
# ============================================================

UNITS = set("""
g gr gram grams kg kilogram kilograms
mg milligram milligrams
ml milliliter milliliters millilitre millilitres
cl dl l liter liters litre litres
oz ounce ounces lb lbs pound pounds
tsp tsps ts teaspoon teaspoons tps
tbsp tbs tbsps tablespoon tablespoons
cup cups c
pint pints quart quarts gallon gallons
cm mm
pkt pkts packet packets
""".split())

# Do not include actual foods or distinguishing terms such as
# cream, vinegar, stock, sauce, black, white, or brown.
PREPARATION = set("""
chopped chop finely roughly coarsely minced diced sliced
grated shredded crushed sifted peeled deseeded seeded
washed drained drain rinsed beaten melted softened
fresh freshly dried ground whole
large medium small optional
lukewarm cold warm
heaped heaping level firmly packed
cubed blanched boiled
""".split())

INVALID_INGREDIENTS = {
    "",
    "ei",
    "undefined",
    "none",
    "nan",
    "plain",
    "extra",
    "more",
    "some",
    "little",
    "enough",
    "or",
    "and",
    "for",
    "to",
    "taste",
}

REMOVE_PHRASES = [
    "to taste",
    "as needed",
    "as required",
    "for serving",
    "for garnish",
    "for garnishing",
    "for glazing",
    "for brushing",
    "room temperature",
    "finely chopped",
    "roughly chopped",
    "firmly packed",
    "juice",
]

# Only explicit equivalences are applied.
# Extend this dictionary after reviewing the ingredient names.
ALIASES = {
    "onions": "onion",
    "eggs": "egg",
    "tomatoes": "tomato",
    "potatoes": "potato",
    "carrots": "carrot",
    "lemons": "lemon",
    "limes": "lime",
    "oranges": "orange",
    "mushrooms": "mushroom",
    "garlic cloves": "garlic",
    "garlic clove": "garlic",
    "cloves garlic": "garlic",
    "clove garlic": "garlic",
    "chillies": "chili",
    "chilies": "chili",
    "chilli": "chili",
    "green chillies": "green chili",
    "green chilies": "green chili",
    "red chillies": "red chili",
    "red chilies": "red chili",
    "black peppercorns": "black pepper",
    "white peppercorns": "white pepper",
    "sia dona": "nigella",
    "sia dona (nigella seeds)": "nigella",
}

# Preserve expressions that normally describe one product.
PROTECTED_PHRASES = {
    "half and half": "halfandhalfprotected",
    "macaroni and cheese": "macaroniandcheeseprotected",
    "sweet and sour sauce": "sweetandsoursauceprotected",
}

audit_rows = []


# ============================================================
# 3. TEXT NORMALIZATION AND INGREDIENT CLEANING
# ============================================================

def normalize_text(value):
    """Normalize case, accents, spacing, and attached quantities."""
    text = html.unescape(str(value)).casefold()

    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        char
        for char in text
        if unicodedata.category(char) != "Mn"
    )

    text = text.replace("⁄", "/")
    text = re.sub(r"[-_–—]", " ", text)

    # Examples: 250ml -> 250 ml; salt250 -> salt 250.
    text = re.sub(r"(?<=\d)(?=[^\W\d_])", " ", text)
    text = re.sub(r"(?<=[^\W\d_])(?=\d)", " ", text)

    return re.sub(r"\s+", " ", text).strip()


@lru_cache(maxsize=100000)
def clean_ingredient(value):
    """Clean one ingredient after combined entries are separated."""
    text = normalize_text(value)

    # Apply aliases containing parentheses first.
    text = ALIASES.get(text, text)

    # Remove parenthetical quantities and notes.
    text = re.sub(r"\([^()]*\)", " ", text)

    for phrase in REMOVE_PHRASES:
        text = re.sub(
            r"\b" + re.escape(phrase) + r"\b",
            " ",
            text,
        )

    # Remove quantities, decimals, and fractions.
    text = re.sub(
        r"\d+(?:[.,]\d+)?(?:\s*/\s*\d+)?",
        " ",
        text,
    )

    # Keep letters and spaces.
    text = "".join(
        char if char.isalpha() or char.isspace() else " "
        for char in text
    )

    tokens = [
        token
        for token in text.split()
        if token not in UNITS
        and token not in PREPARATION
    ]

    # Remove consecutive repeated words.
    tokens = [
        token
        for i, token in enumerate(tokens)
        if i == 0 or token != tokens[i - 1]
    ]

    text = ALIASES.get(" ".join(tokens), " ".join(tokens))

    if text in INVALID_INGREDIENTS:
        return ""

    return text


def split_ingredient_entry(value, recipe_id):
    """Separate combined entries and flag ambiguous cases."""
    original = str(value)
    text = normalize_text(original)

    if "\ufffd" in original:
        audit_rows.append({
            "recipe_id": recipe_id,
            "original": original,
            "reason": "Damaged character: review original name",
        })

    # Exclude recipe section headings.
    if re.match(r"^for\b.*:\s*$", text):
        return []

    for phrase in REMOVE_PHRASES:
        text = re.sub(
            r"\b" + re.escape(phrase) + r"\b",
            " ",
            text,
        )

    # Explicit policy: retain the first alternative.
    # Do not count alternatives as confirmed co-occurring foods.
    if re.search(r"\bor\b", text):
        audit_rows.append({
            "recipe_id": recipe_id,
            "original": original,
            "reason": "Alternative ingredients: first option retained",
        })
        text = re.split(r"\bor\b", text, maxsplit=1)[0]

    for phrase, marker in PROTECTED_PHRASES.items():
        text = text.replace(phrase, marker)

    # Split salt, pepper / salt and pepper / salt & pepper.
    # Avoid splitting separators inside parentheses.
    pieces = re.split(
        r"[,;+\n](?![^()]*\))|\band\b(?![^()]*\))|&",
        text,
    )

    if len(pieces) > 1:
        audit_rows.append({
            "recipe_id": recipe_id,
            "original": original,
            "reason": "Combined entry split: review components",
        })

    cleaned = []

    for piece in pieces:
        for phrase, marker in PROTECTED_PHRASES.items():
            piece = piece.replace(marker, phrase)

        ingredient = clean_ingredient(piece)

        if ingredient:
            cleaned.append(ingredient)

    return cleaned


def parse_ingredients(value, recipe_id):
    """Parse, clean, and deduplicate ingredients within a recipe."""
    if isinstance(value, (list, tuple)):
        items = value
    else:
        if pd.isna(value):
            return []

        text = str(value).strip()

        if not text:
            return []

        try:
            parsed = ast.literal_eval(text)
        except (ValueError, SyntaxError):
            if text.startswith(("[", "(")):
                raise ValueError(
                    f"Recipe {recipe_id}: malformed ingredient list: "
                    f"{text[:200]}"
                )
            parsed = text

        if isinstance(parsed, str):
            items = [parsed]
        elif isinstance(parsed, (list, tuple)):
            items = parsed
        else:
            raise ValueError(
                f"Recipe {recipe_id}: unexpected ingredient format."
            )

    ingredients = set()

    for item in items:
        if item is None:
            continue

        ingredients.update(
            split_ingredient_entry(item, recipe_id)
        )

    return sorted(ingredients)


# ============================================================
# 4. LOAD AND CLEAN RECIPES
# ============================================================

df = pd.read_stata(INPUT_PATH)

required_columns = ["coreingredient", "continent_name"]
missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

recipe_columns = [
    column
    for column in [
        "coreingredient",
        "continent_name",
        "adm0",
        "country",
    ]
    if column in df.columns
]

df = df[recipe_columns].copy().reset_index(drop=True)

# Preserve the original assumption: one input row is one recipe.
df["recipe_id"] = df.index + 1

df["ingredients_list"] = [
    parse_ingredients(value, recipe_id)
    for value, recipe_id in zip(
        df["coreingredient"],
        df["recipe_id"],
    )
]

# Standardize geography representation before grouping.
df["continent_name"] = (
    df["continent_name"]
    .astype(object)
    .map(lambda value: "" if pd.isna(value) else str(value))
)

# ORIGINAL VALID-RECIPE CRITERION:
# Require at least two distinct cleaned ingredients.
df_valid = df[
    df["ingredients_list"].map(len) >= 2
].copy()

if df_valid.empty:
    raise ValueError(
        "No recipes contain at least two valid cleaned ingredients."
    )

print("Original rows:", len(df))
print(
    "Recipes without cleaned ingredients:",
    df["ingredients_list"].map(len).eq(0).sum(),
)
print(
    "Recipes with exactly one cleaned ingredient:",
    df["ingredients_list"].map(len).eq(1).sum(),
)
print(
    "Recipes with at least two valid ingredients:",
    df_valid["recipe_id"].nunique(),
)


# ============================================================
# 5. GENERATE ORDERED PAIRS — ORIGINAL PAIR STRUCTURE
# ============================================================

keep_vars = [
    column
    for column in [
        "recipe_id",
        "continent_name",
        "adm0",
        "country",
    ]
    if column in df_valid.columns
]

rows = []

for values in df_valid[
    keep_vars + ["ingredients_list"]
].itertuples(index=False, name=None):

    recipe_information = dict(zip(keep_vars, values[:-1]))
    ingredients = values[-1]

    for ingredient in ingredients:
        for ingredient2 in ingredients:
            if ingredient == ingredient2:
                continue

            rows.append({
                **recipe_information,
                "ingredient": ingredient,
                "ingredient2": ingredient2,
            })

df_pairs = pd.DataFrame(
    rows,
    columns=keep_vars + ["ingredient", "ingredient2"],
)

del rows

# Each ordered pair must appear at most once per recipe.
assert not df_pairs.duplicated(
    ["recipe_id", "ingredient", "ingredient2"]
).any()


# ============================================================
# 6. FREQUENCY CALCULATION
# ============================================================

def add_pair_statistics(pair_data, denominator_recipes):
    """
    Calculate counts and shares using an explicitly supplied
    recipe-level denominator.
    """
    result = pair_data.copy()

    total_recipes = denominator_recipes["recipe_id"].nunique()

    if total_recipes == 0:
        raise ValueError("The denominator contains no recipes.")

    pair_counts = (
        result.groupby(
            ["ingredient", "ingredient2"],
            observed=True,
        )["recipe_id"]
        .nunique()
        .reset_index(name="pair_recipe_count")
    )

    result = result.merge(
        pair_counts,
        on=["ingredient", "ingredient2"],
        how="left",
        validate="many_to_one",
    )

    result["total_recipes"] = total_recipes

    result["pair_share"] = (
        result["pair_recipe_count"]
        / result["total_recipes"]
    )

    pair_counts_continent = (
        result.groupby(
            ["continent_name", "ingredient", "ingredient2"],
            dropna=False,
            observed=True,
        )["recipe_id"]
        .nunique()
        .reset_index(name="pair_recipe_count_cont")
    )

    result = result.merge(
        pair_counts_continent,
        on=["continent_name", "ingredient", "ingredient2"],
        how="left",
        validate="many_to_one",
    )

    continent_totals = (
        denominator_recipes.groupby(
            "continent_name",
            dropna=False,
            observed=True,
        )["recipe_id"]
        .nunique()
        .reset_index(name="total_recipes_cont")
    )

    result = result.merge(
        continent_totals,
        on="continent_name",
        how="left",
        validate="many_to_one",
    )

    result["pair_share_cont"] = (
        result["pair_recipe_count_cont"]
        / result["total_recipes_cont"]
    )

    assert result["pair_share"].between(0, 1).all()
    assert result["pair_share_cont"].between(0, 1).all()

    return result


# ============================================================
# 7. ALL-RECIPES OUTPUT — ORIGINAL DENOMINATOR
# ============================================================

# All recipes with at least two valid cleaned ingredients.
all_denominator = df_valid[
    ["recipe_id", "continent_name"]
].copy()

pairs_all = add_pair_statistics(
    pair_data=df_pairs,
    denominator_recipes=all_denominator,
)

print(
    "\nALL-RECIPES denominator:",
    all_denominator["recipe_id"].nunique(),
)
print("ALL-RECIPES pair observations:", len(pairs_all))


# ============================================================
# 8. LOAD SPICE LISTS
# ============================================================

spices1 = pd.read_excel(
    SPICES_FILE1,
    sheet_name="Spices",
    usecols=["Spice"],
)["Spice"]

spices2 = pd.read_excel(
    SPICES_FILE2,
    sheet_name="spices",
    usecols=["Spice Name"],
)["Spice Name"]

spices_raw = pd.concat(
    [spices1, spices2],
    ignore_index=True,
).dropna()

# Apply consistent cleaning to the spice catalogue.
spice_names = {
    clean_ingredient(str(name))
    for name in spices_raw
}
spice_names.discard("")

if not spice_names:
    raise ValueError(
        "No valid spice names were loaded from the spice files."
    )

# Preserve the original classification approach:
# match complete spice names within an ingredient string.
spice_patterns = [
    re.compile(
        r"\b"
        + re.escape(name).replace(r"\ ", r"\s+")
        + r"\b"
    )
    for name in sorted(spice_names, key=len, reverse=True)
]


@lru_cache(maxsize=100000)
def contains_spice(ingredient):
    text = normalize_text(ingredient)
    return any(
        pattern.search(text)
        for pattern in spice_patterns
    )


# Classify unique ingredient names once.
unique_ingredients = pd.unique(
    df_pairs[["ingredient", "ingredient2"]]
    .to_numpy()
    .ravel()
)

spice_lookup = {
    ingredient: contains_spice(ingredient)
    for ingredient in unique_ingredients
}

print("Unique cleaned spice names:", len(spice_names))


# ============================================================
# 9. SPICE-PAIR OUTPUT — ORIGINAL DENOMINATOR
# ============================================================

spice_pairs = df_pairs.copy()

spice_pairs["ingredient_is_spice"] = (
    spice_pairs["ingredient"]
    .map(spice_lookup)
    .astype(bool)
)

spice_pairs["ingredient2_is_spice"] = (
    spice_pairs["ingredient2"]
    .map(spice_lookup)
    .astype(bool)
)

spice_pairs = spice_pairs[
    spice_pairs["ingredient_is_spice"]
    | spice_pairs["ingredient2_is_spice"]
].copy()

# ORIGINAL SPICE DENOMINATOR:
# Only recipes represented in pairs containing at least one spice.
spice_denominator = (
    spice_pairs[["recipe_id", "continent_name"]]
    .drop_duplicates()
)

if spice_denominator.empty:
    raise ValueError(
        "No qualifying spice pairs were found. "
        "Review the spice catalogue and ingredient names."
    )

pairs_spices = add_pair_statistics(
    pair_data=spice_pairs,
    denominator_recipes=spice_denominator,
)

print(
    "\nSPICE-PAIR denominator:",
    spice_denominator["recipe_id"].nunique(),
)
print(
    "SPICE-PAIR observations before aggregation:",
    len(pairs_spices),
)

# Preserve the original spice-output unit of observation:
# one ordered ingredient pair per continent.
pairs_spices = pairs_spices.drop(
    columns=["recipe_id", "country", "adm0"],
    errors="ignore",
)

pairs_spices = pairs_spices.rename(
    columns={"continent_name": "continent"}
)

pairs_spices = (
    pairs_spices.drop_duplicates()
    .reset_index(drop=True)
)

pair_key = ["continent", "ingredient", "ingredient2"]

if pairs_spices.duplicated(pair_key).any():
    raise ValueError(
        "Conflicting statistics for a continent and ingredient pair."
    )

pairs_spices = pairs_spices[
    pair_key
    + [
        column
        for column in pairs_spices.columns
        if column not in pair_key
    ]
]

print("Final SPICE-PAIR rows:", len(pairs_spices))


# ============================================================
# 10. CLEANING REVIEW TABLES — KEPT IN MEMORY
# ============================================================

cleaning_audit = pd.DataFrame(
    audit_rows,
    columns=["recipe_id", "original", "reason"],
).drop_duplicates()

ingredient_review = (
    df_valid[["recipe_id", "ingredients_list"]]
    .explode("ingredients_list")
    .rename(columns={"ingredients_list": "ingredient"})
    .groupby("ingredient", observed=True)["recipe_id"]
    .nunique()
    .reset_index(name="recipe_count")
    .sort_values("recipe_count", ascending=False)
)

ingredient_review["is_spice"] = (
    ingredient_review["ingredient"]
    .map(spice_lookup)
    .fillna(False)
    .astype(bool)
)

denominator_summary = pd.DataFrame({
    "analysis": ["all_recipes", "spice_pairs"],
    "total_recipes": [
        all_denominator["recipe_id"].nunique(),
        spice_denominator["recipe_id"].nunique(),
    ],
})

print("\nDenominator summary:")
print(denominator_summary.to_string(index=False))

print("\nMost frequent cleaned ingredients:")
print(ingredient_review.head(30).to_string(index=False))

print("\nEntries flagged for cleaning review:", len(cleaning_audit))
print(cleaning_audit.head(20).to_string(index=False))


# ============================================================
# 11. BASIC VALIDATION
# ============================================================

assert clean_ingredient("salt ml") == "salt"
assert clean_ingredient("250ml salt") == "salt"
assert clean_ingredient("1/2 tsp ground ginger") == "ginger"

# Preserve actual ingredient names.
assert clean_ingredient("white wine vinegar") == "white wine vinegar"
assert clean_ingredient("heavy cream") == "heavy cream"

# Verify splitting and deduplication without adding audit entries.
audit_length = len(audit_rows)

assert parse_ingredients(
    ["salt, pepper", "salt ml", "ginger"],
    recipe_id=0,
) == ["ginger", "pepper", "salt"]

del audit_rows[audit_length:]

assert (
    all_denominator["recipe_id"].nunique()
    == df_valid["recipe_id"].nunique()
)

assert (
    spice_denominator["recipe_id"].nunique()
    <= all_denominator["recipe_id"].nunique()
)


# ============================================================
# 12. OPTIONAL EXPORT
# ============================================================

def prepare_stata_strings(data):
    """Convert object and categorical text columns for Stata export."""
    result = data.copy()

    for column in result.columns:
        if (
            pd.api.types.is_object_dtype(result[column].dtype)
            or isinstance(result[column].dtype, pd.CategoricalDtype)
            or pd.api.types.is_string_dtype(result[column].dtype)
        ):
            result[column] = (
                result[column]
                .astype(object)
                .map(
                    lambda value:
                    "" if pd.isna(value) else str(value)
                )
            )

    return result


if SAVE_OUTPUTS:
    prepare_stata_strings(pairs_all).to_stata(
        OUTPUT_ALL,
        write_index=False,
        version=118,
    )

    prepare_stata_strings(pairs_spices).to_stata(
        OUTPUT_SPICES,
        write_index=False,
        version=118,
    )

    print("\nSaved:", OUTPUT_ALL)
    print("Saved:", OUTPUT_SPICES)

else:
    print("\nExport disabled. No output files were modified.")
    print("Results are available in:")
    print("  pairs_all")
    print("  pairs_spices")
    print("  ingredient_review")
    print("  cleaning_audit")
    print("  denominator_summary")