# -*- coding: utf-8 -*-
"""
Map final ingredient categories back to country-recipe dataset.

Uses:
- listofingredients_eng when available/parseable
- otherwise falls back to listofingredients

Outputs:
- recipe_ingredient_categories_long.csv
- country_broad_category_shares.csv
- country_broad_category_shares_wide.csv
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

ingredient_category_file = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\unique_raw_ingredients_cleaned_manual_with_categories.csv"
)

output_dir = stata_file.parent / "ingredients"

long_output_csv = output_dir / "recipe_ingredient_categories_long.csv"
country_category_output_csv = output_dir / "country_broad_category_shares.csv"
wide_output_csv = output_dir / "country_broad_category_shares_wide.csv"


# ------------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------------

COUNTRY_COL = "country"
INGREDIENT_COL_ENG = "listofingredients_eng"
INGREDIENT_COL_RAW = "listofingredients"


# ------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------

def parse_ingredient_list(x):
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
    x = str(x).strip()
    x = re.sub(r"\s+", " ", x)
    return x


# ------------------------------------------------------------------
# LOAD RECIPE DATA
# ------------------------------------------------------------------

recipes = pd.read_stata(stata_file)

for col in [COUNTRY_COL, INGREDIENT_COL_ENG, INGREDIENT_COL_RAW]:
    if col not in recipes.columns:
        raise ValueError(f"Could not find column: {col}")

recipes = recipes.reset_index(drop=True)
recipes["recipe_id"] = recipes.index + 1


# ------------------------------------------------------------------
# CREATE COMBINED INGREDIENT SOURCE
# ------------------------------------------------------------------

recipes["ingredient_source"] = recipes[INGREDIENT_COL_ENG]

# fallback if English variable is missing
mask_missing_eng = recipes["ingredient_source"].isna()

recipes.loc[mask_missing_eng, "ingredient_source"] = recipes.loc[
    mask_missing_eng,
    INGREDIENT_COL_RAW
]

# fallback if English variable exists but does not parse
parsed_lengths = recipes["ingredient_source"].apply(parse_ingredient_list).apply(len)
mask_empty_parse = parsed_lengths.eq(0)

recipes.loc[mask_empty_parse, "ingredient_source"] = recipes.loc[
    mask_empty_parse,
    INGREDIENT_COL_RAW
]

# recompute final parsed ingredient list
recipes["parsed_ingredients"] = recipes["ingredient_source"].apply(parse_ingredient_list)
recipes["n_parsed_ingredients"] = recipes["parsed_ingredients"].apply(len)

print("Unique countries in raw recipe dataset:", recipes[COUNTRY_COL].nunique())
print("Rows using fallback raw ingredient list:", mask_empty_parse.sum())


# ------------------------------------------------------------------
# EXPLODE RECIPE INGREDIENT LISTS
# ------------------------------------------------------------------

rows = []

for _, row in recipes.iterrows():

    country = row[COUNTRY_COL]
    recipe_id = row["recipe_id"]

    for ing in row["parsed_ingredients"]:

        raw_ingredient = clean_raw_ingredient(ing)

        if raw_ingredient != "":
            rows.append({
                "recipe_id": recipe_id,
                COUNTRY_COL: country,
                "raw_ingredient": raw_ingredient
            })

recipe_ingredients = pd.DataFrame(rows)

print("Unique countries after exploding ingredients:", recipe_ingredients[COUNTRY_COL].nunique())


# ------------------------------------------------------------------
# LOAD RAW → CLEANED INGREDIENT FILE
# ------------------------------------------------------------------

raw_clean_file = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\unique_raw_ingredients_cleaned_manual.csv"
)

canonical_file = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\temp_list.csv"
)

raw_clean = pd.read_csv(raw_clean_file)

raw_clean = raw_clean[
    ["raw_ingredient", "clean_manual_flags_removed"]
].copy()

raw_clean["raw_ingredient"] = (
    raw_clean["raw_ingredient"]
    .astype(str)
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
)

raw_clean["clean_manual_flags_removed"] = (
    raw_clean["clean_manual_flags_removed"]
    .astype(str)
    .str.strip()
    .str.lower()
    .str.replace(r"\s+", " ", regex=True)
)


# ------------------------------------------------------------------
# LOAD CLEANED INGREDIENT → CATEGORY/CANONICAL FILE
# ------------------------------------------------------------------

canonical_map = pd.read_csv(canonical_file)

canonical_map = canonical_map[
    ["ingredient", "category", "canonical_ingredient"]
].copy()

canonical_map["ingredient"] = (
    canonical_map["ingredient"]
    .astype(str)
    .str.strip()
    .str.lower()
    .str.replace(r"\s+", " ", regex=True)
)

canonical_map["canonical_ingredient"] = (
    canonical_map["canonical_ingredient"]
    .astype(str)
    .str.strip()
    .str.lower()
    .str.replace(r"\s+", " ", regex=True)
)

canonical_map["category"] = (
    canonical_map["category"]
    .astype(str)
    .str.strip()
)


# ------------------------------------------------------------------
# CREATE FINAL MAPPING:
# raw ingredient → cleaned ingredient → category/canonical
# ------------------------------------------------------------------

mapping = raw_clean.merge(
    canonical_map,
    left_on="clean_manual_flags_removed",
    right_on="ingredient",
    how="left",
    validate="many_to_one"
)


# ------------------------------------------------------------------
# MERGE BACK TO RECIPE INGREDIENTS
# ------------------------------------------------------------------

recipe_ingredients = recipe_ingredients.merge(
    mapping[
        [
            "raw_ingredient",
            "category",
            "canonical_ingredient"
        ]
    ],
    on="raw_ingredient",
    how="left",
    validate="many_to_one"
)

recipe_ingredients["category"] = (
    recipe_ingredients["category"]
    .fillna("unmatched")
)

recipe_ingredients["broad_category_final"] = recipe_ingredients["category"]

recipe_ingredients["canonical_ingredient"] = (
    recipe_ingredients["canonical_ingredient"]
    .fillna("unmatched")
)

# ------------------------------------------------------------------
# COUNTRY-CATEGORY FREQUENCIES
# ------------------------------------------------------------------

country_category_counts = (
    recipe_ingredients
    .groupby([COUNTRY_COL, "broad_category_final"])
    .size()
    .reset_index(name="ingredient_count")
)

country_totals = (
    recipe_ingredients
    .groupby(COUNTRY_COL)
    .size()
    .reset_index(name="total_ingredients")
)

country_category = country_category_counts.merge(
    country_totals,
    on=COUNTRY_COL,
    how="left"
)

country_category["share_of_ingredients"] = (
    country_category["ingredient_count"] /
    country_category["total_ingredients"]
)


# ------------------------------------------------------------------
# WIDE FORMAT
# ------------------------------------------------------------------

country_category_wide = country_category.pivot_table(
    index=COUNTRY_COL,
    columns="broad_category_final",
    values="share_of_ingredients",
    fill_value=0
).reset_index()


# ------------------------------------------------------------------
# SAVE
# ------------------------------------------------------------------

recipe_ingredients.to_csv(long_output_csv, index=False, encoding="utf-8-sig")
country_category.to_csv(country_category_output_csv, index=False, encoding="utf-8-sig")
country_category_wide.to_csv(wide_output_csv, index=False, encoding="utf-8-sig")


# ------------------------------------------------------------------
# DIAGNOSTICS
# ------------------------------------------------------------------

print("\nDone.")

print(f"\nLong recipe-ingredient-category file saved to:\n{long_output_csv}")
print(f"\nCountry-category shares saved to:\n{country_category_output_csv}")
print(f"\nWide country-category shares saved to:\n{wide_output_csv}")

print("\nUnique countries in final country-category file:")
print(country_category[COUNTRY_COL].nunique())

print("\nUnmatched ingredient rows:")
print((recipe_ingredients["broad_category_final"] == "unmatched").sum())

print("\nCategory counts:")
print(recipe_ingredients["broad_category_final"].value_counts(dropna=False).to_string())

print("\nCountries with zero parsed ingredients:")
zero_parsed = (
    recipes
    .groupby(COUNTRY_COL)["n_parsed_ingredients"]
    .sum()
    .loc[lambda x: x == 0]
)

print(zero_parsed.to_string())


# ------------------------------------------------------------------
# NORMALIZE SHARES EXCLUDING UNMATCHED
# ------------------------------------------------------------------

matched_counts = (
    country_category
    .loc[country_category["broad_category_final"] != "unmatched"]
    .groupby(COUNTRY_COL)["ingredient_count"]
    .sum()
    .reset_index(name="matched_ingredients")
)

country_category = country_category.merge(
    matched_counts,
    on=COUNTRY_COL,
    how="left"
)

country_category["share_excluding_unmatched"] = (
    country_category["ingredient_count"] /
    country_category["matched_ingredients"]
)

country_category.loc[
    country_category["broad_category_final"].eq("unmatched"),
    "share_excluding_unmatched"
] = pd.NA

country_category.to_csv(country_category_output_csv, index=False, encoding="utf-8-sig")


# ------------------------------------------------------------------
# MAP CATEGORY SHARES
# ------------------------------------------------------------------

import geopandas as gpd
import matplotlib.pyplot as plt

map_dir = output_dir / "maps_broad_categories"
map_dir.mkdir(parents=True, exist_ok=True)

# Natural Earth country shapefile
world_url = (
    "https://naturalearth.s3.amazonaws.com/"
    "110m_cultural/ne_110m_admin_0_countries.zip"
)

world = gpd.read_file(world_url)

# Exclude Antarctica
world = world[world["ADMIN"] != "Antarctica"].copy()

# Natural Earth country name column
world = world.rename(columns={"ADMIN": "country_map"})




# # ------------------------------------------------------------------
# # COUNTRY NAME HARMONIZATION
# # ------------------------------------------------------------------

# country_name_map = {
#     "United States": "United States of America",
#     "Cote D'Ivoire": "Côte d'Ivoire",
#     "Bosnia And Herzegovina": "Bosnia and Herzegovina",
#     "North Korea": "Dem. Rep. Korea",
#     "South Korea": "Republic of Korea",
#     "United Arab Emirates": "United Arab Emirates",
#     "Cabo Verde": "Cape Verde",
# }

# country_category["country_map"] = country_category[COUNTRY_COL].replace(country_name_map)


# ------------------------------------------------------------------
# COUNTRY NAME HARMONIZATION
# ------------------------------------------------------------------

country_name_map = {
    "United States": "United States of America",
    "Cote D'Ivoire": "Côte d'Ivoire",
    "Bosnia And Herzegovina": "Bosnia and Herzegovina",
    "North Korea": "North Korea",
    "South Korea": "South Korea",
    "Cabo Verde": "Cape Verde",
    "Czech Republic": "Czechia",
}

country_category["country_map"] = country_category[COUNTRY_COL].replace(country_name_map)

# ------------------------------------------------------------------
# BUILD FLEXIBLE NATURAL EARTH CROSSWALK
# ------------------------------------------------------------------

name_cols = [
    col for col in ["ADMIN", "NAME", "NAME_LONG", "SOVEREIGNT", "FORMAL_EN"]
    if col in world.columns
]

world_names = []

for idx, row in world.iterrows():
    for col in name_cols:
        val = row[col]
        if pd.notna(val):
            world_names.append({
                "world_index": idx,
                "country_map": str(val).strip()
            })

world_names = pd.DataFrame(world_names).drop_duplicates()

# merge recipe country names to any Natural Earth name variant
country_to_world = (
    country_category[[COUNTRY_COL, "country_map"]]
    .drop_duplicates()
    .merge(world_names, on="country_map", how="left")
)

not_matched = country_to_world[country_to_world["world_index"].isna()]

print("\nCountries still not matched to map:")
print(not_matched[[COUNTRY_COL, "country_map"]].drop_duplicates().to_string(index=False))

# ------------------------------------------------------------------
# MERGE DIAGNOSTICS
# ------------------------------------------------------------------

not_matched = country_to_world[country_to_world["world_index"].isna()]

print("\nCountries still not matched to map:")
print(
    not_matched[[COUNTRY_COL, "country_map"]]
    .drop_duplicates()
    .to_string(index=False)
)

unmatched_country_output = output_dir / "countries_not_matched_to_map.csv"

not_matched[[COUNTRY_COL, "country_map"]].drop_duplicates().to_csv(
    unmatched_country_output,
    index=False,
    encoding="utf-8-sig"
)




# ------------------------------------------------------------------
# COUNTRY RECIPE COUNTS
# ------------------------------------------------------------------

country_recipe_counts = (
    recipes
    .groupby(COUNTRY_COL)
    .size()
    .reset_index(name="n_recipes")
)

country_category = country_category.merge(
    country_recipe_counts,
    on=COUNTRY_COL,
    how="left"
)

# choose threshold
MIN_RECIPES = 10

country_category.loc[
    country_category["n_recipes"] <= MIN_RECIPES,
    "share_excluding_unmatched"
] = pd.NA


# ------------------------------------------------------------------
# PLOT ONE MAP PER CATEGORY — QUANTILE BINS
# ------------------------------------------------------------------

categories_to_plot = sorted(
    country_category.loc[
        country_category["broad_category_final"].notna()
        & ~country_category["broad_category_final"].isin(["unmatched"]),
        "broad_category_final"
    ].unique()
)

for cat in categories_to_plot:

    cat_df = country_category.loc[
    country_category["broad_category_final"].eq(cat),
    ["country_map", "share_excluding_unmatched"]
    ].copy()
    
    cat_df = cat_df.merge(
        world_names,
        on="country_map",
        how="left"
    )
    
    cat_df = (
        cat_df
        .dropna(subset=["world_index"])
        .groupby("world_index", as_index=False)["share_excluding_unmatched"]
        .mean()
    )
    
    map_df = world.reset_index().rename(columns={"index": "world_index"}).merge(
        cat_df,
        on="world_index",
        how="left"
    )

    # number of quantiles cannot exceed number of non-missing unique values
    n_unique = map_df["share_excluding_unmatched"].dropna().nunique()
    k = min(10, n_unique)

    fig, ax = plt.subplots(figsize=(14, 8))

    if k >= 2:
        map_df.plot(
            column="share_excluding_unmatched",
            ax=ax,
            scheme="Quantiles",
            k=k,
            cmap="YlOrRd",
            legend=True,
            edgecolor="black",
            linewidth=0.25,
            missing_kwds={
                "color": "lightgrey",
                "edgecolor": "black",
                "hatch": "///",
                "label": "No data"
            },
            legend_kwds={
                "title": "Share",
                "loc": "lower left"
            }
        )
    else:
        map_df.plot(
            column="share_excluding_unmatched",
            ax=ax,
            cmap="YlOrRd",
            legend=True,
            edgecolor="black",
            linewidth=0.25,
            missing_kwds={
                "color": "lightgrey",
                "edgecolor": "black",
                "hatch": "///",
                "label": "No data"
            },
            legend_kwds={
                "title": "Share",
                "loc": "lower left"
            }
        )

    ax.set_title(
        f"Share of matched ingredients: {cat}",
        fontsize=16
    )

    ax.axis("off")

    output_map = map_dir / f"map_{cat}_quantiles.png"

    plt.tight_layout()
    plt.savefig(output_map, dpi=300)
    plt.close()

    print(f"Saved map: {output_map}")
    
    
    
    
# ------------------------------------------------------------------
# SCATTER PLOT BETWEEN GROUPS OF INGREDIENT CATEGORIES
# ------------------------------------------------------------------

import matplotlib.pyplot as plt

# choose category groups
x_cats = ["meat", "poultry", "fish_seafood", "egg", "dairy"]
y_cats = ["legume"]


x_cats = ["condiment_sauce"]
y_cats = ["spice", "herb"]

# x_cats = ["dairy"]
# y_cats = ["fish_seafood"]

# ------------------------------------------------------------------
# PREPARE COUNTRY-LEVEL DATA
# ------------------------------------------------------------------

plot_df = country_category.copy()

# remove unmatched before normalization
matched_only = plot_df.loc[
    plot_df["broad_category_final"] != "unmatched"
].copy()

# total matched ingredients by country
matched_totals = (
    matched_only
    .groupby(COUNTRY_COL)["ingredient_count"]
    .sum()
    .reset_index(name="matched_total")
)

matched_only = matched_only.merge(
    matched_totals,
    on=COUNTRY_COL,
    how="left"
)

# normalized share excluding unmatched
matched_only["share_norm"] = (
    matched_only["ingredient_count"] /
    matched_only["matched_total"]
)

# wide country format
wide = matched_only.pivot_table(
    index=COUNTRY_COL,
    columns="broad_category_final",
    values="share_norm",
    fill_value=0
).reset_index()

# keep recipe counts
recipe_counts = (
    recipes
    .groupby(COUNTRY_COL)
    .size()
    .reset_index(name="n_recipes")
)

wide = wide.merge(
    recipe_counts,
    on=COUNTRY_COL,
    how="left"
)

# optional recipe threshold
MIN_RECIPES = 10

wide = wide.loc[wide["n_recipes"] > MIN_RECIPES].copy()

# ------------------------------------------------------------------
# CREATE GROUPED SHARES
# ------------------------------------------------------------------

# ensure all categories exist as columns
for cat in x_cats + y_cats:
    if cat not in wide.columns:
        wide[cat] = 0

wide["x_share"] = wide[x_cats].sum(axis=1)
wide["y_share"] = wide[y_cats].sum(axis=1)

x_label = " + ".join(x_cats)
y_label = " + ".join(y_cats)

# ------------------------------------------------------------------
# SCATTER PLOT
# ------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 8))

ax.scatter(
    wide["x_share"],
    wide["y_share"]
)

# add country labels
for _, row in wide.iterrows():
    ax.text(
        row["x_share"],
        row["y_share"],
        row[COUNTRY_COL],
        fontsize=7
    )

ax.set_xlabel(f"{x_label} share")
ax.set_ylabel(f"{y_label} share")

ax.set_title(
    f"{y_label} vs {x_label}\n(normalized excluding unmatched)"
)

plt.tight_layout()
plt.show()