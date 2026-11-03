# -*- coding: utf-8 -*-
"""
Refined staples analysis: split the recipe category `grain_starch` into
rice / wheat / other grains / maize / potato / tropical roots using the
canonical-ingredient mapping, then pair each with the EA variables it should
plausibly track (irrigation, plow, cereal vs roots as main crop, ...).

Reuses helpers from validate_recipes_atlas_targeted.py.
Continent FEs are OFF (USE_CONTINENT_FE = False), per request.

Two kinds of recipe measures per group:
  <g>           share of ALL matched ingredients in the country (as before)
  <g>_of_starch share of the country's starch-staple mentions (composition:
                what do people use as their starch, conditional on using one)
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")

import validate_recipes_atlas_targeted as T

warnings.filterwarnings("ignore")

USE_CONTINENT_FE = False
MIN_STARCH_MENTIONS = 20   # min. starch-staple mentions for composition shares

long_path = (
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes"
    r"\ingredients\recipe_ingredient_categories_canonical_long.csv"
)
OUTPUT_DIR = r"C:\Users\stevebc\Dropbox\Cuisine_complexity\3_results\temp\ea_staples"

# canonical ingredient -> staple group  ('unspecified' starch is left out)
GROUPS = {
    "rice":           ["rice"],
    "wheat":          ["wheat", "spelt"],
    "other_grains":   ["barley", "oats", "ryeflour", "buckwheat", "millet",
                       "teff", "quinoa", "amaranth"],
    "maize":          ["corn_sweetcorn"],
    "potato":         ["potato"],
    "tropical_roots": ["cassava", "yam", "taro", "sweetpotato", "sago_palm",
                       "french_plantain"],
}
BREAD = ["bread_wheaten"]   # sits in processed_prepared_food in the category map

AGGS = {   # aggregates built from the groups
    "all_cereals": ["rice", "wheat", "other_grains", "maize"],
    "all_roots":   ["potato", "tropical_roots"],
}
COMPOSITION = ["rice", "wheat", "other_grains", "maize", "potato",
               "tropical_roots", "all_cereals", "all_roots"]


# =============================================================================
# recipe side: staple groups from canonical ingredients
# =============================================================================
def build_staples():
    l = pd.read_csv(long_path, usecols=["country", "category",
                                        "canonical_ingredient"])
    l["adm0"] = T.to_iso3(l["country"])
    miss = l.loc[l["adm0"].isna(), "country"].unique()
    if len(miss):
        print("WARNING unmapped countries:", list(miss))
    l = l.dropna(subset=["adm0"])
    matched = l[l["category"] != "unmatched"]
    denom = matched.groupby("adm0").size()

    counts = pd.DataFrame(index=denom.index)
    c2g = {c: g for g, cs in GROUPS.items() for c in cs}
    sub = matched[(matched["category"] == "grain_starch")
                  & matched["canonical_ingredient"].isin(c2g)]
    sub = sub.assign(group=sub["canonical_ingredient"].map(c2g))
    tab = sub.groupby(["adm0", "group"]).size().unstack(fill_value=0)
    counts = counts.join(tab).fillna(0)
    for g in GROUPS:
        if g not in counts:
            counts[g] = 0
    for a, parts in AGGS.items():
        counts[a] = counts[parts].sum(axis=1)
    counts["starch_all"] = counts[list(GROUPS)].sum(axis=1)
    counts["wheat_bread"] = (counts["wheat"] + matched[
        matched["canonical_ingredient"].isin(BREAD)].groupby("adm0").size()
        .reindex(counts.index).fillna(0))

    out = pd.DataFrame(index=counts.index)
    for g in list(GROUPS) + list(AGGS) + ["wheat_bread"]:
        out[g] = counts[g] / denom
    ok = counts["starch_all"] >= MIN_STARCH_MENTIONS
    for g in COMPOSITION:
        out[f"{g}_of_starch"] = (counts[g] / counts["starch_all"]).where(ok)
    out["wheat_bread_of_starch"] = (counts["wheat_bread"]
                                    / (counts["starch_all"]
                                       + counts["wheat_bread"]
                                       - counts["wheat"])).where(ok)
    out["starch_all"] = counts["starch_all"] / denom
    return out, counts, denom


def check_against_category_file(out):
    ref = pd.read_csv(
        r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes"
        r"\ingredients\country_category_shares.csv")
    ref["adm0"] = T.to_iso3(ref["country"])
    ref = (ref[ref["category"] == "grain_starch"].dropna(subset=["adm0"])
           .set_index("adm0")["share_excluding_unmatched"])
    # my starch_all leaves out 'unspecified'/duplicates -> expect small gap
    both = pd.concat([out["starch_all"], ref], axis=1, keys=["mine", "ref"]).dropna()
    diff = (both["ref"] - both["mine"])
    print(f"\nCheck vs country_category_shares (grain_starch): n={len(both)}, "
          f"corr={both.corr().iloc[0, 1]:.4f}, "
          f"mean gap (ref-mine, excl. 'unspecified')={diff.mean()*100:.3f}pp, "
          f"max gap={diff.max()*100:.3f}pp, min gap={diff.min()*100:.3f}pp")


# =============================================================================
# EA side: extra variables for rice / plow / low-intensity farming
# =============================================================================
def extra_ea(ea_raw):
    ex = pd.DataFrame(index=ea_raw.index)
    valid = [f"v28_grp{i}" for i in range(2, 8)]
    tot = ea_raw[valid].fillna(0).sum(axis=1)
    def share(cols):
        s = ea_raw[cols].fillna(0).sum(axis=1) / tot
        return s.where(tot >= T.MIN_COVERAGE)
    ex["v28_irrigated"] = share(["v28_grp7"])
    ex["v28_extensive_hort"] = share(["v28_grp4", "v28_grp5"])
    return ex


# =============================================================================
# labels
# =============================================================================
def register_labels():
    T.LABELS.update({
        "v28_irrigated": "Intensive irrigated agriculture [EA028]: share",
        "v28_extensive_hort": "Extensive/shifting or horticulture [EA028]: share",
    })
    T.SHORT.update({"v28_irrigated": "irrigated ag",
                    "v28_extensive_hort": "shifting/hort ag"})
    T.SHARE_X.update({"v28_irrigated", "v28_extensive_hort"})
    names = {
        "rice": "Rice", "wheat": "Wheat", "wheat_bread": "Wheat (incl. bread)",
        "other_grains": "Other grains (barley, oats, rye, millet...)",
        "maize": "Maize/corn", "potato": "Potato",
        "tropical_roots": "Tropical roots (cassava, yam, taro, plantain...)",
        "all_cereals": "All cereals", "all_roots": "All roots & tubers",
    }
    for g, n in names.items():
        T.CATEGORY_PRETTY[g] = n
        T.YLAB[g] = f"{n} (% of all ingredients)"
        T.CATEGORY_PRETTY[f"{g}_of_starch"] = f"{n}, share of starch staples"
        T.YLAB[f"{g}_of_starch"] = f"{n} (% of starch-staple mentions)"


# =============================================================================
# themes: (x, recipe measure, colour)
# =============================================================================
P = T.pairs_for
THEMES = {
    "A_rice": (
        P("v28_irrigated", ["rice", "rice_of_starch"])
        + P("v28", ["rice", "rice_of_starch"])
        + P("v39", ["rice", "rice_of_starch"])
        + P("v29_cereal", ["rice", "rice_of_starch"])
        + P("v5", ["rice"])
    ),
    "B_wheat_temperate_grains": (
        P("v39", ["wheat", "wheat_bread", "wheat_of_starch",
                  "other_grains", "other_grains_of_starch"])
        + P("v28", ["wheat", "wheat_bread", "wheat_of_starch",
                    "other_grains", "other_grains_of_starch"])
        + P("v29_cereal", ["wheat", "wheat_bread", "wheat_of_starch",
                           "other_grains", "other_grains_of_starch"])
    ),
    "C_maize": (
        P("v29_cereal", ["maize", "maize_of_starch"])
        + P("v28_extensive_hort", ["maize", "maize_of_starch"])
        + P("v39", ["maize", "maize_of_starch"])
    ),
    "D_roots_tubers": (
        P("v29_roots", ["all_roots", "all_roots_of_starch", "potato",
                        "tropical_roots", "tropical_roots_of_starch"])
        + P("v28_extensive_hort", ["all_roots", "all_roots_of_starch", "potato",
                                   "tropical_roots", "tropical_roots_of_starch"])
        + P("v28", ["all_roots", "all_roots_of_starch", "potato",
                    "tropical_roots", "tropical_roots_of_starch"])
    ),
    "E_cereals_vs_roots": (
        P("v29_cereal", ["all_cereals", "all_cereals_of_starch"])
        + P("v29_roots", ["all_cereals", "all_cereals_of_starch"])
        + P("v39", ["all_cereals", "all_cereals_of_starch"])
        + P("v28", ["all_cereals", "all_cereals_of_starch"])
    ),
}


# =============================================================================
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    register_labels()

    staples, counts, denom = build_staples()
    check_against_category_file(staples)
    print("\nTop-5 countries per staple group (share of all ingredients):")
    for g in list(GROUPS) + ["wheat_bread"] + list(AGGS):
        top = staples[g].dropna().sort_values(ascending=False).head(5)
        print(f"  {g:15s}", ", ".join(f"{i} {v*100:.1f}%" for i, v in top.items()))
    print("\nCountries with >= %d starch mentions (composition measures): %d of %d"
          % (MIN_STARCH_MENTIONS, staples["rice_of_starch"].notna().sum(),
             len(staples)))

    ea_raw = T.pd.read_stata(T.ea_path)
    key = "isocode" if "isocode" in ea_raw.columns else "adm0"
    ea_raw["adm0"] = ea_raw[key].str.strip().str.upper()
    ea_raw = ea_raw.dropna(subset=["adm0"]).drop_duplicates("adm0").set_index("adm0")
    ea = T.build_ea(ea_raw).join(extra_ea(ea_raw))

    cont_d = None
    if USE_CONTINENT_FE:
        ctrl = pd.read_stata(T.controls_path)
        ctrl["adm0"] = ctrl["adm0"].str.strip().str.upper()
        ctrl = ctrl.dropna(subset=["adm0"]).drop_duplicates("adm0").set_index("adm0")
        cont_d = pd.get_dummies(ctrl["continent"], prefix="cont",
                                drop_first=True).astype(float)

    df = staples.join(ea, how="inner")
    if cont_d is not None:
        cont_d = cont_d.reindex(df.index).dropna(how="all", axis=1)
    print(f"\nCountries with recipes AND EA: {len(df)}")

    staples.assign(n_starch_mentions=counts["starch_all"]).to_csv(
        os.path.join(OUTPUT_DIR, "staple_shares_by_country.csv"))

    rows = []
    for theme, pairs in THEMES.items():
        tdir = os.path.join(OUTPUT_DIR, theme)
        os.makedirs(tdir, exist_ok=True)
        print(f"\n=== {theme} ({len(pairs)} pairs) ===")
        smap = {}
        for xv, cat, cv in pairs:
            st = T.pair_stats(df, xv, cat, cont_d)
            if st is None:
                continue
            smap[(xv, cat, cv)] = st
            T.single_figure(df, xv, cat, cv, st,
                            os.path.join(tdir, f"scatter_{xv}_vs_{cat}.png"))
            rows.append({**st, "theme": theme})
            print(f"  {xv:20s} {cat:26s} r={st['pearson_r']:+.2f} "
                  f"p={st['pearson_p']:.3f} rho={st['spearman_rho']:+.2f} "
                  f"n={st['n']}")
        T.contact_sheet(df, pairs, smap, theme,
                        os.path.join(OUTPUT_DIR, f"overview_{theme}.png"))

    pd.DataFrame(rows).drop(columns=["partial_r_contFE", "partial_p_contFE"]
                            if cont_d is None else []).to_csv(
        os.path.join(OUTPUT_DIR, "staples_correlations.csv"), index=False)
    print("\nAll done ->", OUTPUT_DIR)


if __name__ == "__main__":
    main()
