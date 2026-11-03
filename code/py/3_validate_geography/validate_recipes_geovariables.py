# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 14:54:58 2026

@author: stevebc
"""

# -*- coding: utf-8 -*-
"""
Cuisine Diversity, Fractionalization, and Fish/Seafood vs Bounty of the Sea
"""

import ast
import re
import warnings
from collections import Counter
from itertools import combinations
from pathlib import Path
from random import sample, seed

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from adjustText import adjust_text
from scipy import stats

warnings.filterwarnings("ignore", category=FutureWarning)

# ------------------------------------------------------------------
# FILE PATHS
# ------------------------------------------------------------------

STATA_FILE = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\recipe_all_countries_web.dta"
)
CANONICAL_FILE = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\ChatGPT_output\ingredient_batch100\ingredient_all.csv"
)
RAW_CLEAN_FILE = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\unique_raw_ingredients_cleaned_manual.csv"
)
BOUNTY_PATH = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\raw\bounty_sea"
    r"\BountyOfTheSea_DataForTheWeb\data_03_crosscountry.dta"
)

# Landcover classes for shrubs and grassland


# TODO: change to Dropbox\food4thought\analysis23\data\raw\landcover
RASTER_5 = Path(r"C:\Users\stevebc\Downloads\consensus_full_class_5.tif")
RASTER_6 = Path(r"C:\Users\stevebc\Downloads\consensus_full_class_6.tif")
RASTER_7 = Path(r"C:\Users\stevebc\Downloads\consensus_full_class_7.tif")

# TODO: change to Dropbox\food4thought\analysis23\data\raw\livestock
RASTER_CATTLE = Path(r"C:\Users\stevebc\Downloads\GLW4-2020.D-DA.CTL.tif")
RASTER_SHEEP  = Path(r"C:\Users\stevebc\Downloads\GLW4-2020.D-DA.SHP.tif")
RASTER_PIGS   = Path(r"C:\Users\stevebc\Downloads\GLW4-2020.D-DA.PGS.tif")

# TODO: change output path
OUTPUT_DIR = Path(
    r"C:\Users\stevebc\Dropbox\Cuisine_complexity\3_results\temp"
)

# ------------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------------

COUNTRY_COL           = "country"
INGREDIENT_ENG        = "listofingredients_eng"
INGREDIENT_RAW        = "listofingredients"
MIN_RECIPES           = 10
MAX_PAIRS_PER_COUNTRY = 500
RANDOM_SEED           = 42

SUIT_VARS    = ["aasuit50_mfish", "suit50_mfish"]
COASTAL_VARS = ["coastland50", "coastland100", "distcr"]

NAME_TO_ISO3 = {
    "Afghanistan": "AFG", "Albania": "ALB", "Algeria": "DZA",
    "Argentina": "ARG", "Armenia": "ARM", "Australia": "AUS",
    "Austria": "AUT", "Azerbaijan": "AZE",
    "Bangladesh": "BGD", "Belarus": "BLR", "Belgium": "BEL",
    "Bolivia": "BOL", "Bosnia and Herzegovina": "BIH",
    "Bosnia & Herzegovina": "BIH", "Botswana": "BWA", "Brazil": "BRA",
    "Bulgaria": "BGR",
    "Cambodia": "KHM", "Cameroon": "CMR", "Canada": "CAN",
    "Chile": "CHL", "China": "CHN", "Colombia": "COL",
    "Costa Rica": "CRI", "Croatia": "HRV", "Czech Republic": "CZE",
    "Czechia": "CZE",
    "Denmark": "DNK", "Dominican Republic": "DOM",
    "Ecuador": "ECU", "Egypt": "EGY", "El Salvador": "SLV",
    "Estonia": "EST", "Ethiopia": "ETH",
    "Finland": "FIN", "France": "FRA",
    "Georgia": "GEO", "Germany": "DEU", "Ghana": "GHA",
    "Greece": "GRC", "Guatemala": "GTM",
    "Haiti": "HTI", "Honduras": "HND", "Hungary": "HUN",
    "India": "IND", "Indonesia": "IDN", "Iran": "IRN",
    "Iraq": "IRQ", "Ireland": "IRL", "Israel": "ISR", "Italy": "ITA",
    "Jamaica": "JAM", "Japan": "JPN", "Jordan": "JOR",
    "Kazakhstan": "KAZ", "Kenya": "KEN", "Kosovo": "XKX", "Kyrgyzstan": "KGZ",
    "Latvia": "LVA", "Lithuania": "LTU",
    "Malawi": "MWI", "Malaysia": "MYS", "Mali": "MLI",
    "Mexico": "MEX", "Moldova": "MDA", "Morocco": "MAR", "Mozambique": "MOZ",
    "Nepal": "NPL", "Netherlands": "NLD", "New Zealand": "NZL",
    "Nicaragua": "NIC", "Niger": "NER", "Nigeria": "NGA", "Norway": "NOR",
    "Pakistan": "PAK", "Panama": "PAN", "Paraguay": "PRY",
    "Peru": "PER", "Philippines": "PHL", "Poland": "POL",
    "Portugal": "PRT", "Romania": "ROU", "Russia": "RUS", "Rwanda": "RWA",
    "Saudi Arabia": "SAU", "Senegal": "SEN", "Serbia": "SRB",
    "Slovakia": "SVK", "Slovenia": "SVN", "South Africa": "ZAF",
    "South Korea": "KOR", "Korea, Republic of": "KOR",
    "Republic of Korea": "KOR", "Korea": "KOR",
    "Spain": "ESP", "Sri Lanka": "LKA", "Sudan": "SDN",
    "Suriname": "SUR", "Sweden": "SWE", "Switzerland": "CHE",
    "Tanzania": "TZA", "Thailand": "THA", "Tunisia": "TUN",
    "Turkey": "TUR", "Turkiye": "TUR",
    "Uganda": "UGA", "Ukraine": "UKR",
    "United Kingdom": "GBR", "UK": "GBR",
    "United States": "USA", "United States of America": "USA", "USA": "USA",
    "Uruguay": "URY",
    "Venezuela": "VEN", "Vietnam": "VNM", "Viet Nam": "VNM",
    "Zambia": "ZMB", "Zimbabwe": "ZWE",
}

def to_iso3(series):
    def _convert(val):
        if not isinstance(val, str):
            return np.nan
        v = val.strip()
        if len(v) <= 3 and v.isupper():
            return v
        return NAME_TO_ISO3.get(v, NAME_TO_ISO3.get(v.title(), np.nan))
    return series.map(_convert)

# ------------------------------------------------------------------
# HELPERS
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

def clean_text(x):
    if x is None:
        return ""
    if isinstance(x, (list, tuple)):
        x = " ".join(str(i) for i in x)
    try:
        if pd.isna(x):
            return ""
    except Exception:
        pass
    return re.sub(r"\s+", " ", str(x).strip())

def clean_key(x):
    return clean_text(x).casefold()

# ===========================================================================
# LOAD RECIPE DATA
# ===========================================================================

print("Loading recipe Stata file ...")
recipes = pd.read_stata(STATA_FILE)
recipes = recipes.reset_index(drop=True)
recipes["recipe_id"] = recipes.index + 1

recipes["ingredient_source"] = recipes[INGREDIENT_ENG]
mask_na    = recipes["ingredient_source"].isna()
recipes.loc[mask_na, "ingredient_source"] = recipes.loc[mask_na, INGREDIENT_RAW]
parsed_len = recipes["ingredient_source"].apply(parse_ingredient_list).apply(len)
mask_empty = parsed_len.eq(0)
recipes.loc[mask_empty, "ingredient_source"] = recipes.loc[mask_empty, INGREDIENT_RAW]
recipes["parsed_ingredients"] = recipes["ingredient_source"].apply(parse_ingredient_list)
print(f"  Loaded {len(recipes):,} recipes from {recipes[COUNTRY_COL].nunique()} countries")

# ===========================================================================
# LOAD & BUILD CANONICAL MAPPING
# ===========================================================================

print("Building canonical ingredient mapping ...")

raw_clean = pd.read_csv(RAW_CLEAN_FILE)
raw_clean["raw_ingredient"]     = raw_clean["raw_ingredient"].apply(clean_text)
raw_clean["raw_ingredient_key"] = raw_clean["raw_ingredient"].apply(clean_key)
raw_clean["clean_manual_flags_removed"] = (
    raw_clean["clean_manual_flags_removed"]
    .apply(clean_text).str.casefold()
    .str.replace(r"\s+", " ", regex=True)
)
raw_clean.loc[
    raw_clean["clean_manual_flags_removed"].isin(["", "nan", "none"]),
    "clean_manual_flags_removed"
] = pd.NA
raw_clean = raw_clean.loc[raw_clean["raw_ingredient_key"] != ""]
raw_clean = raw_clean.drop_duplicates(subset=["raw_ingredient_key"], keep="first")

canonical_map = pd.read_csv(CANONICAL_FILE)
canonical_map["ingredient"] = (
    canonical_map["ingredient"].apply(clean_text).str.casefold()
    .str.replace(r"\s+", " ", regex=True)
)
canonical_map["canonical_ingredient"] = (
    canonical_map["canonical_ingredient"].apply(clean_text).str.casefold()
    .str.replace(r"\s+", " ", regex=True)
)
canonical_map = canonical_map.drop_duplicates(subset=["ingredient"], keep="first")

mapping = raw_clean.merge(
    canonical_map[["ingredient", "canonical_ingredient"]],
    left_on="clean_manual_flags_removed", right_on="ingredient", how="left"
)
raw_to_canonical = dict(zip(mapping["raw_ingredient_key"], mapping["canonical_ingredient"]))

# ===========================================================================
# BUILD RECIPE x CANONICAL-INGREDIENT TABLE
# ===========================================================================

print("Exploding ingredients and mapping to canonical ...")

rows = []
for _, row in recipes.iterrows():
    country   = row[COUNTRY_COL]
    recipe_id = row["recipe_id"]
    canonicals = set()
    for ing in row["parsed_ingredients"]:
        key = clean_key(clean_text(ing))
        can = raw_to_canonical.get(key)
        if can and can != "unmatched" and not pd.isna(can):
            canonicals.add(can)
    if canonicals:
        rows.append({
            "recipe_id":     recipe_id,
            COUNTRY_COL:     country,
            "canonical_set": frozenset(canonicals),
            "n_canonical":   len(canonicals),
        })

recipe_canonical = pd.DataFrame(rows)
print(f"  {len(recipe_canonical):,} recipes with >=1 matched canonical ingredient")

n_per_country = recipe_canonical.groupby(COUNTRY_COL).size().rename("n_recipes")
eligible      = n_per_country[n_per_country >= MIN_RECIPES].index
recipe_canonical = recipe_canonical[recipe_canonical[COUNTRY_COL].isin(eligible)].copy()
print(f"  {recipe_canonical[COUNTRY_COL].nunique()} countries with >={MIN_RECIPES} recipes")

# ===========================================================================
# FISH/SEAFOOD RECIPE FREQUENCY SHARE
# ===========================================================================

print("\nComputing fish/seafood recipe share ...")

#fish_canonicals = {"crab", "marine"}
fish_canonicals = {"marine"}
#fish_canonicals = {"crab", "marine", "freshwater"}
print(f"  Fish canonicals: {fish_canonicals}")

recipe_canonical["has_fish"] = recipe_canonical["canonical_set"].apply(
    lambda s: int(bool(s & fish_canonicals))
)

country_fish_share = (
    recipe_canonical.groupby(COUNTRY_COL)["has_fish"]
    .mean()
    .rename("fish_recipe_share")
    .reset_index()
)
print(f"  Fish recipe share computed for {len(country_fish_share)} countries")
print(country_fish_share.sort_values("fish_recipe_share", ascending=False).head(10).to_string(index=False))

# ===========================================================================
# LOAD BOUNTY OF THE SEA DATA
# ===========================================================================

print("\nLoading Bounty of the Sea data ...")
bounty_raw = pd.read_stata(BOUNTY_PATH)
bounty_raw["adm0"] = bounty_raw["code"].str.strip().str.upper()
bounty_raw["adm0"] = bounty_raw["adm0"].replace({"ROM": "ROU", "SCG": "SRB", "YUG": "SRB"})

all_vars  = list(set(SUIT_VARS + COASTAL_VARS))
available = [v for v in all_vars if v in bounty_raw.columns]
missing   = [v for v in all_vars if v not in bounty_raw.columns]
if missing:
    print(f"  WARNING — not found: {missing}")

bounty = (bounty_raw.dropna(subset=["adm0"])
                    .drop_duplicates(subset="adm0")
                    .set_index("adm0")[available])

if "distcr" in bounty.columns:
    bounty["distcr"] = 1.0 / bounty["distcr"].replace(0, np.nan)

print(f"  Countries with bounty data: {len(bounty)}")

# ===========================================================================
# MERGE FISH SHARE + BOUNTY
# ===========================================================================

# Convert country names to ISO3
fish_iso = country_fish_share.copy()
fish_iso["adm0"] = to_iso3(fish_iso[COUNTRY_COL])
fish_iso = fish_iso.dropna(subset=["adm0"]).set_index("adm0")

df = fish_iso[["fish_recipe_share"]].join(bounty, how="inner")
print(f"  Countries after merge: {len(df)}")
print(f"  In fish but not bounty: {sorted(set(fish_iso.index) - set(bounty.index))}")



# ===========================================================================
# FIGURE 1: BINSCATTER — coastland50 vs fish share
# ===========================================================================

# Build fish_coast from full recipe country set
fish_coast = country_fish_share.copy()
fish_coast["adm0"] = to_iso3(fish_coast[COUNTRY_COL])
fish_coast = fish_coast.dropna(subset=["adm0"]).set_index("adm0")
fish_coast = fish_coast.join(bounty[["coastland50"]], how="inner")
print(f"  Countries for binscatter: {len(fish_coast)}")

fig, ax = plt.subplots(figsize=(8, 5))

bin_data = fish_coast[["fish_recipe_share", "coastland50"]].dropna().copy()
n_bins = 6
bin_data["bin"] = pd.qcut(bin_data["coastland50"], q=n_bins, duplicates="drop")

binned = bin_data.groupby("bin", observed=True).agg(
    x_mid=("coastland50", "mean"),
    y_mean=("fish_recipe_share", "mean"),
    n=("fish_recipe_share", "count")
).reset_index()
print(binned[["bin", "x_mid", "y_mean", "n"]].to_string())

ax.scatter(binned["x_mid"], binned["y_mean"] * 100,
           s=80, alpha=0.85, color="#2171b5",
           edgecolors="white", linewidths=0.4, zorder=3)

for _, row in binned.iterrows():
    ax.annotate(f"n={int(row['n'])}", (row["x_mid"], row["y_mean"] * 100),
                fontsize=7, color="#555555", ha="center",
                xytext=(0, 8), textcoords="offset points")

ax.plot(binned["x_mid"], binned["y_mean"] * 100,
        color="#e63946", linewidth=1.2, alpha=0.6, zorder=2)

ax.set_xlabel("% land within 50 km of coast (bin mean)", fontsize=10)
ax.set_ylabel("Seafood recipe share (%)", fontsize=10)
ax.set_title(
    f"Binscatter: seafood recipe share vs. coastal access\n"
    f"({n_bins} quantile bins, positioned at bin mean)",
    fontsize=9
)
ax.tick_params(labelsize=8)
ax.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
out_binscatter = OUTPUT_DIR / "binscatter_fish_vs_coastland50.pdf"
plt.savefig(out_binscatter, dpi=150, bbox_inches="tight")
plt.savefig(str(out_binscatter).replace(".pdf", ".png"), dpi=150, bbox_inches="tight")
print(f"  Saved → {out_binscatter}")
plt.show()

# ===========================================================================
# FIGURE 2: SCATTER — suit50_mfish × coastland50 (Box-Cox) vs fish share
# ===========================================================================

from scipy.stats import boxcox

fig, ax = plt.subplots(figsize=(8, 6))

suit = "suit50_mfish"
sub = df[["fish_recipe_share", suit, "coastland50"]].dropna().copy()
sub["composite_raw"] = sub[suit] * sub["coastland50"]
sub = sub[sub["composite_raw"] > 0]
sub["composite"], lambda_bc = boxcox(sub["composite_raw"])

r_val, p_val = stats.pearsonr(sub["composite"], sub["fish_recipe_share"])

ax.scatter(sub["composite"], sub["fish_recipe_share"] * 100,
           s=35, alpha=0.65, edgecolors="white", linewidths=0.3, color="#2171b5")

for adm0, row in sub.iterrows():
    ax.annotate(adm0, (row["composite"], row["fish_recipe_share"] * 100),
                fontsize=5.5, color="#555555", xytext=(2, 2), textcoords="offset points")

m, b_coef = np.polyfit(sub["composite"], sub["fish_recipe_share"] * 100, 1)
x_line = np.linspace(sub["composite"].min(), sub["composite"].max(), 200)
ax.plot(x_line, m * x_line + b_coef, color="#e63946", linewidth=1.5, zorder=3)

ax.set_xlabel("Fish suitability × coastal land share (Box-Cox transformed)", fontsize=10)
ax.set_ylabel("Seafood in recipe share (%)", fontsize=10)
ax.set_title(f"r = {r_val:.3f}, p = {p_val:.3f}  (n = {len(sub)})", fontsize=10)
ax.tick_params(labelsize=8)
ax.spines[["top", "right"]].set_visible(False)


plt.tight_layout()
out_fig = OUTPUT_DIR / "scatter_fish_vs_suitability.pdf"
plt.savefig(out_fig, dpi=150, bbox_inches="tight")
plt.savefig(str(out_fig).replace(".pdf", ".png"), dpi=150, bbox_inches="tight")
print(f"  Saved → {out_fig}")
plt.show()













# ===========================================================================
# FIGURE 3-8: GRASSLAND vs MEAT/MUTTON RECIPE SHARE
# ===========================================================================

print("\nComputing meat/mutton recipe shares ...")

beef_canonicals   = {"beef"}
mutton_canonicals = {"mutton"}
pork_canonicals = {"pork"}
dairy_canonicals = {"butter", "cheese", "cream", "ghee", "kefir", "milk", "yogurt"}
beef_mutton_canonicals = beef_canonicals | mutton_canonicals  # combined set
beef_pork_canonicals = beef_canonicals | pork_canonicals       # new combined set
beef_dairy_canonicals = beef_canonicals | dairy_canonicals     # new combined set
meat_canonicals =   beef_canonicals | mutton_canonicals | pork_canonicals

recipe_canonical["has_beef"]   = recipe_canonical["canonical_set"].apply(
    lambda s: int(bool(s & beef_canonicals))
)
recipe_canonical["has_mutton"] = recipe_canonical["canonical_set"].apply(
    lambda s: int(bool(s & mutton_canonicals))
)
recipe_canonical["has_beef_mutton"] = recipe_canonical["canonical_set"].apply(
    lambda s: int(bool(s & beef_mutton_canonicals))
)
recipe_canonical["has_beef_pork"] = recipe_canonical["canonical_set"].apply(
    lambda s: int(bool(s & beef_pork_canonicals))
)
recipe_canonical["has_beef_dairy"] = recipe_canonical["canonical_set"].apply(
    lambda s: int(bool(s & beef_dairy_canonicals))
)
recipe_canonical["has_meat"] = recipe_canonical["canonical_set"].apply(
    lambda s: int(bool(s & meat_canonicals))
)
recipe_canonical["has_pork"] = recipe_canonical["canonical_set"].apply(
    lambda s: int(bool(s & pork_canonicals))
)

country_meat_share = (
    recipe_canonical.groupby(COUNTRY_COL)[["has_beef", "has_mutton", "has_beef_mutton", "has_beef_pork", "has_beef_dairy", "has_meat", "has_pork"]]
    .mean()
    .rename(columns={
        "has_beef": "beef_recipe_share",
        "has_mutton": "mutton_recipe_share",
        "has_beef_mutton": "beef_mutton_recipe_share",
        "has_beef_pork": "beef_pork_recipe_share",
        "has_beef_dairy": "beef_dairy_recipe_share",
        "has_meat": "meat_recipe_share",
        "has_pork": "pork_recipe_share",
    })
    .reset_index()
)

print(country_meat_share.sort_values("beef_recipe_share", ascending=False).head(10).to_string(index=False))

# ------------------------------------------------------------------
# Extract raster means by country
# ------------------------------------------------------------------

import rasterio
from rasterio.mask import mask as rio_mask
import urllib.request
import geopandas as gpd

ne_local = Path(r"C:\Users\stevebc\Dropbox\food4thought\analysis23\outputs\Figures\ethnographic\fractionalization\ne_110m_admin_0_countries.zip")
world = gpd.read_file(f"zip://{ne_local}")

iso_col = next(c for c in ["ISO_A3", "ADM0_A3", "ISO_A3_EH"] if c in world.columns)
print(f"  Using ISO column: {iso_col}")

def extract_raster_mean_by_country(raster_path, world_gdf, iso_col):
    """Return a Series: ISO3 -> mean raster value (ignoring nodata)."""
    results = {}
    with rasterio.open(raster_path) as src:
        nodata = src.nodata
        for _, row in world_gdf.iterrows():
            iso3 = row[iso_col]
            if not isinstance(iso3, str) or iso3 == "-99":
                continue
            geom = [row["geometry"]]
            try:
                out_image, _ = rio_mask(src, geom, crop=True)
                data = out_image.astype(float).flatten()
                if nodata is not None:
                    data = data[data != nodata]
                data = data[np.isfinite(data)]
                if len(data) > 0:
                    results[iso3] = data.mean()
            except Exception:
                pass
    return pd.Series(results)

print("  Extracting class_6 raster ...")
class6_mean = extract_raster_mean_by_country(RASTER_6, world, iso_col).rename("class6_mean")

print("  Extracting class_7 raster ...")
class7_mean = extract_raster_mean_by_country(RASTER_7, world, iso_col).rename("class7_mean")

grassland = pd.DataFrame({
    "class6_mean": class6_mean,
    "class7_mean": class7_mean,
})
grassland["class67_sum"] = grassland["class6_mean"] + grassland["class7_mean"]
print(f"  Raster extracted for {len(grassland)} countries")


print("  Extracting cattle density raster ...")
cattle_mean = extract_raster_mean_by_country(RASTER_CATTLE, world, iso_col).rename("cattle_density_mean")

print("  Extracting sheep density raster ...")
sheep_mean = extract_raster_mean_by_country(RASTER_SHEEP, world, iso_col).rename("sheep_density_mean")

print("  Extracting pig density raster ...")
pig_mean = extract_raster_mean_by_country(RASTER_PIGS, world, iso_col).rename("pig_density_mean")

livestock = pd.DataFrame({
    "cattle_density_mean": cattle_mean,
    "sheep_density_mean": sheep_mean,
    "pig_density_mean": pig_mean,
})
print(f"  Livestock density extracted for {len(livestock)} countries")

# ===========================================================================
# WORLD MAP: Grassland cover (class 6)
# ===========================================================================

print("\nGenerating world map of grassland cover (class 6) ...")

import geopandas as gpd
import matplotlib.colors as mcolors

ne_local_frac = Path(r"C:\Users\stevebc\Dropbox\food4thought\analysis23\outputs\Figures\ethnographic\fractionalization\ne_110m_admin_0_countries.zip")
world_map = gpd.read_file(f"zip://{ne_local_frac}")

iso_col_map = next(
    (c for c in ["ISO_A3", "ADM0_A3", "iso_a3", "ISO_A3_EH"]
     if c in world_map.columns), None
)

world_m = world_map.merge(
    grassland[["class6_mean"]].reset_index().rename(columns={"index": "iso3"}),
    left_on=iso_col_map, right_on="iso3", how="left"
)
if "CONTINENT" in world_m.columns:
    world_m = world_m[world_m["CONTINENT"] != "Antarctica"]
else:
    world_m = world_m[~world_m[iso_col_map].isin(["ATA"])]

fig, ax = plt.subplots(figsize=(16, 7))
ax.set_facecolor("#e8f0f7")

world_m[world_m["class6_mean"].isna()].plot(
    ax=ax, color="#cccccc", edgecolor="#aaaaaa", linewidth=0.3
)
world_m[world_m["class6_mean"].notna()].plot(
    column="class6_mean", ax=ax, cmap="YlGn", vmin=0, vmax=world_m["class6_mean"].quantile(0.95),
    edgecolor="#aaaaaa", linewidth=0.3, legend=False,
)

sm = plt.cm.ScalarMappable(
    cmap="YlGn",
    norm=mcolors.Normalize(vmin=0, vmax=world_m["class6_mean"].quantile(0.95))
)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, orientation="horizontal",
                    shrink=0.45, pad=0.02, fraction=0.03)
cbar.set_label("Grassland cover — country mean (class 6)", fontsize=13)
cbar.ax.tick_params(labelsize=11)

ax.set_title(
    "Grassland Cover (Class 6)\nCountry mean from consensus land cover",
    fontsize=14, pad=12,
)
ax.axis("off")
plt.tight_layout()

map_out = OUTPUT_DIR / "map_grassland_class6.png"
plt.savefig(map_out, dpi=150, bbox_inches="tight")
plt.savefig(str(map_out).replace(".png", ".pdf"), dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved → {map_out}")

# ===========================================================================
# WORLD MAP: Grassland cover (class 6) — raw raster with country borders
# ===========================================================================

print("\nGenerating raw raster map of grassland cover (class 6) ...")

import rasterio
from rasterio.plot import show as rioshow
import matplotlib.colors as mcolors

fig, ax = plt.subplots(figsize=(16, 7))
ax.set_facecolor("#e8f0f7")

with rasterio.open(RASTER_6) as src:
    # Aggressively downsample to 1000px wide to avoid memory crash
    target_width  = 2000
    scale         = target_width / src.width
    target_height = int(src.height * scale)
    
    data = src.read(
        1,
        out_shape=(1, target_height, target_width),
        resampling=rasterio.enums.Resampling.average
    ).astype(np.float32)  # float32 not float64 — halves memory
    
    nodata = src.nodata
    if nodata is not None:
        data[data == nodata] = np.nan
    data[data == 0] = np.nan
    
    vmax = np.nanpercentile(data, 95)
    extent = [src.bounds.left, src.bounds.right,
              src.bounds.bottom, src.bounds.top]

    im = ax.imshow(
        data,
        cmap="YlGn",
        vmin=0,
        vmax=vmax,
        extent=extent,
        aspect="auto",
        interpolation="nearest",
    )

# Overlay country borders
world_map.boundary.plot(ax=ax, linewidth=0.3, edgecolor="#aaaaaa")

cbar = fig.colorbar(im, ax=ax, orientation="horizontal",
                    shrink=0.45, pad=0.02, fraction=0.03)
cbar.set_label("Grassland cover — raw pixel value (class 6)", fontsize=13)
cbar.ax.tick_params(labelsize=11)

# ax.set_title(
#     "Grassland Cover (Class 6) — Raw Raster\nwith country borders",
#     fontsize=14, pad=12,
# )
ax.set_xlim(-180, 180)
ax.set_ylim(-60, 85)
ax.axis("off")
plt.tight_layout()

map_raw_out = OUTPUT_DIR / "map_grassland_class6_raw_raster.png"
plt.savefig(map_raw_out, dpi=150, bbox_inches="tight")
plt.savefig(str(map_raw_out).replace(".png", ".pdf"), dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved → {map_raw_out}")


# ------------------------------------------------------------------
# Extract TOTAL head count (area-weighted), for per-capita measures
# ------------------------------------------------------------------

def extract_raster_total_by_country(raster_path, world_gdf, iso_col):
    """Return a Series: ISO3 -> total head count (density * pixel area, summed)."""
    results = {}
    with rasterio.open(raster_path) as src:
        nodata = src.nodata
        transform = src.transform

        # pixel size in degrees (assumes geographic CRS, e.g. EPSG:4326)
        pixel_width_deg  = abs(transform.a)
        pixel_height_deg = abs(transform.e)

        for _, row in world_gdf.iterrows():
            iso3 = row[iso_col]
            if not isinstance(iso3, str) or iso3 == "-99":
                continue
            geom = [row["geometry"]]
            try:
                out_image, out_transform = rio_mask(src, geom, crop=True)
                data = out_image[0].astype(float)  # 2D array (rows, cols)

                if nodata is not None:
                    data[data == nodata] = np.nan

                n_rows, n_cols = data.shape
                row_indices = np.arange(n_rows)
                lats = out_transform.f + (row_indices + 0.5) * out_transform.e

                km_per_deg_lat = 111.32
                km_per_deg_lon = 111.32 * np.cos(np.radians(lats))

                pixel_area_km2 = (pixel_height_deg * km_per_deg_lat) * (pixel_width_deg * km_per_deg_lon)
                pixel_area_km2 = pixel_area_km2[:, np.newaxis]

                head_count = data * pixel_area_km2
                total = np.nansum(head_count)

                if np.isfinite(total) and total > 0:
                    results[iso3] = total
            except Exception:
                pass
    return pd.Series(results)

print("  Extracting cattle total head count ...")
cattle_total = extract_raster_total_by_country(RASTER_CATTLE, world, iso_col).rename("cattle_total")

print("  Extracting sheep total head count ...")
sheep_total = extract_raster_total_by_country(RASTER_SHEEP, world, iso_col).rename("sheep_total")

print("  Extracting pig total head count ...")
pig_total = extract_raster_total_by_country(RASTER_PIGS, world, iso_col).rename("pig_total")

livestock_totals = pd.DataFrame({
    "cattle_total": cattle_total,
    "sheep_total": sheep_total,
    "pig_total": pig_total,
})
print(f"  Livestock totals extracted for {len(livestock_totals)} countries")

# ------------------------------------------------------------------
# Pull World Bank population data
# ------------------------------------------------------------------

import requests

print("  Fetching World Bank population data ...")
pop_url = "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=20000&date=2020"
pop_resp = requests.get(pop_url)
pop_json = pop_resp.json()

pop_records = pop_json[1]
pop_df = pd.DataFrame(pop_records)
pop_df = pop_df[["countryiso3code", "value"]].dropna()
pop_df = pop_df.rename(columns={"countryiso3code": "adm0", "value": "population"})
pop_df = pop_df.drop_duplicates(subset="adm0").set_index("adm0")
print(f"  Population data for {len(pop_df)} countries")


# ------------------------------------------------------------------
# Merge with meat shares (single rebuild — safe to re-run)
# ------------------------------------------------------------------

meat_iso = country_meat_share.copy()
meat_iso["adm0"] = to_iso3(meat_iso[COUNTRY_COL])
meat_iso = meat_iso.dropna(subset=["adm0"]).set_index("adm0")

meat_df = (
    meat_iso
    .join(grassland, how="inner")
    .join(livestock, how="inner")
    .join(livestock_totals, how="inner")
    .join(pop_df, how="inner")
)
print(f"  Countries in final meat_df: {len(meat_df)}")

meat_df["cattle_per_capita"] = meat_df["cattle_total"] / meat_df["population"]
meat_df["sheep_per_capita"]  = meat_df["sheep_total"] / meat_df["population"]
meat_df["pig_per_capita"]    = meat_df["pig_total"] / meat_df["population"]

# ------------------------------------------------------------------
# 9 scatter plots: 3 y-vars (beef, mutton, beef+mutton) × 3 x-vars (class6, class7, class6+7)
# ------------------------------------------------------------------

y_vars = {
    "beef_recipe_share":         "Beef recipe share (%)",
    "mutton_recipe_share":       "Mutton recipe share (%)",
    "beef_mutton_recipe_share":  "Beef + mutton recipe share (%)",
    "beef_pork_recipe_share":    "Beef + pork recipe share (%)",
    "beef_dairy_recipe_share":   "Beef + dairy recipe share (%)",
    "meat_recipe_share":         "Meat recipe share (%)",
}
x_vars = {
    "class6_mean":  "Natural grassland (country mean, %)",
    "class7_mean":  "Cultivated land (country mean, %)",
    "class67_sum":  "Cultivated land and natural grassland (country mean, %)",
}

for y_col, y_label in y_vars.items():
    for x_col, x_label in x_vars.items():

        fig, ax = plt.subplots(figsize=(8, 6))

        sub = meat_df[[y_col, x_col]].dropna().copy()

        r_val, p_val = stats.pearsonr(sub[x_col], sub[y_col])

        ax.scatter(sub[x_col], sub[y_col] * 100,
                   s=30, alpha=0.65, color="#2171b5",
                   edgecolors="white", linewidths=0.3, zorder=3)

        for adm0, row in sub.iterrows():
            ax.annotate(adm0, (row[x_col], row[y_col] * 100),
                        fontsize=5.5, color="#555555",
                        xytext=(2, 2), textcoords="offset points")

        m, b_coef = np.polyfit(sub[x_col], sub[y_col] * 100, 1)
        x_line = np.linspace(sub[x_col].min(), sub[x_col].max(), 200)
        ax.plot(x_line, m * x_line + b_coef, color="#e63946",
                linewidth=1.5, zorder=4)

        ax.set_title(f"r = {r_val:.3f}, p = {p_val:.3f}  (n = {len(sub)})", fontsize=10)
        ax.set_xlabel(x_label, fontsize=10)
        ax.set_ylabel(y_label, fontsize=10)
        ax.tick_params(labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)

        plt.tight_layout()
        out_name = OUTPUT_DIR / f"scatter_{y_col}_vs_{x_col}.pdf"
        plt.savefig(out_name, dpi=150, bbox_inches="tight")
        plt.savefig(str(out_name).replace(".pdf", ".png"), dpi=150, bbox_inches="tight")
        print(f"  Saved → {out_name}")
        plt.show()


livestock_pairs = [
    ("beef_recipe_share",       "cattle_density_mean", "Beef recipe share (%)",        "Cattle density (country mean, head/km²)"),
    ("mutton_recipe_share",     "sheep_density_mean",  "Mutton recipe share (%)",       "Sheep density (country mean, head/km²)"),
    ("pork_recipe_share",       "pig_density_mean",    "Pork recipe share (%)",        "Pig density (country mean, head/km²)"),
    ("beef_dairy_recipe_share", "cattle_density_mean", "Beef + dairy recipe share (%)", "Cattle density (country mean, head/km²)"),
]

for y_col, x_col, y_label, x_label in livestock_pairs:

    fig, ax = plt.subplots(figsize=(8, 6))

    sub = meat_df[[y_col, x_col]].dropna().copy()

    r_val, p_val = stats.pearsonr(sub[x_col], sub[y_col])

    ax.scatter(sub[x_col], sub[y_col] * 100,
               s=30, alpha=0.65, color="#2171b5",
               edgecolors="white", linewidths=0.3, zorder=3)

    for adm0, row in sub.iterrows():
        ax.annotate(adm0, (row[x_col], row[y_col] * 100),
                    fontsize=5.5, color="#555555",
                    xytext=(2, 2), textcoords="offset points")

    m, b_coef = np.polyfit(sub[x_col], sub[y_col] * 100, 1)
    x_line = np.linspace(sub[x_col].min(), sub[x_col].max(), 200)
    ax.plot(x_line, m * x_line + b_coef, color="#e63946",
            linewidth=1.5, zorder=4)

    ax.set_title(f"r = {r_val:.3f}, p = {p_val:.3f}  (n = {len(sub)})", fontsize=10)
    ax.set_xlabel(x_label, fontsize=10)
    ax.set_ylabel(y_label, fontsize=10)
    ax.tick_params(labelsize=8)
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    out_name = OUTPUT_DIR / f"scatter_{y_col}_vs_{x_col}.pdf"
    plt.savefig(out_name, dpi=150, bbox_inches="tight")
    plt.savefig(str(out_name).replace(".pdf", ".png"), dpi=150, bbox_inches="tight")
    print(f"  Saved → {out_name}")
    plt.show()




# ------------------------------------------------------------------
# POOLED scatter: beef/cattle, mutton/sheep, pork/pig — per capita, one fit
# ------------------------------------------------------------------

pooled_rows = []
for y_col, x_col, y_label in [
    ("beef_recipe_share",   "cattle_per_capita", "Beef recipe share (%)"),
    ("mutton_recipe_share", "sheep_per_capita",  "Mutton recipe share (%)"),
    ("pork_recipe_share",   "pig_per_capita",    "Pork recipe share (%)"),
]:
    sub = meat_df[[y_col, x_col]].dropna().copy()
    sub["y"] = sub[y_col]
    sub["x"] = sub[x_col]
    sub["animal"] = y_label
    sub["adm0"] = sub.index
    pooled_rows.append(sub[["adm0", "animal", "x", "y"]])

pooled = pd.concat(pooled_rows, ignore_index=True)
print(f"  Pooled n = {len(pooled)} (across beef/cattle, mutton/sheep, pork/pig)")

fig, ax = plt.subplots(figsize=(8, 6))

colors = {"Beef recipe share (%)": "#2171b5", "Mutton recipe share (%)": "#e63946", "Pork recipe share (%)": "#2ca02c"}

for animal, group in pooled.groupby("animal"):
    ax.scatter(group["x"], group["y"] * 100,
               s=30, alpha=0.65, color=colors[animal],
               edgecolors="white", linewidths=0.3, zorder=3, label=animal)

r_val, p_val = stats.pearsonr(pooled["x"], pooled["y"])

m, b_coef = np.polyfit(pooled["x"], pooled["y"] * 100, 1)
x_line = np.linspace(pooled["x"].min(), pooled["x"].max(), 200)
ax.plot(x_line, m * x_line + b_coef, color="black", linewidth=1.5, zorder=4)

ax.set_title(f"Pooled: r = {r_val:.3f}, p = {p_val:.3f}  (n = {len(pooled)})", fontsize=10)
ax.set_xlabel("Livestock per capita (head per person, country total / population)", fontsize=10)
ax.set_ylabel("Recipe share (%)", fontsize=10)
ax.legend(fontsize=8, frameon=False)
ax.tick_params(labelsize=8)
ax.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
out_name = OUTPUT_DIR / "scatter_pooled_animal_to_animal_percapita.pdf"
plt.savefig(out_name, dpi=150, bbox_inches="tight")
plt.savefig(str(out_name).replace(".pdf", ".png"), dpi=150, bbox_inches="tight")
print(f"  Saved → {out_name}")
plt.show()



# ------------------------------------------------------------------
# POOLED scatter: beef, mutton, pork — all vs cultivated + grassland
# ------------------------------------------------------------------

pooled_rows_grass = []
for y_col, y_label in [
    ("beef_recipe_share",   "Beef recipe share (%)"),
    ("mutton_recipe_share", "Mutton recipe share (%)"),
    #("pork_recipe_share",   "Pork recipe share (%)"),
]:
    sub = meat_df[[y_col, "class6_mean"]].dropna().copy()
    sub["y"] = sub[y_col]
    sub["x"] = sub["class6_mean"]
    sub["animal"] = y_label
    sub["adm0"] = sub.index
    pooled_rows_grass.append(sub[["adm0", "animal", "x", "y"]])

pooled_grass = pd.concat(pooled_rows_grass, ignore_index=True)
print(f"  Pooled (grassland) n = {len(pooled_grass)} (across beef, mutton, pork)")

fig, ax = plt.subplots(figsize=(8, 6))

colors = {"Beef recipe share (%)": "#2171b5", "Mutton recipe share (%)": "#e63946", "Pork recipe share (%)": "#2ca02c"}

for animal, group in pooled_grass.groupby("animal"):
    ax.scatter(group["x"], group["y"] * 100,
               s=30, alpha=0.65, color=colors[animal],
               edgecolors="white", linewidths=0.3, zorder=3, label=animal)

r_val, p_val = stats.pearsonr(pooled_grass["x"], pooled_grass["y"])

m, b_coef = np.polyfit(pooled_grass["x"], pooled_grass["y"] * 100, 1)
x_line = np.linspace(pooled_grass["x"].min(), pooled_grass["x"].max(), 200)
ax.plot(x_line, m * x_line + b_coef, color="black", linewidth=1.5, zorder=4)

ax.set_title(f"Pooled: r = {r_val:.3f}, p = {p_val:.3f}  (n = {len(pooled_grass)})", fontsize=10)
ax.set_xlabel("Natural grassland (country mean, %)", fontsize=10)
ax.set_ylabel("Recipe share (%)", fontsize=10)
ax.legend(fontsize=8, frameon=False)
ax.tick_params(labelsize=8)
ax.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
out_name = OUTPUT_DIR / "scatter_pooled_animal_to_grassland.pdf"
plt.savefig(out_name, dpi=150, bbox_inches="tight")
plt.savefig(str(out_name).replace(".pdf", ".png"), dpi=150, bbox_inches="tight")
print(f"  Saved → {out_name}")
plt.show()
