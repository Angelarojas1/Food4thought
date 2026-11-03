# -*- coding: utf-8 -*-
"""
Map ingredient categories and canonical ingredients back to country-recipe dataset.

Updates relative to the earlier script:
- Reads ingredient_category_file from temp_list.csv
- Expects temp_list.csv to contain:
    ingredient              raw ingredient name as it appears in recipe data
    category                broad ingredient category
    canonical_ingredient    refined standardized ingredient name
- Produces country-level shares by both category and canonical ingredient
- Clusters countries into 6 groups using k-means on canonical-ingredient shares
- Creates diagnostic maps for rice, milk, and potato canonical ingredient frequency

Uses:
- listofingredients_eng when available/parseable
- otherwise falls back to listofingredients
"""

import ast
import re
from pathlib import Path

import pandas as pd


# ------------------------------------------------------------------
# FILE PATHS
# ------------------------------------------------------------------

stata_file = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\recipe_all_countries_web.dta"
)

ingredient_category_file = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\ChatGPT_output\ingredient_batch100\ingredient_all.csv"
)

# ingredient_category_file = Path(
#     r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\temp_list.csv"
# )

output_dir = stata_file.parent / "ingredients"
output_dir.mkdir(parents=True, exist_ok=True)

long_output_csv = output_dir / "recipe_ingredient_categories_canonical_long.csv"

country_category_output_csv = output_dir / "country_category_shares.csv"
country_category_wide_output_csv = output_dir / "country_category_shares_wide.csv"

country_canonical_output_csv = output_dir / "country_canonical_ingredient_shares.csv"
country_canonical_wide_output_csv = output_dir / "country_canonical_ingredient_shares_wide.csv"

cluster_output_csv = output_dir / "country_canonical_ingredient_kmeans_clusters.csv"

unmatched_ingredient_output_csv = output_dir / "unmatched_raw_ingredients.csv"
unmatched_country_output_csv = output_dir / "countries_not_matched_to_map.csv"


# ------------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------------

COUNTRY_COL = "country"
INGREDIENT_COL_ENG = "listofingredients_eng"
INGREDIENT_COL_RAW = "listofingredients"

# Countries with <= MIN_RECIPES are kept in output tables but set to missing in maps/clustering.
MIN_RECIPES = 10

# K-means settings.
N_CLUSTERS = 5
RANDOM_STATE = 12345

# Diagnostic canonical ingredients to map.
CANONICAL_INGREDIENTS_TO_MAP = ["rice", "milk", "potato", "wheat", "tomato", "olive", "pork", "corn_sweetcorn", "beef", "marine"]


# ------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------

def parse_ingredient_list(x):
    """Parse a Stata/stringified Python list of ingredients."""
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


def clean_text(x):
    """Trim text and collapse repeated whitespace, robust to weird list/array values."""
    if x is None:
        return ""

    if isinstance(x, (list, tuple)):
        x = " ".join(str(i) for i in x)

    try:
        import numpy as np
        if isinstance(x, np.ndarray):
            x = " ".join(x.astype(str))
    except Exception:
        pass

    try:
        if pd.isna(x):
            return ""
    except Exception:
        pass

    x = str(x).strip()
    x = re.sub(r"\s+", " ", x)
    return x


def clean_key(x):
    """Cleaning used only for matching raw ingredient strings."""
    return clean_text(x).casefold()


def country_match_key(x):
    """Stable key for matching recipe country names to Natural Earth names."""
    return clean_text(x).casefold()


def safe_filename(x):
    """Make category/canonical ingredient names safe for filenames."""
    x = clean_text(x).lower()
    x = re.sub(r"[^a-z0-9]+", "_", x)
    x = re.sub(r"_+", "_", x).strip("_")
    return x or "missing"


def add_recipe_counts(df, recipes):
    recipe_counts = (
        recipes
        .groupby(COUNTRY_COL)
        .size()
        .reset_index(name="n_recipes")
    )
    return df.merge(recipe_counts, on=COUNTRY_COL, how="left")


def build_country_shares(recipe_ingredients, group_col, value_label):
    """
    Build long and wide country-level ingredient share tables for either
    category or canonical_ingredient.
    """
    counts = (
        recipe_ingredients
        .groupby([COUNTRY_COL, group_col])
        .size()
        .reset_index(name="ingredient_count")
    )

    totals_all = (
        recipe_ingredients
        .groupby(COUNTRY_COL)
        .size()
        .reset_index(name="total_ingredients")
    )

    out = counts.merge(totals_all, on=COUNTRY_COL, how="left")
    out["share_of_ingredients"] = out["ingredient_count"] / out["total_ingredients"]

    # Matched-only denominator. This excludes rows where the mapping failed.
    matched_counts = (
        out
        .loc[out[group_col] != "unmatched"]
        .groupby(COUNTRY_COL)["ingredient_count"]
        .sum()
        .reset_index(name=f"matched_{value_label}_ingredients")
    )

    out = out.merge(matched_counts, on=COUNTRY_COL, how="left")
    out["share_excluding_unmatched"] = (
        out["ingredient_count"] / out[f"matched_{value_label}_ingredients"]
    )
    out.loc[out[group_col].eq("unmatched"), "share_excluding_unmatched"] = pd.NA

    wide = out.pivot_table(
        index=COUNTRY_COL,
        columns=group_col,
        values="share_excluding_unmatched",
        fill_value=0
    ).reset_index()

    return out, wide


def load_world_map():
    """Load Natural Earth countries using the same structure as the working old script."""
    import geopandas as gpd

    world_url = (
        "https://naturalearth.s3.amazonaws.com/"
        "110m_cultural/ne_110m_admin_0_countries.zip"
    )

    world = gpd.read_file(world_url)
    world = world[world["ADMIN"] != "Antarctica"].copy()

    # Keep the old-script convention: Natural Earth ADMIN becomes country_map.
    world = world.rename(columns={"ADMIN": "country_map"})

    return world


def make_world_name_crosswalk(world):
    """Create the Natural Earth country-name crosswalk, old-script style plus a robust key."""
    name_cols = [
        col for col in ["country_map", "ADMIN", "NAME", "NAME_LONG", "SOVEREIGNT", "FORMAL_EN"]
        if col in world.columns
    ]

    world_names = []

    for idx, row in world.iterrows():
        for col in name_cols:
            val = row[col]
            if pd.notna(val):
                name = clean_text(val)
                if name != "":
                    world_names.append({
                        "world_index": idx,
                        "country_map_world": name,
                        "country_key": country_match_key(name)
                    })

    world_names = pd.DataFrame(world_names).drop_duplicates()

    if world_names.empty:
        raise ValueError("Natural Earth country-name crosswalk is empty; map matching cannot proceed.")

    return world_names


def harmonize_country_names(df):
    """Harmonize recipe country names to Natural Earth names where needed."""
    country_name_map = {
        "United States": "United States of America",
        "Cote D'Ivoire": "Côte d'Ivoire",
        "Bosnia And Herzegovina": "Bosnia and Herzegovina",
        "North Korea": "North Korea",
        "South Korea": "South Korea",
        "Cabo Verde": "Cape Verde",
        "Czech Republic": "Czechia",
    }

    df = df.copy()
    df["country_map"] = df[COUNTRY_COL].replace(country_name_map)
    df["country_key"] = df["country_map"].apply(country_match_key)
    return df


def report_map_matches(country_df, world_names):
    country_to_world = (
        country_df[[COUNTRY_COL, "country_map", "country_key"]]
        .drop_duplicates()
        .merge(world_names[["world_index", "country_key"]].drop_duplicates(), on="country_key", how="left")
    )

    not_matched = country_to_world[country_to_world["world_index"].isna()]

    print("\nCountries still not matched to map:")
    print(
        not_matched[[COUNTRY_COL, "country_map"]]
        .drop_duplicates()
        .to_string(index=False)
    )

    not_matched[[COUNTRY_COL, "country_map"]].drop_duplicates().to_csv(
        unmatched_country_output_csv,
        index=False,
        encoding="utf-8-sig"
    )


def plot_share_map(country_df, world, world_names, value_col, title, output_png):
    """Plot one country-level share map using quantile bins when possible."""
    import matplotlib.pyplot as plt

    country_df = country_df.copy()

    if "country_key" not in country_df.columns:
        country_df["country_key"] = (
            country_df["country_map"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    plot_df = country_df[["country_map", "country_key", value_col]].copy()

    plot_df = plot_df.merge(
        world_names[["world_index", "country_key"]].drop_duplicates(),
        on="country_key",
        how="left"
    )

    plot_df = (
        plot_df
        .dropna(subset=["world_index"])
        .groupby("world_index", as_index=False)[value_col]
        .mean()
    )

    map_df = world.reset_index().rename(columns={"index": "world_index"}).merge(
        plot_df,
        on="world_index",
        how="left"
    )

    n_unique = map_df[value_col].dropna().nunique()
    k = min(10, n_unique)

    fig, ax = plt.subplots(figsize=(14, 8))

    plot_kwargs = dict(
        column=value_col,
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
        }
    )

    if k >= 2:
        map_df.plot(scheme="Quantiles", k=k, **plot_kwargs)
    else:
        map_df.plot(**plot_kwargs)

    ax.set_title(title, fontsize=16)
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(output_png, dpi=300)
    plt.close()

    print(f"Saved map: {output_png}")


# ------------------------------------------------------------------
# LOAD RECIPE DATA
# ------------------------------------------------------------------

recipes = pd.read_stata(stata_file)

for col in [COUNTRY_COL, INGREDIENT_COL_ENG, INGREDIENT_COL_RAW]:
    if col not in recipes.columns:
        raise ValueError(f"Could not find column in recipe data: {col}")

recipes = recipes.reset_index(drop=True)
recipes["recipe_id"] = recipes.index + 1


# ------------------------------------------------------------------
# CREATE COMBINED INGREDIENT SOURCE
# ------------------------------------------------------------------

recipes["ingredient_source"] = recipes[INGREDIENT_COL_ENG]

# Fallback if English variable is missing.
mask_missing_eng = recipes["ingredient_source"].isna()
recipes.loc[mask_missing_eng, "ingredient_source"] = recipes.loc[
    mask_missing_eng,
    INGREDIENT_COL_RAW
]

# Fallback if English variable exists but does not parse.
parsed_lengths = recipes["ingredient_source"].apply(parse_ingredient_list).apply(len)
mask_empty_parse = parsed_lengths.eq(0)
recipes.loc[mask_empty_parse, "ingredient_source"] = recipes.loc[
    mask_empty_parse,
    INGREDIENT_COL_RAW
]

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
        raw_ingredient = clean_text(ing)

        if raw_ingredient != "":
            rows.append({
                "recipe_id": recipe_id,
                COUNTRY_COL: country,
                "raw_ingredient": raw_ingredient,
                "ingredient_key": clean_key(raw_ingredient)
            })

recipe_ingredients = pd.DataFrame(rows)

if recipe_ingredients.empty:
    raise ValueError("No ingredients were parsed from the recipe data.")

print("Unique countries after exploding ingredients:", recipe_ingredients[COUNTRY_COL].nunique())


# ------------------------------------------------------------------
# LOAD RAW → CLEANED INGREDIENT FILE
# ------------------------------------------------------------------

raw_clean_file = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\unique_raw_ingredients_cleaned_manual.csv"
)

raw_clean = pd.read_csv(raw_clean_file)

needed_cols = {"raw_ingredient", "clean_manual_flags_removed"}
missing = needed_cols - set(raw_clean.columns)
if missing:
    raise ValueError(f"Raw-clean file is missing columns: {missing}")

raw_clean = raw_clean[["raw_ingredient", "clean_manual_flags_removed"]].copy()

# raw_ingredient must match the exploded raw recipe ingredient.
raw_clean["raw_ingredient"] = raw_clean["raw_ingredient"].apply(clean_text)
raw_clean["raw_ingredient_key"] = raw_clean["raw_ingredient"].apply(clean_key)

# clean_manual_flags_removed is the common/simple ingredient name that matches temp_list.
raw_clean["clean_manual_flags_removed"] = (
    raw_clean["clean_manual_flags_removed"]
    .apply(clean_text)
    .str.casefold()
    .str.replace(r"\s+", " ", regex=True)
)

raw_clean.loc[
    raw_clean["clean_manual_flags_removed"].isin(["", "nan", "none"]),
    "clean_manual_flags_removed"
] = pd.NA

raw_clean = raw_clean.loc[raw_clean["raw_ingredient_key"] != ""].copy()

# Guard against duplicate raw ingredient rows.
n_duplicate_raw_keys = raw_clean["raw_ingredient_key"].duplicated().sum()
if n_duplicate_raw_keys > 0:
    print(f"\nWarning: {n_duplicate_raw_keys} duplicate raw ingredient keys in raw-clean file.")
    print("Keeping the first cleaned value for each raw ingredient key.")
    raw_clean = raw_clean.drop_duplicates(subset=["raw_ingredient_key"], keep="first")


# ------------------------------------------------------------------
# LOAD CLEANED INGREDIENT → CATEGORY/CANONICAL FILE
# ------------------------------------------------------------------

canonical_map = pd.read_csv(ingredient_category_file)

needed_cols = {"ingredient", "category", "canonical_ingredient"}
missing = needed_cols - set(canonical_map.columns)
if missing:
    raise ValueError(f"Canonical file is missing columns: {missing}")

canonical_map = canonical_map[["ingredient", "category", "canonical_ingredient"]].copy()

canonical_map["ingredient"] = (
    canonical_map["ingredient"]
    .apply(clean_text)
    .str.casefold()
    .str.replace(r"\s+", " ", regex=True)
)
canonical_map["category"] = canonical_map["category"].apply(clean_text)
canonical_map["canonical_ingredient"] = (
    canonical_map["canonical_ingredient"]
    .apply(clean_text)
    .str.casefold()
    .str.replace(r"\s+", " ", regex=True)
)

canonical_map = canonical_map.loc[canonical_map["ingredient"] != ""].copy()

n_duplicate_ingredient_keys = canonical_map["ingredient"].duplicated().sum()
if n_duplicate_ingredient_keys > 0:
    print(f"\nWarning: {n_duplicate_ingredient_keys} duplicate ingredient keys in canonical file.")
    print("Keeping the first category/canonical mapping for each ingredient.")
    canonical_map = canonical_map.drop_duplicates(subset=["ingredient"], keep="first")


# ------------------------------------------------------------------
# CREATE FINAL MAPPING:
# raw recipe ingredient → cleaned common ingredient → category/canonical
# ------------------------------------------------------------------

mapping = raw_clean.merge(
    canonical_map,
    left_on="clean_manual_flags_removed",
    right_on="ingredient",
    how="left",
    validate="many_to_one"
)


# ------------------------------------------------------------------
# MERGE CATEGORY AND CANONICAL INGREDIENT BACK TO EACH RECIPE INGREDIENT
# ------------------------------------------------------------------

recipe_ingredients = recipe_ingredients.merge(
    mapping[[
        "raw_ingredient_key",
        "clean_manual_flags_removed",
        "ingredient",
        "category",
        "canonical_ingredient"
    ]],
    left_on="ingredient_key",
    right_on="raw_ingredient_key",
    how="left",
    validate="many_to_one"
)

recipe_ingredients["category"] = recipe_ingredients["category"].replace("", pd.NA).fillna("unmatched")
recipe_ingredients["canonical_ingredient"] = (
    recipe_ingredients["canonical_ingredient"]
    .replace("", pd.NA)
    .fillna("unmatched")
)

# Clear indicator showing whether the raw ingredient ultimately matched temp_list.csv.
recipe_ingredients["matched_mapping"] = recipe_ingredients["category"].ne("unmatched")

# Backward-compatible alias, useful if you reuse old code snippets.
recipe_ingredients["broad_category_final"] = recipe_ingredients["category"]

# Match diagnostics.
total_ingredients = len(recipe_ingredients)
matched_ingredients = int(recipe_ingredients["matched_mapping"].sum())
unmatched_ingredients = total_ingredients - matched_ingredients

print("\nMATCH SHARE")
print(f"Total ingredient rows: {total_ingredients:,}")
print(f"Matched ingredient rows: {matched_ingredients:,}")
print(f"Unmatched ingredient rows: {unmatched_ingredients:,}")
print(f"Share matched: {matched_ingredients / total_ingredients:.2%}")

# ------------------------------------------------------------------
# COUNTRY-LEVEL SHARES: CATEGORY AND CANONICAL INGREDIENT
# ------------------------------------------------------------------

country_category, country_category_wide = build_country_shares(
    recipe_ingredients,
    group_col="category",
    value_label="category"
)

country_canonical, country_canonical_wide = build_country_shares(
    recipe_ingredients,
    group_col="canonical_ingredient",
    value_label="canonical"
)

country_category = add_recipe_counts(country_category, recipes)
country_canonical = add_recipe_counts(country_canonical, recipes)
country_category_wide = add_recipe_counts(country_category_wide, recipes)
country_canonical_wide = add_recipe_counts(country_canonical_wide, recipes)


# ------------------------------------------------------------------
# SAVE MAIN OUTPUTS
# ------------------------------------------------------------------

recipe_ingredients.to_csv(long_output_csv, index=False, encoding="utf-8-sig")
country_category.to_csv(country_category_output_csv, index=False, encoding="utf-8-sig")
country_category_wide.to_csv(country_category_wide_output_csv, index=False, encoding="utf-8-sig")
country_canonical.to_csv(country_canonical_output_csv, index=False, encoding="utf-8-sig")
country_canonical_wide.to_csv(country_canonical_wide_output_csv, index=False, encoding="utf-8-sig")

unmatched_raw = (
    recipe_ingredients
    .loc[~recipe_ingredients["matched_mapping"], "raw_ingredient"]
    .value_counts()
    .rename_axis("raw_ingredient")
    .reset_index(name="count")
)
unmatched_raw.to_csv(unmatched_ingredient_output_csv, index=False, encoding="utf-8-sig")


# ------------------------------------------------------------------
# DIAGNOSTICS
# ------------------------------------------------------------------

print("\nDone creating category/canonical outputs.")

print(f"\nLong recipe-ingredient file saved to:\n{long_output_csv}")
print(f"\nCountry-category shares saved to:\n{country_category_output_csv}")
print(f"\nWide country-category shares saved to:\n{country_category_wide_output_csv}")
print(f"\nCountry-canonical shares saved to:\n{country_canonical_output_csv}")
print(f"\nWide country-canonical shares saved to:\n{country_canonical_wide_output_csv}")
print(f"\nUnmatched raw ingredients saved to:\n{unmatched_ingredient_output_csv}")

print("\nUnique countries in final country-category file:")
print(country_category[COUNTRY_COL].nunique())

print("\nUnmatched ingredient rows:")
print((recipe_ingredients["category"] == "unmatched").sum())

print("\nCategory counts:")
print(recipe_ingredients["category"].value_counts(dropna=False).to_string())

print("\nTop 50 canonical ingredients:")
print(recipe_ingredients["canonical_ingredient"].value_counts(dropna=False).head(50).to_string())

print("\nCountries with zero parsed ingredients:")
zero_parsed = (
    recipes
    .groupby(COUNTRY_COL)["n_parsed_ingredients"]
    .sum()
    .loc[lambda x: x == 0]
)
print(zero_parsed.to_string())


# ------------------------------------------------------------------
# K-MEANS CLUSTERING OF COUNTRIES BY CANONICAL INGREDIENT SHARES
# ------------------------------------------------------------------

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import normalize

# Use only canonical ingredient shares, excluding unmatched and metadata.
feature_df = country_canonical_wide.copy()

# Remove low-recipe countries from clustering but leave them in main output tables.
feature_df = feature_df.loc[feature_df["n_recipes"] > MIN_RECIPES].copy()

metadata_cols = {COUNTRY_COL, "n_recipes", "unmatched"}
feature_cols = [c for c in feature_df.columns if c not in metadata_cols]

if len(feature_df) < N_CLUSTERS:
    raise ValueError(
        f"Only {len(feature_df)} countries have more than {MIN_RECIPES} recipes; "
        f"cannot estimate {N_CLUSTERS} clusters."
    )

X = feature_df[feature_cols].fillna(0).to_numpy()

# Normalize each country vector to unit length so k-means uses similarity in composition
# rather than overall ingredient count scale. Since these are shares, this mainly makes
# the clustering closer to cosine-similarity clustering.
X_norm = normalize(X, norm="l2", axis=1)

kmeans = KMeans(
    n_clusters=N_CLUSTERS,
    random_state=RANDOM_STATE,
    n_init=50
)

feature_df["canonical_kmeans_cluster"] = kmeans.fit_predict(X_norm) + 1

# Optional diagnostic; silhouette requires at least 2 clusters and fewer clusters than rows.
if 1 < N_CLUSTERS < len(feature_df):
    sil = silhouette_score(X_norm, feature_df["canonical_kmeans_cluster"])
    print(f"\nSilhouette score for {N_CLUSTERS} canonical-ingredient clusters: {sil:.3f}")

cluster_output = feature_df[[COUNTRY_COL, "n_recipes", "canonical_kmeans_cluster"]].copy()

# Add top canonical ingredients per country to make clusters interpretable.
top_n = 10
country_top_ingredients = []

for _, row in feature_df.iterrows():
    country = row[COUNTRY_COL]
    shares = row[feature_cols].sort_values(ascending=False)
    top_items = [f"{idx}: {val:.3f}" for idx, val in shares.head(top_n).items() if val > 0]
    country_top_ingredients.append({
        COUNTRY_COL: country,
        f"top_{top_n}_canonical_ingredients": "; ".join(top_items)
    })

cluster_output = cluster_output.merge(
    pd.DataFrame(country_top_ingredients),
    on=COUNTRY_COL,
    how="left"
)

cluster_output.to_csv(cluster_output_csv, index=False, encoding="utf-8-sig")

print(f"\nCountry k-means clusters saved to:\n{cluster_output_csv}")
print("\nCluster sizes:")
print(cluster_output["canonical_kmeans_cluster"].value_counts().sort_index().to_string())


# ------------------------------------------------------------------
# MAPS: CATEGORY SHARES AND SELECT CANONICAL INGREDIENT FREQUENCIES
# ------------------------------------------------------------------

import geopandas as gpd  # noqa: F401 imported here so missing install fails before map loop

world = load_world_map()
world_names = make_world_name_crosswalk(world)

# Harmonize names for map matching.
country_category_map = harmonize_country_names(country_category)
country_canonical_map = harmonize_country_names(country_canonical)
cluster_map = harmonize_country_names(cluster_output)

report_map_matches(country_category_map, world_names)


# ------------------------------------------------------------------
# MAP CATEGORY SHARES
# ------------------------------------------------------------------

map_dir = output_dir / "maps_categories"
map_dir.mkdir(parents=True, exist_ok=True)

country_category_map.loc[
    country_category_map["n_recipes"] <= MIN_RECIPES,
    "share_excluding_unmatched"
] = pd.NA

categories_to_plot = sorted(
    country_category_map.loc[
        country_category_map["category"].notna()
        & ~country_category_map["category"].isin(["unmatched"]),
        "category"
    ].unique()
)

for cat in categories_to_plot:
    cat_df = country_category_map.loc[
        country_category_map["category"].eq(cat),
        [COUNTRY_COL, "country_map", "share_excluding_unmatched", "n_recipes"]
    ].copy()

    output_map = map_dir / f"map_category_{safe_filename(cat)}_quantiles.png"


    

    plot_share_map(
        country_df=cat_df,
        world=world,
        world_names=world_names,
        value_col="share_excluding_unmatched",
        title=f"Share of matched ingredients in category: {cat}",
        output_png=output_map
    )


# ------------------------------------------------------------------
# MAP SELECT CANONICAL INGREDIENT FREQUENCIES: RICE, MILK, POTATO
# ------------------------------------------------------------------

canonical_map_dir = output_dir / "maps_canonical_ingredients"
canonical_map_dir.mkdir(parents=True, exist_ok=True)

country_canonical_map.loc[
    country_canonical_map["n_recipes"] <= MIN_RECIPES,
    "share_excluding_unmatched"
] = pd.NA

for canonical in CANONICAL_INGREDIENTS_TO_MAP:
    canonical_key = canonical.casefold()

    ing_df = country_canonical_map.loc[
        country_canonical_map["canonical_ingredient"].str.casefold().eq(canonical_key),
        [COUNTRY_COL, "country_map", "share_excluding_unmatched", "n_recipes"]
    ].copy()

    # Add countries with zero use of this canonical ingredient, so they map as 0 rather than missing.
    all_countries = (
        country_canonical_map[[COUNTRY_COL, "country_map", "n_recipes"]]
        .drop_duplicates()
    )

    ing_df = all_countries.merge(
        ing_df[[COUNTRY_COL, "share_excluding_unmatched"]],
        on=COUNTRY_COL,
        how="left"
    )

    ing_df["share_excluding_unmatched"] = ing_df["share_excluding_unmatched"].fillna(0)

    # But keep low-recipe countries as missing/no data.
    ing_df.loc[ing_df["n_recipes"] <= MIN_RECIPES, "share_excluding_unmatched"] = pd.NA

    output_map = canonical_map_dir / f"map_canonical_{safe_filename(canonical)}_quantiles.png"

    plot_share_map(
        country_df=ing_df,
        world=world,
        world_names=world_names,
        value_col="share_excluding_unmatched",
        title=f"Share of matched ingredients that are canonical ingredient: {canonical}",
        output_png=output_map
    )


# ------------------------------------------------------------------
# OPTIONAL: MAP K-MEANS CLUSTERS
# ------------------------------------------------------------------

cluster_map_dir = output_dir / "maps_clusters"
cluster_map_dir.mkdir(parents=True, exist_ok=True)

cluster_plot = cluster_map.merge(
    world_names[["world_index", "country_key"]].drop_duplicates(),
    on="country_key",
    how="left"
)
cluster_plot = cluster_plot.dropna(subset=["world_index"])
cluster_plot = cluster_plot.groupby("world_index", as_index=False)["canonical_kmeans_cluster"].first()

map_df = world.reset_index().rename(columns={"index": "world_index"}).merge(
    cluster_plot,
    on="world_index",
    how="left"
)

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(14, 8))
map_df.plot(
    column="canonical_kmeans_cluster",
    categorical=True,
    legend=True,
    ax=ax,
    edgecolor="black",
    linewidth=0.25,
    missing_kwds={
        "color": "lightgrey",
        "edgecolor": "black",
        "hatch": "///",
        "label": "No data"
    },
    legend_kwds={
        "loc": "lower left"
    }
)
ax.set_title(f"K-means clusters of countries by canonical ingredient shares, k={N_CLUSTERS}", fontsize=16)
ax.axis("off")
plt.tight_layout()
cluster_map_png = cluster_map_dir / f"map_canonical_ingredient_kmeans_k{N_CLUSTERS}.png"
plt.savefig(cluster_map_png, dpi=300)
plt.close()
print(f"Saved cluster map: {cluster_map_png}")
