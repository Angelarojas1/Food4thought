# 1_classify_ingredients

Turns the ~248k unique raw ingredient strings scraped from the recipes into cleaned ingredient names, and
matches each to a broad **category** (e.g. `spice`, `dairy`) and a **canonical ingredient** (e.g. `cinnamon`,
`milk`). The result feeds `../2_build_country_data/`.

Two steps in this pipeline are manual or LLM-based and cannot be re-run identically. Their outputs are
provided as fixed inputs (see "Frozen inputs" below), so replicators can start from them.

## Pipeline

| # | Script | What it does |
|---|--------|--------------|
| 01 | `01_stata_recipes_to_ingredients.py` | Reads `recipe_all_countries_web.dta` and writes `unique_raw_ingredients.csv` (the raw ingredient strings). |
| 02 | `02_clean_ingredients.py` | Strips digits and whitespace and writes `unigram_frequencies.csv`, a ranked list of single words. |
| – | *manual step* | Unigrams that are not ingredient words (units, cooking verbs, stopwords such as "of", "cup", "chopped") were flagged `0` in `unigram_frequencies_manual_flags_UPDATED.csv`. |
| 03 | `03_clean_ingredients_manual.py` | Drops every unigram flagged `0` and writes `unique_clean_manual.csv` (~70k potential ingredient names). |
| 04 | `04_create_ingredient_prompts.py` | Writes batches of 100 ingredient names as `prompt_batch_###.txt`. The canonical category-ingredient list (267 pairs) is embedded in the script and matches `ingredient_list_full.csv`. |
| – | *LLM step* | Each prompt was pasted into ChatGPT, which returned a CSV (`ingredient, category, canonical_ingredient`) per batch, saved in `ChatGPT_output/ingredient_batch100/`. Ingredients not in the list are classified as `unspecified`. Non-English names are mapped to the English ingredient. |
| 05 | `05_concatenate_chatgpt_ingredients.py` | Combines the batch CSVs into `ingredient_all.csv`. |
| → | `../2_build_country_data/01_merge_countries_maps_v2.py` | Joins `ingredient_all.csv` back to the recipes and builds country-level shares and clusters. |

## Frozen inputs

| File | Produced by | Why it is provided |
|------|-------------|--------------------|
| `unigram_frequencies_manual_flags_UPDATED.csv` | manual review of the ranked unigram list | Human judgment. The flags were made on an earlier version of the unigram list, so counts in a re-generated `unigram_frequencies.csv` differ slightly. Use the provided file for step 03. |
| `ChatGPT_output/ingredient_batch100/*.csv` and `ingredient_all.csv` | ChatGPT run on the step-04 prompts | LLM output is not deterministic, so a re-run will not give identical matches. |

To reproduce the paper, start from these files: run 01 and 03, skip 02, 04 and the LLM step, run 05 (or use
`ingredient_all.csv` directly), then continue with `2_build_country_data`. Steps 02 and 04 are included to document how
the manual and LLM inputs were created.

## Why a predefined list

The LLM matches to a fixed list of canonical ingredients and categories to reduce variation and hallucination across
prompts. The plant ingredients on the list come from external suitability datasets, which allows suitability to be
linked to recipes directly. Animal products are added as categories (dairy, meat, etc.) with canonical ingredients such as
milk, beef and pork. Ingredients not on the list are `unspecified` and can be re-submitted to the LLM later without
redoing the full matching.

## LLM run details

- Model and version: _to fill in_
- Date: _to fill in_ (May 2026)
- Interface: ChatGPT web interface, 100 ingredients per prompt
- Spot-check of matches: _to fill in (share of randomly selected non-`unspecified` matches that were correct)_
