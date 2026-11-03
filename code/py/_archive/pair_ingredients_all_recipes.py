
# ============================================================
# keeping all recipes, not only those that use spices.
# ============================================================

import pandas as pd
import ast
import re
import unicodedata
from itertools import combinations

# 1. Define file paths
input_path = r"C:\Users\wb617321\Dropbox\food4thought\analysis23\data\coded\recipes\recipe_all_countries_web.dta"
output_path = r"C:\Users\wb617321\Dropbox\food4thought\analysis23\data\coded\recipes\recipes_pairs.dta"

# 2. Load the dataset
df = pd.read_stata(input_path)

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

# 4. Clean an individual ingredient
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

# 5. Parse and clean each recipe's ingredient list
def parse_ingredients(x):
    if pd.isna(x):
        return []

    if isinstance(x, list):
        ingredients = x
    else:
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

df["ingredients_list"] = df["coreingredient"].apply(parse_ingredients)

# 6. Create a unique identifier for each recipe
df = df.reset_index(drop=True)
df["recipe_id"] = df.index + 1

# 7. Keep only the desired recipe-level variables
keep_vars = ["recipe_id", "continent_name", "adm0", "country"]
keep_vars = [var for var in keep_vars if var in df.columns]

# 9. Keep only recipes with at least two valid ingredients
df_valid = df[df["ingredients_list"].apply(len) >= 2].copy()

# Total number of valid recipes in the final dataset
total_recipes = df_valid["recipe_id"].nunique()

# 8. Generate all unique ingredient pairs
rows = []

for _, row in df_valid.iterrows():
    ingredients = row["ingredients_list"]

    for ingredient in ingredients:
        for ingredient1 in ingredients:
            if ingredient != ingredient1:
                new_row = {var: row[var] for var in keep_vars}
                new_row["ingredient"] = ingredient
                new_row["ingredient2"] = ingredient1
                rows.append(new_row)

# Create the final long-format dataset
columns = keep_vars + ["ingredient", "ingredient2"]
df_long = pd.DataFrame(rows, columns=columns)

# 10. Calculate pair frequencies in the full valid-recipe sample
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
    df_long["pair_recipe_count"] / df_long["total_recipes"]
)

# 11. Calculate pair frequencies by continent
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

# Total valid recipes per continent
continent_totals = (
    df_valid.groupby("continent_name", dropna=False)["recipe_id"]
    .nunique()
    .reset_index(name="total_recipes_cont")
)

df_long = df_long.merge(
    continent_totals,
    on="continent_name",
    how="left"
)

df_long["pair_share_cont"] = (
    df_long["pair_recipe_count_cont"] /
    df_long["total_recipes_cont"]
)

# 12. Save the final dataset
df_long.to_stata(
    output_path,
    write_index=False,
    version=118
)

print("Total valid recipes:", total_recipes)
print("Total ingredient-pair observations:", len(df_long))
print("Dataset saved to:", output_path)
