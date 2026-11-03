# ============================================================
# PAIR_INGREDIENTS.PY
# 1. Read and clean recipes
# 2. Generate ordered ingredient pairs
# 3. Identify spices using two Excel files
# 4. Keep pairs containing at least one spice
# 5. Calculate pair frequencies overall and by continent
# 6. Export to Stata
# ============================================================

import pandas as pd
import ast
import re
import unicodedata
from pathlib import Path

# ============================================================
# 1. FILE PATHS
# ============================================================

# Works both in code/py and as a downloaded standalone script.
project_root = Path(__file__).resolve().parents[2]
if not (project_root / "data").is_dir():
    project_root = Path.home() / "Dropbox" / "food4thought" / "analysis23"

spices_file1 = project_root / "data/raw/roster_spices/roster_spices_edited.xlsx"
spices_file2 = project_root / "data/raw/roster_spices/spices.xlsx"
input_path = project_root / "data/coded/recipes/recipe_all_countries_web.dta"
output_path = project_root / "data/coded/recipes/recipes_pairs_spices.dta"

# ============================================================
# 2. STOP WORDS
# ============================================================

# 3. Define unwanted standalone words and tokens
stop_words = """
tbs more litres stock or large to taste g for the conserve residue
from boiling cup of lb finely chopped fresh medium temperature c pkt
beated glazing dilute dressing preferably ts all-purporse all-purpose
ground ml kg soaked cold in cm canned liquid little undefined so some
whipping seasoned semi-coarse special plain processed with diced one
night mexico seasoning smokey extra virgin small blend self-raising
lilydale free range thigh premium good quality half x uncle ben
microwave firmly packed shredded tub mashed danish cubes dried cooked
mix salted unsalted colouring frac deseeded if you don't like it too
hot full-fat round wrappers pieces into torn tablespoon best low sodium
example tail intact and deveined each their cellophane glass your choice
beaten mixed frying sauce oceans slices spread vinegar meatballs packet
_ tbsp pure oz drumsticks a pizza base dough lb packet s o d e r fast-acting tsp 
n powdered lukewarm white brown icing whipped cream heavy grain long 
black puree sia dona flakes parts quick rising crushed solid tinned 
confectioners leaves split paste stew can drain chop washed drained
minced melted brushing over after grilling dry whole garnish powdered
full cream condensed tps powder freshly pound chops plus tablespoons
shoulder sella strands extracted adornment cracked teaspoon softish 
boiled cut blanched flaked on bone tsp cups 8ounces optional baby tbs
mince m ei er take toppings italian bit hirisan landslide sifted
ingredients cubed enough marinating crispy excess smoked my case home 
made left marinate overnight grated original originale frozen concentrated
soup plenty sprinkling
"""

stop_words = set(stop_words.split())

# ============================================================
# 3. TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """Lowercase, remove accents, and normalize spaces."""

    text = str(text).lower()

    # Remove accents: purée -> puree, jalapeño -> jalapeno
    text = "".join(
        char
        for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )

    # Treat hyphens and underscores as spaces
    text = re.sub(r"[-_]", " ", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text

# ============================================================
# 4. CLEAN INDIVIDUAL INGREDIENTS
# ============================================================

def clean_ingredient(ingredient):
    ingredient = str(ingredient).lower().strip()

    # Remove numbers, including fractions such as 1/2
    ingredient = re.sub(r"\b\d+(?:[./]\d+)*\b", " ", ingredient)

    # Remove unwanted standalone words only
    for word in stop_words:
        pattern = r"(?<!\w)" + re.escape(word) + r"(?!\w)"
        ingredient = re.sub(pattern, " ", ingredient, flags=re.IGNORECASE)

    # Remove registered trademark symbols and punctuation
    ingredient = ingredient.replace("®", " ")
    ingredient = re.sub(r"[^\w\s-]", "", ingredient)
    
    # Replace hyphens with spaces
    ingredient = ingredient.replace("-", " ")

    # Remove leftover underscores and extra spaces
    ingredient = ingredient.replace("_", " ")
    ingredient = re.sub(r"\s+", " ", ingredient).strip()
    
    # Remove consecutive duplicate words
    ingredient = re.sub(r"\b(\w+)(\s+\1\b)+", r"\1", ingredient)
    
    # Remove Unicode fraction characters
    ingredient = re.sub(r"[½¾¼]", " ", ingredient)
    
    ingredient = re.sub(r"\s+", " ", ingredient)
    ingredient = ingredient.strip()
    
    ingredient = ''.join(
        c for c in unicodedata.normalize('NFD', ingredient)
        if unicodedata.category(c) != 'Mn'
    )

    return ingredient


# ============================================================
# 5. PARSE AND CLEAN EACH RECIPE'S INGREDIENT LIST
# ============================================================

def parse_ingredients(x):
    if isinstance(x, list):
        ingredients = x
    else:
        if pd.isna(x):
            return []
        x = str(x).strip()

        try:
            ingredients = ast.literal_eval(x)
        except (ValueError, SyntaxError):
            ingredients = re.findall(r"""['"]([^'"]*)['"]""", x)

    cleaned = []

    for ingredient in ingredients:
        ingredient = clean_ingredient(ingredient)

        # Remove empty ingredients and avoid duplicate ingredients
        if ingredient and ingredient not in cleaned:
            cleaned.append(ingredient)

    return cleaned


# ============================================================
# 6. READ THE ORIGINAL RECIPE DATA
# ============================================================

df = pd.read_stata(input_path)

# Keep the exact column names used by pair_ingredients_all_recipes.py.
# In Stata, country/Country and totaltime/TotalTime are distinct variables.
# Only load the columns needed for ingredient pairs; no lowercasing.
required_columns = ["coreingredient", "continent_name"]
missing_columns = [name for name in required_columns if name not in df.columns]
if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")
pair_columns = [
    name for name in ["coreingredient", "continent_name", "adm0", "country"]
    if name in df.columns
]
df = df.loc[:, pair_columns].copy()
# Check required columns
if "coreingredient" not in df.columns:
    raise ValueError(
        "The input data does not contain a 'coreingredient' column. "
        f"Available columns: {df.columns.tolist()}"
    )

if "continent_name" not in df.columns:
    raise ValueError(
        "The input data does not contain a 'continent' column. "
        f"Available columns: {df.columns.tolist()}"
    )

# Unique recipe identifier
df = df.reset_index(drop=True)
df["recipe_id"] = df.index + 1

# Parse and clean all recipes
df["ingredients_list"] = df["coreingredient"].apply(parse_ingredients)

# Keep recipe-level variables when available
keep_vars = [
    var for var in ["recipe_id", "continent_name", "adm0", "country"]
    if var in df.columns
]

# A recipe must have at least two distinct valid ingredients
df_valid = df[
    df["ingredients_list"].apply(len) >= 2
].copy()

print("Original number of recipes:", df["recipe_id"].nunique())
print(
    "Recipes with at least two cleaned ingredients:",
    df_valid["recipe_id"].nunique()
)


# ============================================================
# 7. GENERATE ALL ORDERED INGREDIENT PAIRS
# ============================================================

rows = []

for _, row in df_valid.iterrows():

    ingredients = row["ingredients_list"]

    for ingredient in ingredients:

        for ingredient1 in ingredients:

            # Exclude self-pairs
            if ingredient != ingredient1:

                new_row = {
                    var: row[var]
                    for var in keep_vars
                }

                new_row["ingredient"] = ingredient
                new_row["ingredient2"] = ingredient1

                rows.append(new_row)

columns = keep_vars + ["ingredient", "ingredient2"]

df_long = pd.DataFrame(rows, columns=columns)

print("Ordered ingredient pairs before spice filtering:", len(df_long))


# ============================================================
# 8. LOAD BOTH SPICE LISTS
# ============================================================

spices1 = pd.read_excel(
    spices_file1,
    sheet_name="Spices",
    usecols=["Spice"]
)["Spice"]

spices2 = pd.read_excel(
    spices_file2,
    sheet_name="spices",
    usecols=["Spice Name"]
)["Spice Name"]

# Combine both lists
spices = pd.concat(
    [spices1, spices2],
    ignore_index=True
)

spices = spices.dropna().astype(str).str.strip()
spices = spices[spices != ""]

# Normalize names and remove duplicates
spices = sorted(
    {
        normalize_text(spice)
        for spice in spices
        if normalize_text(spice)
    },
    key=len,
    reverse=True
)

print("Unique spice names loaded:", len(spices))


# ============================================================
# 9. IDENTIFY SPICES WITHIN INGREDIENT STRINGS
# ============================================================

# Match complete spice names, ignoring capitalization and accents.
# Allows multiple spaces between words in a spice name.
spice_patterns = [
    re.compile(
        r"\b" + re.escape(spice).replace(r"\ ", r"\s+") + r"\b",
        flags=re.IGNORECASE
    )
    for spice in spices
]


def contains_spice(ingredient):

    if pd.isna(ingredient):
        return False

    ingredient = normalize_text(ingredient)

    return any(
        pattern.search(ingredient)
        for pattern in spice_patterns
    )


# Check both ingredients in every pair
df_long["ingredient_is_spice"] = (
    df_long["ingredient"].apply(contains_spice)
)

df_long["ingredient2_is_spice"] = (
    df_long["ingredient2"].apply(contains_spice)
)


# ============================================================
# 10. KEEP PAIRS WHERE AT LEAST ONE INGREDIENT IS A SPICE
# ============================================================

df_long = df_long[
    df_long["ingredient_is_spice"]
    | df_long["ingredient2_is_spice"]
].copy()

# Retain both spice indicators so the qualifying ingredient is identifiable.

print("Ordered pairs involving at least one spice:", len(df_long))

print(
    "Distinct recipes with at least one qualifying pair:",
    df_long["recipe_id"].nunique()
)


# ============================================================
# 11. CALCULATE OVERALL PAIR FREQUENCIES
# ============================================================

# Total distinct recipes represented in the filtered pair data
total_recipes = df_long["recipe_id"].nunique()

# Distinct recipes containing each ordered pair
pair_counts = (
    df_long.groupby(["ingredient", "ingredient2"])["recipe_id"]
    .nunique()
    .reset_index(name="pair_recipe_count")
)

df_long = df_long.merge(
    pair_counts,
    on=["ingredient", "ingredient2"],
    how="left"
)

df_long["total_recipes"] = total_recipes

df_long["pair_share"] = (
    df_long["pair_recipe_count"]
    / df_long["total_recipes"]
)


# ============================================================
# 12. CALCULATE PAIR FREQUENCIES BY CONTINENT
# ============================================================

pair_counts_cont = (
    df_long.groupby(
        ["continent_name", "ingredient", "ingredient2"],
        dropna=False
    )["recipe_id"]
    .nunique()
    .reset_index(name="pair_recipe_count_cont")
)

df_long = df_long.merge(
    pair_counts_cont,
    on=["continent_name", "ingredient", "ingredient2"],
    how="left"
)

# Distinct qualifying recipes per continent
continent_totals = (
    df_long.groupby("continent_name", dropna=False)["recipe_id"]
    .nunique()
    .reset_index(name="total_recipes_cont")
)

df_long = df_long.merge(
    continent_totals,
    on="continent_name",
    how="left"
)

df_long["pair_share_cont"] = (
    df_long["pair_recipe_count_cont"]
    / df_long["total_recipes_cont"]
)

# Final unit of observation: one ordered ingredient pair per continent.
# Counts and shares were computed above from distinct recipes.
qualifying_recipe_count = df_long["recipe_id"].nunique()
df_long = df_long.drop(columns=["recipe_id", "country", "adm0"], errors="ignore")
df_long = df_long.rename(columns={"continent_name": "continent"})
df_long = df_long.drop_duplicates().reset_index(drop=True)
pair_key = ["continent", "ingredient", "ingredient2"]
if df_long.duplicated(subset=pair_key).any():
    raise ValueError("Conflicting statistics for the same continent and ingredient pair.")
df_long = df_long[pair_key + [col for col in df_long.columns if col not in pair_key]]
# Stata string columns need Python strings; missing strings use "".
# Do not stringify arbitrary numeric columns or drop empty geography columns.
for var in ["continent", "ingredient", "ingredient2"]:
    if var in df_long.columns:
        df_long[var] = df_long[var].astype(object).map(
            lambda value: "" if pd.isna(value) else str(value)
        )
# ============================================================
# 13. SAVE THE FINAL DATASET
# ============================================================

df_long.to_stata(
    output_path,
    write_index=False,
    version=118
)

print("Final dataset saved to:", output_path)
print("Final number of rows:", len(df_long))
