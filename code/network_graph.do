/* ------------------------------------------------------------------------
        Cuisine Complexity and Female Labor Force Participation	    

Authors: Girija Borker, Margarita Gafaro, Steve Beggreen

Created on: February 23, 2026
Created by: Angela Rojas

Last modified: 

Description:
This code creates a network graph for spices
------------------------------------------------------------------------ */

use "$versatility/native_versatility_m_c.dta", clear

ren (ingredient1 ingredient) (ingredient ingredient2)

merge m:1 ingredient ingredient2 using "${versatility}/common_flavor_clean_m_c.dta"
keep if _merge == 3
keep if only_native == 1 & spice == 1

keep ingredient ingredient2 common
duplicates drop

export delimited using "${versatility}/ingredient_network.csv", replace

python:

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np 

# -------------------------------------------------
# 1. Import data
# -------------------------------------------------

df = pd.read_csv("${versatility}/ingredient_network.csv")

# Filter values
df = df[df["common"] >= 90]

# -------------------------------------------------
# 2. Create network
# -------------------------------------------------

G = nx.from_pandas_edgelist(df,
                            source="ingredient",
                            target="ingredient2",
                            edge_attr="common")

# -------------------------------------------------
# 3. PREVALENCE 
# -------------------------------------------------

strength = dict(G.degree())
vals = np.array(list(strength.values()))

vals_log = np.log(vals)

node_sizes = 300 + 6000 * (vals_log - vals_log.min()) / (vals_log.max() - vals_log.min())

# -------------------------------------------------
# 4. Colors 
# -------------------------------------------------

spices = set(df["ingredient"])

node_colors = ["#B22222" if n in spices else "#228B22" for n in G.nodes()]

# -------------------------------------------------
# 5. Edges thickness
# -------------------------------------------------

commons = np.array([G[u][v]["common"] for u, v in G.edges()])
commons_log = np.log(commons)

weights = 0.5 + 4 * (commons_log - commons_log.min()) / (commons_log.max() - commons_log.min())

# -------------------------------------------------
# 6. Layout
# -------------------------------------------------

pos = nx.spring_layout(G,
                       k=1.5,
                       iterations=50,
                       seed=123)

# -------------------------------------------------
# 7. Graph
# -------------------------------------------------

plt.figure(figsize=(18,14))

nx.draw_networkx_edges(G, pos,
                       width=weights,
                       alpha=0.12)

nx.draw_networkx_nodes(G, pos,
                       node_size=node_sizes,
                       node_color=node_colors)

nx.draw_networkx_labels(G, pos,
                        labels={n:n for n in G.nodes()},
                        font_size=7)

plt.axis("off")
plt.tight_layout()
plt.show()

end
