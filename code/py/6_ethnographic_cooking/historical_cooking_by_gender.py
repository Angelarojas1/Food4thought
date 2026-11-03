# -*- coding: utf-8 -*-
"""
Created on Mon Feb 23 13:34:13 2026
@author: stevebc
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import pyreadstat
import matplotlib.pyplot as plt


# ============================================================
# 1. LOAD SCCS DATA
# ============================================================

sccs_data_path = r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\raw\SCCS_ethnographic\raw\data.csv"
sccs_societies_path = r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\raw\SCCS_ethnographic\raw\societies.csv"

sccs = pd.read_csv(sccs_data_path, low_memory=False)
societies = pd.read_csv(sccs_societies_path)

# Keep only relevant cooking variables
COOK_TOTAL = "SCCS121"
COOK_ADULT = "SCCS1592"
COOK_CHILD = "SCCS1593"

sccs = sccs[sccs["var_id"].isin([COOK_TOTAL, COOK_ADULT, COOK_CHILD])]


# ============================================================
# 2. RESHAPE TO ONE ROW PER SOCIETY
# ============================================================

sccs_wide = sccs.pivot(index="soc_id",
                        columns="var_id",
                        values="code").reset_index()

# Merge coordinates
df = sccs_wide.merge(
    societies[["id", "Lat", "Long"]],
    left_on="soc_id", right_on="id",
    how="left"
)


# ============================================================
# 3. CODE FEMALE COOKING INTENSITY (1–4 SCALE)
# ============================================================

def recode_total(x):
    """
    SCCS121 codes:
    2 = males predominant
    3 = equal
    4 = females predominant
    5 = females exclusively
    """
    if pd.isna(x):
        return np.nan
    if x == 2:
        return 1
    elif x == 3:
        return 2
    elif x == 4:
        return 3
    elif x == 5:
        return 4
    else:
        return np.nan


def recode_adult(x):
    """
    SCCS1592:
    2 men pred
    3 equal
    4 women pred
    5 women only
    9 women no data men
    """
    if pd.isna(x):
        return np.nan
    if x == 2:
        return 1
    elif x == 3:
        return 2
    elif x == 4:
        return 3
    elif x in [5, 9]:
        return 4
    else:
        return np.nan


def recode_child(x):
    """
    SCCS1593:
    2 boys pred
    3 equal
    4 girls pred
    5 girls only
    9 girls no data boys
    """
    if pd.isna(x):
        return np.nan
    if x == 2:
        return 1
    elif x == 3:
        return 2
    elif x == 4:
        return 3
    elif x in [5, 9]:
        return 4
    else:
        return np.nan


df["female_total"] = df[COOK_TOTAL].apply(recode_total)
df["female_adult"] = df[COOK_ADULT].apply(recode_adult)
df["female_child"] = df[COOK_CHILD].apply(recode_child)


# ============================================================
# 4. CONVERT TO GEODATAFRAME
# ============================================================

df = df.dropna(subset=["Lat", "Long"])

geometry = [Point(xy) for xy in zip(df["Long"], df["Lat"])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")


# ============================================================
# SPATIAL MATCH (ROBUST VERSION)
# ============================================================

world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

# Project both to metric CRS
world = world.to_crs("EPSG:3857")
gdf = gdf.to_crs("EPSG:3857")

# Assign exactly ONE nearest country to each society
gdf = gpd.sjoin_nearest(
    gdf,
    world[["iso_a3", "geometry"]],
    how="left",
    distance_col="dist"
)

gdf = gdf.rename(columns={"iso_a3": "adm0"})

# Optional: sanity check distances
print("Max match distance (meters):", gdf["dist"].max())

# Back to lat/lon
gdf = gdf.to_crs("EPSG:4326")


# # ============================================================
# # 6. HANDLE ISLAND STATES (NEAREST MATCH)
# # ============================================================

# missing = gdf[gdf["adm0"].isna()].copy()

# if len(missing) > 0:

#     world_proj = world.to_crs("EPSG:3857")
#     missing_proj = missing.to_crs("EPSG:3857")

#     nearest = gpd.sjoin_nearest(
#         missing_proj,
#         world_proj[["iso_a3", "geometry"]],
#         how="left"
#     )

#     # nearest keeps original index from missing
#     # so we assign using index alignment
#     gdf.loc[nearest.index, "adm0"] = nearest["iso_a3"]


# ============================================================
# 7. LOAD PCA AND IV DATA (STATA)
# ============================================================

pca_data_path = r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\cookpad\cookpad_adm0.dta"
iv_data_path = r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\iv_versatility\native_versatility_m_c_dist_all.dta"

pca_df = pd.read_stata(
    pca_data_path,
    convert_categoricals=False
)



iv_df = pd.read_stata(
    iv_data_path,
    convert_categoricals=False
)

pca_df = pca_df[["adm0", "z_pca_recipe"]]

pca_df = (
    pca_df
    .groupby("adm0", as_index=False)
    .agg({"z_pca_recipe": "mean"})
)



iv_df = iv_df[["adm0", "vers_distCapital_2000", "trade_distCapital_2000"]]

import statsmodels.api as sm

# ============================================================
# 7B. PARTIAL OUT TRADE CENTRALITY FROM THE IV
# ============================================================

# Use only observations where both variables are observed
resid_df = iv_df[["adm0", "vers_distCapital_2000", "trade_distCapital_2000"]].copy()

# Treat zeros as missing if that is your convention
resid_df.loc[resid_df["vers_distCapital_2000"] == 0, "vers_distCapital_2000"] = np.nan
resid_df.loc[resid_df["trade_distCapital_2000"] == 0, "trade_distCapital_2000"] = np.nan

resid_df = resid_df.dropna(subset=["vers_distCapital_2000", "trade_distCapital_2000"]).copy()

# Regress IV on trade centrality
X = sm.add_constant(resid_df["trade_distCapital_2000"])
y = resid_df["vers_distCapital_2000"]

model = sm.OLS(y, X).fit()

# Residual = IV net of trade centrality
resid_df["vers_trade_resid"] = model.resid

print(model.summary())

# ============================================================
# 8. KEEP ONLY COUNTRIES THAT EXIST IN BOTH PCA AND IV
# ============================================================

valid_adm0 = set(pca_df["adm0"]).intersection(set(iv_df["adm0"]))

#gdf = gdf[gdf["adm0"].isin(valid_adm0)]

# Add continent to gdf
world_cont = world.to_crs("EPSG:4326")[["iso_a3", "continent"]]

gdf = gdf.merge(
    world_cont,
    left_on="adm0",
    right_on="iso_a3",
    how="left"
)

# Merge
gdf = gdf.merge(pca_df, on="adm0", how="left")
gdf = gdf.merge(iv_df, on="adm0", how="left")







# ============================================================
# 9. Binscatter Function (Manual, Matplotlib Only)
# ============================================================

import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

def binscatter(x, y, n_bins=20,
               xtitle="Cuisine Complexity",
               ytitle="Female Cooking Intensity",
               save=None):

    # Drop missing
    df_temp = pd.DataFrame({"x": x, "y": y}).dropna()

    N = len(df_temp)

    # Create bins
    df_temp["bin"] = pd.qcut(df_temp["x"], n_bins, duplicates="drop")
    binned = df_temp.groupby("bin", observed=False).mean()

    # -----------------------------
    # OLS on RAW (not binned) data
    # -----------------------------
    X = sm.add_constant(df_temp["x"])
    model = sm.OLS(df_temp["y"], X).fit()

    intercept, slope = model.params
    r2 = model.rsquared

    # Fitted line range
    x_vals = np.linspace(df_temp["x"].min(), df_temp["x"].max(), 100)
    y_vals = intercept + slope * x_vals

    # -----------------------------
    # Plot
    # -----------------------------
    plt.figure()

    # Binned scatter
    plt.scatter(binned["x"], binned["y"])

    # Fitted line
    plt.plot(x_vals, y_vals)

    plt.xlabel(xtitle)
    plt.ylabel(ytitle)

    # Add R2 and N text
    plt.text(
        0.05, 0.95,
        f"N = {N}\nR² = {r2:.3f}",
        transform=plt.gca().transAxes,
        verticalalignment='top'
    )
    
    ax = plt.gca()

    # Y ticks every 0.5
    ax.set_yticks(np.arange(
        np.floor(df_temp["y"].min()),
        np.ceil(df_temp["y"].max()) + 0.5,
        0.5
    ))
    
    # X ticks in whole units
    ax.set_xticks([1,2,3,4])
    
    if save is not None:
        plt.savefig(save, dpi=300, bbox_inches="tight")

    plt.show()


# ============================================================
# 10. RUN BINSCATTERS
# ============================================================

# Example: use adult female cooking

y_var = "female_total"

# PCA plot

gdf_pca_plot = gdf[(gdf["continent"]!="North America") & (gdf["continent"]!="South America")]

#gdf_pca_plot = gdf_pca_plot[gdf_pca_plot["female_total"]>2]

binscatter(gdf["z_pca_recipe"], gdf_pca_plot[y_var], 20)

# IV plot

gdf_iv_plot = gdf[gdf["vers_distCapital_2000"]!=0]


binscatter(gdf_iv_plot["vers_distCapital_2000"], gdf_iv_plot[y_var], 15, "Import Versatility", "Female Cooking Intensity")



# Baseline daughter-mother scatterplot
y_var = "female_child"
x_var = "female_total"

binscatter(gdf[x_var], gdf[y_var],47, "Adult female cooking", "Child female cooking", save=r"C:\Users\stevebc\Dropbox\food4thought\analysis23\outputs\Figures\ethnographic\binscatter_female_learning.png")

# Correlation and p-value
from scipy import stats

y_var = "female_child"
x_var = "female_adult"

corr_df = gdf[[x_var, y_var]].dropna()

r, p_value = stats.pearsonr(
    corr_df[x_var],
    corr_df[y_var]
)

print(f"N = {len(corr_df)}")
print(f"Pearson r = {r:.3f}")
print(f"p-value = {p_value:.5f}")




# PLOT MAPS HERE: first of trade distance, then of our final instrument ("vers_distCapital_2000")

# ============================================================
# MAP DATA PREPARATION
# ============================================================

# Load world polygons
world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

world = world[world["name"] != "Antarctica"]

# Keep ISO codes
world = world.rename(columns={"iso_a3": "adm0"})

# Merge residualized IV to country polygons
world_iv = world.merge(iv_df, on="adm0", how="left")
world_iv = world_iv.merge(
    resid_df[["adm0", "vers_trade_resid"]],
    on="adm0",
    how="left"
)

# Set zero values to missing for raw variables
world_iv.loc[world_iv["vers_distCapital_2000"] == 0, "vers_distCapital_2000"] = np.nan
world_iv.loc[world_iv["trade_distCapital_2000"] == 0, "trade_distCapital_2000"] = np.nan



fig, ax = plt.subplots(figsize=(12,6))

world_iv.plot(
    column="trade_distCapital_2000",
    cmap="viridis",
    legend=True,
    edgecolor="black",
    linewidth=0.2,
    ax=ax,
    legend_kwds={"shrink":0.5, "pad":0.01},
    missing_kwds={
        "color": "lightgrey",
        "label": "No data"
    }
)

# Access colorbar axis
cbar = fig.axes[-1]

# Set label and font size
cbar.set_ylabel("", fontsize=12, fontweight="bold")

# Reduce tick label size if desired
cbar.tick_params(labelsize=9)

ax.axis("off")

# plt.savefig(
#     r"C:\Users\stevebc\Dropbox\food4thought\analysis23\outputs\Figures\maps\trade_distance_map.png",
#     dpi=300,
#     bbox_inches="tight"
# )

plt.show()


# ONLY show countries with PCA data
valid_adm0 = set(pca_df["adm0"]).intersection(set(iv_df["adm0"]))
world_iv.loc[
    ~world_iv["adm0"].isin(valid_adm0),
    "vers_distCapital_2000"
] = np.nan

fig, ax = plt.subplots(figsize=(12,6))

world_iv.plot(
    column="vers_distCapital_2000",
    cmap="viridis",
    legend=True,
    edgecolor="black",
    linewidth=0.2,
    ax=ax,
    legend_kwds={"shrink":0.5, "pad":0.01},
    missing_kwds={
        "color": "lightgrey",
        "label": "No data"
    }
)

# Access colorbar axis
cbar = fig.axes[-1]

# Set label and font size
cbar.set_ylabel("", fontsize=12, fontweight="bold")

# Reduce tick label size if desired
cbar.tick_params(labelsize=9)

ax.axis("off")

# plt.savefig(
#     r"C:\Users\stevebc\Dropbox\food4thought\analysis23\outputs\Figures\maps\versatility_distance_map.png",
#     dpi=300,
#     bbox_inches="tight"
# )

plt.show()


sdfsdf


fig, ax = plt.subplots(figsize=(12,6))

world_iv.plot(
    column="vers_trade_resid",
    cmap="viridis",
    legend=True,
    edgecolor="black",
    linewidth=0.2,
    ax=ax,
    legend_kwds={"shrink": 0.5, "pad": 0.01},
    missing_kwds={
        "color": "lightgrey",
        "label": "No data"
    }
)

cbar = fig.axes[-1]
cbar.set_ylabel("", fontsize=12, fontweight="bold")
cbar.tick_params(labelsize=9)

ax.axis("off")

# plt.savefig(
#     r"C:\Users\stevebc\Dropbox\food4thought\analysis23\outputs\Figures\maps\versatility_net_of_trade_map.png",
#     dpi=300,
#     bbox_inches="tight"
# )

plt.show()

sdfsdfsdf



# Plot mother-daughter correlation for above vs below median cuisine complexity
median_pca = gdf["z_pca_recipe"].median()

gdf["high_pca"] = (gdf["z_pca_recipe"] > median_pca).astype(int)

print("Median PCA:", median_pca)
print(gdf["high_pca"].value_counts())

y_var = "female_child"
x_var = "female_total"

# Low PCA countries
binscatter(
    gdf.loc[gdf["high_pca"] == 0, x_var],
    gdf.loc[gdf["high_pca"] == 0, y_var],
    10,
    "Female Total (Low PCA)",
    "Female Child"
)

# High PCA countries
binscatter(
    gdf.loc[gdf["high_pca"] == 1, x_var],
    gdf.loc[gdf["high_pca"] == 1, y_var],
    10,
    "Female Total (High PCA)",
    "Female Child"
)

from scipy import stats

for group, label in [(0, "Low PCA"), (1, "High PCA")]:
    
    sub = gdf.loc[gdf["high_pca"] == group, [x_var, y_var]].dropna()
    
    if len(sub) > 2:
        r, p = stats.pearsonr(sub[x_var], sub[y_var])
        print(f"\n{label}")
        print(f"N = {len(sub)}")
        print(f"r = {r:.3f}")
        print(f"p = {p:.4f}")
    else:
        print(f"\n{label}: Too few observations")