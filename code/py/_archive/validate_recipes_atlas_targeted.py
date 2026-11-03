# -*- coding: utf-8 -*-
"""
TARGETED validation of recipe ingredient-category shares against the
Giuliano-Nunn Ancestral Characteristics Database (Ethnographic Atlas).

Instead of every EA variable x every category, we pair a handful of
subsistence variables with the ingredient categories they should plausibly move:

  1_subsistence      EA001-005 (% dependence on gathering/hunting/fishing/husbandry/agriculture)
  2_ag_intensity_plow  v28 agricultural intensity + v39 plow (each coloured by the other)
  3_main_crop        v29 major crop type (cereal / roots / tree fruit / vegetable)
  4_milking_animals  v41 milking + v40 domestic animal type (coloured by milking),
                     plus animal x milking interaction regressions

Differences vs validate_recipes_atlas.py:
  * v39 uses the correct codes (grp2 absent / grp3 not aboriginal / grp4 aboriginal;
    grp1 is "missing data").
  * Ordinal/continuous indices are renormalised over non-missing shares.
  * v28 follows the EA codebook order (none < casual < extensive/shifting <
    horticulture < intensive < irrigated).
  * egg + eggs categories are merged.
"""

import os
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
from scipy import stats

warnings.filterwarnings("ignore")

# =============================================================================
# PATHS
# =============================================================================
country_ingredient = (
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes"
    r"\ingredients\country_category_shares.csv"
)
ea_path = (
    r"C:\Users\stevebc\Dropbox\Culture and Education in Africa\Data"
    r"\Ethno Atlas Giuliano-Nunn Data"
    r"\Ancestral_Characteristics_Database_Baseline_Version_1_1.dta"
)
controls_path = (
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded"
    r"\iv_versatility\first_stage_native_m_c.dta"
)
OUTPUT_DIR = r"C:\Users\stevebc\Dropbox\Cuisine_complexity\3_results\temp\ea_targeted"
SHARE_VAR = "share_excluding_unmatched"
MIN_COVERAGE = 0.5   # min. share of a country's EA groups with non-missing data
MIN_N = 10

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
    # added vs validate_recipes_atlas.py (40 recipe countries were unmapped)
    "Aruba": "ABW", "Bahamas": "BHS", "Barbados": "BRB", "Belize": "BLZ",
    "Benin": "BEN", "Bosnia And Herzegovina": "BIH", "Cabo Verde": "CPV",
    "Comoros": "COM", "Cote D'Ivoire": "CIV", "Cote Divoire": "CIV",
    "Cuba": "CUB", "Cyprus": "CYP", "Dominica": "DMA", "Eritrea": "ERI",
    "Fiji": "FJI", "Guinea": "GIN", "Guyana": "GUY", "Iceland": "ISL",
    "Kuwait": "KWT", "Laos": "LAO", "Lebanon": "LBN", "Liberia": "LBR",
    "Libya": "LBY", "Liechtenstein": "LIE", "Luxembourg": "LUX",
    "Maldives": "MDV", "Malta": "MLT", "Mauritius": "MUS", "Mongolia": "MNG",
    "Myanmar": "MMR", "North Korea": "PRK", "Samoa": "WSM",
    "Singapore": "SGP", "Solomon Islands": "SLB", "Syria": "SYR",
    "Tajikistan": "TJK", "Tonga": "TON", "Turkmenistan": "TKM",
    "Tuvalu": "TUV", "United Arab Emirates": "ARE", "Vanuatu": "VUT",
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
# EA VARIABLE CONSTRUCTION  (all indices renormalised over non-missing shares)
# =============================================================================
MIDPOINTS = {  # % dependence bins for v1-v5
    "grp1": 2.5, "grp2": 10.5, "grp3": 20.5, "grp4": 30.5, "grp5": 40.5,
    "grp6": 50.5, "grp7": 60.5, "grp8": 70.5, "grp9": 80.5, "grp10": 93.0,
}

ORDINAL_SPEC = {
    "v28": {"v28_grp2": 0, "v28_grp3": 1, "v28_grp4": 2,
            "v28_grp5": 3, "v28_grp6": 4, "v28_grp7": 5},
    "v39": {"v39_grp2": 0, "v39_grp3": 1, "v39_grp4": 2},
    "v41": {"v41_grp2": 0, "v41_grp3": 1},
}

# dummy-style shares: output name -> source grp column
SHARE_SPEC = {
    "v29_cereal":   "v29_grp7",
    "v29_roots":    "v29_grp6",
    "v29_treefruit": "v29_grp5",
    "v29_veg":      "v29_grp4",
    "v40_bovine":   "v40_grp8",
    "v40_sheepgoat": "v40_grp4",
    "v40_camelid":  "v40_grp7",
    "v40_pig":      "v40_grp3",
    "v40_equine":   "v40_grp5",
    "v40_none":     "v40_grp2",
}
# denominators for shares: valid (non-missing) groups of the parent variable
SHARE_PARENT = {"v29": [f"v29_grp{i}" for i in range(2, 8)],
                "v40": [f"v40_grp{i}" for i in range(2, 9)]}

LABELS = {
    "v1":  "Gathering [EA001]: % subsistence dependence",
    "v2":  "Hunting [EA002]: % subsistence dependence",
    "v3":  "Fishing [EA003]: % subsistence dependence",
    "v4":  "Animal husbandry [EA004]: % subsistence dependence",
    "v5":  "Agriculture [EA005]: % subsistence dependence",
    "v28": "Agricultural intensity [EA028]\n(0 none, 1 casual, 2 extensive/shifting, 3 horticulture, 4 intensive, 5 irrigated)",
    "v39": "Plow cultivation [EA039]\n(0 absent, 1 not aboriginal, 2 aboriginal)",
    "v41": "Milking [EA041]: share of ancestry milking more than sporadically",
    "v29_cereal":    "Major crop = cereal grains [EA029]: share",
    "v29_roots":     "Major crop = roots/tubers [EA029]: share",
    "v29_treefruit": "Major crop = tree fruits [EA029]: share",
    "v29_veg":       "Major crop = vegetables [EA029]: share",
    "v40_bovine":    "Domestic animals = bovines [EA040]: share",
    "v40_sheepgoat": "Domestic animals = sheep/goats only [EA040]: share",
    "v40_camelid":   "Domestic animals = camels/llamas [EA040]: share",
    "v40_pig":       "Domestic animals = pigs only [EA040]: share",
    "v40_equine":    "Domestic animals = equines [EA040]: share",
    "v40_none":      "Domestic animals = none/near none [EA040]: share",
}
SHORT = {  # for annotations / tables
    "v1": "gathering", "v2": "hunting", "v3": "fishing", "v4": "husbandry",
    "v5": "agriculture", "v28": "ag intensity", "v39": "plow", "v41": "milking",
}
PERCENT_X = {"v1", "v2", "v3", "v4", "v5"}
SHARE_X = set(SHARE_SPEC) | {"v41"}   # 0-1 shares -> display as %

CATEGORY_PRETTY = {
    "acid_citrus_vinegar": "Acids (citrus/vinegar)", "alcohol": "Alcohol",
    "condiment_sauce": "Condiments & sauces", "dairy": "Dairy", "egg": "Eggs",
    "fish_seafood": "Fish & seafood", "fruit": "Fruit",
    "grain_starch": "Cereals, grains & starches", "herb": "Herbs",
    "leavening_thickener": "Leavening & thickeners", "legume": "Legumes",
    "liquid_stock": "Liquids & stock", "meat": "Meat", "nut_seed": "Nuts & seeds",
    "oil_fat": "Oils & fats", "poultry": "Poultry",
    "processed_prepared_food": "Processed foods", "spice": "Spices",
    "sweetener": "Sweeteners", "vegetable": "Vegetables",
}


YLAB = {}   # optional full y-axis labels per category (used by staples script)


def pretty(cat):
    return CATEGORY_PRETTY.get(cat, cat.replace("_", " ").title())


def build_ea(ea_raw):
    out = pd.DataFrame(index=ea_raw.index)
    # v1-v5: weighted mean midpoint over non-missing shares
    for v in ["v1", "v2", "v3", "v4", "v5"]:
        cols = [c for c in ea_raw.columns if c.startswith(f"{v}_grp")
                and c.split("_", 1)[1] in MIDPOINTS]
        w = ea_raw[cols].fillna(0)
        tot = w.sum(axis=1)
        val = sum(w[c] * MIDPOINTS[c.split("_", 1)[1]] for c in cols) / tot
        val[tot < MIN_COVERAGE] = np.nan
        out[v] = val
    # ordinals: weighted mean over valid groups
    for v, spec in ORDINAL_SPEC.items():
        cols = [c for c in spec if c in ea_raw.columns]
        w = ea_raw[cols].fillna(0)
        tot = w.sum(axis=1)
        val = sum(w[c] * spec[c] for c in cols) / tot
        val[tot < MIN_COVERAGE] = np.nan
        out[v] = val
    # shares among valid groups of the parent variable
    for name, src in SHARE_SPEC.items():
        parent = name.split("_")[0]
        pc = [c for c in SHARE_PARENT[parent] if c in ea_raw.columns]
        tot = ea_raw[pc].fillna(0).sum(axis=1)
        val = ea_raw[src].fillna(0) / tot
        val[tot < MIN_COVERAGE] = np.nan
        out[name] = val
    return out


# =============================================================================
# STATS + PLOTTING
# =============================================================================
def partial_resid(s, cont_d):
    """Residualise series s on continent dummies (rows with s observed)."""
    d = s.dropna()
    X = sm.add_constant(cont_d.loc[d.index], has_constant="add")
    return pd.Series(sm.OLS(d.values, X.values).fit().resid, index=d.index)


def pair_stats(df, xv, cat, cont_d):
    sub = df[[xv, cat]].dropna()
    if len(sub) < MIN_N or sub[xv].nunique() < 2 or sub[cat].nunique() < 2:
        return None
    r, p = stats.pearsonr(sub[xv], sub[cat])
    rho, rp = stats.spearmanr(sub[xv], sub[cat])
    out = dict(x=xv, category=cat, n=len(sub), pearson_r=r, pearson_p=p,
               spearman_rho=rho, spearman_p=rp,
               partial_r_contFE=np.nan, partial_p_contFE=np.nan)
    if cont_d is not None:
        sub2 = sub.join(cont_d, how="inner").dropna()
        if len(sub2) >= MIN_N + cont_d.shape[1] and sub2[xv].nunique() > 1:
            rx = partial_resid(sub2[xv], cont_d)
            ry = partial_resid(sub2[cat], cont_d)
            pr, pp = stats.pearsonr(rx, ry)
            out.update(partial_r_contFE=pr, partial_p_contFE=pp)
    return out


def style_axes(ax):
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_linewidth(0.8)
        ax.spines[s].set_color("black")
    ax.tick_params(axis="both", length=4, width=0.8)


def xscale(xv, x):
    return x * 100 if xv in SHARE_X else x


def draw_pair(ax, df, xv, cat, cv, st, labels=True, small=False):
    sub = df[[xv, cat] + ([cv] if cv else [])].dropna()
    x = xscale(xv, sub[xv].values)
    y = sub[cat].values * 100
    if cv:
        cvals = sub[cv].values
        sc = ax.scatter(x, y, s=28 if not small else 14, c=cvals, cmap="viridis",
                        alpha=0.85, edgecolors="none", zorder=4,
                        vmin=df[cv].min(), vmax=df[cv].max())
    else:
        sc = ax.scatter(x, y, s=28 if not small else 14, alpha=0.55,
                        color="#2171b5", edgecolors="none", zorder=4)
    m, b = np.polyfit(x, y, 1)
    xl = np.linspace(x.min(), x.max(), 100)
    ax.plot(xl, m * xl + b, color="#e63946", lw=1.4, zorder=3)
    if labels:
        for xi, yi, lb in zip(x, y, sub.index):
            ax.annotate(lb, (xi, yi), xytext=(3, 2), textcoords="offset points",
                        fontsize=5, color="#444444", alpha=0.8, zorder=5)
    pr = st["partial_r_contFE"]
    txt = (f"r={st['pearson_r']:.2f} (p={st['pearson_p']:.3f}); "
           f"\u03c1={st['spearman_rho']:.2f}; "
           + ("" if np.isnan(pr) else f"cont-FE r={pr:.2f}; ")
           + f"n={st['n']}")
    ax.set_title(txt, fontsize=7 if small else 9)
    ax.set_ylabel(YLAB.get(cat, f"{pretty(cat)} (% of ingredients)"),
                  fontsize=7 if small else 9)
    style_axes(ax)
    return sc


def single_figure(df, xv, cat, cv, st, path):
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    sc = draw_pair(ax, df, xv, cat, cv, st)
    ax.set_xlabel(LABELS[xv] + (" (%)" if xv in SHARE_X else ""), fontsize=9)
    if cv:
        cb = fig.colorbar(sc, ax=ax, pad=0.02)
        cb.set_label(LABELS[cv].replace("\n", " "), fontsize=7)
        cb.ax.tick_params(labelsize=7)
    if xv == "v39":
        ax.set_xticks([0, 1, 2])
    fig.suptitle(f"{SHORT.get(xv, xv)} vs {pretty(cat)}", fontsize=12, fontweight="bold")
    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def contact_sheet(df, pairs, stats_map, theme, path, ncols=3):
    n = len(pairs)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(5.2 * ncols, 3.9 * nrows),
                             squeeze=False)
    for ax in axes.ravel():
        ax.axis("off")
    for ax, (xv, cat, cv) in zip(axes.ravel(), pairs):
        st = stats_map.get((xv, cat, cv))
        if st is None:
            continue
        ax.axis("on")
        draw_pair(ax, df, xv, cat, cv, st, labels=False, small=True)
        xl = SHORT.get(xv, xv) + (" (%)" if xv in SHARE_X else "")
        ax.set_xlabel(xl if xv in SHORT else LABELS[xv].split(":")[0], fontsize=7)
        ax.tick_params(labelsize=7)
    fig.suptitle(theme, fontsize=13, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)


# =============================================================================
# THEMES: (x variable, ingredient category, colour variable or None)
# =============================================================================
def pairs_for(x, cats, cv=None):
    return [(x, c, cv) for c in cats]


THEMES = {
    "1_subsistence": (
        pairs_for("v1", ["vegetable", "fruit", "nut_seed", "herb", "legume"])
        + pairs_for("v2", ["meat", "poultry"])
        + pairs_for("v3", ["fish_seafood"])
        + pairs_for("v4", ["meat", "dairy", "poultry", "egg", "oil_fat"])
        + pairs_for("v5", ["grain_starch", "vegetable", "legume", "sweetener",
                           "leavening_thickener"])
    ),
    "2_ag_intensity_plow": (
        pairs_for("v28", ["grain_starch", "leavening_thickener", "sweetener",
                          "legume", "oil_fat", "alcohol", "dairy"])
        + pairs_for("v28", ["grain_starch", "leavening_thickener", "sweetener",
                            "dairy"], cv="v39")
        + pairs_for("v39", ["grain_starch", "leavening_thickener", "sweetener",
                            "legume", "oil_fat", "alcohol", "dairy"])
        + pairs_for("v39", ["grain_starch", "leavening_thickener", "sweetener",
                            "dairy"], cv="v28")
    ),
    "3_main_crop": (
        pairs_for("v29_cereal", ["grain_starch", "leavening_thickener", "alcohol",
                                 "sweetener"])
        + pairs_for("v29_roots", ["grain_starch", "vegetable", "oil_fat"])
        + pairs_for("v29_treefruit", ["fruit", "sweetener", "nut_seed", "oil_fat"])
        + pairs_for("v29_veg", ["vegetable", "legume", "herb"])
    ),
    "4_milking_animals": (
        pairs_for("v41", ["dairy", "oil_fat", "meat", "egg"])
        + pairs_for("v40_bovine", ["dairy", "meat", "oil_fat"], cv="v41")
        + pairs_for("v40_sheepgoat", ["dairy", "meat"], cv="v41")
        + pairs_for("v40_camelid", ["dairy", "meat"], cv="v41")
        + pairs_for("v40_equine", ["dairy", "meat"], cv="v41")
        + pairs_for("v40_pig", ["meat", "oil_fat", "dairy"])
        + pairs_for("v40_none", ["meat", "dairy"])
    ),
}


# =============================================================================
# MAIN
# =============================================================================
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- recipe category shares -> wide -----------------------------------
    ing = pd.read_csv(country_ingredient)
    ing["adm0"] = to_iso3(ing["country"])
    miss = ing.loc[ing["adm0"].isna(), "country"].unique()
    if len(miss):
        print("WARNING unmapped countries:", list(miss))
    ing = ing.dropna(subset=["adm0"])
    wide = ing.pivot_table(index="adm0", columns="category",
                           values=SHARE_VAR, aggfunc="first")
    wide.columns.name = None
    # merge duplicate egg categories
    egg_cols = [c for c in ["egg", "eggs"] if c in wide.columns]
    wide["egg"] = wide[egg_cols].sum(axis=1, min_count=1)
    if "eggs" in wide.columns:
        wide = wide.drop(columns="eggs")
    print(f"Recipe matrix: {wide.shape[0]} countries x {wide.shape[1]} categories")

    # --- EA -----------------------------------------------------------------
    ea_raw = pd.read_stata(ea_path)
    key = "isocode" if "isocode" in ea_raw.columns else "adm0"
    ea_raw["adm0"] = ea_raw[key].str.strip().str.upper()
    ea_raw = ea_raw.dropna(subset=["adm0"]).drop_duplicates("adm0").set_index("adm0")
    ea = build_ea(ea_raw)
    print("\nEA variable coverage (non-missing countries):")
    print(ea.notna().sum().to_string())

    # --- continents ------------------------------------------------------------
    ctrl = pd.read_stata(controls_path)
    ctrl["adm0"] = ctrl["adm0"].str.strip().str.upper()
    ctrl = ctrl.dropna(subset=["adm0"]).drop_duplicates("adm0").set_index("adm0")
    cont_d = pd.get_dummies(ctrl["continent"], prefix="cont",
                            drop_first=True).astype(float)

    df = wide.join(ea, how="inner")
    cont_d = cont_d.reindex(df.index)
    print(f"\nCountries with recipes AND EA: {len(df)}")

    # --- run themes ---------------------------------------------------------------
    all_rows = []
    for theme, pairs in THEMES.items():
        tdir = os.path.join(OUTPUT_DIR, theme)
        os.makedirs(tdir, exist_ok=True)
        print(f"\n=== {theme} ({len(pairs)} pairs) ===")
        smap = {}
        for xv, cat, cv in pairs:
            if cat not in df.columns:
                print(f"  SKIP {cat}: not in recipe data")
                continue
            st = pair_stats(df, xv, cat, cont_d.dropna(how="all", axis=1))
            if st is None:
                continue
            smap[(xv, cat, cv)] = st
            tag = f"_by_{cv}" if cv else ""
            single_figure(df, xv, cat, cv, st,
                          os.path.join(tdir, f"scatter_{xv}_vs_{cat}{tag}.png"))
            all_rows.append({**st, "theme": theme, "colour_var": cv})
            print(f"  {xv:14s} {cat:22s} r={st['pearson_r']:+.2f} "
                  f"p={st['pearson_p']:.3f} contFE r={st['partial_r_contFE']:+.2f} "
                  f"n={st['n']}")
        contact_sheet(df, pairs, smap, theme,
                      os.path.join(OUTPUT_DIR, f"overview_{theme}.png"))

    res = pd.DataFrame(all_rows)
    res.to_csv(os.path.join(OUTPUT_DIR, "targeted_correlations.csv"), index=False)

    # --- animal x milking interaction regressions -----------------------------
    print("\n=== animal type x milking interaction (cat ~ animal*milk) ===")
    rows = []
    animals = ["v40_bovine", "v40_sheepgoat", "v40_camelid", "v40_equine", "v40_pig"]
    for a in animals:
        for cat in ["dairy", "meat", "oil_fat"]:
            if cat not in df.columns:
                continue
            d = df[[a, "v41", cat]].dropna()
            if len(d) < MIN_N + 4:
                continue
            Z = pd.DataFrame({"animal": d[a] - d[a].mean(),
                              "milk": d["v41"] - d["v41"].mean()})
            Z["animal_x_milk"] = Z["animal"] * Z["milk"]
            m = sm.OLS(d[cat] * 100, sm.add_constant(Z)).fit(cov_type="HC3")
            for term in ["animal", "milk", "animal_x_milk"]:
                rows.append(dict(animal=a, category=cat, term=term, n=len(d),
                                 coef=m.params[term], se=m.bse[term],
                                 p=m.pvalues[term], r2=m.rsquared))
    inter = pd.DataFrame(rows)
    inter.to_csv(os.path.join(OUTPUT_DIR, "animal_x_milking_interactions.csv"),
                 index=False)
    if len(inter):
        print(inter[inter.term == "animal_x_milk"].round(3).to_string(index=False))

    # EA data used (for checking)
    ea.to_csv(os.path.join(OUTPUT_DIR, "ea_variables_used.csv"))
    print("\nAll done ->", OUTPUT_DIR)


if __name__ == "__main__":
    main()
