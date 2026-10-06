# -*- coding: utf-8 -*-
"""
Cuisine Diversity and Fractionalization
========================================
Builds 3 cuisine diversity indices + PMI-based recipe surprise from the
recipe + ingredient data, then correlates with:

  (A) Alesina et al. (2003) ethnic / linguistic / religious fractionalization
  (B) Putterman & Weil (2010) world migration matrix — Shannon entropy &
      Herfindahl index of ancestry/origin-country composition

Diversity indices:
  1. Jaccard dissimilarity  – mean pairwise (1 - |A∩B|/|A∪B|) across recipe
                              pairs within a country (random subsample for speed)
  2. Canonical ingredient entropy – normalised Shannon entropy over canonical
                                    ingredient share distribution within a country
  3. Ingredient richness    – mean distinct canonical ingredients per recipe
  4. PMI surprise           – mean negative pointwise mutual information over
                              ingredient pairs (higher = more unusual combos)

Usage:
  Edit the FILE PATHS block, then run as a plain Python script.
  Outputs are written to OUTPUT_DIR.
"""

import ast
import re
import warnings
from collections import Counter
from itertools import combinations
from pathlib import Path
from random import sample, seed

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from adjustText import adjust_text
from scipy import stats

warnings.filterwarnings("ignore", category=FutureWarning)

# ------------------------------------------------------------------
# FILE PATHS  <- edit these
# ------------------------------------------------------------------

STATA_FILE = Path(
    r"C:\Users\stell\Dropbox\food4thought\analysis23\data\coded\recipes\recipe_all_countries_web.dta"
)
CANONICAL_FILE = Path(
    r"C:\Users\stell\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\ChatGPT_output\ingredient_batch100\ingredient_all.csv"
)
RAW_CLEAN_FILE = Path(
    r"C:\Users\stell\Dropbox\food4thought\analysis23\data\coded\recipes\ingredients\unique_raw_ingredients_cleaned_manual.csv"
)
FRACTIONALIZATION_XLS = Path(
    r"C:\Users\stell\Dropbox\food4thought\analysis23\data\raw\ethnic\2003_fractionalization.xls"
)
MIGRATION_MATRIX_XLS = Path(
    r"C:\Users\stell\Dropbox\food4thought\analysis23\data\raw\migration\matrix version 1.1.xls"
)
CONTROLS_PATH = Path(
    r"C:\Users\stell\Dropbox\food4thought\analysis23\data\coded"
    r"\iv_versatility\first_stage_native_m_c.dta"
)
OUTPUT_DIR = Path(
    r"C:\Users\stell\Dropbox\food4thought\analysis23\outputs\Figures\ethnographic\fractionalization"
)

# Non-standard World Bank codes -> ISO3
WB_TO_ISO3 = {
    "ZAR": "COD",
    "CIL": None,
    "TMP": "TLS",
    "NIU": None,
    "YUG": "SRB",
    "OAN": "TWN",
}

# ------------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------------

COUNTRY_COL           = "country"
INGREDIENT_ENG        = "listofingredients_eng"
INGREDIENT_RAW        = "listofingredients"
MIN_RECIPES           = 10
MAX_PAIRS_PER_COUNTRY = 500
RANDOM_SEED           = 42

FULL_CONTROLS = [
    "numrecipes", "avg_suitability", "al_mn", "ph_mn", "rough",
    "landlocked", "staple_suitability", "GDP",
]

FRAC_OUTCOMES = ["ethnic", "language", "religion"]

FRAC_VARS = {
    "ethnic":   "Ethnic Fractionalization\n(Alesina et al. 2003)",
    "language": "Linguistic Fractionalization\n(Alesina et al. 2003)",
    "religion": "Religious Fractionalization\n(Alesina et al. 2003)",
}

MIGRATION_VARS = {
    "migration_entropy": "Ancestry Diversity - Shannon Entropy\n(Putterman & Weil 2010)",
    "migration_herf":    "Ancestry Diversity - Herfindahl Index\n(Putterman & Weil 2010, 1 - Sp^2)",
}

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

def jaccard_dissimilarity(set_a, set_b):
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union        = len(set_a | set_b)
    return 1.0 - intersection / union if union > 0 else 0.0

def shannon_entropy(counts):
    n = np.array(counts, dtype=float)
    n = n[n > 0]
    if len(n) == 0:
        return np.nan
    p = n / n.sum()
    return -np.sum(p * np.log(p))

def partial_residuals(y, covariates):
    mask = (~np.isnan(y)) & np.all(~np.isnan(covariates), axis=1)
    if mask.sum() < 5:
        return y, mask
    X  = np.column_stack([np.ones(mask.sum()), covariates[mask]])
    y_ = y[mask]
    b  = np.linalg.lstsq(X, y_, rcond=None)[0]
    res = np.full_like(y, np.nan)
    res[mask] = y_ - X @ b
    return res, mask

def style_axes(ax):
    """Remove top/right spines; explicitly restore left and bottom."""
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_linewidth(0.8)
        ax.spines[spine].set_color("black")
    ax.tick_params(axis="both", labelsize=11, length=4, width=0.8, color="black")

def style_axes_panel(ax):
    """Same as style_axes but lighter weight for panel subplots."""
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_linewidth(0.7)
        ax.spines[spine].set_color("black")
    ax.tick_params(labelsize=8, length=3, width=0.7, color="black")

def make_scatter(df, x_col, y_col, x_label, y_label, title, out_path,
                 condition=False, partial_control_col="log_n_recipes"):
    """
    Scatter of x_col vs y_col with OLS fit + 95% bootstrap CI + country labels.
    condition=True -> residualise both axes on partial_control_col first.
    """
    cols = [x_col, y_col, COUNTRY_COL] + ([partial_control_col] if condition else [])
    d = df[cols].dropna()
    if len(d) < 10:
        print(f"  Skipping {x_col} vs {y_col} - too few obs ({len(d)})")
        return

    x_arr = d[x_col].values.astype(float)
    y_arr = d[y_col].values.astype(float)

    if condition:
        ctrl       = d[[partial_control_col]].values
        x_resid, _ = partial_residuals(x_arr, ctrl)
        y_resid, _ = partial_residuals(y_arr, ctrl)
        mask = ~np.isnan(x_resid) & ~np.isnan(y_resid)
        x_p, y_p = x_resid[mask], y_resid[mask]
    else:
        mask = ~np.isnan(x_arr) & ~np.isnan(y_arr)
        x_p, y_p = x_arr[mask], y_arr[mask]

    countries = d[COUNTRY_COL].values[mask]
    slope, intercept, r, pval, _ = stats.linregress(x_p, y_p)
    n = len(x_p)

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(x_p, y_p, s=30, alpha=0.65, color="#2c6fad", zorder=3)

    texts = [ax.text(xi, yi, cn, fontsize=7.5, alpha=0.75)
             for xi, yi, cn in zip(x_p, y_p, countries)]
    adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle="-", color="grey", lw=0.4))

    x_line = np.linspace(x_p.min(), x_p.max(), 200)
    ax.plot(x_line, intercept + slope * x_line, color="#c0392b", linewidth=1.5, zorder=4)

    rng = np.random.default_rng(RANDOM_SEED)
    boot_lines = []
    for _ in range(500):
        idx = rng.integers(0, n, n)
        if len(np.unique(x_p[idx])) < 2:
            continue
        bs, bi, *_ = stats.linregress(x_p[idx], y_p[idx])
        boot_lines.append(bi + bs * x_line)
    if boot_lines:
        ax.fill_between(x_line,
                        np.percentile(boot_lines, 2.5, axis=0),
                        np.percentile(boot_lines, 97.5, axis=0),
                        color="#c0392b", alpha=0.12, zorder=2)

    stars    = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""
    cond_str = "\n(residual, partialling out log recipe count)" if condition else ""
    ax.set_xlabel(f"{x_label}{cond_str}", fontsize=13)
    ax.set_ylabel(f"{y_label}{cond_str}", fontsize=13)
    ax.set_title(title, fontsize=14, pad=10)
    ax.annotate(
        f"b = {slope:.3f}{stars}  |  r = {r:.3f}  |  p = {pval:.3f}  |  N = {n}",
        xy=(0.03, 0.96), xycoords="axes fraction", fontsize=10, va="top",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.7),
    )
    style_axes(ax)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out_path}")


def run_regressions(reg_df, cuisine_var, cuisine_label, cont_cols, avail_controls,
                    outcome_vars=None):
    """Run 3-spec regressions for all outcomes and return results df."""
    if outcome_vars is None:
        outcome_vars = FRAC_OUTCOMES
    rows = []
    for outcome in outcome_vars:
        for spec_label, extra_vars in [
            ("1_raw",                   []),
            ("2_continent_FE",          cont_cols),
            ("3_continent_FE_controls", cont_cols + avail_controls),
        ]:
            sub = reg_df[[outcome, cuisine_var] + extra_vars].dropna()
            if len(sub) < 10:
                continue
            rhs   = " + ".join([cuisine_var] + extra_vars) if extra_vars else cuisine_var
            model = smf.ols(f"{outcome} ~ {rhs}", data=sub).fit(cov_type="HC3")
            coef  = model.params[cuisine_var]
            se    = model.bse[cuisine_var]
            pval  = model.pvalues[cuisine_var]
            stars = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""
            rows.append({
                "cuisine_measure": cuisine_label,
                "outcome":  outcome,
                "spec":     spec_label,
                "coef":     round(coef, 4),
                "se":       round(se, 4),
                "t":        round(model.tvalues[cuisine_var], 3),
                "p":        round(pval, 4),
                "stars":    stars,
                "r2":       round(model.rsquared, 3),
                "n":        int(model.nobs),
            })
            print(f"  {outcome:<22} {spec_label:<30}  b={coef:.4f}{stars}  "
                  f"se={se:.4f}  p={pval:.4f}  R2={model.rsquared:.3f}  N={int(model.nobs)}")
    return pd.DataFrame(rows)


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
# INDEX 1: MEAN PAIRWISE JACCARD DISSIMILARITY
# ===========================================================================

print("Computing mean pairwise Jaccard dissimilarity ...")
seed(RANDOM_SEED)

jaccard_rows = []
for country, grp in recipe_canonical.groupby(COUNTRY_COL):
    sets      = grp["canonical_set"].tolist()
    all_pairs = list(combinations(range(len(sets)), 2))
    if len(all_pairs) > MAX_PAIRS_PER_COUNTRY:
        all_pairs = sample(all_pairs, MAX_PAIRS_PER_COUNTRY)
    if not all_pairs:
        continue
    dists = [jaccard_dissimilarity(sets[i], sets[j]) for i, j in all_pairs]
    jaccard_rows.append({COUNTRY_COL: country, "jaccard_mean": np.mean(dists)})

country_jaccard = pd.DataFrame(jaccard_rows)

# ===========================================================================
# INDEX 2: NORMALISED CANONICAL INGREDIENT ENTROPY
# ===========================================================================

print("Computing canonical ingredient entropy ...")

long_rows = []
for _, row in recipe_canonical.iterrows():
    for ci in row["canonical_set"]:
        long_rows.append({COUNTRY_COL: row[COUNTRY_COL], "canonical_ingredient": ci})
long_df = pd.DataFrame(long_rows)

country_entropy_rows = []
for country, grp in long_df.groupby(COUNTRY_COL):
    counts = grp["canonical_ingredient"].value_counts().values
    k      = len(counts)
    raw_h  = shannon_entropy(counts)
    norm_h = raw_h / np.log(k) if k > 1 else np.nan
    country_entropy_rows.append({
        COUNTRY_COL:              country,
        "canonical_entropy_raw":  raw_h,
        "canonical_entropy_norm": norm_h,
        "n_distinct_canonicals":  k,
    })
country_entropy = pd.DataFrame(country_entropy_rows)

# ===========================================================================
# INDEX 3: MEAN INGREDIENT RICHNESS PER RECIPE
# ===========================================================================

print("Computing mean ingredient richness ...")
richness = (
    recipe_canonical.groupby(COUNTRY_COL)["n_canonical"]
    .mean().rename("mean_richness").reset_index()
)

# ===========================================================================
# INDEX 4: PMI-BASED RECIPE SURPRISE
# ===========================================================================

print("Computing PMI-based recipe surprise ...")

n_global         = len(recipe_canonical)
singleton_counts = Counter()
pair_counts      = Counter()

for cset in recipe_canonical["canonical_set"]:
    for ing in cset:
        singleton_counts[ing] += 1
    for a, b in combinations(sorted(cset), 2):
        pair_counts[(a, b)] += 1

def pmi_score(a, b):
    p_a  = singleton_counts[a] / n_global
    p_b  = singleton_counts[b] / n_global
    p_ab = pair_counts[(min(a, b), max(a, b))] / n_global
    if p_ab == 0 or p_a == 0 or p_b == 0:
        return np.nan
    return np.log(p_ab / (p_a * p_b))

# Score each recipe: mean *negative* PMI -> unusual combos score high
surprise_rows = []
for _, row in recipe_canonical.iterrows():
    cset  = row["canonical_set"]
    pairs = list(combinations(sorted(cset), 2))
    if not pairs:
        continue
    pmis = [pmi_score(a, b) for a, b in pairs]
    pmis = [v for v in pmis if not np.isnan(v)]
    if not pmis:
        continue
    surprise_rows.append({
        COUNTRY_COL:    row[COUNTRY_COL],
        "recipe_id":    row["recipe_id"],
        "mean_neg_pmi": -np.mean(pmis),
    })

recipe_surprise = pd.DataFrame(surprise_rows)
print(f"  Scored {len(recipe_surprise):,} recipes")

country_surprise = (
    recipe_surprise.groupby(COUNTRY_COL)
    .agg(mean_recipe_surprise=("mean_neg_pmi", "mean"))
    .reset_index()
)
print("  Top 10 countries by recipe surprise:")
print(country_surprise.sort_values("mean_recipe_surprise", ascending=False)
      .head(10).to_string(index=False))

# ===========================================================================
# COMBINE ALL DIVERSITY INDICES
# ===========================================================================

diversity = (
    n_per_country.reset_index()
    .merge(country_jaccard,  on=COUNTRY_COL, how="left")
    .merge(country_entropy,  on=COUNTRY_COL, how="left")
    .merge(richness,         on=COUNTRY_COL, how="left")
    .merge(country_surprise, on=COUNTRY_COL, how="left")
)

# Save diversity measures to Stata
diversity_to_save = diversity[[
    COUNTRY_COL,
    "jaccard_mean",
    "canonical_entropy_norm"
]].copy()

diversity_to_save.to_stata(
    r"C:\Users\stell\Dropbox\food4thought\analysis23\data\coded\recipes\cuisine_diversity_measures.dta",
    write_index=False,
    version=118
)

print("Saved: cuisine_diversity_measures.dta")

# ===========================================================================
# LOAD FRACTIONALIZATION DATA (Alesina et al. 2003)
# ===========================================================================

print("Loading Alesina et al. (2003) fractionalization data ...")
try:
    frac_raw = pd.read_excel(FRACTIONALIZATION_XLS, engine="xlrd", header=None)
except ImportError:
    frac_raw = pd.read_excel(FRACTIONALIZATION_XLS, engine="openpyxl", header=None)

frac = frac_raw.iloc[2:].copy()
frac.columns = ["country", "source_eth", "date_eth", "ethnic", "language", "religion"]
frac = frac[["country", "ethnic", "language", "religion"]].copy()
frac["country"] = frac["country"].apply(clean_text)
for col in ["ethnic", "language", "religion"]:
    frac[col] = pd.to_numeric(frac[col], errors="coerce")
frac = frac.dropna(subset=["country"])
frac = frac[frac["country"] != ""]

name_map = {
    "United States":                    "United States",
    "South Korea":                      "Korea, Republic of",
    "North Korea":                      "Korea, Dem. Rep.",
    "Cote D'Ivoire":                    "Cote D'Ivoire",
    "Bosnia And Herzegovina":           "Bosnia-Herzegovina",
    "Czech Republic":                   "Czech Republic",
    "Cabo Verde":                       "Cape Verde",
    "Taiwan":                           "Taiwan",
    "Trinidad And Tobago":              "Trinidad and Tobago",
    "United Kingdom":                   "United Kingdom",
    "United Arab Emirates":             "United Arab Emirates",
    "Democratic Republic Of The Congo": "Congo, Dem. Rep.",
    "Republic Of Congo":                "Congo, Rep.",
    "Tanzania":                         "Tanzania",
}

diversity["country_match"] = diversity[COUNTRY_COL].replace(name_map)
frac["country_key"]        = frac["country"].str.strip().str.casefold()
diversity["country_key"]   = diversity["country_match"].str.strip().str.casefold()

merged = diversity.merge(
    frac[["country_key", "ethnic", "language", "religion"]],
    on="country_key", how="inner"
)
print(f"  Matched {len(merged)} countries to fractionalization data")

# ===========================================================================
# LOAD PUTTERMAN & WEIL MIGRATION MATRIX -> ANCESTRY DIVERSITY INDICES
# ===========================================================================

print("\nLoading Putterman & Weil migration matrix ...")
mig_raw = pd.read_excel(MIGRATION_MATRIX_XLS, engine="xlrd")
mig_raw = mig_raw.drop(columns=["update"], errors="ignore")
origin_cols = [c for c in mig_raw.columns if c not in ["wbcode", "wbname"]]
mig_raw["iso3"] = mig_raw["wbcode"].replace(WB_TO_ISO3)
mig_raw = mig_raw.dropna(subset=["iso3"])

mig_stats = []
for _, row in mig_raw.iterrows():
    iso3   = row["iso3"]
    shares = row[origin_cols].values.astype(float)
    shares = shares[np.isfinite(shares) & (shares > 0)]
    if len(shares) == 0:
        continue
    mig_stats.append({
        "iso3":               iso3,
        "migration_entropy":  -np.sum(shares * np.log(shares)),
        "migration_herf":     1.0 - np.sum(shares ** 2),
        "n_ancestry_origins": len(shares),
    })

mig_df = pd.DataFrame(mig_stats)
print(f"  Migration stats computed for {len(mig_df)} countries")

name_to_iso3_mig = dict(zip(
    mig_raw["wbname"].str.strip().str.casefold(),
    mig_raw["iso3"]
))
name_to_iso3_mig.update({
    "united states":            "USA",
    "united states of america": "USA",
    "south korea":              "KOR",
    "korea, republic of":       "KOR",
    "republic of korea":        "KOR",
    "korea":                    "KOR",
    "viet nam":                 "VNM",
    "vietnam":                  "VNM",
    "turkiye":                  "TUR",
    "turkey":                   "TUR",
    "czechia":                  "CZE",
    "czech republic":           "CZE",
    "tanzania":                 "TZA",
    "uk":                       "GBR",
    "united kingdom":           "GBR",
    "bosnia & herzegovina":     "BIH",
    "bosnia and herzegovina":   "BIH",
    "congo, dem. rep.":         "COD",
    "congo, rep.":              "COG",
    "taiwan":                   "TWN",
})

merged["iso3"] = (
    merged["country_match"]
    .str.strip()
    .str.casefold()
    .map(name_to_iso3_mig)
)

n_before  = len(merged)
merged    = merged.merge(
    mig_df[["iso3", "migration_entropy", "migration_herf"]], on="iso3", how="left"
)
n_matched = merged["migration_entropy"].notna().sum()
print(f"  Matched migration stats to {n_matched}/{n_before} recipe countries")
unmatched = merged.loc[merged["migration_entropy"].isna(), "country"].tolist()
if unmatched:
    print(f"  Countries without migration data: {unmatched}")

# ===========================================================================
# SAVE COUNTRY-LEVEL TABLE
# ===========================================================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
save_cols = [c for c in merged.columns if c not in ["country_key", "country_match", "iso3"]]
merged[save_cols].to_csv(
    OUTPUT_DIR / "cuisine_diversity_fractionalization.csv",
    index=False, encoding="utf-8-sig"
)
print(f"  Saved master table.")

merged["log_n_recipes"] = np.log(merged["n_recipes"])

# ===========================================================================
# SCATTER PLOTS — ALESINA FRACTIONALIZATION
# ===========================================================================

DIVERSITY_VARS = {
    "jaccard_mean":           ("Cuisine Diversity\n(Mean Pairwise Jaccard Dissimilarity)",            False),
    "canonical_entropy_norm": ("Cuisine Diversity\n(Normalised Shannon Entropy, H / log k)",          False),
    "mean_richness":          ("Cuisine Diversity\n(Mean Canonical Ingredients per Recipe)",           False),
    "mean_recipe_surprise":   ("Recipe Creativity\n(Mean Negative PMI - higher = more unusual)",      False),
    "canonical_entropy_raw":  ("Cuisine Diversity\n(Raw Shannon Entropy - robustness, conditioned)",  True),
}

print("\nGenerating scatter plots vs. Alesina fractionalization ...")
for div_col, (div_label, condition) in DIVERSITY_VARS.items():
    subdir = OUTPUT_DIR / div_col
    subdir.mkdir(parents=True, exist_ok=True)
    cond_note = "conditional on log recipe count" if condition else "unconditional"
    for frac_col, frac_label in FRAC_VARS.items():
        out_png = subdir / f"{div_col}_vs_{frac_col}.png"
        title   = (f"{div_col.replace('_', ' ').title()} vs "
                   f"{frac_col.title()} Fractionalization\n({cond_note})")
        make_scatter(
            df=merged, x_col=frac_col, y_col=div_col,
            x_label=frac_label, y_label=div_label,
            title=title, out_path=out_png, condition=condition,
        )

# ===========================================================================
# SCATTER PLOTS — PUTTERMAN & WEIL MIGRATION DIVERSITY
# ===========================================================================

print("\nGenerating scatter plots vs. Putterman & Weil migration diversity ...")
for div_col, (div_label, condition) in DIVERSITY_VARS.items():
    subdir = OUTPUT_DIR / "migration" / div_col
    subdir.mkdir(parents=True, exist_ok=True)
    cond_note = "conditional on log recipe count" if condition else "unconditional"
    for mig_col, mig_label in MIGRATION_VARS.items():
        out_png = subdir / f"{div_col}_vs_{mig_col}.png"
        title   = (f"{div_col.replace('_', ' ').title()} vs "
                   f"{mig_col.replace('_', ' ').title()}\n({cond_note})")
        make_scatter(
            df=merged, x_col=mig_col, y_col=div_col,
            x_label=mig_label, y_label=div_label,
            title=title, out_path=out_png, condition=condition,
        )

# ===========================================================================
# CORRELATION SUMMARY TABLE — BOTH SETS OF PREDICTORS
# ===========================================================================

print("\n--- Correlations ---")
all_x_vars = {**FRAC_VARS, **MIGRATION_VARS}
rows_summary = []
for div_col, (_, condition) in DIVERSITY_VARS.items():
    for x_col, x_label in all_x_vars.items():
        cols = [div_col, x_col] + (["log_n_recipes"] if condition else [])
        d = merged[cols].dropna()
        if len(d) < 10:
            continue
        if condition:
            ctrl = d[["log_n_recipes"]].values
            x_r, _ = partial_residuals(d[x_col].values.astype(float), ctrl)
            y_r, _ = partial_residuals(d[div_col].values.astype(float), ctrl)
            mask = ~np.isnan(x_r) & ~np.isnan(y_r)
            xv, yv = x_r[mask], y_r[mask]
        else:
            mask = np.ones(len(d), dtype=bool)
            xv   = d[x_col].values.astype(float)
            yv   = d[div_col].values.astype(float)
        if mask.sum() < 5:
            continue
        r, p = stats.pearsonr(xv, yv)
        rows_summary.append({
            "diversity_index": div_col,
            "conditioned":     condition,
            "x_variable":      x_col,
            "x_source":        "Alesina" if x_col in FRAC_VARS else "Putterman",
            "r":               round(r, 4),
            "p_value":         round(p, 4),
            "n":               int(mask.sum()),
        })

summary = pd.DataFrame(rows_summary)
print(summary.to_string(index=False))
summary.to_csv(OUTPUT_DIR / "correlations_summary_all.csv", index=False)

# ===========================================================================
# 4x3 SUMMARY FIGURE — ALESINA
# ===========================================================================

print("\nGenerating 4x3 summary figure (Alesina) ...")

MAIN_DIVERSITY_VARS = {
    "jaccard_mean":           "Jaccard dissimilarity",
    "canonical_entropy_norm": "Normalised entropy",
    "mean_richness":          "Ingredient richness",
    "mean_recipe_surprise":   "PMI surprise",
}
frac_labels_short = {
    "ethnic":   "Ethnic frac.",
    "language": "Linguistic frac.",
    "religion": "Religious frac.",
}

fig, axes = plt.subplots(nrows=4, ncols=3, figsize=(15, 12))
for row_i, (div_col, div_short) in enumerate(MAIN_DIVERSITY_VARS.items()):
    for col_j, (frac_col, frac_short) in enumerate(frac_labels_short.items()):
        ax   = axes[row_i][col_j]
        d    = merged[[div_col, frac_col, COUNTRY_COL]].dropna()
        if len(d) < 8:
            ax.axis("off")
            continue
        xp = d[frac_col].values.astype(float)
        yp = d[div_col].values.astype(float)
        slope, intercept, r, pval, _ = stats.linregress(xp, yp)
        stars = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""
        ax.scatter(xp, yp, s=14, alpha=0.55, color="#2c6fad", zorder=3)
        texts = [ax.text(xi, yi, cn, fontsize=6.5, alpha=0.7)
                 for xi, yi, cn in zip(xp, yp, d[COUNTRY_COL].values)]
        adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle="-", color="grey", lw=0.3))
        xl = np.linspace(xp.min(), xp.max(), 100)
        ax.plot(xl, intercept + slope * xl, color="#c0392b", linewidth=1.2, zorder=4)
        ax.set_title(f"r={r:.2f}{stars}  N={len(d)}", fontsize=10, pad=4)
        if row_i == 3:
            ax.set_xlabel(frac_short, fontsize=10)
        if col_j == 0:
            ax.set_ylabel(div_short, fontsize=10)
        style_axes_panel(ax)

plt.suptitle(
    "Cuisine Diversity & Recipe Creativity vs Fractionalization (Alesina et al. 2003)",
    fontsize=12, y=1.01
)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "summary_cuisine_vs_alesina_4x3.png", dpi=200, bbox_inches="tight")
plt.close()
print("  Saved: summary_cuisine_vs_alesina_4x3.png")

# ===========================================================================
# 4x2 SUMMARY FIGURE — PUTTERMAN & WEIL
# ===========================================================================

print("Generating 4x2 summary figure (Putterman & Weil) ...")

mig_labels_short = {
    "migration_entropy": "Ancestry entropy",
    "migration_herf":    "Ancestry Herfindahl",
}

fig, axes = plt.subplots(nrows=4, ncols=2, figsize=(10, 12))
for row_i, (div_col, div_short) in enumerate(MAIN_DIVERSITY_VARS.items()):
    for col_j, (mig_col, mig_short) in enumerate(mig_labels_short.items()):
        ax   = axes[row_i][col_j]
        d    = merged[[div_col, mig_col, COUNTRY_COL]].dropna()
        if len(d) < 8:
            ax.axis("off")
            continue
        xp = d[mig_col].values.astype(float)
        yp = d[div_col].values.astype(float)
        slope, intercept, r, pval, _ = stats.linregress(xp, yp)
        stars = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""
        ax.scatter(xp, yp, s=14, alpha=0.55, color="#2c6fad", zorder=3)
        texts = [ax.text(xi, yi, cn, fontsize=6.5, alpha=0.7)
                 for xi, yi, cn in zip(xp, yp, d[COUNTRY_COL].values)]
        adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle="-", color="grey", lw=0.3))
        xl = np.linspace(xp.min(), xp.max(), 100)
        ax.plot(xl, intercept + slope * xl, color="#c0392b", linewidth=1.2, zorder=4)
        ax.set_title(f"r={r:.2f}{stars}  N={len(d)}", fontsize=10, pad=4)
        if row_i == 3:
            ax.set_xlabel(mig_short, fontsize=10)
        if col_j == 0:
            ax.set_ylabel(div_short, fontsize=10)
        style_axes_panel(ax)

plt.suptitle(
    "Cuisine Diversity & Recipe Creativity vs Ancestry Diversity\n"
    "Putterman & Weil (2010) World Migration Matrix",
    fontsize=12, y=1.01
)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "summary_cuisine_vs_putnam_4x2.png", dpi=200, bbox_inches="tight")
plt.close()
print("  Saved: summary_cuisine_vs_putnam_4x2.png")

# ===========================================================================
# LOAD CONTROLS & BUILD REG_DF
# ===========================================================================

print("\nLoading controls ...")
ctrl_raw = pd.read_stata(CONTROLS_PATH)
if "country" in ctrl_raw.columns:
    ctrl_raw["country_key"] = ctrl_raw["country"].str.strip().str.casefold()
ctrl_raw = ctrl_raw.drop_duplicates(subset=["country_key"])
avail_controls = [c for c in FULL_CONTROLS if c in ctrl_raw.columns]
print(f"  Controls available: {avail_controls}")

reg_df = merged.copy()
reg_df["country_key"] = reg_df[COUNTRY_COL].str.strip().str.casefold()
reg_df = reg_df.merge(
    ctrl_raw[["country_key", "continent"] + avail_controls],
    on="country_key", how="left"
)
cont_dummies = pd.get_dummies(reg_df["continent"], prefix="cont", drop_first=True, dtype=float)
cont_dummies.columns = [re.sub(r"\W+", "_", c) for c in cont_dummies.columns]
reg_df = pd.concat([reg_df, cont_dummies], axis=1)
cont_cols = list(cont_dummies.columns)

# ===========================================================================
# REGRESSIONS — ALESINA OUTCOMES
# ===========================================================================

print("\n" + "="*70)
print("REGRESSIONS (Alesina): fractionalization ~ normalised entropy")
print("="*70)
entropy_results = run_regressions(
    reg_df, "canonical_entropy_norm", "canonical_entropy_norm",
    cont_cols, avail_controls, outcome_vars=FRAC_OUTCOMES,
)
entropy_results.to_csv(OUTPUT_DIR / "regressions_frac_on_entropy.csv", index=False)

print("\n" + "="*70)
print("REGRESSIONS (Alesina): fractionalization ~ PMI recipe surprise")
print("="*70)
pmi_results = run_regressions(
    reg_df, "mean_recipe_surprise", "mean_recipe_surprise",
    cont_cols, avail_controls, outcome_vars=FRAC_OUTCOMES,
)
pmi_results.to_csv(OUTPUT_DIR / "regressions_frac_on_pmi_surprise.csv", index=False)

print("\n" + "="*70)
print("REGRESSIONS (Alesina): fractionalization ~ Jaccard dissimilarity")
print("="*70)
jaccard_frac_results = run_regressions(
    reg_df, "jaccard_mean", "jaccard_mean",
    cont_cols, avail_controls, outcome_vars=FRAC_OUTCOMES,
)
jaccard_frac_results.to_csv(OUTPUT_DIR / "regressions_frac_on_jaccard.csv", index=False)

# ===========================================================================
# REGRESSIONS — PUTTERMAN & WEIL OUTCOMES
# ===========================================================================

print("\n" + "="*70)
print("REGRESSIONS (Putterman): migration diversity ~ normalised entropy")
print("="*70)
mig_entropy_results = run_regressions(
    reg_df, "canonical_entropy_norm", "canonical_entropy_norm",
    cont_cols, avail_controls, outcome_vars=list(MIGRATION_VARS.keys()),
)
mig_entropy_results.to_csv(OUTPUT_DIR / "regressions_migration_on_entropy.csv", index=False)

print("\n" + "="*70)
print("REGRESSIONS (Putterman): migration diversity ~ PMI recipe surprise")
print("="*70)
mig_pmi_results = run_regressions(
    reg_df, "mean_recipe_surprise", "mean_recipe_surprise",
    cont_cols, avail_controls, outcome_vars=list(MIGRATION_VARS.keys()),
)
mig_pmi_results.to_csv(OUTPUT_DIR / "regressions_migration_on_pmi_surprise.csv", index=False)

print("\n" + "="*70)
print("REGRESSIONS (Putterman): migration diversity ~ Jaccard dissimilarity")
print("="*70)
jaccard_mig_results = run_regressions(
    reg_df, "jaccard_mean", "jaccard_mean",
    cont_cols, avail_controls, outcome_vars=list(MIGRATION_VARS.keys()),
)
jaccard_mig_results.to_csv(OUTPUT_DIR / "regressions_migration_on_jaccard.csv", index=False)

all_results = pd.concat(
    [entropy_results, pmi_results, jaccard_frac_results,
     mig_entropy_results, mig_pmi_results, jaccard_mig_results],
    ignore_index=True,
)
all_results.to_csv(OUTPUT_DIR / "regressions_all.csv", index=False)
print(f"\n  Saved combined results -> {OUTPUT_DIR / 'regressions_all.csv'}")

# ===========================================================================
# DIAGNOSTICS
# ===========================================================================

print("\n--- Cross-correlations between ethnic/migration measures ---")
diag_vars = ["ethnic", "language", "religion", "migration_entropy", "migration_herf"]
diag_df = merged[diag_vars].dropna()
print(f"  N = {len(diag_df)} countries with all measures")
print(diag_df.corr().round(3).to_string())
diag_df.corr().round(3).to_csv(OUTPUT_DIR / "crosscorr_ethnic_migration.csv")

print("\n--- Cross-correlations between cuisine diversity measures ---")
cuisine_vars = ["jaccard_mean", "canonical_entropy_norm", "mean_recipe_surprise"]
cuisine_diag = merged[cuisine_vars].dropna()
print(f"  N = {len(cuisine_diag)} countries with all cuisine measures")
print(cuisine_diag.corr().round(3).to_string())

# ===========================================================================
# WORLD MAP: Herfindahl index (Putterman & Weil migration matrix)
# ===========================================================================

print("\nGenerating world map of ancestry Herfindahl index (Putterman & Weil) ...")

try:
    import geopandas as gpd
    import urllib.request
    import matplotlib.colors as mcolors

    # Re-compute for all 165 countries (not just recipe-matched subset)
    mig_raw_map = pd.read_excel(MIGRATION_MATRIX_XLS, engine="xlrd")
    mig_raw_map = mig_raw_map.drop(columns=["update"], errors="ignore")
    origin_cols_map = [c for c in mig_raw_map.columns if c not in ["wbcode", "wbname"]]
    mig_raw_map["iso3"] = mig_raw_map["wbcode"].replace(WB_TO_ISO3)
    mig_raw_map = mig_raw_map.dropna(subset=["iso3"])

    herf_rows = []
    for _, row in mig_raw_map.iterrows():
        shares = row[origin_cols_map].values.astype(float)
        shares = shares[np.isfinite(shares) & (shares > 0)]
        if len(shares) == 0:
            continue
        herf_rows.append({
            "iso3":           row["iso3"],
            "migration_herf": 1.0 - np.sum(shares ** 2),
        })
    herf_full = pd.DataFrame(herf_rows).set_index("iso3")
    print(f"  Herfindahl computed for {len(herf_full)} countries")

    NE_URL    = ("https://naturalearth.s3.amazonaws.com/110m_cultural/"
                 "ne_110m_admin_0_countries.zip")
    _ne_local = OUTPUT_DIR / "ne_110m_admin_0_countries.zip"
    if not _ne_local.exists():
        print("  Downloading Natural Earth 110m countries shapefile ...")
        urllib.request.urlretrieve(NE_URL, str(_ne_local))
    world = gpd.read_file(f"zip://{_ne_local}")

    iso_col = next(
        (c for c in ["ISO_A3", "ADM0_A3", "iso_a3", "ISO_A3_EH"]
         if c in world.columns), None
    )
    if iso_col is None:
        raise ValueError(f"No ISO3 column found. Columns: {list(world.columns)}")
    print(f"  Using shapefile ISO column: {iso_col}")

    world_m = world.merge(
        herf_full.reset_index(), left_on=iso_col, right_on="iso3", how="left"
    )
    if "CONTINENT" in world_m.columns:
        world_m = world_m[world_m["CONTINENT"] != "Antarctica"]
    else:
        world_m = world_m[~world_m[iso_col].isin(["ATA"])]

    fig, ax = plt.subplots(figsize=(16, 7))
    ax.set_facecolor("#e8f0f7")
    world_m[world_m["migration_herf"].isna()].plot(
        ax=ax, color="#cccccc", edgecolor="#aaaaaa", linewidth=0.3
    )
    world_m[world_m["migration_herf"].notna()].plot(
        column="migration_herf", ax=ax, cmap="YlOrRd", vmin=0, vmax=1,
        edgecolor="#aaaaaa", linewidth=0.3, legend=False,
    )
    sm = plt.cm.ScalarMappable(cmap="YlOrRd", norm=mcolors.Normalize(vmin=0, vmax=1))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation="horizontal",
                        shrink=0.45, pad=0.02, fraction=0.03)
    cbar.set_label("Ancestry Herfindahl index  (1 - Sp_j^2)", fontsize=13)
    cbar.ax.tick_params(labelsize=11)
    ax.set_title(
        "Ancestry Diversity - Herfindahl Index\n"
        "Putterman & Weil (2010) World Migration Matrix  "
        "(year-1500 origins of current population)",
        fontsize=14, pad=12,
    )
    ax.axis("off")
    plt.tight_layout()
    map_out = OUTPUT_DIR / "map_migration_herfindahl.png"
    plt.savefig(map_out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved -> {map_out}")

except ImportError:
    print("  geopandas not installed - skipping world map.")
    print("  Install with:  conda install geopandas  or  pip install geopandas")
except Exception as e:
    print(f"  World map skipped: {e}")

print("\nDone.")