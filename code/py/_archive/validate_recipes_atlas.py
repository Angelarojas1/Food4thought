# -*- coding: utf-8 -*-
"""
Correlations between country category shares and Giuliano-Nunn
Ancestral Characteristics Database variables.
  v1–v5:  reconstructed as continuous (midpoint-weighted % dependence)
  v6+:    reconstructed as meaningful ordinal/continuous or key dummies
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import warnings
import os
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

OUTPUT_DIR  = r"C:\Users\stevebc\Dropbox\Cuisine_complexity\3_results\temp\ea"
SHARE_VAR   = "share_excluding_unmatched"

FULL_CONTROLS = [
    "numrecipes", "avg_suitability", "al_mn", "ph_mn", "rough",
    "landlocked", "staple_suitability", "GDP", "import_potential"
]

# =============================================================================
# MIDPOINTS for v1–v5
# =============================================================================
MIDPOINTS = {
    "grp1": 2.5, "grp2": 10.5, "grp3": 20.5, "grp4": 30.5, "grp5": 40.5,
    "grp6": 50.5, "grp7": 60.5, "grp8": 70.5, "grp9": 80.5, "grp10": 93.0,
}
V_CONTINUOUS = ["v1", "v2", "v3", "v4", "v5"]

# =============================================================================
# HUMAN-READABLE LABELS FOR v1–v5 SCATTER PLOTS
# =============================================================================
V_CONT_LABELS = {
    "v1_continuous": "Subsistence economy: gathering [EA001]\n% dependence on gathering of wild plants and small land fauna",
    "v2_continuous": "Subsistence economy: hunting [EA002]\n% dependence on hunting (incl. trapping and fowling)",
    "v3_continuous": "Subsistence economy: fishing [EA003]\n% dependence on fishing (incl. shellfishing and large aquatic animals)",
    "v4_continuous": "Subsistence economy: animal husbandry [EA004]\n% dependence on animal husbandry",
    "v5_continuous": "Subsistence economy: agriculture [EA005]\n% dependence on agriculture",
}

# =============================================================================
# VARIABLE CONSTRUCTION SPEC for v6+
#
# Each entry: varname → ("type", spec)
#   type = "ordinal"  → spec is dict {grp_col: numeric_value}
#   type = "dummy"    → spec is list of grp_cols to keep as separate dummies
#   type = "skip"     → drop entirely (missing-heavy or redundant)
# =============================================================================
V6_PLUS_SPEC = {

    # --- MARRIAGE & FAMILY -----------------------------------------------

    # v6: type of marriage consideration
    "v6": ("ordinal", {
        "v6_grp7": 0,
        "v6_grp4": 1,
        "v6_grp5": 2,
        "v6_grp6": 2,
        "v6_grp3": 3,
        "v6_grp2": 4,
        "v6_grp8": 5,
    }),

    # v8: family organization
    "v8": ("ordinal", {
        "v8_grp2": 1,
        "v8_grp3": 1,
        "v8_grp4": 1,
        "v8_grp5": 2,
        "v8_grp6": 2,
        "v8_grp7": 3,
        "v8_grp8": 4,
        "v8_grp9": 5,
    }),

    # v9: polygyny
    "v9": ("dummy", [
        "v9_grp2",
        "v9_grp3",
        "v9_grp6",
    ]),

    # v11: marital residence
    "v11": ("dummy", [
        "v11_grp2",
        "v11_grp4",
        "v11_grp3",
    ]),

    # v12: residence rule
    "v12": ("dummy", [
        "v12_grp9",
        "v12_grp6",
        "v12_grp7",
        "v12_grp3",
    ]),

    # v21: descent system
    "v21": ("dummy", [
        "v21_grp8",
        "v21_grp2",
        "v21_grp3",
    ]),

    # v43: kin group descent
    "v43": ("dummy", [
        "v43_grp2",
        "v43_grp4",
        "v43_grp7",
    ]),

    # --- SUBSISTENCE & ECONOMY -------------------------------------------

    # v28: intensity of agriculture
    "v28": ("ordinal", {
        "v28_grp2": 0,
        "v28_grp3": 1,
        "v28_grp5": 2,
        "v28_grp4": 3,
        "v28_grp6": 4,
        "v28_grp7": 5,
    }),

    # v29: main crop type
    "v29": ("dummy", [
        "v29_grp7",
        "v29_grp6",
        "v29_grp5",
        "v29_grp4",
    ]),

    # v39: plow cultivation [EA039]
    "v39": ("ordinal", {
        "v39_grp1": 0,  # absent (no plow animals)
        "v39_grp2": 1,  # plow cultivation not aboriginal but well established
        "v39_grp3": 2,  # animals employed in plow cultivation prior to contact
    }),

    # v40: domestic animals
    "v40": ("dummy", [
        "v40_grp8",
        "v40_grp4",
        "v40_grp3",
        "v40_grp2",
        "v40_grp7",
    ]),

    # v41: milking [EA041]
    "v41": ("ordinal", {
        "v41_grp2": 0,  # little or no milking
        "v41_grp3": 1,  # milked more than sporadically
    }),

    # v42: primary subsistence type
    "v42": ("ordinal", {
        "v42_grp2": 1,
        "v42_grp3": 2,
        "v42_grp4": 3,
        "v42_grp5": 4,
        "v42_grp6": 5,
        "v42_grp7": 6,
        "v42_grp8": 3,
        "v42_grp9": 5,
    }),

    # --- SETTLEMENT & POLITICAL ORGANIZATION -----------------------------

    # v30: settlement permanence
    "v30": ("ordinal", {
        "v30_grp2": 1,
        "v30_grp3": 2,
        "v30_grp4": 3,
        "v30_grp5": 4,
        "v30_grp6": 5,
        "v30_grp7": 6,
        "v30_grp8": 7,
        "v30_grp9": 8,
    }),

    # v31: community size
    "v31": ("ordinal", {
        "v31_grp2": 1,
        "v31_grp3": 2,
        "v31_grp4": 3,
        "v31_grp5": 4,
        "v31_grp6": 5,
        "v31_grp7": 6,
        "v31_grp8": 7,
        "v31_grp9": 8,
    }),

    # v32: jurisdictional hierarchy levels
    "v32": ("ordinal", {
        "v32_grp2": 1,
        "v32_grp3": 2,
        "v32_grp4": 3,
    }),

    # v33: levels beyond local community
    "v33": ("ordinal", {
        "v33_grp2": 0,
        "v33_grp3": 1,
        "v33_grp4": 2,
        "v33_grp5": 3,
        "v33_grp6": 4,
    }),

    # v90: political complexity
    "v90": ("ordinal", {
        "v90_grp2": 0,
        "v90_grp3": 1,
        "v90_grp4": 2,
        "v90_grp5": 3,
        "v90_grp6": 4,
        "v90_grp7": 5,
        "v90_grp8": 4,
    }),

    # --- RELIGION & BELIEFS ----------------------------------------------

    # v34: high gods
    "v34": ("ordinal", {
        "v34_grp2": 0,
        "v34_grp3": 1,
        "v34_grp4": 2,
        "v34_grp5": 3,
    }),

    # v35: games
    "v35": ("dummy", [
        "v35_grp8",
        "v35_grp2",
        "v35_grp3",
        "v35_grp5",
    ]),

    # --- SOCIAL STRATIFICATION -------------------------------------------

    # v66: class stratification
    "v66": ("ordinal", {
        "v66_grp2": 0,
        "v66_grp3": 1,
        "v66_grp4": 2,
        "v66_grp5": 3,
        "v66_grp6": 4,
    }),

    # v70: slavery
    "v70": ("ordinal", {
        "v70_grp2": 0,
        "v70_grp3": 1,
        "v70_grp4": 2,
        "v70_grp5": 3,
    }),

    # --- INHERITANCE -----------------------------------------------------

    # v74: inheritance of real property
    "v74": ("dummy", [
        "v74_grp8",
        "v74_grp3",
        "v74_grp5",
        "v74_grp6",
    ]),

    # v75: order of inheritance
    "v75": ("dummy", [
        "v75_grp5",
        "v75_grp4",
        "v75_grp2",
    ]),

    # --- GENDER IN SUBSISTENCE -------------------------------------------

    # v44: hunting
    "v44": ("dummy", [
        "v44_grp2",
        "v44_grp6",
    ]),

    # v53: food preparation
    "v53": ("ordinal", {
        "v53_grp2": 1,
        "v53_grp3": 2,
        "v53_grp4": 3,
        "v53_grp5": 4,
        "v53_grp6": 5,
        "v53_grp7": 6,
    }),

    # v54: cooking
    "v54": ("ordinal", {
        "v54_grp2": 1,
        "v54_grp3": 2,
        "v54_grp4": 3,
        "v54_grp5": 4,
        "v54_grp6": 5,
        "v54_grp7": 6,
    }),

    # --- ENVIRONMENT -----------------------------------------------------

    # v95: biome
    "v95": ("dummy", [
        "v95_grp16",
        "v95_grp14",
        "v95_grp10",
        "v95_grp5",
        "v95_grp9",
        "v95_grp7",
        "v95_grp6",
    ]),

    # skip these
    "v7":   ("skip", []),
    "v10":  ("skip", []),
    "v13":  ("skip", []),
    "v14":  ("skip", []),
    "v15":  ("skip", []),
    "v16":  ("skip", []),
    "v17":  ("skip", []),
    "v18":  ("skip", []),
    "v19":  ("skip", []),
    "v20":  ("skip", []),
    "v22":  ("skip", []),
    "v23":  ("skip", []),
    "v24":  ("skip", []),
    "v25":  ("skip", []),
    "v26":  ("skip", []),
    "v27":  ("skip", []),
    "v36":  ("skip", []),
    "v37":  ("skip", []),
    "v38":  ("skip", []),
    "v45":  ("skip", []),
    "v46":  ("skip", []),
    "v47":  ("skip", []),
    "v48":  ("skip", []),
    "v49":  ("skip", []),
    "v50":  ("skip", []),
    "v51":  ("skip", []),
    "v52":  ("skip", []),
    "v55":  ("skip", []),
    "v56":  ("skip", []),
    "v57":  ("skip", []),
    "v58":  ("skip", []),
    "v59":  ("skip", []),
    "v60":  ("skip", []),
    "v61":  ("skip", []),
    "v62":  ("skip", []),
    "v63":  ("skip", []),
    "v64":  ("skip", []),
    "v65":  ("skip", []),
    "v67":  ("skip", []),
    "v68":  ("skip", []),
    "v69":  ("skip", []),
    "v71":  ("skip", []),
    "v72":  ("skip", []),
    "v73":  ("skip", []),
    "v76":  ("skip", []),
    "v77":  ("skip", []),
    "v78":  ("skip", []),
    "v79":  ("skip", []),
    "v80":  ("skip", []),
    "v81":  ("skip", []),
    "v82":  ("skip", []),
    "v83":  ("skip", []),
    "v84":  ("skip", []),
    "v85":  ("skip", []),
    "v86":  ("skip", []),
    "v87":  ("skip", []),
    "v88":  ("skip", []),
    "v89":  ("skip", []),
    "v91":  ("skip", []),
    "v92":  ("skip", []),
    "v94":  ("skip", []),
    "v96":  ("skip", []),
    "v97":  ("skip", []),
    "v112": ("skip", []),
    "v113": ("skip", []),
}

# =============================================================================
# COUNTRY NAME → ISO3
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
# HELPERS
# =============================================================================

def partial_out(df, dep_cols, control_cols):
    df = df.copy()
    result = pd.DataFrame(np.nan, index=df.index, columns=dep_cols)
    ctrl_ok  = df[control_cols].notna().all(axis=1)
    X_ctrl   = df.loc[ctrl_ok, control_cols].values.astype(float)
    X_design = np.column_stack([np.ones(len(X_ctrl)), X_ctrl])
    for col in dep_cols:
        both_ok    = ctrl_ok & df[col].notna()
        if both_ok.sum() < len(control_cols) + 2:
            continue
        inner_mask = both_ok.values[ctrl_ok.values]
        X_fit  = X_design[inner_mask]
        y_fit  = df.loc[both_ok, col].values.astype(float)
        coef, *_ = np.linalg.lstsq(X_fit, y_fit, rcond=None)
        resid    = y_fit - X_fit @ coef
        pos = np.where(both_ok.values)[0]
        result.iloc[pos, result.columns.get_loc(col)] = resid
    for col in dep_cols:
        df[col] = result[col].values
    return df


def continent_dummies(series):
    return pd.get_dummies(series, prefix="cont", drop_first=True).astype(float)


def correlate_categories(wide_df, ea_df, ea_vars, label, n_top=10):
    merged = wide_df.join(ea_df[ea_vars], how="inner")
    print(f"  Countries in merged dataset: {len(merged)}")
    category_cols = list(wide_df.columns)
    results = {}
    for ev in ea_vars:
        rows = []
        for cat in category_cols:
            sub = merged[[cat, ev]].dropna()
            if len(sub) < 10:
                continue
            r, p = stats.pearsonr(sub[cat].astype(float), sub[ev].astype(float))
            rows.append({"category": cat, "r": r, "p": p, "n": len(sub)})
        if not rows:
            continue
        df_res = (pd.DataFrame(rows)
                    .sort_values("r", ascending=False)
                    .reset_index(drop=True))
        results[ev] = df_res
        print(f"\n{'='*60}")
        print(f"  {label}  |  {ev}")
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
    for ev, df_res in results_dict.items():
        df_out = df_res.assign(ea_var=ev, spec=label)
        all_dfs.append(df_out)
        df_out.to_csv(os.path.join(output_dir, f"corr_{tag}_{ev}.csv"), index=False)
    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        combined.to_csv(os.path.join(output_dir, f"corr_{tag}_ALL.csv"), index=False)


def scatter_with_labels(ax, x, y, labels, color="#2171b5", fit_color="#e63946"):
    """Scatter plot with ISO3 country labels on each point."""
    ax.scatter(x, y, s=25, alpha=0.5, color=color, edgecolors="none", zorder=4)
    m, b = np.polyfit(x, y, 1)
    x_line = np.linspace(x.min(), x.max(), 200)
    ax.plot(x_line, m * x_line + b, color=fit_color, linewidth=1.5, zorder=3)
    for xi, yi, lbl in zip(x, y, labels):
        ax.annotate(
            lbl,
            xy=(xi, yi),
            xytext=(3, 2),
            textcoords="offset points",
            fontsize=5,
            color="#444444",
            alpha=0.8,
            zorder=5,
        )

def style_axes(ax):
    """Explicitly draw clean left and bottom axis lines; remove top and right."""
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_visible(True)
        ax.spines[spine].set_linewidth(0.8)
        ax.spines[spine].set_color("black")
    ax.tick_params(axis="both", which="both", color="black", labelcolor="black",
                   length=4, width=0.8)


# =============================================================================
# FUNCTION: build meaningful EA variables from raw grp dummies
# =============================================================================

def build_ea_vars(ea_raw, v_cont_cols):
    """
    Returns a DataFrame indexed like ea_raw with all constructed EA variables.
    Also returns a label dict {colname: human_readable_label}.
    """
    out   = pd.DataFrame(index=ea_raw.index)
    labels = {}

    # v1–v5 continuous (already built) — use rich EA labels
    for col in v_cont_cols:
        out[col] = ea_raw[col]
        labels[col] = V_CONT_LABELS.get(col, col)

    # human-readable labels for ordinal/dummy variables
    HUMAN_LABELS = {
        "v6_ordinal":          "v6: marriage consideration (0=absent → 5=dowry)",
        "v8_ordinal":          "v8: family organization (1=nuclear → 5=large extended)",
        "v9_grp2":             "v9: nuclear family monogamous",
        "v9_grp3":             "v9: nuclear family polygyny",
        "v9_grp6":             "v9: non-sororal polygyny",
        "v11_grp2":            "v11: patrilocal (wife to husband's group)",
        "v11_grp4":            "v11: matrilocal (husband to wife's group)",
        "v11_grp3":            "v11: neolocal/ambilocal",
        "v12_grp9":            "v12: patrilocal residence",
        "v12_grp6":            "v12: matrilocal residence",
        "v12_grp7":            "v12: neolocal residence",
        "v12_grp3":            "v12: ambilocal residence",
        "v21_grp8":            "v21: unilineal descent",
        "v21_grp2":            "v21: bilateral descent",
        "v21_grp3":            "v21: kindreds (bilateral ego-oriented)",
        "v28_ordinal":         "v28: agriculture intensity (0=none → 5=intensive irrigated)",
        "v29_grp7":            "v29: main crop = cereal grains",
        "v29_grp6":            "v29: main crop = roots/tubers",
        "v29_grp5":            "v29: main crop = tree fruits",
        "v29_grp4":            "v29: main crop = vegetables",
        "v30_ordinal":         "v30: settlement permanence (1=nomadic → 8=complex)",
        "v31_ordinal":         "v31: community size (1=<50 → 8=cities 50k+)",
        "v32_ordinal":         "v32: jurisdictional hierarchy levels (1–3)",
        "v33_ordinal":         "v33: levels beyond local community (0–4)",
        "v34_ordinal":         "v34: high gods (0=absent → 3=morally active)",
        "v35_grp8":            "v35: games — all types (skill, chance, strategy)",
        "v35_grp2":            "v35: games — none",
        "v35_grp3":            "v35: games — physical skill only",
        "v35_grp5":            "v35: games — strategy only",
        "v39_ordinal":         "Domestic animals: plow cultivation [EA039]\n(0=absent → 2=plow cultivation prior to contact)",
        "v40_grp8":            "v40: domestic animals = bovine",
        "v40_grp4":            "v40: domestic animals = sheep/goats",
        "v40_grp3":            "v40: domestic animals = pigs only",
        "v40_grp2":            "v40: domestic animals = absent",
        "v40_grp7":            "v40: domestic animals = camels/llamas",
        "v41_ordinal":         "Domestic animals: milking [EA041]\n(0=absence or near absence → 1=milked regularly)",
        "v42_ordinal":         "v42: primary subsistence (1=gathering → 6=intensive ag)",
        "v43_grp2":            "v43: patrilineal descent",
        "v43_grp4":            "v43: matrilineal descent",
        "v43_grp7":            "v43: bilateral",
        "v53_ordinal":         "v53: food preparation — gender (1=male only → 6=female only)",
        "v54_ordinal":         "v54: cooking — gender (1=male only → 6=female only)",
        "v66_ordinal":         "v66: class stratification (0=absent → 4=complex)",
        "v70_ordinal":         "v70: slavery (0=absent → 3=hereditary)",
        "v74_grp8":            "v74: land inheritance = patrilineal sons",
        "v74_grp3":            "v74: land inheritance = matrilineal",
        "v74_grp5":            "v74: land inheritance = children, daughters less",
        "v74_grp6":            "v74: land inheritance = children equally",
        "v75_grp5":            "v75: primogeniture",
        "v75_grp4":            "v75: ultimogeniture",
        "v75_grp2":            "v75: equal inheritance",
        "v44_grp2":            "v44: hunting = males only",
        "v44_grp6":            "v44: hunting = absent/unimportant",
        "v90_ordinal":         "v90: political complexity (0=absent → 5=states)",
        "v95_grp16":           "v95: biome = tropical rain forest",
        "v95_grp14":           "v95: biome = tropical grassland",
        "v95_grp10":           "v95: biome = temperate woodland",
        "v95_grp5":            "v95: biome = temperate forest",
        "v95_grp9":            "v95: biome = mediterranean",
        "v95_grp7":            "v95: biome = desert grasses/shrubs",
        "v95_grp6":            "v95: biome = desert",
    }

    for vname, (vtype, spec) in V6_PLUS_SPEC.items():
        if vtype == "skip":
            continue

        elif vtype == "ordinal":
            col_out = f"{vname}_ordinal"
            vals = pd.Series(np.nan, index=ea_raw.index)
            for grp_col, ord_val in spec.items():
                if grp_col not in ea_raw.columns:
                    continue
                w = ea_raw[grp_col].fillna(0)
                vals = vals.combine(w * ord_val, lambda a, b: b if np.isnan(a) else a + b)

            total_w = sum(
                ea_raw[g].fillna(0)
                for g in spec.keys()
                if g in ea_raw.columns
            )
            vals[total_w < 1e-6] = np.nan
            out[col_out] = vals
            labels[col_out] = HUMAN_LABELS.get(col_out, col_out)

        elif vtype == "dummy":
            for grp_col in spec:
                if grp_col not in ea_raw.columns:
                    print(f"  WARNING: {grp_col} not found in EA data")
                    continue
                out[grp_col] = ea_raw[grp_col]
                labels[grp_col] = HUMAN_LABELS.get(grp_col, grp_col)

    print(f"\n  Built {len(out.columns)} meaningful EA variables "
          f"(from {len(V6_PLUS_SPEC)} v6+ variable specs)")
    return out, labels


# =============================================================================
# MAIN
# =============================================================================
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ------------------------------------------------------------------
# 1. Category shares → wide
# ------------------------------------------------------------------
print("Loading category shares...")
ing = pd.read_csv(country_ingredient)
ing["adm0"] = to_iso3(ing["country"])
unmapped = ing.loc[ing["adm0"].isna(), "country"].unique()
if len(unmapped):
    print(f"  WARNING — unmapped: {list(unmapped)}")
ing = ing.dropna(subset=["adm0"])

name_col = next(
    (c for c in ["category", "canonical_ingredient", "ingredient", "ingredient_name"]
     if c in ing.columns),
    [c for c in ing.columns if c not in ["adm0", "country", SHARE_VAR]][0]
)
wide = ing.pivot_table(index="adm0", columns=name_col,
                       values=SHARE_VAR, aggfunc="first")
wide.columns.name = None
print(f"  Wide matrix: {wide.shape[0]} countries × {wide.shape[1]} categories")

# ------------------------------------------------------------------
# 2. EA data
# ------------------------------------------------------------------
print("\nLoading EA data...")
ea_raw = pd.read_stata(ea_path)

if "isocode" in ea_raw.columns:
    ea_raw["adm0"] = ea_raw["isocode"].str.strip().str.upper()
elif "adm0" in ea_raw.columns:
    ea_raw["adm0"] = ea_raw["adm0"].str.strip().str.upper()
elif "country" in ea_raw.columns:
    ea_raw["adm0"] = to_iso3(ea_raw["country"])

ea_raw = (ea_raw.dropna(subset=["adm0"])
                .drop_duplicates(subset="adm0")
                .set_index("adm0"))

# build v1–v5 continuous
print("\nReconstructing v1–v5 as continuous...")
for v in V_CONTINUOUS:
    grp_cols = [c for c in ea_raw.columns if c.startswith(f"{v}_grp")]
    cont_vals = pd.Series(0.0, index=ea_raw.index)
    for col in grp_cols:
        grp_key  = col.split("_", 1)[1]
        midpoint = MIDPOINTS.get(grp_key)
        if midpoint is None:
            continue
        cont_vals += ea_raw[col].fillna(0) * midpoint
    ea_raw[f"{v}_continuous"] = cont_vals

v_cont_cols = [f"{v}_continuous" for v in V_CONTINUOUS
               if f"{v}_continuous" in ea_raw.columns]

# build all meaningful variables
ea_built, var_labels = build_ea_vars(ea_raw, v_cont_cols)
all_ea_vars = list(ea_built.columns)

print(f"\n  EA variables built: {all_ea_vars}")
print(f"\n  Variable labels:")
for k, v in var_labels.items():
    print(f"    {k:<30} {v}")

# ------------------------------------------------------------------
# 3. Controls
# ------------------------------------------------------------------
print("\nLoading controls...")
ctrl_raw = pd.read_stata(controls_path)
if "adm0" in ctrl_raw.columns:
    ctrl_raw["adm0"] = ctrl_raw["adm0"].str.strip().str.upper()
elif "country" in ctrl_raw.columns:
    ctrl_raw["adm0"] = to_iso3(ctrl_raw["country"])
ctrl = (ctrl_raw.dropna(subset=["adm0"])
                .drop_duplicates(subset="adm0")
                .set_index("adm0"))

# ------------------------------------------------------------------
# 4. Master frame
# ------------------------------------------------------------------
master = ea_built.copy()
cols_needed = ["continent"] + [c for c in FULL_CONTROLS if c in ctrl.columns]
master = master.join(ctrl[cols_needed], how="left")

print(f"\n  Overlap — category ∩ EA: "
      f"{len(set(wide.index) & set(master.index))} countries")

# ------------------------------------------------------------------
# 5. Three specs
# ------------------------------------------------------------------
ea_v1 = master[all_ea_vars].copy()

if "continent" in master.columns and master["continent"].notna().any():
    cont_d  = continent_dummies(master["continent"])
    work_v2 = master[all_ea_vars].join(cont_d)
    work_v2 = partial_out(work_v2, all_ea_vars, list(cont_d.columns))
    ea_v2   = work_v2[all_ea_vars]
else:
    ea_v2 = ea_v1.copy()

avail_fc = [c for c in FULL_CONTROLS if c in master.columns]
if "continent" in master.columns and avail_fc:
    cont_d   = continent_dummies(master["continent"])
    all_ctrl = list(cont_d.columns) + avail_fc
    work_v3  = master[all_ea_vars].join(cont_d).join(master[avail_fc])
    work_v3  = partial_out(work_v3, all_ea_vars, all_ctrl)
    ea_v3    = work_v3[all_ea_vars]
    print(f"  Full controls used: {avail_fc}")
else:
    ea_v3 = ea_v2.copy()

# ------------------------------------------------------------------
# 6. Correlations
# ------------------------------------------------------------------
specs = [
    ("1_Raw",                           ea_v1),
    ("2_Residual_ContFE",               ea_v2),
    ("3_Residual_ContFE_plus_Controls", ea_v3),
]

for label, ea_use in specs:
    print(f"\n\n{'#'*70}")
    print(f"  SPEC: {label}")
    print(f"{'#'*70}")
    res = correlate_categories(wide, ea_use, all_ea_vars, label)
    save_results(res, label, OUTPUT_DIR)

# ------------------------------------------------------------------
# 7. Scatter plots: v1–v5 continuous + v39 + v41 vs each category
# ------------------------------------------------------------------
print("\nGenerating scatter plots for v1–v5, v39, v41...")
category_cols = list(wide.columns)

# ------------------------------------------------------------------
# Pretty names for ingredient category y-axis labels
# Add / extend this dict to cover your actual category column names.
# ------------------------------------------------------------------
CATEGORY_PRETTY = {
    "fish_seafood":        "Fish & Seafood",
    "meat_poultry":        "Meat & Poultry",
    "dairy":               "Dairy",
    "dairy_eggs":          "Dairy & Eggs",
    "eggs":                "Eggs",
    "vegetables":          "Vegetables",
    "fruits":              "Fruits",
    "grains_cereals":      "Grains & Cereals",
    "grains":              "Grains",
    "cereals":             "Cereals",
    "legumes":             "Legumes",
    "legumes_pulses":      "Legumes & Pulses",
    "nuts_seeds":          "Nuts & Seeds",
    "herbs_spices":        "Herbs & Spices",
    "spices":              "Spices",
    "herbs":               "Herbs",
    "fats_oils":           "Fats & Oils",
    "oils":                "Oils",
    "sugar_sweets":        "Sugar & Sweets",
    "sweeteners":          "Sweeteners",
    "condiments_sauces":   "Condiments & Sauces",
    "condiments":          "Condiments",
    "beverages":           "Beverages",
    "alcohol":             "Alcohol",
    "bread_bakery":        "Bread & Bakery",
    "pasta_noodles":       "Pasta & Noodles",
    "rice":                "Rice",
    "wheat":               "Wheat",
    "corn_maize":          "Corn & Maize",
    "roots_tubers":        "Roots & Tubers",
    "mushrooms":           "Mushrooms",
    "fermented":           "Fermented Foods",
    "processed":           "Processed Foods",
    "soups_stews":         "Soups & Stews",
    "sauces":              "Sauces",
}

def pretty_category(cat):
    """Return a human-readable label for an ingredient category column name."""
    if cat in CATEGORY_PRETTY:
        return CATEGORY_PRETTY[cat]
    # Generic fallback: replace underscores with spaces, title-case
    return cat.replace("_", " ").title()

# Variables to scatter: v1–v5 continuous, plus v39 and v41 ordinals
scatter_vars = v_cont_cols + ["v39_ordinal", "v41_ordinal"]

for v_col in scatter_vars:
    if v_col not in ea_v1.columns:
        print(f"  SKIP {v_col} — not in ea_v1")
        continue

    v_label = var_labels.get(v_col, v_col)
    merged  = wide.join(ea_v1[[v_col]], how="inner").dropna(subset=[v_col])

    for cat in category_cols:
        sub = merged[[cat, v_col]].dropna()
        if len(sub) < 10:
            continue
        r, p = stats.pearsonr(sub[v_col], sub[cat])

        fig, ax = plt.subplots(figsize=(7, 5))

        scatter_with_labels(
            ax,
            x=sub[v_col].values,
            y=(sub[cat].values * 100),   # convert share → %
            labels=sub.index.tolist(),
        )

        ax.set_title(f"r = {r:.3f},  p = {p:.3f},  n = {len(sub)}", fontsize=10)
        ax.set_xlabel(v_label, fontsize=9)
        ax.set_ylabel(f"{pretty_category(cat)} (%)", fontsize=9)

        style_axes(ax)

        # x-axis formatting by variable type
        if v_col in v_cont_cols:
            # v1–v5: continuous % dependence
            ax.xaxis.set_major_formatter(
                plt.FuncFormatter(lambda val, _: f"{val:.0f}%")
            )
        elif v_col == "v39_ordinal":
            # Three-level ordinal: label each value
            ax.set_xticks([0, 1, 2])
            ax.set_xticklabels(
                ["0 (absent)", "1 (post-contact)", "2 (pre-contact)"],
                fontsize=8,
            )
            ax.set_xlim(-0.3, 2.3)
        # v41 is aggregated to country level so values are continuous 0–1;
        # leave the default matplotlib axis formatting in place

        v_short = v_col.replace("_continuous", "").replace("_ordinal", "")
        fig.suptitle(f"EA {v_short} vs. {pretty_category(cat)}", fontsize=12, fontweight="bold")
        plt.tight_layout()

        fname = f"scatter_{v_short}_vs_{cat.replace('/', '_').replace(' ', '_')}.png"
        plt.savefig(os.path.join(OUTPUT_DIR, fname), dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  {fname}  r={r:.3f}, p={p:.3f}")

# ------------------------------------------------------------------
# 8. World map: Domestic animals — milking [EA041]
# ------------------------------------------------------------------
print("\nGenerating world map for v41 (milking)...")

try:
    import geopandas as gpd
    import urllib.request

    # geopandas.datasets was removed in geopandas 1.0 — download directly from Natural Earth
    NE_URL   = ("https://naturalearth.s3.amazonaws.com/110m_cultural/"
                "ne_110m_admin_0_countries.zip")
    _ne_local = os.path.join(OUTPUT_DIR, "ne_110m_admin_0_countries.zip")
    if not os.path.exists(_ne_local):
        print("  Downloading Natural Earth 110m countries shapefile...")
        urllib.request.urlretrieve(NE_URL, _ne_local)
    world = gpd.read_file(f"zip://{_ne_local}")

    # Pull v41_ordinal from ea_v1 and attach ISO3
    milk_data = ea_v1[["v41_ordinal"]].dropna().copy()
    milk_data.index.name = "iso3"

    # The 110m admin shapefile may use ISO_A3 or ADM0_A3 — find whichever is present
    iso_col = next(
        (c for c in ["ISO_A3", "ADM0_A3", "iso_a3", "ISO_A3_EH"]
         if c in world.columns),
        None,
    )
    if iso_col is None:
        raise ValueError(f"No ISO3 column found in shapefile. Columns: {list(world.columns)}")
    print(f"  Using shapefile ISO column: {iso_col}")

    world_m = world.merge(
        milk_data.reset_index(),
        left_on=iso_col,
        right_on="iso3",
        how="left",
    )

    # Discrete colour map: 0 = little/no milking, 1 = milked regularly, NaN = grey
    cmap_milk = {
        0: "#b2d8e8",   # light blue — no/little milking
        1: "#1a6fa8",   # deep blue  — milked regularly
    }

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_facecolor("#f7f7f7")

    # Base layer: all countries in light grey
    world.plot(ax=ax, color="#dddddd", edgecolor="#aaaaaa", linewidth=0.3)

    # Overlay milking categories
    for val, color in cmap_milk.items():
        subset = world_m[world_m["v41_ordinal"] == val]
        if not subset.empty:
            subset.plot(ax=ax, color=color, edgecolor="#aaaaaa", linewidth=0.3)

    # Manual legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=cmap_milk[0], edgecolor="#aaaaaa",
              label="0 — Absence or near absence of milking"),
        Patch(facecolor=cmap_milk[1], edgecolor="#aaaaaa",
              label="1 — Milked more than sporadically"),
        Patch(facecolor="#dddddd",    edgecolor="#aaaaaa",
              label="No data"),
    ]
    ax.legend(handles=legend_elements, loc="lower left", fontsize=9,
              framealpha=0.9, title="Domestic animals: milking [EA041]",
              title_fontsize=9)

    ax.set_title("Domestic animals: milking [EA041]", fontsize=13, fontweight="bold", pad=10)
    ax.axis("off")
    plt.tight_layout()

    map_fname = "map_v41_milking.png"
    plt.savefig(os.path.join(OUTPUT_DIR, map_fname), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved {map_fname}")

except ImportError:
    # geopandas not available — fall back to a matplotlib patch-based map
    print("  geopandas not found; falling back to pycountry + matplotlib approach.")
    try:
        import pycountry

        # Use a simple Robinson-like equirectangular scatter of centroids
        # (requires only scipy + matplotlib, which are already imported)
        from matplotlib.patches import FancyArrowPatch

        milk_data = ea_v1[["v41_ordinal"]].dropna().copy()

        # Rough ISO3 → (lon, lat) centroids for the countries we have
        # (subset of common countries; others are simply omitted)
        CENTROIDS = {
            "AFG": (67.7, 33.9), "ALB": (20.2, 41.2), "DZA": (2.6, 28.0),
            "AGO": (17.9, -11.2), "ARG": (-63.6, -38.4), "ARM": (45.0, 40.1),
            "AUS": (133.8, -25.3), "AUT": (14.6, 47.7), "AZE": (47.4, 40.1),
            "BGD": (90.4, 23.7), "BLR": (27.9, 53.7), "BEL": (4.5, 50.5),
            "BOL": (-64.7, -16.3), "BIH": (17.7, 44.2), "BWA": (24.7, -22.3),
            "BRA": (-51.9, -14.2), "BGR": (25.5, 42.8),
            "CMR": (12.4, 3.9), "CAN": (-96.8, 60.8), "CHL": (-71.5, -35.7),
            "CHN": (104.2, 35.9), "COL": (-74.3, 4.1), "CRI": (-83.8, 9.7),
            "HRV": (15.2, 45.1), "CZE": (15.5, 49.8),
            "DNK": (10.0, 56.3), "DOM": (-70.2, 18.7),
            "ECU": (-78.2, -1.8), "EGY": (30.8, 26.8), "SLV": (-88.9, 13.8),
            "EST": (25.0, 58.6), "ETH": (40.5, 9.1),
            "FIN": (25.7, 61.9), "FRA": (2.2, 46.2),
            "GEO": (43.4, 42.3), "DEU": (10.4, 51.2), "GHA": (-1.0, 7.9),
            "GRC": (21.8, 39.1), "GTM": (-90.2, 15.8),
            "HTI": (-72.3, 18.9), "HND": (-86.6, 15.2), "HUN": (19.5, 47.2),
            "IND": (78.9, 20.6), "IDN": (113.9, -0.8), "IRN": (53.7, 32.4),
            "IRQ": (43.7, 33.2), "IRL": (-8.2, 53.4), "ISR": (34.9, 31.5),
            "ITA": (12.6, 42.8),
            "JAM": (-77.3, 18.1), "JPN": (138.3, 36.2), "JOR": (37.1, 31.2),
            "KAZ": (66.9, 48.0), "KEN": (37.9, -0.0), "KGZ": (74.8, 41.2),
            "LVA": (24.6, 56.9), "LTU": (23.9, 55.9),
            "MWI": (34.3, -13.3), "MYS": (109.7, 4.2), "MLI": (-2.0, 17.6),
            "MEX": (-102.6, 23.6), "MDA": (28.4, 47.4), "MAR": (-7.1, 31.8),
            "MOZ": (35.5, -18.7),
            "NPL": (84.1, 28.4), "NLD": (5.3, 52.1), "NZL": (172.0, -42.0),
            "NIC": (-85.2, 12.8), "NER": (8.1, 17.6), "NGA": (8.7, 9.1),
            "NOR": (8.5, 60.5),
            "PAK": (69.3, 30.4), "PAN": (-80.8, 8.5), "PRY": (-58.4, -23.4),
            "PER": (-75.0, -9.2), "PHL": (121.8, 12.9), "POL": (19.1, 52.0),
            "PRT": (-8.2, 39.4), "ROU": (25.0, 45.9), "RUS": (97.7, 61.5),
            "RWA": (29.9, -1.9),
            "SAU": (45.1, 23.9), "SEN": (-14.5, 14.5), "SRB": (21.0, 44.0),
            "SVK": (19.7, 48.7), "SVN": (14.8, 46.1), "ZAF": (25.1, -29.0),
            "KOR": (127.8, 35.9), "ESP": (-3.7, 40.2), "LKA": (80.8, 7.9),
            "SDN": (29.9, 15.6), "SWE": (17.0, 62.2), "CHE": (8.2, 46.8),
            "TZA": (34.9, -6.4), "THA": (101.0, 15.9), "TUN": (9.6, 33.9),
            "TUR": (35.2, 38.9),
            "UGA": (32.3, 1.4), "UKR": (31.2, 49.0),
            "GBR": (-3.4, 55.4), "USA": (-100.4, 37.1), "URY": (-56.0, -32.5),
            "VEN": (-66.6, 8.0), "VNM": (108.3, 14.1),
            "ZMB": (27.8, -13.1), "ZWE": (30.0, -19.0),
        }

        colors_map = {0: "#b2d8e8", 1: "#1a6fa8"}
        label_map  = {0: "0 — No/little milking", 1: "1 — Milked regularly"}

        fig, ax = plt.subplots(figsize=(14, 7))
        ax.set_facecolor("#f0f4f8")
        ax.set_xlim(-180, 180)
        ax.set_ylim(-60, 85)
        ax.set_aspect("equal")
        ax.axis("off")

        plotted = {0: False, 1: False}
        for iso3, (lon, lat) in CENTROIDS.items():
            val = milk_data.loc[iso3, "v41_ordinal"] if iso3 in milk_data.index else np.nan
            if np.isnan(val):
                color = "#cccccc"
                lbl   = None
            else:
                val   = int(val)
                color = colors_map[val]
                lbl   = label_map[val] if not plotted[val] else None
                plotted[val] = True
            ax.scatter(lon, lat, s=60, color=color,
                       edgecolors="#666666", linewidth=0.4,
                       label=lbl, zorder=4)

        ax.scatter([], [], s=60, color="#cccccc",
                   edgecolors="#666666", linewidth=0.4, label="No data")
        ax.legend(loc="lower left", fontsize=9, framealpha=0.9,
                  title="Domestic animals: milking [EA041]", title_fontsize=9)
        ax.set_title("Domestic animals: milking [EA041]",
                     fontsize=13, fontweight="bold", pad=10)
        plt.tight_layout()

        map_fname = "map_v41_milking_centroids.png"
        plt.savefig(os.path.join(OUTPUT_DIR, map_fname), dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  Saved {map_fname} (centroid fallback — install geopandas for filled polygons)")

    except Exception as e:
        print(f"  World map skipped: {e}")

print("\nAll done.")