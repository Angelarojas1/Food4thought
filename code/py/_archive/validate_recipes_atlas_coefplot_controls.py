# -*- coding: utf-8 -*-
"""
Coefficient plots under different control sets (same pairs and outcome as
validate_recipes_atlas_coefplot.py):

  A_none        no controls, all countries (identical to the original plot)
  A_common      no controls, restricted to countries with complete controls
  B_contFE      continent fixed effects
  C_contFE_ctrl continent FE + geography/economy controls
                (numrecipes, avg_suitability, al_mn, ph_mn, rough, landlocked,
                 staple_suitability, GDP, import_potential)

B and C use the same sample as A_common so the three are directly comparable.
One plot per spec, plus comparison plots (unweighted, weighted).
"""

import os
import re
import textwrap
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import validate_recipes_atlas_targeted as T
import validate_recipes_atlas_staples as S
import validate_recipes_atlas_coefplot as C

warnings.filterwarnings("ignore")

OUT = C.OUTPUT_DIR + "_controls"
MIN_PER_CONTINENT = 3
CONTROLS = ["numrecipes", "avg_suitability", "al_mn", "ph_mn", "rough",
            "landlocked", "staple_suitability", "GDP", "import_potential"]
SPEC_LABEL = {
    "A_none": "No controls (all countries)",
    "B_contFE_all": "Continent FE (all countries)",
    "A_common": "No controls (common sample)",
    "B_contFE": "Continent fixed effects",
    "C_contFE_ctrl": "Continent FE + geography/economy controls",
}


def estimate(df, x, y, weighted, dummies, conts):
    xs = list(x) if isinstance(x, tuple) else [x]
    need = xs + [y, "n_recipes"] + dummies + conts
    d = df[need].dropna()
    d = d[d["n_recipes"] >= C.MIN_RECIPES]
    # a continent with <3 countries in this sample is fit perfectly by its dummy
    # (leverage 1 -> infinite HC3 s.e.); drop those countries and their dummy
    small = [c for c in dummies if d[c].sum() < MIN_PER_CONTINENT]
    if small:
        d = d[~(d[small].sum(axis=1) > 0)]
        dummies = [c for c in dummies if c not in small]
    # if every country sits in some dummy category, the dummies sum to the
    # constant (rank-deficient): drop the largest one as the reference
    if dummies and (d[dummies].sum(axis=1) > 0).all():
        ref = d[dummies].sum().idxmax()
        dummies = [c for c in dummies if c != ref]
    if len(d) < 15 + len(dummies) + len(conts) \
            or any(d[c].nunique() < 2 for c in xs + [y]):
        return None
    Z = pd.DataFrame({c: C.zs(d[c]) for c in xs})
    if len(xs) == 2:
        Z["inter"] = Z[xs[0]] * Z[xs[1]]
        term = "inter"
    else:
        term = xs[0]
    for c in conts:
        if d[c].std(ddof=0) > 0:
            Z[c] = C.zs(d[c])
    for c in dummies:
        Z[c] = d[c]
    X = sm.add_constant(Z)
    yy = C.zs(d[y])
    mod = (sm.WLS(yy, X, weights=d["n_recipes"]) if weighted else sm.OLS(yy, X))
    r = mod.fit(cov_type="HC3")
    lo, hi = r.conf_int().loc[term]
    if not np.isfinite(r.bse[term]):
        print(f"  WARNING non-finite s.e.: x={x} y={y} wtd={weighted}")
    return dict(beta=r.params[term], se=r.bse[term], lo=lo, hi=hi,
                p=r.pvalues[term], n=len(d))


def run_spec(df, dummies, conts, sample_idx):
    rows = []
    d = df.loc[sample_idx] if sample_idx is not None else df
    for group, specs in C.SPECS:
        for x, y, sign in specs:
            is_int = isinstance(x, tuple)
            name = (f"{C.X_LABEL[x[0]]} × milking" if is_int else C.X_LABEL[x])
            xa = x[0] if is_int else x
            support = int((d[xa] > 0.10).sum()) if xa.startswith("v40_") else ""
            for wtd in (False, True):
                e = estimate(d, x, y, wtd, dummies, conts)
                if e is None:
                    continue
                rows.append(dict(group=group, x=name, y=y, expected=sign,
                                 interaction=is_int, weighted=wtd,
                                 countries_x_gt10pct=support, **e))
    return pd.DataFrame(rows)


def compare_plot(res_all, specs, weighted, path, title, sample_note, headers=True,
                 annotate=False, xlim=None, label_above=False):
    ink, mute, grid = "#1f2933", "#6b7785", "#e4e8ec"
    # no-controls spec in a deeper blue; the other specs in mid-tone, slightly
    # muted colours (same line width / marker size for all)
    cols = {"A_none": "#1c4f9c", "A_common": "#1c4f9c", "B_contFE_all": "#c98f4e",
            "B_contFE": "#c98f4e", "C_contFE_ctrl": "#7fae93"}
    lws = {k: 1.2 for k in cols}
    mss = {k: 5 for k in cols}
    marks = {"A_none": "o", "A_common": "o", "B_contFE_all": "s",
             "B_contFE": "s", "C_contFE_ctrl": "^"}
    span = 0.22 if len(specs) == 3 else 0.14
    if label_above and len(specs) == 2:
        span = 0.21   # label fits between the two estimates of a pair, with a
        #               little room to spare (~22pt between the two lines)
    # first spec in `specs` is drawn on top within each row (y axis points up)
    offs = dict(zip(specs, np.linspace(span, -span, len(specs))))
    layout = []
    for group, sp in C.SPECS:
        if headers:
            layout.append(("hdr", group))
        layout += [("row", (x, y, s)) for x, y, s in sp]
    n = len(layout)
    # more inches per row so pairs are easy to separate (taller when labels sit
    # above the markers)
    fig_h = (0.72 if label_above else 0.66) * n + 2.6
    fig, ax = plt.subplots(figsize=(10.5, fig_h))
    for i, (k, payload) in enumerate(layout):
        yv = n - i
        if k == "hdr":
            ax.text(-0.02, yv, payload, transform=ax.get_yaxis_transform(),
                    ha="right", va="center", fontsize=9, fontweight="bold", color=ink)
            continue
        x, y, sign = payload
        is_int = isinstance(x, tuple)
        name = (f"{C.X_LABEL[x[0]]} × milking" if is_int else C.X_LABEL[x])
        # parenthetical details are dropped from the row labels to save width
        row_label = re.sub(r"\s*\([^)]*\)", "", f"{name} → {C.Y_LABEL[y]}")
        ax.text(-0.02, yv, row_label,
                transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontsize=10, color=ink)
        for sp in specs:
            r = res_all[(res_all.spec == sp) & (res_all.weighted == weighted)
                        & (res_all.x == name) & (res_all.y == y)]
            if r.empty:
                continue
            r = r.iloc[0]
            yy = yv + offs[sp]
            top = sp in ("A_none", "A_common")
            ax.plot([r.lo, r.hi], [yy, yy], color=cols[sp], lw=lws[sp],
                    solid_capstyle="round", zorder=5 if top else 3)
            ax.plot(r.beta, yy, marker=marks[sp], ms=mss[sp], color=cols[sp],
                    mec="white", mew=0.6, zorder=6 if top else 4)
            if annotate:
                st = ("***" if r.p < 0.01 else "**" if r.p < 0.05
                      else "*" if r.p < 0.10 else "")
                if label_above:   # centred above the point estimate (= CI midpoint)
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
        ax.plot([], [], marker=marks[sp], ls="", color=cols[sp],
                ms=mss[sp] * 1.1, label=SPEC_LABEL[sp])
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=3, fontsize=8,
              frameon=False)
    nn = res_all[res_all.spec.isin(specs) & (res_all.weighted == weighted)]["n"].median()
    fig.suptitle(title + (" (weighted by recipes)" if weighted else " (unweighted)"),
                 x=0.02, ha="left", fontsize=12, fontweight="bold", color=ink)
    has_int = any(isinstance(x, tuple) for _, sp in C.SPECS for x, _, _ in sp)
    foot = ("Outcome: share of a country's recipes with ≥1 ingredient from the "
            f"category/group. {sample_note} (median n ≈ {int(nn)})."
            + (" Interaction rows: coefficient on animal share × milking."
               if has_int else "")
            + (" Labels: point estimate; * p<0.10, ** p<0.05, *** p<0.01 (HC3)."
               if annotate else ""))
    fig.text(0.02, 0.15 / fig_h, textwrap.fill(foot, 140), fontsize=7, color=mute,
             ha="left", va="bottom")
    # margins in inches so short figures do not overlap title/legend/footnote
    plt.subplots_adjust(left=0.50, right=0.97, top=1 - 1.05 / fig_h,
                        bottom=1.55 / fig_h)
    fig.savefig(path, dpi=200)
    plt.close(fig)


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
    have = [c for c in CONTROLS if c in ctrl.columns]
    miss = [c for c in CONTROLS if c not in ctrl.columns]
    print("Controls available:", have, "| missing:", miss)
    # numrecipes: use our own recipe count if the file lacks it
    cont_d = pd.get_dummies(ctrl["continent"], prefix="cont",
                            drop_first=True).astype(float)
    dummies = list(cont_d.columns)
    df = pres.join(ea, how="inner").join(ctrl[have]).join(cont_d)
    df["cont_missing"] = ctrl["continent"].reindex(df.index).isna()
    if "numrecipes" not in have:
        df["numrecipes"] = df["n_recipes"]
        have = ["numrecipes"] + have
    base = df[(df.n_recipes >= C.MIN_RECIPES)]
    full_ok = base[~base["cont_missing"]].dropna(subset=have)
    print(f"Countries (>= {C.MIN_RECIPES} recipes, with EA): {len(base)}")
    print(f"  with continent: {int((~base['cont_missing']).sum())}")
    print(f"  with continent + all controls (common sample): {len(full_ok)}")
    lost = base.index.difference(full_ok.index)
    print("  dropped from common sample:", list(lost))
    common_idx = full_ok.index
    print("  continent counts, full sample:",
          base[dummies].sum().astype(int).to_dict(),
          "| reference category n =", int(len(base) - base[dummies].sum().sum()))
    print("  continent counts, common sample:",
          full_ok[dummies].sum().astype(int).to_dict(),
          "| reference category n =",
          int(len(full_ok) - full_ok[dummies].sum().sum()))

    out = {}
    out["A_none"] = run_spec(df, [], [], None)
    out["B_contFE_all"] = run_spec(df, dummies, [], None)   # max sample with FE
    out["A_common"] = run_spec(df, [], [], common_idx)
    out["B_contFE"] = run_spec(df, dummies, [], common_idx)
    out["C_contFE_ctrl"] = run_spec(df, dummies, have, common_idx)
    res_all = pd.concat([r.assign(spec=k) for k, r in out.items()],
                        ignore_index=True)
    res_all.to_csv(os.path.join(OUT, "coefplot_estimates_by_spec.csv"), index=False)

    ctrl_note = ("Controls: " + ", ".join(have))
    for k, r in out.items():
        n_med = int(r["n"].median())
        note = (f"Outcome: share of a country's recipes with ≥1 ingredient from "
                f"the category/group; countries with ≥20 recipes (median n "
                f"≈ {n_med}). Specification: {SPEC_LABEL[k]}."
                + (f" {ctrl_note}." if k == "C_contFE_ctrl" else ""))
        C.plot(r, os.path.join(OUT, f"coefplot_{k}.png"),
               title=f"Recipe–ancestry validations: {SPEC_LABEL[k]}", note=note)
    # (1) largest possible samples: no controls vs continent FE only
    for w, nm in [(False, "unweighted"), (True, "weighted")]:
        compare_plot(res_all, ["A_none", "B_contFE_all"], w,
                     os.path.join(OUT, f"coefplot_compare_maxsample_{nm}.png"),
                     "No controls vs continent FE",
                     "Largest sample: each estimate uses all countries with the "
                     "needed data")
        # (2) identical sample across all three specifications
        compare_plot(res_all, ["A_common", "B_contFE", "C_contFE_ctrl"], w,
                     os.path.join(OUT, f"coefplot_compare_commonsample_{nm}.png"),
                     "Recipe–ancestry validations under different controls",
                     "Same countries in all three specifications")

    # compact printout
    p = (res_all[~res_all.weighted]
         .pivot_table(index=["group", "x", "y"], columns="spec",
                      values=["beta", "p"], aggfunc="first"))
    order = []
    for g, sp in C.SPECS:
        for x, y, s in sp:
            nm = (f"{C.X_LABEL[x[0]]} × milking" if isinstance(x, tuple)
                  else C.X_LABEL[x])
            order.append((g, nm, y))
    p = p.reindex(order)
    pd.set_option("display.width", 250)
    print("\nUnweighted beta (p) by spec:")
    for idx, r in p.iterrows():
        s = "  ".join(f"{k[:3]}={r[('beta', k)]:+.2f}({r[('p', k)]:.2f})"
                      for k in ["A_none", "B_contFE_all", "A_common", "B_contFE",
                                "C_contFE_ctrl"]
                      if pd.notna(r.get(('beta', k), np.nan)))
        print(f"  {idx[1][:34]:34s} -> {idx[2]:15s} {s}")
    print("\nAll done ->", OUT)


if __name__ == "__main__":
    main()
