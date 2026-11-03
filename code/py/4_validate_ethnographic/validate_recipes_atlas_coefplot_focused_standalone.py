# -*- coding: utf-8 -*-
"""
STANDALONE script: recipe <-> Ethnographic Atlas coefficient plots (focused set).

Self-contained version of validate_recipes_atlas_coefplot_focused.py (it does not
import any of the other validate_recipes_atlas_*.py scripts).  Produces, for
minimum-recipe cutoffs 5/10/20/30/50:

  coefplot_focused_min{c}.png                         plain
  coefplot_focused_labeled_min{c}.png                 + point estimate and stars
  coefplot_focused_labeled_xrange_min{c}.png          + fixed x-axis (-0.5 to 1.0)
  coefplot_focused_labeled_xrange_above_min{c}.png    + labels above the markers
  coefplot_focused_estimates.csv                      all estimates
  coefplot_focused_table.md / .tex                    stars table

Method
  Outcome (y): share of a country's RECIPES containing >= 1 ingredient of the
    category/group (presence, not share of ingredient mentions); denominator is all
    of the country's recipes, so presence is a lower bound.  Game meat is found by a
    keyword search of the raw ingredient text; the other outcomes use the canonical
    ingredient / category mapping.
  Ancestral variables (x): Giuliano-Nunn Ancestral Characteristics Database
    (Ethnographic Atlas), country level; indices renormalised over non-missing shares.
  Estimates: bivariate OLS with x and y standardised (coefficient = SD change in
    recipe-presence per SD of x), unweighted, HC3 robust 95% CI.
    Spec A: no controls.  Spec B: continent fixed effects (continents with < 3
    countries in a sample are dropped; if the dummies cover every country one dummy
    is dropped as the reference).  Both use the largest available sample.
  Stars: * p<0.10, ** p<0.05, *** p<0.01.

Usage:   python validate_recipes_atlas_coefplot_focused_standalone.py [output_dir]
Requires: pandas, numpy, statsmodels, matplotlib (Windows paths below as in the
          project; edit the PATHS block if the data move).
"""

import os
import re
import shutil
import sys
import tempfile
import textwrap
import time
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

# =============================================================================
# PATHS AND SETTINGS
# =============================================================================
LONG_PATH = (
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes"
    r"\ingredients\recipe_ingredient_categories_canonical_long.csv"
)
EA_PATH = (
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\raw"
    r"\Ethno Atlas Giuliano-Nunn Data"
    r"\Ancestral_Characteristics_Database_Baseline_Version_1_1.dta"
)
CONTROLS_PATH = (   # only used for the continent of each country
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded"
    r"\iv_versatility\first_stage_native_m_c.dta"
)
OUT = (sys.argv[1] if len(sys.argv) > 1 else
       r"C:\Users\stevebc\Dropbox\food4thought\analysis23\outputs\Figures\ethnographic\ea_plots")

CUTOFFS = [5, 10, 20, 30, 50]   # minimum recipes per country
MIN_COVERAGE = 0.5              # min. share of a country's EA groups with data
MIN_PER_CONTINENT = 3           # smaller continents are dropped from FE models

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
# ANCESTRAL (EA) VARIABLES
# =============================================================================
MIDPOINTS = {   # % dependence bins for v1-v5 (v2 hunting, v3 fishing, v4 husbandry)
    "grp1": 2.5, "grp2": 10.5, "grp3": 20.5, "grp4": 30.5, "grp5": 40.5,
    "grp6": 50.5, "grp7": 60.5, "grp8": 70.5, "grp9": 80.5, "grp10": 93.0,
}
ORDINAL_SPEC = {   # v39 plough use (0 absent, 1 not aboriginal, 2 aboriginal);
    #               v41 milking (0 little/none, 1 milked more than sporadically)
    "v39": {"v39_grp2": 0, "v39_grp3": 1, "v39_grp4": 2},
    "v41": {"v41_grp2": 0, "v41_grp3": 1},
}


def build_ea(ea_raw):
    """Country-level indices, renormalised over non-missing shares."""
    out = pd.DataFrame(index=ea_raw.index)
    for v in ["v1", "v2", "v3", "v4", "v5"]:        # weighted mean midpoint
        cols = [c for c in ea_raw.columns if c.startswith(f"{v}_grp")
                and c.split("_", 1)[1] in MIDPOINTS]
        w = ea_raw[cols].fillna(0)
        tot = w.sum(axis=1)
        val = sum(w[c] * MIDPOINTS[c.split("_", 1)[1]] for c in cols) / tot
        val[tot < MIN_COVERAGE] = np.nan
        out[v] = val
    for v, spec in ORDINAL_SPEC.items():            # weighted mean over valid groups
        cols = [c for c in spec if c in ea_raw.columns]
        w = ea_raw[cols].fillna(0)
        tot = w.sum(axis=1)
        val = sum(w[c] * spec[c] for c in cols) / tot
        val[tot < MIN_COVERAGE] = np.nan
        out[v] = val
    return out


def extra_ea(ea_raw):
    """Shares of agriculture types among valid v28 groups (2..7)."""
    ex = pd.DataFrame(index=ea_raw.index)
    valid = [f"v28_grp{i}" for i in range(2, 8)]
    tot = ea_raw[valid].fillna(0).sum(axis=1)

    def share(cols):
        s = ea_raw[cols].fillna(0).sum(axis=1) / tot
        return s.where(tot >= MIN_COVERAGE)
    ex["v28_irrigated"] = share(["v28_grp7"])                       # irrigated
    ex["v28_extensive_hort"] = share(["v28_grp4", "v28_grp5"])      # shifting/horticulture
    return ex


# =============================================================================
# RECIPE-PRESENCE OUTCOMES
# =============================================================================
PP = ["wheat", "spelt", "barley", "ryeflour", "teff"]   # plough-positive grains
TROPICAL_ROOTS = ["cassava", "yam", "taro", "sweetpotato", "sago_palm",
                  "french_plantain"]
# y name -> ("category", name) | ("canon", [canonical ingredients]) | ("regex", ...)
Y_DEF = {
    "fish_seafood":   ("category", "fish_seafood"),
    "meat":           ("category", "meat"),
    "dairy":          ("category", "dairy"),
    "rice":           ("canon", ["rice"]),
    "pp":             ("canon", PP),
    "tropical_roots": ("canon", TROPICAL_ROOTS),
    # game meat is not a canonical ingredient: keyword search of the raw ingredient
    # text on ALL lines (including ones the category pipeline left unmatched)
    "game":           ("regex", (
        r"\b(?:venison|venado|deer|reindeer|caribou|elk|moose|wild boar|boar|bison"
        r"|kangaroo|pheasant|partridge|grouse|ptarmigan|woodcock|wild duck|mallard"
        r"|game meat|wild game|game birds?|antelope|springbok|kudu|wildebeest"
        r"|squirrel|possum|opossum|armadillo|capybara|agouti|bushmeat)\b"
        r"|\bgame\b(?!\s*(?:hen|day|time|night|changer))",
        r"boar'?s head|deer horn|deer salt|hartshorn")),
}
Y_LABEL = {
    "fish_seafood": "fish & seafood", "meat": "meat", "dairy": "dairy",
    "game": "game meat (venison, wild boar, reindeer, elk...)",
    "rice": "rice", "pp": "plough-positive grains (wheat, barley, rye, teff)",
    "tropical_roots": "tropical roots (cassava, yam, taro, plantain...)",
}
X_LABEL = {
    "v2": "reliance on hunting", "v3": "reliance on fishing",
    "v4": "reliance on animal husbandry", "v41": "milking",
    "v28_irrigated": "irrigated agriculture (share)", "v39": "plough use (0-2)",
    "v28_extensive_hort": "shifting/horticultural agriculture (share)",
}
# (row label, [(x variable, y outcome, expected sign)]) -- order = order on the plot
FOCUSED = [
    ("Fishing", [("v3", "fish_seafood", "+")]),
    ("Animal husbandry \u2192 meat", [("v4", "meat", "+")]),
    ("Hunting \u2192 game meat", [("v2", "game", "+")]),
    ("Milking \u2192 dairy", [("v41", "dairy", "+")]),
    ("Irrigated agriculture \u2192 rice", [("v28_irrigated", "rice", "+")]),
    ("Shifting/horticultural agriculture \u2192 tropical roots",
     [("v28_extensive_hort", "tropical_roots", "+")]),
    ("Plough use \u2192 plough-positive grains", [("v39", "pp", "+")]),
]


def build_presence():
    """Country x outcome: share of recipes with >= 1 matching ingredient."""
    l = pd.read_csv(LONG_PATH, usecols=["country", "recipe_id", "category",
                                        "canonical_ingredient", "raw_ingredient"])
    l["adm0"] = to_iso3(l["country"])
    l = l.dropna(subset=["adm0"])
    l["raw_lc"] = l["raw_ingredient"].fillna("").str.lower()
    n_rec = l.groupby("adm0")["recipe_id"].nunique()
    m = l[l["category"] != "unmatched"]
    out = pd.DataFrame(index=n_rec.index)
    for y, (kind, spec) in Y_DEF.items():
        if kind == "regex":
            inc, exc = spec
            hit = l[l["raw_lc"].str.contains(inc, regex=True)
                    & ~l["raw_lc"].str.contains(exc, regex=True)]
            k = hit.groupby("adm0")["recipe_id"].nunique()
        else:
            sel = (m["category"] == spec) if kind == "category" \
                else m["canonical_ingredient"].isin(spec)
            k = m[sel].groupby("adm0")["recipe_id"].nunique()
        out[y] = (k.reindex(n_rec.index).fillna(0) / n_rec)
    out["n_recipes"] = n_rec
    return out


# =============================================================================
# ESTIMATION
# =============================================================================
def zs(s):
    return (s - s.mean()) / s.std(ddof=0)


def estimate(df, x, y, dummies, min_recipes):
    """Standardised bivariate OLS (HC3), optionally with continent dummies."""
    d = df[[x, y, "n_recipes"] + dummies].dropna()
    d = d[d["n_recipes"] >= min_recipes]
    # a continent with < 3 countries is fit perfectly by its dummy (leverage 1 ->
    # infinite HC3 s.e.): drop those countries and the dummy
    small = [c for c in dummies if d[c].sum() < MIN_PER_CONTINENT]
    if small:
        d = d[~(d[small].sum(axis=1) > 0)]
        dummies = [c for c in dummies if c not in small]
    # if every country sits in some dummy the dummies sum to the constant
    # (rank-deficient): drop the largest one as the reference
    if dummies and (d[dummies].sum(axis=1) > 0).all():
        ref = d[dummies].sum().idxmax()
        dummies = [c for c in dummies if c != ref]
    if len(d) < 15 + len(dummies) or any(d[c].nunique() < 2 for c in (x, y)):
        return None
    Z = pd.DataFrame({x: zs(d[x])})
    for c in dummies:
        Z[c] = d[c]
    r = sm.OLS(zs(d[y]), sm.add_constant(Z)).fit(cov_type="HC3")
    lo, hi = r.conf_int().loc[x]
    if not np.isfinite(r.bse[x]):
        print(f"  WARNING non-finite s.e.: x={x} y={y}")
    return dict(beta=r.params[x], se=r.bse[x], lo=lo, hi=hi, p=r.pvalues[x], n=len(d))


def run_spec(df, dummies, min_recipes):
    rows = []
    for group, specs in FOCUSED:
        for x, y, sign in specs:
            e = estimate(df, x, y, dummies, min_recipes)
            if e is None:
                continue
            rows.append(dict(group=group, x=X_LABEL[x], y=y, expected=sign,
                             interaction=False, weighted=False,
                             countries_x_gt10pct="", **e))
    return pd.DataFrame(rows)


# =============================================================================
# PLOT
# =============================================================================
SPEC_LABEL = {"A_none": "No controls (all countries)",
              "B_contFE_all": "Continent FE (all countries)"}


def stars(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


def coef_plot(res, path, title, sample_note, annotate=False, xlim=None,
              label_above=False, specs=("A_none", "B_contFE_all")):
    ink, mute, grid = "#1f2933", "#6b7785", "#e4e8ec"
    cols = {"A_none": "#1c4f9c", "B_contFE_all": "#c98f4e"}   # blue / muted orange
    marks = {"A_none": "o", "B_contFE_all": "s"}
    span = 0.21 if label_above else 0.14
    # first spec is drawn on top within each row (y axis points up)
    offs = dict(zip(specs, np.linspace(span, -span, len(specs))))
    rows = [(x, y) for _, sp in FOCUSED for x, y, _ in sp]
    n = len(rows)
    fig_h = (0.72 if label_above else 0.66) * n + 2.6
    fig, ax = plt.subplots(figsize=(10.5, fig_h))
    for i, (x, y) in enumerate(rows):
        yv = n - i
        name = X_LABEL[x]
        # parenthetical details are dropped from the row labels to save width
        row_label = re.sub(r"\s*\([^)]*\)", "", f"{name} \u2192 {Y_LABEL[y]}")
        ax.text(-0.02, yv, row_label, transform=ax.get_yaxis_transform(),
                ha="right", va="center", fontsize=10, color=ink)
        for sp in specs:
            r = res[(res.spec == sp) & (~res.weighted) & (res.x == name)
                    & (res.y == y)]
            if r.empty:
                continue
            r = r.iloc[0]
            yy = yv + offs[sp]
            top = sp == "A_none"
            ax.plot([r.lo, r.hi], [yy, yy], color=cols[sp], lw=1.2,
                    solid_capstyle="round", zorder=5 if top else 3)
            ax.plot(r.beta, yy, marker=marks[sp], ms=5, color=cols[sp],
                    mec="white", mew=0.6, zorder=6 if top else 4)
            if annotate:
                st = stars(r.p)
                if label_above:     # centred above the point estimate (= CI midpoint)
                    ax.annotate(f"{r.beta:+.2f}{st}", (r.beta, yy), xytext=(0, 5),
                                textcoords="offset points", va="bottom",
                                ha="center", fontsize=7.5, color=ink)
                else:
                    ax.annotate(f"{r.beta:+.2f}{st}", (r.hi, yy), xytext=(6, 0),
                                textcoords="offset points", va="center", ha="left",
                                fontsize=7.5, color=ink)
    if annotate:   # room on the right for the labels
        xl = ax.get_xlim()
        ax.set_xlim(xl[0], xl[1] + 0.17 * (xl[1] - xl[0]))
    if xlim is not None:   # fixed axis range overrides the automatic one
        ax.set_xlim(*xlim)
        ax.set_xticks(np.arange(np.ceil(xlim[0] * 4) / 4, xlim[1] + 1e-9, 0.25))
    ax.axvline(0, color=ink, lw=0.8, zorder=1)
    ax.set_ylim(0.3, n + 0.9)
    ax.set_yticks([])
    ax.grid(axis="x", color=grid, lw=0.6, zorder=0)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="x", labelsize=8, colors=mute)
    ax.set_xlabel("Standardised coefficient (SD of recipe-presence per SD of x), "
                  "95% CI (HC3)", fontsize=9, color=ink)
    for sp in specs:
        ax.plot([], [], marker=marks[sp], ls="", color=cols[sp], ms=5 * 1.1,
                label=SPEC_LABEL[sp])
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=3, fontsize=8,
              frameon=False)
    nn = res[res.spec.isin(specs) & (~res.weighted)]["n"].median()
    fig.suptitle(title + " (unweighted)", x=0.02, ha="left", fontsize=12,
                 fontweight="bold", color=ink)
    foot = ("Outcome: share of a country's recipes with \u22651 ingredient from the "
            f"category/group. {sample_note} (median n \u2248 {int(nn)})."
            + (" Labels: point estimate; * p<0.10, ** p<0.05, *** p<0.01 (HC3)."
               if annotate else ""))
    fig.text(0.02, 0.15 / fig_h, textwrap.fill(foot, 140), fontsize=7, color=mute,
             ha="left", va="bottom")
    # margins in inches so short figures do not overlap title/legend/footnote
    plt.subplots_adjust(left=0.50, right=0.97, top=1 - 1.05 / fig_h,
                        bottom=1.55 / fig_h)
    fig.savefig(path, dpi=200)
    plt.close(fig)


# =============================================================================
# STARS TABLE (Markdown + LaTeX)
# =============================================================================
TABLE_ROWS = [   # (x label, y, LaTeX label, Markdown label) -- plot order
    ("reliance on fishing", "fish_seafood", "Fishing $\\to$ fish \\& seafood",
     "Fishing \u2192 fish & seafood"),
    ("reliance on animal husbandry", "meat", "Animal husbandry $\\to$ meat",
     "Animal husbandry \u2192 meat"),
    ("reliance on hunting", "game", "Hunting $\\to$ game meat",
     "Hunting \u2192 game meat"),
    ("milking", "dairy", "Milking $\\to$ dairy", "Milking \u2192 dairy"),
    ("irrigated agriculture (share)", "rice", "Irrigated agriculture $\\to$ rice",
     "Irrigated agriculture \u2192 rice"),
    ("shifting/horticultural agriculture (share)", "tropical_roots",
     "Shifting/horticultural agr. $\\to$ tropical roots",
     "Shifting/horticultural agr. \u2192 tropical roots"),
    ("plough use (0-2)", "pp", "Plough use $\\to$ plough-positive grains",
     "Plough use \u2192 plough-positive grains"),
]
PANELS = [("B_contFE_all", "Panel A: continent fixed effects"),
          ("A_none", "Panel B: no controls")]


def build_tables(d):
    md = ["| Recipe-presence outcome | " + " | ".join(f"\u2265{c}" for c in CUTOFFS)
          + " |", "|---|" + "---:|" * len(CUTOFFS)]
    tex = ["\\begin{tabular}{l" + "c" * len(CUTOFFS) + "}\\toprule",
           " & \\multicolumn{%d}{c}{Minimum recipes per country}\\\\" % len(CUTOFFS),
           "\\cmidrule(lr){2-%d}" % (len(CUTOFFS) + 1),
           "Pair & " + " & ".join(str(c) for c in CUTOFFS) + "\\\\ \\midrule"]
    for spec, title in PANELS:
        md.append(f"| **{title}** |" + " |" * len(CUTOFFS))
        tex.append(f"\\multicolumn{{{len(CUTOFFS)+1}}}{{l}}{{\\textit{{{title}}}}}\\\\")
        Ns = {c: [] for c in CUTOFFS}
        for x, y, tl, ml in TABLE_ROWS:
            b, s, tb, ts = [], [], [], []
            for c in CUTOFFS:
                r = d[(d.spec == spec) & (d.cutoff == c) & (d.x == x)
                      & (d.y == y)].iloc[0]
                st = stars(r.p)
                Ns[c].append(int(r.n))
                b.append(f"{r.beta:+.2f}{st}")
                s.append(f"({r.se:.2f})")
                tb.append(f"{r.beta:.2f}" + ("$^{%s}$" % st if st else ""))
                ts.append(f"({r.se:.2f})")
            md.append(f"| {ml} | " + " | ".join(b) + " |")
            md.append("|  | " + " | ".join(s) + " |")
            tex.append(f"{tl} & " + " & ".join(tb) + "\\\\")
            tex.append(" & " + " & ".join(ts) + "\\\\")
        rng = [(f"{min(Ns[c])}" if min(Ns[c]) == max(Ns[c])
                else f"{min(Ns[c])}\u2013{max(Ns[c])}") for c in CUTOFFS]
        md.append("| *N countries* | " + " | ".join(rng) + " |")
        tex.append("N countries & " + " & ".join(r.replace("\u2013", "--")
                                                 for r in rng) + "\\\\")
        if spec == "B_contFE_all":
            tex.append("\\midrule")
    tex.append("\\bottomrule\\end{tabular}")
    note = ("Standardised coefficients (SD of recipe-presence per SD of the ancestral "
            "variable), unweighted OLS; HC3 robust standard errors in parentheses. "
            "Outcome: share of a country's recipes containing \u22651 ingredient from "
            "the category/group. Continent fixed effects absorb continent-level "
            "differences; continents with <3 countries in a sample are dropped. "
            "* p<0.10, ** p<0.05, *** p<0.01.")
    return "\n".join(md) + "\n\n" + note + "\n", \
        "\n".join(tex) + "\n\n% Note: " + note.replace("%", "\\%") + "\n"


# =============================================================================
# OUTPUT HELPERS (Dropbox can briefly lock a file: render to temp, copy w/ retries)
# =============================================================================
def safe_copy(src, dst, tries=8, wait=3.0):
    for i in range(tries):
        try:
            shutil.copyfile(src, dst)
            return True
        except OSError as e:
            print(f"  copy to {os.path.basename(dst)} failed ({e}); retry {i+1}/{tries}")
            time.sleep(wait)
    return False


def save_text(name, content):
    tmp = os.path.join(tempfile.gettempdir(), name)
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)
    ok = safe_copy(tmp, os.path.join(OUT, name))
    print(f"           {name} {'saved' if ok else 'FAILED'}")


# =============================================================================
# MAIN
# =============================================================================
def main():
    os.makedirs(OUT, exist_ok=True)

    # recipe-presence outcomes (country level)
    pres = build_presence()

    # ancestral variables
    ea_raw = pd.read_stata(EA_PATH)
    key = "isocode" if "isocode" in ea_raw.columns else "adm0"
    ea_raw["adm0"] = ea_raw[key].str.strip().str.upper()
    ea_raw = ea_raw.dropna(subset=["adm0"]).drop_duplicates("adm0").set_index("adm0")
    ea = build_ea(ea_raw).join(extra_ea(ea_raw))

    # continent dummies
    ctrl = pd.read_stata(CONTROLS_PATH)
    ctrl["adm0"] = ctrl["adm0"].str.strip().str.upper()
    ctrl = ctrl.dropna(subset=["adm0"]).drop_duplicates("adm0").set_index("adm0")
    cont_d = pd.get_dummies(ctrl["continent"], prefix="cont",
                            drop_first=True).astype(float)
    dummies = list(cont_d.columns)
    df = pres.join(ea, how="inner").join(cont_d)

    variants = [   # (file name, annotate, xlim, label_above)
        ("coefplot_focused_min{c}.png", False, None, False),
        ("coefplot_focused_labeled_min{c}.png", True, None, False),
        ("coefplot_focused_labeled_xrange_min{c}.png", True, (-0.5, 1.0), False),
        ("coefplot_focused_labeled_xrange_above_min{c}.png", True, (-0.5, 1.0), True),
    ]
    allres = []
    for cut in CUTOFFS:
        ncount = int((df.n_recipes >= cut).sum())
        a = run_spec(df, [], cut).assign(spec="A_none", cutoff=cut)
        b = run_spec(df, dummies, cut).assign(spec="B_contFE_all", cutoff=cut)
        res = pd.concat([a, b], ignore_index=True)
        allres.append(res)
        title = f"Recipe\u2013ancestry validations, \u2265{cut} recipes per country"
        note = (f"Countries with \u2265{cut} recipes ({ncount} with EA data); each "
                "estimate uses all countries with the needed data. Unweighted")
        print(f"cutoff {cut:2d}: {ncount} countries with EA data")
        for pattern, annotate, xlim, above in variants:
            fname = pattern.format(c=cut)
            tmp = os.path.join(tempfile.gettempdir(), fname)
            coef_plot(res, tmp, title, note, annotate=annotate, xlim=xlim,
                      label_above=above)
            ok = safe_copy(tmp, os.path.join(OUT, fname))
            print(f"           {fname} {'saved' if ok else 'FAILED'}")

    res_all = pd.concat(allres, ignore_index=True)
    tmp_csv = os.path.join(tempfile.gettempdir(), "coefplot_focused_estimates.csv")
    res_all.to_csv(tmp_csv, index=False)
    safe_copy(tmp_csv, os.path.join(OUT, "coefplot_focused_estimates.csv"))

    md, tex = build_tables(res_all)
    save_text("coefplot_focused_table.md", md)
    save_text("coefplot_focused_table.tex", tex)

    print("\nUnweighted beta (p) by minimum-recipe cutoff  [" +
          " | ".join(f">={c}" for c in CUTOFFS) + "]")
    for spec in ["A_none", "B_contFE_all"]:
        print(f"\n### {spec}")
        for g, sp in FOCUSED:
            for x, y, s in sp:
                cells = []
                for cut in CUTOFFS:
                    r = res_all[(res_all.spec == spec) & (res_all.cutoff == cut)
                                & (res_all.x == X_LABEL[x]) & (res_all.y == y)]
                    cells.append("n/a" if r.empty else
                                 f"{r.iloc[0].beta:+.2f}({r.iloc[0].p:.2f}) "
                                 f"n={int(r.iloc[0].n)}")
                print(f"  {g[:44]:44s} " + " | ".join(cells))
    print("\nAll done ->", OUT)


if __name__ == "__main__":
    main()
