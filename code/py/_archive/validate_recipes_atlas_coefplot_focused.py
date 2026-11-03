# -*- coding: utf-8 -*-
"""
Focused coefficient plots: six pre-specified pairs, no controls vs continent FE,
unweighted, largest sample, at minimum-recipe cutoffs 5/10/20/30/50.
Reuses the estimation and plotting code in validate_recipes_atlas_coefplot*.py.
"""

import os
import shutil
import tempfile
import time
import warnings
import pandas as pd

import validate_recipes_atlas_targeted as T
import validate_recipes_atlas_staples as S
import validate_recipes_atlas_coefplot as C
import validate_recipes_atlas_coefplot_controls as K

warnings.filterwarnings("ignore")

CUTOFFS = [5, 10, 20, 30, 50]
OUT = C.OUTPUT_DIR + "_focused"

FOCUSED = [
    ("Fishing", [("v3", "fish_seafood", "+")]),
    ("Animal husbandry → meat", [("v4", "meat", "+")]),
    ("Hunting → game meat", [("v2", "game", "+")]),
    ("Milking → dairy", [("v41", "dairy", "+")]),
    ("Irrigated agriculture → rice", [("v28_irrigated", "rice", "+")]),
    ("Shifting/horticultural agriculture → tropical roots",
     [("v28_extensive_hort", "tropical_roots", "+")]),
    ("Plough use → plough-positive grains", [("v39", "pp", "+")]),
]
C.SPECS = FOCUSED   # run_spec / compare_plot read the pairs from C.SPECS


def safe_copy(src, dst, tries=8, wait=3.0):
    for i in range(tries):
        try:
            shutil.copyfile(src, dst)
            return True
        except OSError as e:
            print(f"  copy to {os.path.basename(dst)} failed ({e}); retry {i+1}/{tries}")
            time.sleep(wait)
    return False


def main():
    os.makedirs(OUT, exist_ok=True)
    pres = C.build_presence()
    ea_raw = pd.read_stata(T.ea_path)
    key = "isocode" if "isocode" in ea_raw.columns else "adm0"
    ea_raw["adm0"] = ea_raw[key].str.strip().str.upper()
    ea_raw = ea_raw.dropna(subset=["adm0"]).drop_duplicates("adm0").set_index("adm0")
    ea = T.build_ea(ea_raw).join(S.extra_ea(ea_raw))
    ctrl = pd.read_stata(T.controls_path)
    ctrl["adm0"] = ctrl["adm0"].str.strip().str.upper()
    ctrl = ctrl.dropna(subset=["adm0"]).drop_duplicates("adm0").set_index("adm0")
    cont_d = pd.get_dummies(ctrl["continent"], prefix="cont",
                            drop_first=True).astype(float)
    dummies = list(cont_d.columns)
    df = pres.join(ea, how="inner").join(cont_d)

    allres = []
    for cut in CUTOFFS:
        C.MIN_RECIPES = cut
        ncount = int((df.n_recipes >= cut).sum())
        a = K.run_spec(df, [], [], None).assign(spec="A_none", cutoff=cut)
        b = K.run_spec(df, dummies, [], None).assign(spec="B_contFE_all", cutoff=cut)
        res = pd.concat([a, b], ignore_index=True)
        allres.append(res)
        fname = f"coefplot_focused_min{cut}.png"
        tmp = os.path.join(tempfile.gettempdir(), fname)
        K.compare_plot(
            res, ["A_none", "B_contFE_all"], False, tmp,
            f"Recipe–ancestry validations, ≥{cut} recipes per country",
            f"Countries with ≥{cut} recipes ({ncount} with EA data); each "
            "estimate uses all countries with the needed data. Unweighted",
            headers=False)
        ok = safe_copy(tmp, os.path.join(OUT, fname))
        print(f"cutoff {cut:2d}: {ncount} countries with EA data -> "
              f"{fname} {'saved' if ok else 'FAILED'}")
        # labelled version: point estimate + significance stars
        fname2 = f"coefplot_focused_labeled_min{cut}.png"
        tmp2 = os.path.join(tempfile.gettempdir(), fname2)
        K.compare_plot(
            res, ["A_none", "B_contFE_all"], False, tmp2,
            f"Recipe–ancestry validations, ≥{cut} recipes per country",
            f"Countries with ≥{cut} recipes ({ncount} with EA data); each "
            "estimate uses all countries with the needed data. Unweighted",
            headers=False, annotate=True)
        ok2 = safe_copy(tmp2, os.path.join(OUT, fname2))
        print(f"           {fname2} {'saved' if ok2 else 'FAILED'}")
        # labelled version on a wider, fixed x-axis (-0.5 to 1.0)
        fname3 = f"coefplot_focused_labeled_xrange_min{cut}.png"
        tmp3 = os.path.join(tempfile.gettempdir(), fname3)
        K.compare_plot(
            res, ["A_none", "B_contFE_all"], False, tmp3,
            f"Recipe–ancestry validations, ≥{cut} recipes per country",
            f"Countries with ≥{cut} recipes ({ncount} with EA data); each "
            "estimate uses all countries with the needed data. Unweighted",
            headers=False, annotate=True, xlim=(-0.5, 1.0))
        ok3 = safe_copy(tmp3, os.path.join(OUT, fname3))
        print(f"           {fname3} {'saved' if ok3 else 'FAILED'}")
        # same, with each label centred above its point estimate
        fname4 = f"coefplot_focused_labeled_xrange_above_min{cut}.png"
        tmp4 = os.path.join(tempfile.gettempdir(), fname4)
        K.compare_plot(
            res, ["A_none", "B_contFE_all"], False, tmp4,
            f"Recipe–ancestry validations, ≥{cut} recipes per country",
            f"Countries with ≥{cut} recipes ({ncount} with EA data); each "
            "estimate uses all countries with the needed data. Unweighted",
            headers=False, annotate=True, xlim=(-0.5, 1.0), label_above=True)
        ok4 = safe_copy(tmp4, os.path.join(OUT, fname4))
        print(f"           {fname4} {'saved' if ok4 else 'FAILED'}")
    res_all = pd.concat(allres, ignore_index=True)
    res_all = res_all[~res_all.weighted]
    tmp_csv = os.path.join(tempfile.gettempdir(), "coefplot_focused_estimates.csv")
    res_all.to_csv(tmp_csv, index=False)
    safe_copy(tmp_csv, os.path.join(OUT, "coefplot_focused_estimates.csv"))

    print("\nUnweighted beta (p) by minimum-recipe cutoff  [" +
          " | ".join(f">={c}" for c in CUTOFFS) + "]")
    for spec in ["A_none", "B_contFE_all"]:
        print(f"\n### {spec}")
        for g, sp in FOCUSED:
            for x, y, s in sp:
                nm = C.X_LABEL[x]
                cells = []
                for cut in CUTOFFS:
                    r = res_all[(res_all.spec == spec) & (res_all.cutoff == cut)
                                & (res_all.x == nm) & (res_all.y == y)]
                    cells.append("n/a" if r.empty else
                                 f"{r.iloc[0].beta:+.2f}({r.iloc[0].p:.2f}) n={int(r.iloc[0].n)}")
                print(f"  {g[:44]:44s} " + " | ".join(cells))
    print("\nAll done ->", OUT)


if __name__ == "__main__":
    main()
