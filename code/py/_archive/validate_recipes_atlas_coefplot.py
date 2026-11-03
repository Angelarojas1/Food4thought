# -*- coding: utf-8 -*-
"""
Coefficient plot of the pre-specified recipe <-> Ethnographic Atlas validations.

Y = share of a country's RECIPES containing >= 1 ingredient of the category/group
    (presence, not share of ingredient mentions). Denominator = all recipes of the
    country, including recipes with no matched ingredient (so presence is a lower
    bound). Countries need >= MIN_RECIPES recipes.
X = ancestral EA variable (Giuliano-Nunn), country level.

Estimates: bivariate OLS, x and y standardised (coefficient = SD change in
recipe-presence per SD of x), HC3 robust 95% CI. Two samples/weightings:
unweighted (filled) and weighted by number of recipes (hollow).
Interaction rows: y ~ A + M + A*M with A, M standardised; the plotted coefficient
is on A*M.  No continent fixed effects.
"""

import os
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import validate_recipes_atlas_targeted as T
import validate_recipes_atlas_staples as S

warnings.filterwarnings("ignore")

MIN_RECIPES = 20
OUTPUT_DIR = r"C:\Users\stevebc\Dropbox\Cuisine_complexity\3_results\temp\ea_coefplot"

PP = ["wheat", "spelt", "barley", "ryeflour", "teff"]
PN_CEREALS = ["corn_sweetcorn", "millet"]
PN_ROOTS = ["potato", "cassava", "yam", "taro", "sweetpotato", "sago_palm",
            "french_plantain"]
TROPICAL_ROOTS = ["cassava", "yam", "taro", "sweetpotato", "sago_palm",
                  "french_plantain"]
TREE_OILS = ["olive", "coconut", "oil_palm"]

# y name -> ("category", name) or ("canon", [names])
Y_DEF = {
    "fish_seafood":   ("category", "fish_seafood"),
    "meat":           ("category", "meat"),
    "dairy":          ("category", "dairy"),
    "oil_fat":        ("category", "oil_fat"),
    "tree_oils":      ("canon", TREE_OILS),
    "rice":           ("canon", ["rice"]),
    "pp":             ("canon", PP),
    "pn_cereals":     ("canon", PN_CEREALS),
    "pn_roots":       ("canon", PN_ROOTS),
    "tropical_roots": ("canon", TROPICAL_ROOTS),
    "potato":         ("canon", ["potato"]),
    # game meat is not a canonical ingredient: search the raw ingredient text
    # (all lines, including ones the category pipeline left unmatched)
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
    "oil_fat": "oils & fats (generic/rapeseed/palm)",
    "tree_oils": "tree-crop oils (olive, coconut, oil palm)",
    "rice": "rice", "pp": "plough-positive grains (wheat, barley, rye, teff)",
    "pn_cereals": "plough-negative cereals (maize, millet)",
    "pn_roots": "plough-negative roots & tubers",
    "tropical_roots": "tropical roots (cassava, yam, taro, plantain...)",
    "potato": "potato",
}
X_LABEL = {
    "v2": "reliance on hunting",
    "v3": "reliance on fishing", "v4": "reliance on animal husbandry",
    "v41": "milking", "v40_bovine": "bovines", "v40_sheepgoat": "sheep/goats",
    "v40_camelid": "camels/llamas", "v29_treefruit": "tree fruit as main crop",
    "v28_irrigated": "irrigated agriculture (share)",
    "v28": "agricultural intensity (0-5)", "v39": "plough use (0-2)",
    "v29_roots": "roots/tubers as main crop",
    "v28_extensive_hort": "shifting/horticultural agriculture (share)",
}

# (group header, [(x or (A,M), y, expected sign)])
SPECS = [
    ("Fishing \u2192 fish & seafood", [("v3", "fish_seafood", "+")]),
    ("Animal husbandry \u2192 meat, dairy",
     [("v4", "meat", "+"), ("v4", "dairy", "+")]),
    ("Hunting \u2192 game meat", [("v2", "game", "+")]),
    ("Milking animals \u2192 dairy",
     [("v41", "dairy", "+"), ("v40_bovine", "dairy", "+"),
      ("v40_sheepgoat", "dairy", "+"), ("v40_camelid", "dairy", "+"),
      (("v40_bovine", "v41"), "dairy", "+"),
      (("v40_sheepgoat", "v41"), "dairy", "+"),
      (("v40_camelid", "v41"), "dairy", "+")]),
    ("Tree crops \u2192 oils",
     [("v29_treefruit", "oil_fat", "+"), ("v29_treefruit", "tree_oils", "+")]),
    ("Intensive agriculture \u2192 rice",
     [("v28_irrigated", "rice", "+"), ("v28", "rice", "+")]),
    ("Plough use \u2192 plough-positive / -negative crops",
     [("v39", "pp", "+"), ("v39", "pn_cereals", "\u2212"),
      ("v39", "pn_roots", "\u2212")]),
    ("Roots/tubers as main crop \u2192 root ingredients",
     [("v29_roots", "tropical_roots", "+"), ("v29_roots", "potato", "\u2212")]),
    ("Shifting/horticultural agriculture \u2192 root ingredients",
     [("v28_extensive_hort", "tropical_roots", "+"),
      ("v28_extensive_hort", "potato", "\u2212")]),
]


# =============================================================================
def build_presence():
    l = pd.read_csv(S.long_path, usecols=["country", "recipe_id", "category",
                                          "canonical_ingredient", "raw_ingredient"])
    l["adm0"] = T.to_iso3(l["country"])
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
            out[y] = (k.reindex(n_rec.index).fillna(0) / n_rec)
            continue
        sel = (m["category"] == spec) if kind == "category" \
            else m["canonical_ingredient"].isin(spec)
        k = m[sel].groupby("adm0")["recipe_id"].nunique()
        out[y] = (k.reindex(n_rec.index).fillna(0) / n_rec)
    out["n_recipes"] = n_rec
    return out


def zs(s):
    return (s - s.mean()) / s.std(ddof=0)


def estimate(df, x, y, weighted):
    xs = list(x) if isinstance(x, tuple) else [x]
    d = df[xs + [y, "n_recipes"]].dropna()
    d = d[d["n_recipes"] >= MIN_RECIPES]
    if len(d) < 15 or any(d[c].nunique() < 2 for c in xs + [y]):
        return None
    Z = pd.DataFrame({c: zs(d[c]) for c in xs})
    if len(xs) == 2:
        Z["inter"] = Z[xs[0]] * Z[xs[1]]
        term = "inter"
    else:
        term = xs[0]
    X = sm.add_constant(Z)
    yy = zs(d[y])
    mod = (sm.WLS(yy, X, weights=d["n_recipes"]) if weighted else sm.OLS(yy, X))
    r = mod.fit(cov_type="HC3")
    lo, hi = r.conf_int().loc[term]
    return dict(beta=r.params[term], se=r.bse[term], lo=lo, hi=hi,
                p=r.pvalues[term], n=len(d))


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pres = build_presence()
    print(f"Countries with recipes: {len(pres)}; "
          f"with >= {MIN_RECIPES} recipes: {(pres.n_recipes >= MIN_RECIPES).sum()}")
    print("\nMean recipe-presence across countries (%):")
    print((pres.drop(columns='n_recipes').mean() * 100).round(1).to_string())
    pres.to_csv(os.path.join(OUTPUT_DIR, "recipe_presence_by_country.csv"))

    ea_raw = pd.read_stata(T.ea_path)
    key = "isocode" if "isocode" in ea_raw.columns else "adm0"
    ea_raw["adm0"] = ea_raw[key].str.strip().str.upper()
    ea_raw = ea_raw.dropna(subset=["adm0"]).drop_duplicates("adm0").set_index("adm0")
    ea = T.build_ea(ea_raw).join(S.extra_ea(ea_raw))
    df = pres.join(ea, how="inner")

    rows = []
    for group, specs in SPECS:
        for x, y, sign in specs:
            is_int = isinstance(x, tuple)
            name = (f"{X_LABEL[x[0]]} \u00d7 milking" if is_int else X_LABEL[x])
            support = ""
            xa = x[0] if is_int else x
            if xa.startswith("v40_"):
                k = int((df[xa] > 0.10).sum())
                support = k
            for wtd in (False, True):
                e = estimate(df, x, y, wtd)
                if e is None:
                    continue
                rows.append(dict(group=group, x=name, y=y, expected=sign,
                                 interaction=is_int, weighted=wtd,
                                 countries_x_gt10pct=support, **e))
    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(OUTPUT_DIR, "coefplot_estimates.csv"), index=False)
    show = res[~res.weighted][["group", "x", "y", "expected", "beta", "lo", "hi",
                               "p", "n"]].round(3)
    print("\nUnweighted estimates:\n", show.to_string(index=False))

    plot(res, os.path.join(OUTPUT_DIR, "coefplot_recipe_presence.png"))
    print("\nAll done ->", OUTPUT_DIR)


def plot(res, path, title="Do ancestral subsistence traits show up in recipes?",
         note=None):
    ink, mute, grid = "#1f2933", "#6b7785", "#e4e8ec"
    blue = "#2a6fb0"
    layout = []   # (kind, payload)
    for group, specs in SPECS:
        layout.append(("hdr", group))
        for x, y, sign in specs:
            layout.append(("row", (x, y, sign)))
    n = len(layout)
    fig_h = 0.34 * n + 1.8
    fig, ax = plt.subplots(figsize=(10.5, fig_h))
    ypos, ylabels, hdrs = {}, [], []
    cur = 0
    for i, (k, payload) in enumerate(layout):
        yv = n - i
        if k == "hdr":
            ax.text(-0.02, yv, payload, transform=ax.get_yaxis_transform(),
                    ha="right", va="center", fontsize=9, fontweight="bold", color=ink)
        else:
            x, y, sign = payload
            ypos[(x, y)] = yv
    for (x, y), yv in ypos.items():
        is_int = isinstance(x, tuple)
        name = (f"{X_LABEL[x[0]]} \u00d7 milking" if is_int else X_LABEL[x])
        sub = res[(res["x"] == name) & (res["y"] == y)]
        # row label
        sign = sub["expected"].iloc[0] if len(sub) else ""
        lab = f"{name} \u2192 {Y_LABEL[y]}"
        un = sub[~sub.weighted]
        sup = un["countries_x_gt10pct"].iloc[0] if len(un) else ""
        if sup != "" and sup < 10:
            lab += f"  [only {sup} countries >10%]"
        ax.text(-0.02, yv, lab, transform=ax.get_yaxis_transform(), ha="right",
                va="center", fontsize=8, color=ink)
        for _, r in sub.iterrows():
            off = -0.13 if not r.weighted else 0.13
            ax.plot([r.lo, r.hi], [yv + off] * 2, color=blue, lw=1.2,
                    alpha=1.0 if not r.weighted else 0.55, solid_capstyle="round")
            ax.plot(r.beta, yv + off, marker="o" if not r.weighted else "D",
                    ms=5.5, mfc=blue if not r.weighted else "white", mec=blue,
                    mew=1.2, zorder=4)
    ax.axvline(0, color=ink, lw=0.8, zorder=1)
    ax.set_ylim(0.3, n + 0.9)
    ax.set_yticks([])
    ax.grid(axis="x", color=grid, lw=0.6, zorder=0)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="x", labelsize=8, colors=mute)
    ax.set_xlabel("Standardised coefficient (SD of recipe-presence per SD of x), "
                  "95% CI (HC3)", fontsize=9, color=ink)
    ax.plot([], [], "o", color=blue, ms=5.5, label="Unweighted")
    ax.plot([], [], "D", mfc="white", mec=blue, ms=5.5, label="Weighted by number of recipes")
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=2, fontsize=8,
              frameon=False)
    fig.suptitle(title, x=0.02, ha="left", fontsize=12, fontweight="bold",
                 color=ink)
    fig.text(0.02, 0.005,
             note or ("Outcome: share of a country's recipes with \u22651 ingredient "
                      "from the category/group. Countries with \u226520 recipes. "
                      "No continent controls. Interaction rows: coefficient on "
                      "animal share \u00d7 milking, with both main effects included."),
             fontsize=7, color=mute, ha="left", va="bottom", wrap=True)
    plt.subplots_adjust(left=0.50, right=0.97, top=0.94, bottom=0.10)
    fig.savefig(path, dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
