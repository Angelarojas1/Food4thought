# -*- coding: utf-8 -*-
"""
Created on Fri May 29 15:46:35 2026
@author: stevebc

Correlations between country ingredient shares and GPS cultural/preference variables.
Three versions:
  1. Raw (unconditional)
  2. Residuals after partialling out continent FEs
  3. Residuals after partialling out continent FEs + full controls
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
import os
warnings.filterwarnings("ignore")

# =============================================================================
# PATHS
# =============================================================================
country_ingredient = (
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes"
    r"\ingredients\country_canonical_ingredient_shares.csv"
)

country_ingredient = (
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\recipes"
    r"\ingredients\country_category_shares.csv"
)

gps_path = (
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\raw\GPS\country.dta"
)
controls_path = (
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded"
    r"\iv_versatility\first_stage_native_m_c.dta"
)

import_potential_path = (
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded"
    r"\iv_versatility\ingredient_import_potential.dta"
)

SHARE_VAR  = "share_excluding_unmatched"

OUTPUT_DIR = r"C:\Users\stevebc\Dropbox\Cuisine_complexity\3_results\temp"

diabetes_path = r"C:\Users\stevebc\Downloads\diabetes-prevalence.filtered\diabetes-prevalence.csv"  # ← your path
DIABETES_VAR  = "Diabetes prevalence (% of population ages 20 to 79)"

# =============================================================================
# COUNTRY NAME → ISO3 BRIDGE  (covers both GPS and ingredient file)
# =============================================================================
NAME_TO_ISO3 = {
    # A
    "Afghanistan": "AFG", "Albania": "ALB", "Algeria": "DZA",
    "Argentina": "ARG", "Armenia": "ARM", "Australia": "AUS",
    "Austria": "AUT", "Azerbaijan": "AZE",
    # B
    "Bangladesh": "BGD", "Belarus": "BLR", "Belgium": "BEL",
    "Bolivia": "BOL", "Bosnia and Herzegovina": "BIH",
    "Bosnia & Herzegovina": "BIH", "Botswana": "BWA", "Brazil": "BRA",
    "Bulgaria": "BGR",
    # C
    "Cambodia": "KHM", "Cameroon": "CMR", "Canada": "CAN",
    "Chile": "CHL", "China": "CHN", "Colombia": "COL",
    "Costa Rica": "CRI", "Croatia": "HRV", "Czech Republic": "CZE",
    "Czechia": "CZE",
    # D–E
    "Denmark": "DNK", "Dominican Republic": "DOM",
    "Ecuador": "ECU", "Egypt": "EGY", "El Salvador": "SLV",
    "Estonia": "EST", "Ethiopia": "ETH",
    # F–G
    "Finland": "FIN", "France": "FRA",
    "Georgia": "GEO", "Germany": "DEU", "Ghana": "GHA",
    "Greece": "GRC", "Guatemala": "GTM",
    # H–I
    "Haiti": "HTI", "Honduras": "HND", "Hungary": "HUN",
    "India": "IND", "Indonesia": "IDN", "Iran": "IRN",
    "Iraq": "IRQ", "Ireland": "IRL", "Israel": "ISR",
    "Italy": "ITA",
    # J–K
    "Jamaica": "JAM", "Japan": "JPN", "Jordan": "JOR",
    "Kazakhstan": "KAZ", "Kenya": "KEN", "Kosovo": "XKX",
    "Kyrgyzstan": "KGZ",
    # L–M
    "Latvia": "LVA", "Lithuania": "LTU",
    "Malawi": "MWI", "Malaysia": "MYS", "Mali": "MLI",
    "Mexico": "MEX", "Moldova": "MDA", "Morocco": "MAR",
    "Mozambique": "MOZ",
    # N–O
    "Nepal": "NPL", "Netherlands": "NLD", "New Zealand": "NZL",
    "Nicaragua": "NIC", "Niger": "NER", "Nigeria": "NGA",
    "Norway": "NOR",
    # P–R
    "Pakistan": "PAK", "Panama": "PAN", "Paraguay": "PRY",
    "Peru": "PER", "Philippines": "PHL", "Poland": "POL",
    "Portugal": "PRT", "Romania": "ROU", "Russia": "RUS",
    "Rwanda": "RWA",
    # S
    "Saudi Arabia": "SAU", "Senegal": "SEN", "Serbia": "SRB",
    "Slovakia": "SVK", "Slovenia": "SVN", "South Africa": "ZAF",
    "South Korea": "KOR", "Korea, Republic of": "KOR",
    "Republic of Korea": "KOR", "Korea": "KOR",
    "Spain": "ESP", "Sri Lanka": "LKA", "Sudan": "SDN",
    "Suriname": "SUR", "Sweden": "SWE", "Switzerland": "CHE",
    # T–U
    "Tanzania": "TZA", "Thailand": "THA", "Tunisia": "TUN",
    "Turkey": "TUR", "Turkiye": "TUR",
    "Uganda": "UGA", "Ukraine": "UKR",
    "United Kingdom": "GBR", "UK": "GBR",
    "United States": "USA", "United States of America": "USA", "USA": "USA",
    "Uruguay": "URY",
    # V–Z
    "Venezuela": "VEN", "Vietnam": "VNM", "Viet Nam": "VNM",
    "Zambia": "ZMB", "Zimbabwe": "ZWE",
}

GPS_VARS      = ["patience", "risktaking", "posrecip", "negrecip", "altruism", "trust"]
# FULL_CONTROLS = [
#     "numrecipes", "avg_suitability", "trade_distCapital_2000",
#     "al_mn", "ph_mn", "rough", "landlocked", "staple_suitability", "GDP"
# ]

FULL_CONTROLS = [
    "numrecipes", "avg_suitability", "al_mn", "ph_mn", "rough", "landlocked", "staple_suitability", "GDP",
    "import_potential"  
]

# =============================================================================
# HELPERS
# =============================================================================

def to_iso3(series):
    """
    Convert a Series of country identifiers to uppercase ISO3.
    Tries: direct upper-case match (already iso3), then NAME_TO_ISO3 lookup.
    """
    def _convert(val):
        if not isinstance(val, str):
            return np.nan
        v = val.strip()
        # already looks like iso3 (2–3 uppercase letters)
        if len(v) <= 3 and v.isupper():
            return v
        # try name bridge
        return NAME_TO_ISO3.get(v, NAME_TO_ISO3.get(v.title(), np.nan))
    return series.map(_convert)


def partial_out(df, dep_cols, control_cols):
    """
    Residualise dep_cols on control_cols (OLS, with intercept).
    Pure numpy to avoid all pandas index alignment issues.
    Returns df copy with residualised dep_cols.
    """
    df = df.copy()
    result = pd.DataFrame(np.nan, index=df.index, columns=dep_cols)

    ctrl_ok  = df[control_cols].notna().all(axis=1)
    X_ctrl   = df.loc[ctrl_ok, control_cols].values.astype(float)
    X_design = np.column_stack([np.ones(len(X_ctrl)), X_ctrl])

    for col in dep_cols:
        both_ok  = ctrl_ok & df[col].notna()
        if both_ok.sum() < len(control_cols) + 2:
            continue
        # boolean mask *within* ctrl_ok rows
        inner_mask = both_ok.values[ctrl_ok.values]
        X_fit  = X_design[inner_mask]
        y_fit  = df.loc[both_ok, col].values.astype(float)
        coef, *_ = np.linalg.lstsq(X_fit, y_fit, rcond=None)
        resid    = y_fit - X_fit @ coef
        # write back via integer position
        pos = np.where(both_ok.values)[0]
        result.iloc[pos, result.columns.get_loc(col)] = resid

    for col in dep_cols:
        df[col] = result[col].values
    return df


def continent_dummies(series):
    return pd.get_dummies(series, prefix="cont", drop_first=True).astype(float)


def correlate_ingredients(wide_df, gps_df, gps_vars, label, n_top=10):
    """
    Inner-join wide_df and gps_df on index (adm0), then correlate.
    """
    merged = wide_df.join(gps_df[gps_vars], how="inner")
    print(f"  Countries in merged dataset: {len(merged)}")

    ingredient_cols = list(wide_df.columns)
    results = {}

    for gv in gps_vars:
        rows = []
        for ing in ingredient_cols:
            sub = merged[[ing, gv]].dropna()
            if len(sub) < 10:
                continue
            r, p = stats.pearsonr(sub[ing].astype(float), sub[gv].astype(float))
            rows.append({"ingredient": ing, "r": r, "p": p, "n": len(sub)})

        if not rows:
            print(f"  No valid pairs for {gv} — skipping.")
            continue

        df_res = (pd.DataFrame(rows)
                    .sort_values("r", ascending=False)
                    .reset_index(drop=True))
        results[gv] = df_res

        print(f"\n{'='*60}")
        print(f"  {label}  |  {gv}")
        print(f"{'='*60}")
        print(f"  TOP {n_top} POSITIVE:")
        print(df_res.head(n_top).to_string(index=False))
        print(f"\n  TOP {n_top} NEGATIVE:")
        print(df_res.tail(n_top).iloc[::-1].to_string(index=False))

    return results


def save_results(results_dict, label, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    tag = (label.lower()
               .replace(" ", "_").replace(":", "")
               .replace("+", "plus").replace("__", "_"))
    all_dfs = []
    for gv, df_res in results_dict.items():
        df_out = df_res.assign(gps_var=gv, spec=label)
        all_dfs.append(df_out)
        df_out.to_csv(os.path.join(output_dir, f"corr_{tag}_{gv}.csv"), index=False)

    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        combined.to_csv(os.path.join(output_dir, f"corr_{tag}_ALL.csv"), index=False)
        return combined
    return pd.DataFrame()


def top_n_table(results_dict, label, n=10):
    rows = []
    for gv, df_res in results_dict.items():
        for direction, sub in [
            ("positive", df_res.head(n)),
            ("negative", df_res.tail(n).iloc[::-1])
        ]:
            for rank, (_, row) in enumerate(sub.iterrows(), 1):
                rows.append({
                    "spec": label, "gps_var": gv, "direction": direction,
                    "rank": rank, "ingredient": row["ingredient"],
                    "r": round(row["r"], 3), "p": round(row["p"], 3),
                    "n": int(row["n"])
                })
    return pd.DataFrame(rows)


# =============================================================================
# MAIN
# =============================================================================

def main():

    # ------------------------------------------------------------------
    # 1. Ingredient shares → wide (country × ingredient)
    # ------------------------------------------------------------------
    print("Loading ingredient data...")
    ing = pd.read_csv(country_ingredient)

    # The country column contains names, not iso3 — convert
    ing["adm0"] = to_iso3(ing["country"])
    unmapped = ing.loc[ing["adm0"].isna(), "country"].unique()
    if len(unmapped):
        print(f"  WARNING — ingredient countries not mapped to iso3: {list(unmapped)}")
    ing = ing.dropna(subset=["adm0"])

    ing_name_col = next(
        (c for c in ["canonical_ingredient", "ingredient", "ingredient_name"]
         if c in ing.columns),
        [c for c in ing.columns if c not in ["adm0", "country", SHARE_VAR]][0]
    )

    wide = ing.pivot_table(
        index="adm0", columns=ing_name_col,
        values=SHARE_VAR, aggfunc="first"
    )
    wide.columns.name = None
    print(f"  Wide matrix: {wide.shape[0]} countries × {wide.shape[1]} ingredients")
    print(f"  Sample ingredient index (first 5): {list(wide.index[:5])}")

    # ------------------------------------------------------------------
    # 2. Controls
    # ------------------------------------------------------------------
    print("\nLoading controls data...")
    ctrl_raw = pd.read_stata(controls_path)

    # controls file uses 'country' (name) OR 'adm0' (iso3) — handle both
    if "adm0" in ctrl_raw.columns:
        ctrl_raw["adm0"] = ctrl_raw["adm0"].str.strip().str.upper()
    elif "country" in ctrl_raw.columns:
        ctrl_raw["adm0"] = to_iso3(ctrl_raw["country"])

    ctrl = (ctrl_raw.dropna(subset=["adm0"])
                    .drop_duplicates(subset="adm0")
                    .set_index("adm0"))
    print(f"  Controls: {ctrl.shape[0]} unique countries")
    
    # Load and merge import potential into ctrl
    print("\nLoading import potential data...")
    imp_raw = pd.read_stata(import_potential_path)
    
    # The do-file merges on adm0
    if "adm0" in imp_raw.columns:
        imp_raw["adm0"] = imp_raw["adm0"].str.strip().str.upper()
    elif "country" in imp_raw.columns:
        imp_raw["adm0"] = to_iso3(imp_raw["country"])
    
    imp = (imp_raw.dropna(subset=["adm0"])
                  .drop_duplicates(subset="adm0")
                  .set_index("adm0"))
    
    # The do-file uses collapse (mean) on import_potential, so take mean if dupes
    # (after drop_duplicates above, this is a no-op — but safe to be explicit)
    if "import_potential" in imp.columns:
        ctrl = ctrl.join(imp[["import_potential"]], how="left")
        n_matched = ctrl["import_potential"].notna().sum()
        print(f"  import_potential merged: {n_matched} countries matched")
    else:
        print("  WARNING: 'import_potential' column not found in import potential file.")
        print(f"  Available columns: {list(imp.columns)}")

    # ------------------------------------------------------------------
    # 3. GPS
    # ------------------------------------------------------------------
    print("\nLoading GPS data...")
    gps_raw = pd.read_stata(gps_path)

    # GPS has both 'country' (name) and 'isocode' — prefer isocode
    if "isocode" in gps_raw.columns:
        gps_raw["adm0"] = gps_raw["isocode"].str.strip().str.upper()
    else:
        gps_raw["adm0"] = to_iso3(gps_raw.get("country", gps_raw.get("Country", "")))

    gps_raw = (gps_raw.dropna(subset=["adm0"])
                      .drop_duplicates(subset="adm0")
                      .set_index("adm0"))

    avail_gps = [v for v in GPS_VARS if v in gps_raw.columns]
    print(f"  GPS vars: {avail_gps}  ({gps_raw.shape[0]} countries)")
    print(f"  Sample GPS index (first 5): {list(gps_raw.index[:5])}")
    
    
    # ------------------------------------------------------------------
    # 3b. Diabetes
    # ------------------------------------------------------------------
    print("\nLoading diabetes data...")
    diab = pd.read_csv(diabetes_path)
    diab = diab.rename(columns={"Code": "adm0", DIABETES_VAR: "diabetes"})
    diab["adm0"] = diab["adm0"].str.strip().str.upper()
    # keep most recent year per country (already 2024 in your file, but just in case)
    diab = (diab.sort_values("Year", ascending=False)
                .drop_duplicates(subset="adm0")
                .set_index("adm0")[["diabetes"]])
    print(f"  Diabetes: {diab.shape[0]} countries")

    # ------------------------------------------------------------------
    # 4. Diagnostics: check overlap
    # ------------------------------------------------------------------
    overlap_ing_gps  = set(wide.index) & set(gps_raw.index)
    overlap_gps_ctrl = set(gps_raw.index) & set(ctrl.index)
    print(f"\n  Overlap — ingredient ∩ GPS: {len(overlap_ing_gps)} countries")
    print(f"  Overlap — GPS ∩ controls:   {len(overlap_gps_ctrl)} countries")
    if len(overlap_ing_gps) == 0:
        print("\n  !! ZERO OVERLAP — printing sample indices for debugging:")
        print(f"     Ingredient index (first 10): {list(wide.index[:10])}")
        print(f"     GPS index (first 10):        {list(gps_raw.index[:10])}")
        raise ValueError("No country overlap between ingredient and GPS data. "
                         "Check iso3 mapping above.")

    # ------------------------------------------------------------------
    # 5. Build master frame (GPS countries only)
    # ------------------------------------------------------------------
    master = gps_raw[avail_gps].copy()
    cols_needed = ["continent"] + [c for c in FULL_CONTROLS if c in ctrl.columns]
    master = master.join(ctrl[cols_needed], how="left")

    missing_cont = master["continent"].isna().sum() if "continent" in master.columns else len(master)
    if missing_cont:
        print(f"  WARNING: {missing_cont} GPS countries lack continent — they will be "
              f"dropped in continent-FE specs.")

    # ------------------------------------------------------------------
    # 6. Three GPS versions
    # ------------------------------------------------------------------
    gps_v1 = master[avail_gps].copy()

    if "continent" in master.columns and master["continent"].notna().any():
        cont_d  = continent_dummies(master["continent"])
        work_v2 = master[avail_gps].join(cont_d)
        work_v2 = partial_out(work_v2, avail_gps, list(cont_d.columns))
        gps_v2  = work_v2[avail_gps]
    else:
        print("  Skipping continent FE residualisation.")
        gps_v2 = gps_v1.copy()

    avail_fc = [c for c in FULL_CONTROLS if c in master.columns]
    if "continent" in master.columns and avail_fc:
        cont_d   = continent_dummies(master["continent"])
        all_ctrl = list(cont_d.columns) + avail_fc
        work_v3  = master[avail_gps].join(cont_d).join(master[avail_fc])
        work_v3  = partial_out(work_v3, avail_gps, all_ctrl)
        gps_v3   = work_v3[avail_gps]
        print(f"  Full controls used: {avail_fc}")
    else:
        gps_v3 = gps_v2.copy()

    # ------------------------------------------------------------------
    # 7. Run correlations
    # ------------------------------------------------------------------
    specs = [
        ("1_Raw",                           gps_v1),
        ("2_Residual_ContFE",               gps_v2),
        ("3_Residual_ContFE_plus_Controls", gps_v3),
    ]

    all_tops = []
    for label, gps_use in specs:
        print(f"\n\n{'#'*70}")
        print(f"  SPEC: {label}")
        print(f"{'#'*70}")
        res  = correlate_ingredients(wide, gps_use, avail_gps, label)
        save_results(res, label, OUTPUT_DIR)
        if res:
            all_tops.append(top_n_table(res, label))

    if not all_tops:
        print("No results to save.")
        return

    # ------------------------------------------------------------------
    # 8. Master summary
    # ------------------------------------------------------------------
    master_top = pd.concat(all_tops, ignore_index=True)
    out_path   = os.path.join(OUTPUT_DIR, "TOP10_summary_all_specs.csv")
    master_top.to_csv(out_path, index=False)
    print(f"\nSaved master top-10 table → {out_path}")

    for gv in avail_gps:
        for direction in ["positive", "negative"]:
            print(f"\n{'='*80}")
            print(f"  {gv.upper()} | {direction} | top 10 across specs")
            print(f"{'='*80}")
            sub = master_top[
                (master_top["gps_var"] == gv) &
                (master_top["direction"] == direction)
            ][["rank", "ingredient", "spec", "r"]]
            pivot = sub.pivot_table(
                index=["rank", "ingredient"], columns="spec",
                values="r", aggfunc="first"
            )
            print(pivot.to_string())

    print("\nAll done.")
    
    # ------------------------------------------------------------------
    # 9. Diabetes correlations
    # ------------------------------------------------------------------
    print(f"\n\n{'#'*70}")
    print("  DIABETES CORRELATIONS")
    print(f"{'#'*70}")

    # merge ingredient wide matrix with diabetes
    diab_merged = wide.join(diab, how="inner")
    print(f"  Countries with both ingredient and diabetes data: {len(diab_merged)}")

    diab_rows = []
    for ing in wide.columns:
        sub = diab_merged[[ing, "diabetes"]].dropna()
        if len(sub) < 10:
            continue
        r, p = stats.pearsonr(sub[ing].astype(float), sub["diabetes"].astype(float))
        diab_rows.append({"ingredient": ing, "r": r, "p": p, "n": len(sub)})

    diab_results = (pd.DataFrame(diab_rows)
                      .sort_values("r", ascending=False)
                      .reset_index(drop=True))

    n_top = 10
    print(f"\n  TOP {n_top} POSITIVE (more of this → more diabetes):")
    print(diab_results.head(n_top).to_string(index=False))
    print(f"\n  TOP {n_top} NEGATIVE (more of this → less diabetes):")
    print(diab_results.tail(n_top).iloc[::-1].to_string(index=False))

    diab_out = os.path.join(OUTPUT_DIR, "corr_diabetes_ALL.csv")
    diab_results.to_csv(diab_out, index=False)
    print(f"\n  Saved → {diab_out}")

    # also partial out continent FE and full controls (residualise diabetes)
    diab_ctrl = diab.join(ctrl[cols_needed], how="left")

    for spec_label, use_controls in [
        ("2_Residual_ContFE", False),
        ("3_Residual_ContFE_plus_Controls", True),
    ]:
        cont_d = continent_dummies(diab_ctrl["continent"])
        work   = diab_ctrl[["diabetes"]].join(cont_d)
        ctrl_cols = list(cont_d.columns)
        if use_controls:
            fc_here = [c for c in avail_fc if c in diab_ctrl.columns]
            work    = work.join(diab_ctrl[fc_here])
            ctrl_cols = ctrl_cols + fc_here
        work       = partial_out(work, ["diabetes"], ctrl_cols)
        diab_resid = work[["diabetes"]]

        merged_r = wide.join(diab_resid, how="inner")
        rows_r   = []
        for ing in wide.columns:
            sub = merged_r[[ing, "diabetes"]].dropna()
            if len(sub) < 10:
                continue
            r, p = stats.pearsonr(sub[ing].astype(float), sub["diabetes"].astype(float))
            rows_r.append({"ingredient": ing, "r": r, "p": p, "n": len(sub)})

        res_r = (pd.DataFrame(rows_r)
                   .sort_values("r", ascending=False)
                   .reset_index(drop=True))

        print(f"\n  Spec: {spec_label}  ({len(merged_r)} countries)")
        print(f"  TOP {n_top} POSITIVE:"); print(res_r.head(n_top).to_string(index=False))
        print(f"  TOP {n_top} NEGATIVE:"); print(res_r.tail(n_top).iloc[::-1].to_string(index=False))

        tag = spec_label.lower().replace(" ", "_").replace(":", "")
        res_r.to_csv(os.path.join(OUTPUT_DIR, f"corr_diabetes_{tag}.csv"), index=False)

    # ==================================================================
    # SECTION: PCA on ingredient shares → correlate components with GPS
    # ==================================================================
    run_pca_analysis(wide, master, avail_gps, avail_fc, OUTPUT_DIR)


def run_pca_analysis(wide, master, avail_gps, avail_fc, output_dir,
                     n_components_range=(3, 4, 5, 6)):
    """
    1. Restrict to countries present in both wide (ingredients) and master (GPS).
    2. Impute missing ingredient shares with 0 (absent = unused).
    3. Run PCA for each n_components in n_components_range.
    4. For each solution, correlate each PC with each GPS variable —
       raw, continent-FE residual, and continent-FE + controls residual.
    5. Save loadings and correlation tables.
    """
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA

    print(f"\n\n{'#'*70}")
    print("  PCA ON INGREDIENT SHARES")
    print(f"{'#'*70}")

    os.makedirs(output_dir, exist_ok=True)

    # ---- align countries ------------------------------------------------
    common = wide.index.intersection(master.index)
    print(f"  Countries used for PCA: {len(common)}")
    if len(common) < 20:
        print("  Too few countries for PCA — aborting PCA section.")
        return

    X_raw = wide.loc[common].fillna(0).values.astype(float)   # shape: (n_countries, n_ingredients)
    ing_names = list(wide.columns)

    # ---- standardise (mean 0, sd 1 across countries for each ingredient) -
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    # ---- build the three GPS variants for these countries ---------------
    gps_sub = master.loc[common, avail_gps].copy()

    def _residualise(gps_df, ctrl_df, controls):
        """Wrapper around partial_out for the PCA context."""
        work = gps_df.join(ctrl_df[controls], how="left")
        work = partial_out(work, avail_gps, controls)
        return work[avail_gps]

    # GPS v1: raw
    gps_pca_v1 = gps_sub.copy()

    # GPS v2: continent FE
    if "continent" in master.columns:
        cont_d  = continent_dummies(master.loc[common, "continent"])
        gps_pca_v2 = _residualise(gps_sub, cont_d, list(cont_d.columns))
    else:
        gps_pca_v2 = gps_pca_v1.copy()

    # GPS v3: continent FE + full controls
    avail_fc_here = [c for c in avail_fc if c in master.columns]
    if "continent" in master.columns and avail_fc_here:
        cont_d   = continent_dummies(master.loc[common, "continent"])
        all_ctrl = list(cont_d.columns) + avail_fc_here
        ctrl_block = cont_d.join(master.loc[common, avail_fc_here])
        gps_pca_v3 = _residualise(gps_sub, ctrl_block, all_ctrl)
    else:
        gps_pca_v3 = gps_pca_v2.copy()

    gps_versions = {
        "1_Raw":                           gps_pca_v1,
        "2_Residual_ContFE":               gps_pca_v2,
        "3_Residual_ContFE_plus_Controls": gps_pca_v3,
    }

    all_corr_rows = []

    for n_comp in n_components_range:
        print(f"\n  ── PCA with {n_comp} components ──")

        pca   = PCA(n_components=n_comp, random_state=42)
        scores = pca.fit_transform(X_scaled)   # (n_countries, n_comp)

        var_exp = pca.explained_variance_ratio_
        cum_var = np.cumsum(var_exp)
        print(f"  Variance explained per component: "
              f"{[f'{v:.1%}' for v in var_exp]}")
        print(f"  Cumulative: {[f'{v:.1%}' for v in cum_var]}")

        # ---- loadings table (top ingredients per component) ------------
        loadings = pd.DataFrame(
            pca.components_.T,
            index=ing_names,
            columns=[f"PC{k+1}" for k in range(n_comp)]
        )
        load_path = os.path.join(output_dir, f"pca{n_comp}_loadings.csv")
        loadings.to_csv(load_path)

        # Print top-5 positive and negative loadings per PC
        for k in range(n_comp):
            col = f"PC{k+1}"
            top_pos = loadings[col].nlargest(5)
            top_neg = loadings[col].nsmallest(5)
            print(f"\n    PC{k+1} ({var_exp[k]:.1%} var)  — "
                  f"top positive: {dict(zip(top_pos.index, top_pos.round(3).values))}  |  "
                  f"top negative: {dict(zip(top_neg.index, top_neg.round(3).values))}")

        # scores DataFrame (indexed by adm0)
        scores_df = pd.DataFrame(
            scores,
            index=common,
            columns=[f"PC{k+1}" for k in range(n_comp)]
        )

        # ---- correlate PCs with GPS vars, for each spec -----------------
        for spec_label, gps_df in gps_versions.items():
            merged = scores_df.join(gps_df, how="inner")
            n_countries = len(merged)

            print(f"\n    Spec: {spec_label}  ({n_countries} countries)")
            print(f"    {'GPS var':<14}", end="")
            for k in range(n_comp):
                print(f"  PC{k+1}(r / p)", end="")
            print()

            for gv in avail_gps:
                row = {"n_comp": n_comp, "spec": spec_label, "gps_var": gv,
                       "n_countries": n_countries}
                line = f"    {gv:<14}"
                for k in range(n_comp):
                    col = f"PC{k+1}"
                    sub = merged[[col, gv]].dropna()
                    if len(sub) < 10:
                        r, p = np.nan, np.nan
                    else:
                        r, p = stats.pearsonr(sub[col].astype(float),
                                              sub[gv].astype(float))
                    row[f"PC{k+1}_r"] = round(r, 3) if not np.isnan(r) else np.nan
                    row[f"PC{k+1}_p"] = round(p, 3) if not np.isnan(p) else np.nan
                    sig = "*" if (not np.isnan(p) and p < 0.10) else " "
                    line += f"  {r:+.3f}{sig} / {p:.3f}" if not np.isnan(r) else "  —     / —    "
                print(line)
                all_corr_rows.append(row)

    # ---- save master correlation table ----------------------------------
    corr_df = pd.DataFrame(all_corr_rows)
    corr_path = os.path.join(output_dir, "pca_gps_correlations.csv")
    corr_df.to_csv(corr_path, index=False)
    print(f"\n  Saved PCA–GPS correlation table → {corr_path}")
    print("  Loadings saved as pca{N}_loadings.csv for each N in n_components_range.")


if __name__ == "__main__":
    main()