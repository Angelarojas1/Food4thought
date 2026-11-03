# -*- coding: utf-8 -*-
"""
Scatter plot: country-ingredient level suitability vs. recipe share.

Ingredient shares are computed directly from the raw recipe data using the
same pipeline as recipe_ethnic_diversity.py:
  share = (number of recipes in country containing ingredient) / (total recipes in country)
"""

import ast
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os
from pathlib import Path
from scipy import stats
warnings.filterwarnings("ignore")

# =============================================================================
# PATHS
# =============================================================================
STATA_FILE = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\recipe_all_countries_web.dta"
)
CANONICAL_FILE = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\ChatGPT_output\ingredient_batch100\ingredient_all.csv"
)
RAW_CLEAN_FILE = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\unique_raw_ingredients_cleaned_manual.csv"
)
suitability_path = Path(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded"
    r"\iv_versatility\suitability.dta"
)

OUTPUT_DIR = r"C:\Users\stevebc\Dropbox\Cuisine_complexity\3_results\temp"
MIN_RECIPES = 10

# =============================================================================
# COUNTRY NAME -> ISO3
# =============================================================================
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

# =============================================================================
# SHARED HELPERS (same as recipe_ethnic_diversity.py)
# =============================================================================

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

def binscatter(ax, x, y, n_bins=20, color="#2171b5", fit_color="#e63946"):
    df_b = pd.DataFrame({"x": x, "y": y}).dropna()
    df_b["bin"] = pd.qcut(df_b["x"], n_bins, duplicates="drop")
    grouped = df_b.groupby("bin", observed=True)["y"]
    means   = grouped.mean()
    sems    = grouped.sem()
    xmids   = df_b.groupby("bin", observed=True)["x"].mean()
    ax.errorbar(xmids, means, yerr=1.96 * sems,
                fmt="o", color=color, markersize=5,
                ecolor=color, elinewidth=1, capsize=3, zorder=4)
    m, b = np.polyfit(xmids, means, 1)
    x_line = np.linspace(xmids.min(), xmids.max(), 200)
    ax.plot(x_line, m * x_line + b, color=fit_color, linewidth=1.5, zorder=3)

def style_axes(ax):
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_linewidth(0.8)
        ax.spines[spine].set_color("black")
    ax.tick_params(axis="both", labelsize=11, length=4, width=0.8, color="black")

# =============================================================================
# MAIN
# =============================================================================
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ------------------------------------------------------------------
# 1. Load recipes and build canonical mapping (same as recipe_ethnic_diversity.py)
# ------------------------------------------------------------------
print("Loading recipe Stata file ...")
INGREDIENT_ENG = "listofingredients_eng"
INGREDIENT_RAW = "listofingredients"
COUNTRY_COL    = "country"

recipes = pd.read_stata(STATA_FILE)
recipes = recipes.reset_index(drop=True)

recipes["ingredient_source"] = recipes[INGREDIENT_ENG]
mask_na    = recipes["ingredient_source"].isna()
recipes.loc[mask_na, "ingredient_source"] = recipes.loc[mask_na, INGREDIENT_RAW]
parsed_len = recipes["ingredient_source"].apply(parse_ingredient_list).apply(len)
mask_empty = parsed_len.eq(0)
recipes.loc[mask_empty, "ingredient_source"] = recipes.loc[mask_empty, INGREDIENT_RAW]
recipes["parsed_ingredients"] = recipes["ingredient_source"].apply(parse_ingredient_list)
print(f"  Loaded {len(recipes):,} recipes from {recipes[COUNTRY_COL].nunique()} countries")

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

# ------------------------------------------------------------------
# 2. Build recipe x canonical-ingredient table
# ------------------------------------------------------------------
print("Exploding ingredients and mapping to canonical ...")
rows = []
for _, row in recipes.iterrows():
    country    = row[COUNTRY_COL]
    canonicals = set()
    for ing in row["parsed_ingredients"]:
        key = clean_key(clean_text(ing))
        can = raw_to_canonical.get(key)
        if can and can != "unmatched" and not pd.isna(can):
            canonicals.add(can)
    if canonicals:
        rows.append({COUNTRY_COL: country, "canonical_set": frozenset(canonicals)})

recipe_canonical = pd.DataFrame(rows)
n_per_country = recipe_canonical.groupby(COUNTRY_COL).size().rename("n_recipes")
eligible      = n_per_country[n_per_country >= MIN_RECIPES].index
recipe_canonical = recipe_canonical[recipe_canonical[COUNTRY_COL].isin(eligible)].copy()
print(f"  {recipe_canonical[COUNTRY_COL].nunique()} countries with >={MIN_RECIPES} recipes")

# ------------------------------------------------------------------
# 3. Compute ingredient shares (recipe-weighted)
#    share = n_recipes_with_ingredient / n_recipes_in_country
# ------------------------------------------------------------------
print("Computing ingredient shares (recipe-weighted) ...")
long_rows = []
for _, row in recipe_canonical.iterrows():
    for ci in row["canonical_set"]:
        long_rows.append({COUNTRY_COL: row[COUNTRY_COL], "canonical_ingredient": ci})
long_df = pd.DataFrame(long_rows)

ing_counts = (
    long_df.groupby([COUNTRY_COL, "canonical_ingredient"])
    .size()
    .reset_index(name="recipe_count")
)
ing_counts = ing_counts.merge(n_per_country.reset_index(), on=COUNTRY_COL, how="left")
ing_counts["share"] = ing_counts["recipe_count"] / ing_counts["n_recipes"]

# ISO3 for merge with suitability
ing_counts["adm0"] = to_iso3(ing_counts[COUNTRY_COL])
unmapped = ing_counts.loc[ing_counts["adm0"].isna(), COUNTRY_COL].unique()
if len(unmapped):
    print(f"  WARNING - unmapped countries: {list(unmapped)}")
ing_counts = ing_counts.dropna(subset=["adm0"])
ing_counts["ingredient_key"] = ing_counts["canonical_ingredient"].str.strip().str.lower()

print(f"  Ingredient shares: {len(ing_counts):,} country-ingredient pairs, "
      f"{ing_counts['adm0'].nunique()} countries, "
      f"{ing_counts['canonical_ingredient'].nunique()} ingredients")

# ------------------------------------------------------------------
# 4. Load suitability
# ------------------------------------------------------------------
print("\nLoading suitability data ...")
suit_raw = pd.read_stata(suitability_path)
print(f"  Columns: {list(suit_raw.columns)}")
print(f"  Rows: {len(suit_raw)}")

if "adm0" in suit_raw.columns:
    suit_raw["adm0"] = suit_raw["adm0"].str.strip().str.upper()
elif "country" in suit_raw.columns:
    suit_raw["adm0"] = to_iso3(suit_raw["country"])

suit_raw["ingredient_key"] = suit_raw["ingredient"].str.strip().str.lower()
suit = suit_raw[["adm0", "ingredient_key", "suitability"]].dropna()
print(f"  Suitability rows after dropna: {len(suit):,}, "
      f"{suit['adm0'].nunique()} countries, "
      f"{suit['ingredient_key'].nunique()} ingredients")

# ------------------------------------------------------------------
# 5. Merge
# ------------------------------------------------------------------
df = ing_counts.merge(suit, on=["adm0", "ingredient_key"], how="inner")
print(f"\n  Merged rows: {len(df):,}")
print(f"  Unique countries: {df['adm0'].nunique()},  "
      f"unique ingredients: {df['ingredient_key'].nunique()}")

if len(df) == 0:
    print("  !! ZERO MATCHES - sample ingredient keys from each side:")
    print(f"     Shares:      {sorted(ing_counts['ingredient_key'].unique())[:10]}")
    print(f"     Suitability: {sorted(suit['ingredient_key'].unique())[:10]}")
    raise ValueError("No rows matched. Check ingredient name formats above.")

df = df.dropna(subset=["share", "suitability"])

# ------------------------------------------------------------------
# 6. Derived variables
# ------------------------------------------------------------------
df["share_log"] = np.log(df["share"] + 0.001)

df["suit_zscore"] = df.groupby("ingredient_key")["suitability"].transform(
    lambda x: (x - x.mean()) / x.std()
)
df["suit_pctrank"] = df.groupby("ingredient_key")["suitability"].transform(
    lambda x: x.rank(pct=True) * 100
)

# ------------------------------------------------------------------
# 7. Plot loop
# ------------------------------------------------------------------
plot_specs = [
    ("suitability",  "share",     "Suitability (0-1)",                            "Ingredient share of recipes",           "raw_level"),
    ("suitability",  "share_log", "Suitability (0-1)",                            "log(Ingredient share + 0.001)",         "raw_logshare"),
    ("suit_zscore",  "share",     "Suitability z-score (within ingredient)",      "Ingredient share of recipes",           "zscore_level"),
    ("suit_zscore",  "share_log", "Suitability z-score (within ingredient)",      "log(Ingredient share + 0.001)",         "zscore_logshare"),
    ("suit_pctrank", "share",     "Suitability percentile rank (within ingred.)", "Ingredient share of recipes",           "pctrank_level"),
    ("suit_pctrank", "share_log", "Suitability percentile rank (within ingred.)", "log(Ingredient share + 0.001)",         "pctrank_logshare"),
]

for xvar, yvar, xlabel, ylabel, tag in plot_specs:
    sub = df[[xvar, yvar]].dropna()
    r, p = stats.pearsonr(sub[xvar], sub[yvar])
    print(f"\n  {tag}:  r = {r:.3f},  p = {p:.3f},  n = {len(sub):,}")

    for plot_type in ["scatter", "binscatter"]:
        fig, ax = plt.subplots(figsize=(9, 6))

        if plot_type == "scatter":
            ax.scatter(sub[xvar], sub[yvar],
                       s=8, alpha=0.25, color="#2171b5", edgecolors="none")
            m, b = np.polyfit(sub[xvar], sub[yvar], 1)
            x_line = np.linspace(sub[xvar].min(), sub[xvar].max(), 200)
            ax.plot(x_line, m * x_line + b, color="#e63946", linewidth=1.5, zorder=3)
        else:
            binscatter(ax, sub[xvar], sub[yvar], n_bins=20)

        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(
            f"Suitability vs. recipe share - {plot_type}\n"
            f"r = {r:.3f},  p = {p:.3f}  (n = {len(sub):,} country-ingredient pairs)",
            fontsize=12
        )
        style_axes(ax)
        plt.tight_layout()

        fname = f"suit_{tag}_{plot_type}.png"
        plt.savefig(os.path.join(OUTPUT_DIR, fname), dpi=150)
        print(f"    Saved -> {fname}")
        plt.close()


# =============================================================================
# REGRESSIONS WITH FIXED EFFECTS + DEMEANED BINSCATTER PLOTS
# =============================================================================

print("\n" + "="*70)
print("REGRESSIONS: ingredient share ~ suitability percentile rank")
print("  (two-way clustering: ingredient x country)")
print("="*70)

import statsmodels.formula.api as smf
from scipy import stats as scipy_stats

def twoway_cluster_se(model, group1, group2):
    """
    Cameron-Gelbach-Miller two-way clustering.
    V = V(group1) + V(group2) - V(group1 x group2)
    """
    g12 = group1.astype(str) + "_" + group2.astype(str)
    V1  = model.get_robustcov_results(cov_type="cluster", groups=group1).cov_params()
    V2  = model.get_robustcov_results(cov_type="cluster", groups=group2).cov_params()
    V12 = model.get_robustcov_results(cov_type="cluster", groups=g12).cov_params()
    V_cgm = V1 + V2 - V12
    # Force positive semi-definite (numerical fix for small negatives on diagonal)
    se_cgm = np.sqrt(np.maximum(np.diag(V_cgm), 0))
    return V_cgm, se_cgm

df["ingredient_fe"] = df["ingredient_key"]
df["country_fe"]    = df["adm0"]

specs = [
    ("1_ingredient_FE",         "share ~ suit_pctrank + C(ingredient_fe)",
     "Ingredient FE",           "share_demean_ing"),
    ("2_country_FE",            "share ~ suit_pctrank + C(country_fe)",
     "Country FE",              "share_demean_cty"),
    ("3_ingredient_country_FE", "share ~ suit_pctrank + C(ingredient_fe) + C(country_fe)",
     "Ingredient + Country FE", "share_demean_both"),
]

reg_results = {}
for label, formula, fe_label, demean_col in specs:
    model = smf.ols(formula, data=df).fit()
    idx   = model.params.index.get_loc("suit_pctrank")
    coef  = model.params["suit_pctrank"]

    V_cgm, se_cgm = twoway_cluster_se(
        model,
        group1=df.loc[model.model.data.row_labels, "ingredient_key"].values,
        group2=df.loc[model.model.data.row_labels, "adm0"].values,
    )
    se    = se_cgm[idx]
    tval  = coef / se
    pval  = 2 * scipy_stats.t.sf(abs(tval), df=model.df_resid)
    stars = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""
    print(f"  {label:<32}  b={coef:.6f}{stars}  se={se:.6f}  "
          f"t={tval:.3f}  p={pval:.4f}  R2={model.rsquared:.3f}  N={int(model.nobs):,}")

    reg_results[demean_col] = {
        "coef": coef, "se": se, "pval": pval, "stars": stars,
        "fe_label": fe_label, "label": label,
    }
    # Partial out everything except suit_pctrank for demeaned binscatter
    df[demean_col] = model.resid + coef * df["suit_pctrank"]

# ------------------------------------------------------------------
# Demeaned binscatter plots
# ------------------------------------------------------------------
print("\nGenerating demeaned binscatter plots ...")

demean_specs = [
    ("share_demean_ing",  "Ingredient share (demeaned: ingredient FE)",  "1_ingredient_FE"),
    ("share_demean_cty",  "Ingredient share (demeaned: country FE)",      "2_country_FE"),
    ("share_demean_both", "Ingredient share (demeaned: ingredient + country FE)", "3_both_FE"),
]

for demean_col, ylabel, tag in demean_specs:
    res = reg_results[demean_col]
    sub = df[["suit_pctrank", demean_col]].dropna()
    r, p = stats.pearsonr(sub["suit_pctrank"], sub[demean_col])

    for plot_type in ["scatter", "binscatter"]:
        fig, ax = plt.subplots(figsize=(9, 6))

        if plot_type == "scatter":
            ax.scatter(sub["suit_pctrank"], sub[demean_col],
                       s=8, alpha=0.25, color="#2171b5", edgecolors="none")
            m, b = np.polyfit(sub["suit_pctrank"], sub[demean_col], 1)
            x_line = np.linspace(sub["suit_pctrank"].min(), sub["suit_pctrank"].max(), 200)
            ax.plot(x_line, m * x_line + b, color="#e63946", linewidth=1.5, zorder=3)
        else:
            binscatter(ax, sub["suit_pctrank"], sub[demean_col], n_bins=10)

        stars = res["stars"]
        ax.set_xlabel("Suitability percentile rank (within ingredient)", fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(
            f"Suitability vs. recipe share — {plot_type}\n"
            f"{res['fe_label']}  |  "
            f"b={res['coef']:.6f}{stars}  p={res['pval']:.4f}  "
            f"(n={len(sub):,})",
            fontsize=11
        )
        ax.axhline(0, color="black", linewidth=0.6, linestyle="--", alpha=0.4)
        style_axes(ax)
        plt.tight_layout()

        fname = f"suit_pctrank_{tag}_{plot_type}.png"
        plt.savefig(os.path.join(OUTPUT_DIR, fname), dpi=150)
        print(f"    Saved -> {fname}")
        plt.close()

print("\nDone.")