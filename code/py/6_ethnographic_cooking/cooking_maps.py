# -*- coding: utf-8 -*-
"""
Created on Wed Nov 19 08:06:47 2025

@author: stevebc

Script to produce map with ancestral and current share of female cooking
"""

import geopandas as gpd
import pandas as pd
import numpy as np

# -------------------------------------------------------------------
# 1. Process Standard Cross-Cultural Sample (SCCS)
# -------------------------------------------------------------------

# csv file where each row has coordinate and a qualitative indicator who cooks most
# -> convert to categorical (1–4) with a consistent 0–1 scale
sccs_csv = r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\precoded\ethnographic\SCCS_who_cooks.csv"

# Load SCCS CSV
sccs = pd.read_csv(sccs_csv)

# Expected fields: "lat", "lon", "cook_cat"
# where cook_cat is qualitative (e.g., "mostly men", "mostly women", etc.)
# Map qualitative categories → numeric 1–4
cook_map = {
    "Males Exclusively": 1,
    "Males Predominantly": 2,
    "Equally": 3,
    "Females Predominantly": 4,
    "Females Exclusively": 5
}

# If already numeric, this has no effect
sccs["cook_num"] = sccs["who_cook"].map(cook_map).astype(float)

# Normalize SCCS to 0–1 scale
# (same scale that Cookpad will be mapped onto)
sccs_min, sccs_max = 1, 4   # qualitative categories

sccs["cook_norm"] = (sccs["cook_num"] - sccs_min) / (sccs_max - sccs_min)

# Convert to GeoDataFrame
sccs_gdf = gpd.GeoDataFrame(
    sccs,
    geometry=gpd.points_from_xy(sccs["Longitude"], sccs["Latitude"]),
    crs="EPSG:4326"
)

# Convert to Voronoi polygons
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, Point
import geopandas as gpd
import numpy as np

# Extract coordinates (must be in 2D numpy array)
points = np.column_stack([sccs_gdf.geometry.x, sccs_gdf.geometry.y])

# Build Voronoi diagram
vor = Voronoi(points)

# Function: Convert Voronoi region to Polygon, skip infinite regions
def region_to_poly(vor, region_index):
    region = vor.regions[region_index]
    if -1 in region or len(region) == 0:
        return None   # skip infinite or empty regions
    
    polygon = Polygon(vor.vertices[region])
    return polygon

# Create list of Voronoi polygons matching point order
polygons = []
for point_idx, region_index in enumerate(vor.point_region):
    poly = region_to_poly(vor, region_index)
    polygons.append(poly)

# Build GeoDataFrame
voronoi_gdf = gpd.GeoDataFrame(
    sccs_gdf.copy(),
    geometry=polygons,
    crs="EPSG:4326"
)

# -------------------------------------------------------------------
# 2. Process Cookpad data
# -------------------------------------------------------------------

cookpad_stata = r"C:\Users\stevebc\Dropbox\food4thought\analysis23\data\coded\cookpad\cookpad_adm0.dta"

# Load without converting to categorical
cookpad = pd.read_stata(cookpad_stata, convert_categoricals=False)

# Total meals cooked per respondent per week
cookpad["total_meals"] = cookpad["numLunCook"] + cookpad["numDinCook"]

# Restrict to married individuals only?
#cookpad = cookpad[cookpad["wp1223"]==2]

# Share of partners (of women) who cooked any meal

# -------------------------------------------------------------------
# 1. Average meals cooked by women in each country
# 2. Average meals cooked by men in each country
# 3. Share = avg_w / (avg_w + avg_m)
# -------------------------------------------------------------------

grouped = (
    cookpad.groupby(["adm0", "fem"])
           .agg(avg_meals=("total_meals", "mean"))
           .reset_index()
)

# Pivot, to get one country per row:

pivoted = grouped.pivot(index="adm0", columns="fem", values="avg_meals")

# Rename columns for clarity
pivoted = pivoted.rename(columns={0: "avg_meals_men", 1: "avg_meals_women"})

# -------------------------------------------------------------------
# 3. Compute share = avg_women / (avg_women + avg_men)
# -------------------------------------------------------------------

pivoted["female_share"] = (
    pivoted["avg_meals_women"] /
    (pivoted["avg_meals_women"] + pivoted["avg_meals_men"])
)

# Reset index so adm0 becomes a column again
cookpad_country = pivoted.reset_index()

# -------------------------------------------------------------------
# 3. Load world shapefile
# -------------------------------------------------------------------

world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

# Map ISO3 → shapefile
world = world.rename(columns={"iso_a3": "adm0"})

# Merge Cookpad country-level data to world polygons
world_cookpad = world.merge(cookpad_country, on="adm0", how="left")

# -------------------------------------------------------------------
# 4. OUTPUT objects ready for mapping
# -------------------------------------------------------------------
print("\nSCCS GeoDataFrame:\n", sccs_gdf.head())
print("\nCookpad + world merged GeoDataFrame:\n", world_cookpad.head())


# Plot Panel  A (Ethnographic) + Panel B (Cookpad)

# -------------------------------------------------------------------
# 5. Plot settings
# -------------------------------------------------------------------

import matplotlib.pyplot as plt
import matplotlib.colors as colors

# Shared 0–1 normalization for both datasets
norm = colors.Normalize(vmin=0, vmax=1)

# Set categorical colormap
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap

# Five colors from green (1) to red (5)
colors_list = ["green", "lime", "yellow", "orange", "red"]

cat_cmap = mcolors.ListedColormap(colors_list)

# Boundaries: 1,2,3,4,5,6 → 5 bins (1–2, 2–3, 3–4, 4–5, 5–6)
bounds = [2, 3, 4, 5, 6]
cat_norm = mcolors.BoundaryNorm(bounds, cat_cmap.N)

cmap = "viridis"   
cmap = "Spectral_r"
cmap = "RdYlBu_r"

# -------------------------------------------------------------------
# Top-bottom comparison (vertical layout)
# -------------------------------------------------------------------

fig, axes = plt.subplots(2, 1, figsize=(10, 12), dpi=200)
#fig, axes = plt.subplots(2, 1, figsize=(10, 12), dpi=200, constrained_layout=True)

from matplotlib.patches import Patch

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

vir = plt.cm.get_cmap("viridis")
vir = plt.cm.get_cmap("Spectral_r")
vir = plt.cm.get_cmap("RdYlBu_r")

# sample 5 evenly spaced viridis colors
viridis_colors = vir(np.linspace(0, 1, 4))

cat_cmap = mcolors.ListedColormap(viridis_colors)
bounds = [2, 3, 4, 5, 6]     # 5 bins
cat_norm = mcolors.BoundaryNorm(bounds, cat_cmap.N)

from matplotlib.lines import Line2D

legend_elements = [
    # Line2D([0], [0], marker='o', color='black',
    #        markerfacecolor=viridis_colors[0], markersize=6,
    #        linestyle='None', label='Males Exclusively'),

    Line2D([0], [0], marker='o', color='black',
           markerfacecolor=viridis_colors[0], markersize=6,
           linestyle='None', label='Males Predominantly'),

    Line2D([0], [0], marker='o', color='black',
           markerfacecolor=viridis_colors[1], markersize=6,
           linestyle='None', label='Equally'),

    Line2D([0], [0], marker='o', color='black',
           markerfacecolor=viridis_colors[2], markersize=6,
           linestyle='None', label='Females Predominantly'),#

    Line2D([0], [0], marker='o', color='black',
           markerfacecolor=viridis_colors[3], markersize=6,
           linestyle='None', label='Females Exclusively'),
]

# Map 1: SCCS points (Ancestral)
world.plot(ax=axes[0], color="lightgray", edgecolor="black", linewidth=0.3)

sccs_gdf.plot(
    ax=axes[0],
    column="cook_num",
    cmap=cat_cmap,
    norm=cat_norm,
    markersize=25,
    edgecolor="black",
    linewidth=0.25
)

axes[0].set_title("Ancestral Cooking (Standard Cross-Cultural Sample)", fontsize=15)

axes[0].legend(
    handles=legend_elements[::-1],   # <--- reversed order
    loc="lower left",
    frameon=True,
    fontsize=10
)

# # Add colorbar
# sm = plt.cm.ScalarMappable(cmap=cat_cmap, norm=cat_norm)
# sm._A = []

# cbar = fig.colorbar(
#     sm,
#     ax=axes[0],
#     orientation="vertical",
#     fraction=0.025,
#     pad=0.02
# )

# # Put ticks in the middle of each category
# cbar.set_ticks([1, 2, 3, 4, 5])
# cbar.set_ticklabels(["1", "2", "3", "4", "5"])
# cbar.set_label("Ancestral Cooking Category")

# Map 2: Cookpad polygons (Contemporary)
world.plot(ax=axes[1], color="lightgray", edgecolor="black", linewidth=0.3)
world_cookpad.plot(
    ax=axes[1],
    column="female_share",
    cmap=cmap,
    norm=mcolors.Normalize(vmin=0.52, vmax=0.92),
    edgecolor="black",
    linewidth=0.3
)
axes[1].set_title("Contemporary Cooking (Cookpad)", fontsize=15)

# Add colorbar UNDER the bottom map
sm1 = plt.cm.ScalarMappable(cmap=cmap, norm=mcolors.Normalize(vmin=0.5, vmax=0.9))
sm1._A = []

# Create a dedicated axis *below* axes[1]
#cbar_ax = fig.add_axes([0.15, 0.05, 0.7, 0.02])  
# [left, bottom, width, height] in figure coordinates


from mpl_toolkits.axes_grid1 import make_axes_locatable

divider = make_axes_locatable(axes[1])
cax = divider.append_axes("bottom", size="5%", pad=0.2)

cbar1 = fig.colorbar(sm1, cax=cax, orientation="horizontal")

# cbar1 = fig.colorbar(
#     sm1,
#     cax=cbar_ax,
#     orientation="horizontal",
#     pad= 0.01
# )
cbar1.set_label("Female Cooking Share")

# Adjust horizontal space
fig.subplots_adjust(hspace=-0.5)

# Set xlimit and ylimit
axes[0].set_xlim(-180, 180)
axes[1].set_xlim(-180, 180)

axes[0].set_ylim(-60, 90)
axes[1].set_ylim(-60, 90)


axes[0].set_xticklabels([])
axes[0].set_yticklabels([])

axes[1].set_xticklabels([])
axes[1].set_yticklabels([])

axes[0].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
axes[1].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

plt.tight_layout()
plt.savefig(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\outputs\Figures\maps\ancestral_vs_cookpad.png",
    dpi=300, bbox_inches="tight")

# -------------------------------------------------------------------
# Contemporary (Cookpad) panel on its own -> map_cookpad.png
# -------------------------------------------------------------------

fig2, ax2 = plt.subplots(figsize=(10, 5.5), dpi=200)

world.plot(ax=ax2, color="lightgray", edgecolor="black", linewidth=0.3)
world_cookpad.plot(
    ax=ax2,
    column="female_share",
    cmap=cmap,
    norm=mcolors.Normalize(vmin=0.52, vmax=0.92),
    edgecolor="black",
    linewidth=0.3
)
ax2.set_title("Contemporary Cooking (Cookpad)", fontsize=15)

divider2 = make_axes_locatable(ax2)
cax2 = divider2.append_axes("bottom", size="5%", pad=0.2)
cbar2 = fig2.colorbar(sm1, cax=cax2, orientation="horizontal")
cbar2.set_label("Female Cooking Share")

ax2.set_xlim(-180, 180)
ax2.set_ylim(-60, 90)
ax2.set_xticklabels([])
ax2.set_yticklabels([])
ax2.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

fig2.tight_layout()
fig2.savefig(
    r"C:\Users\stevebc\Dropbox\food4thought\analysis23\outputs\Figures\maps\map_cookpad.png",
    dpi=200, bbox_inches="tight")

plt.show()
