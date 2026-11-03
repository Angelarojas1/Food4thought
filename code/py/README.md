# Python code

Scripts are grouped by stage of the pipeline. Nothing has been moved here yet; this table is the
*proposed* destination of each script from `food4thought/analysis23/code/py`.

| Folder | Purpose | Proposed scripts |
|--------|---------|------------------|
| `1_classify_ingredients/` | Clean scraped ingredient strings and map them to categories / canonical ingredients (partly via ChatGPT) | `stata_recipes_to_ingredients`, `clean_ingredients`, `clean_ingredients_manual`, `create_ingredient_prompts` (+ `prompts/`), `concatenate_chatgpt_ingredients`, `merge_map_ingredients` |
| `2_build_country_data/` | Merge cleaned ingredients back to recipes; country-level shares, clusters, ingredient pairs | `merge_countries_maps_v2`, `pair_ingredients` (v2), `pair_ingredients_all_recipes` |
| `3_validate_geography/` | Validate recipes against geographic data (bounty of the sea, coastal access, grassland / livestock, crop suitability) | `validate_recipes_geovariables`, `validate_recipes_suitability` |
| `4_validate_ethnographic/` | Validate recipes against the Ethnographic Atlas (Giuliano-Nunn) and cultural data | `validate_recipes_atlas_coefplot_focused_standalone` (self-contained; replaces the old per-pair scatters `scatter_v41_vs_dairy.png`, `scatter_v3_vs_fish_seafood.png`), `pca_culture_correlations` |
| `5_exploratory/` | Cuisine diversity vs. ethnic / linguistic diversity and migration, IV maps, spice hypotheses | `recipe_ethnic_diversity_ar`, `plot_IV_maps`, `spice_use_causes` |
| `_archive/` | Superseded versions, kept out of the replication run | `clean_ingredients` (if replaced), `merge_countries_maps` (v1), `pair_ingredients` (v1), `recipe_ethnic_diversity` (non-`_ar`), `validate_recipes_atlas`, `_targeted`, `_staples`, `_coefplot`, `_coefplot_controls`, `_coefplot_focused` (all superseded by the standalone coefplot script) |

Raw recipe scraping lives in `precode/`, not here.
