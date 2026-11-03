# -*- coding: utf-8 -*-
"""
Plots instrument variable maps
"""

import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import statsmodels.api as sm


# ============================================================
# 1. LOAD IV DATA
# ============================================================

#iv_data_path = "C:/Users/stell/Dropbox/food4thought/analysis23/data/coded/iv_versatility/native_versatility_m_c_dist_all.dta"
iv_data_path = "C:/Users/stevebc/Dropbox/food4thought/analysis23/data/coded/iv_versatility/native_versatility_m_c_dist_all.dta"

iv_df = pd.read_stata(iv_data_path, convert_categoricals=False)

iv_df = iv_df[[
    "adm0",
    "vers_distCapital_2000",
    "trade_distCapital_2000"
]]

# ============================================================
# 1B. LOAD PCA DATA
# ============================================================

pca_data_path = "../../data/coded/cookpad/cookpad_adm0.dta"

pca_df = pd.read_stata(pca_data_path, convert_categoricals=False)

pca_df = pca_df[["adm0", "z_pca_recipe"]]

# Collapse to country level
pca_df = (
    pca_df
    .groupby("adm0", as_index=False)
    .agg({"z_pca_recipe": "mean"})
)


# ============================================================
# 2. CLEAN VARIABLES
# ============================================================

# Treat zeros as missing
iv_df.loc[iv_df["vers_distCapital_2000"] == 0, "vers_distCapital_2000"] = np.nan
iv_df.loc[iv_df["trade_distCapital_2000"] == 0, "trade_distCapital_2000"] = np.nan


# Filter out countries not in the PCA
valid_adm0 = set(pca_df["adm0"])

iv_df.loc[
    ~iv_df["adm0"].isin(valid_adm0),
    ["vers_distCapital_2000", "trade_distCapital_2000"]
] = np.nan


# ============================================================
# 3. RESIDUALIZE IV (for own diagnosis)
# ============================================================

resid_df = iv_df.dropna(
    subset=["vers_distCapital_2000", "trade_distCapital_2000"]
).copy()

X = sm.add_constant(resid_df["trade_distCapital_2000"])
y = resid_df["vers_distCapital_2000"]

model = sm.OLS(y, X).fit()

resid_df["vers_trade_resid"] = model.resid


# ============================================================
# 4. LOAD WORLD SHAPEFILE
# ============================================================

world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
world = world[world["name"] != "Antarctica"]

world = world.rename(columns={"iso_a3": "adm0"})


# ============================================================
# 5. MERGE DATA
# ============================================================

world_iv = world.merge(iv_df, on="adm0", how="left")

world_iv = world_iv.merge(
    resid_df[["adm0", "vers_trade_resid"]],
    on="adm0",
    how="left"
)


# ============================================================
# 6. MAP PLOTTING FUNCTION
# ============================================================

def plot_map(gdf, column, title=None, save_path=None):

    fig, ax = plt.subplots(figsize=(12, 6))

    gdf.plot(
        column=column,
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

    # Colorbar settings
    cbar = fig.axes[-1]
    cbar.set_ylabel("", fontsize=12)
    cbar.tick_params(labelsize=9)

    ax.set_title(title if title else column)
    ax.axis("off")

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()


# ============================================================
# 7. PLOT MAPS
# ============================================================

# Trade distance
plot_map(
    world_iv,
    "trade_distCapital_2000",
    title="Trade Distance to Capital",
    save_path="../../outputs/Figures/maps/trade_distance_map_NEW.png"
)


# Raw instrument
plot_map(
    world_iv,
    "vers_distCapital_2000",
    title="Import Versatility Distance",
    save_path="../../outputs/Figures/maps/versatility_distance_map_NEW.png"
)


# Residualized instrument
# plot_map(
#     world_iv,
#     "vers_trade_resid",
#     title="Import Versatility (Residualized)"
# )