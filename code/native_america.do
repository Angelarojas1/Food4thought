/*
code: native_america.do
created by: AR, 20260506

Description:
This code identifies the number of ingredients that are from America and the ones
that are not. For this we use the database that has native ingredients by country
and the recipes database.

*/

*--- Native ingredients database
use "${versatility}/native/native_clean_p50_m_c.dta", clear

tab continent

*--- Dummy for Ingredients from America
gen native_america = inlist(continent, "Central America", "North America", "South America")

gen native_not_america = inlist(continent, "Africa", "Asia", "Europe", "Oceania")

rename nativeadm0 adm0

collapse native_*, by(ingredient)

br if !inlist(native_america,0,1) | !inlist(native_not_america,0,1)

replace native_america = 1 if native_america > 0.5
replace native_america = 0 if native_america < 0.5
replace native_not_america = 1 if native_not_america > 0.5
replace native_not_america = 0 if native_not_america < 0.5

replace native_america = 1 if ingredient == "avocado"
replace native_not_america = 0 if ingredient == "avocado"
replace native_america = 1 if ingredient == "beans"
replace native_not_america = 0 if ingredient == "beans"
replace native_america = 1 if ingredient == "blueberry"
replace native_not_america = 0 if ingredient == "blueberry"
replace native_america = 1 if ingredient == "breadfruit"
replace native_not_america = 0 if ingredient == "breadfruit"
replace native_america = 1 if ingredient == "groundnut"
replace native_not_america = 0 if ingredient == "groundnut"
replace native_america = 0 if ingredient == "hogplum"
replace native_not_america = 1 if ingredient == "hogplum"
replace native_america = 0 if ingredient == "malabar_spinach"
replace native_not_america = 1 if ingredient == "malabar_spinach"
replace native_america = 0 if ingredient == "oil_palm"
replace native_not_america = 1 if ingredient == "oil_palm"
replace native_america = 0 if ingredient == "peach"
replace native_not_america = 1 if ingredient == "peach"
replace native_america = 1 if ingredient == "potato"
replace native_not_america = 0 if ingredient == "potato"
replace native_america = 1 if ingredient == "tomato"
replace native_not_america = 0 if ingredient == "tomato"

save "${versatility}/native/native_america.dta", replace

*--------------------------------------------------*
* 1. Check Python integration
*--------------------------------------------------*
python query

*--------------------------------------------------*
* 2. Run Python
*--------------------------------------------------*
python:

import pandas as pd
import ast
import re
from collections import Counter

#--------------------------------------------
# 3. Import datasets
#--------------------------------------------

# Load recipes dataset (exported from Stata)
df = pd.read_csv("${recipes}/recipes_ing_countries.csv")

# Load native ingredients dataset
df_native = pd.read_stata("${versatility}/native/native_america.dta")

df_native = df_native[["ingredient", "native_america", "native_not_america"]]

#--------------------------------------------
# 2. Cleaning function 
#--------------------------------------------

def clean_ingredient(text):
    text = str(text).lower()
  
    remove_patterns = [
        r"\b\d+\b",
        r"\b(a|an)\b",
        r"\b(of)\b",
        r"\b(bit|bag|bowl|bouquet|block|piece|slice)\b",
        r"\b(cup|cups|tbsp|tablespoon|tsp|teaspoon)\b",
        r"\b(kg|g|mg|ml|l|oz|lb)\b"
    ]
    
    for pattern in remove_patterns:
        text = re.sub(pattern, "", text)

    # Remove cooking descriptors
    remove_words = [
        "fresh", "dried", "ground", "chopped",
        "minced", "large", "small", "medium",
        "sized", "extra", "virgin", "premium",
        "fine", "coarsely", "favorite",
        "organic", "optional",

        # Additional harmonization words
        "paste", "sauce", "juice", "powder",
        "milk", "oil", "seed", "seeds",
        "leaf", "leaves", "extract"
    ]
    
    for w in remove_words:
        text = re.sub(r"\b" + re.escape(w) + r"\b", "", text)

    # Remove isolated letters
    text = re.sub(r"\b[a-z]\b", "", text)

    # Keep only letters/spaces
    text = re.sub(r"[^a-z\s]", "", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Better singularization
    if text.endswith("es") and len(text) > 4:
        text = text[:-2]

    elif text.endswith("s") and len(text) > 3:
        text = text[:-1]

    return text.strip()

#--------------------------------------------
# 3. CLEAN NATIVE INGREDIENTS
#--------------------------------------------

df_native["ingredient"] = (
    df_native["ingredient"]
    .astype(str)
    .apply(clean_ingredient)
)

# Drop duplicates after cleaning
df_native = df_native.drop_duplicates(subset=["ingredient"])

#--------------------------------------------
# 4. PARSE INGREDIENT LISTS
#--------------------------------------------

def safe_parse(x):

    try:
        val = ast.literal_eval(x)

        if isinstance(val, list):
            return val

        return []

    except:
        return []

def extract_ingredient(x):

    try:
        val = ast.literal_eval(x)

        if isinstance(val, list):

            out = []

            for item in val:

                if isinstance(item, list) and len(item) > 1:
                    out.append(item[1])

                elif isinstance(item, str):
                    out.append(item)

            return out

        return []

    except:
        return []

# Main ingredients column
df["ingredients_list_main"] = (
    df["ingredients"]
    .apply(safe_parse)
)

# Alternative ingredients column
df["ingredients_list_alt"] = (
    df["listofingredients_eng"]
    .apply(extract_ingredient)
)

# Use main if available, otherwise alternative
df["ingredients_list"] = df.apply(
    lambda row:
        row["ingredients_list_main"]
        if len(row["ingredients_list_main"]) > 0
        else row["ingredients_list_alt"],
    axis=1
)

#--------------------------------------------
# 5. CLEAN RECIPE INGREDIENTS
#--------------------------------------------

df["ingredients_clean"] = df["ingredients_list"].apply(
    lambda lst: [
        clean_ingredient(i)
        for i in lst
        if clean_ingredient(i) != ""
    ]
)

#--------------------------------------------
# 6. CREATE LOOKUP SETS
#--------------------------------------------

america_set = set(
    df_native.loc[
        df_native["native_america"] == 1,
        "ingredient"
    ]
)

non_america_set = set(
    df_native.loc[
        df_native["native_not_america"] == 1,
        "ingredient"
    ]
)

# Sort by length so longer matches are prioritized
america_list = sorted(
    list(america_set),
    key=len,
    reverse=True
)

non_america_list = sorted(
    list(non_america_set),
    key=len,
    reverse=True
)

#--------------------------------------------
# 7. FLEXIBLE MATCH FUNCTION
#--------------------------------------------

def flexible_match(ingredient, lookup_list):

    """
    Returns best partial match.

    Example:
        tomato paste -> tomato
        coconut milk -> coconut
    """

    ingredient = " " + ingredient + " "

    for item in lookup_list:

        item_clean = " " + item + " "

        # Exact word match
        if item_clean in ingredient:
            return item

        # Partial substring match
        if item in ingredient:
            return item

    return None

#--------------------------------------------
# 8. MATCHING FUNCTION
#--------------------------------------------

def match_origin(row):

    american = []
    non_american = []

    for ing in row["ingredients_clean"]:

        match_a = flexible_match(ing, america_list)
        match_na = flexible_match(ing, non_america_list)

        # Only American
        if match_a and not match_na:
            american.append(match_a)

        # Only non-American
        elif match_na and not match_a:
            non_american.append(match_na)

        # If both match, ignore ambiguity
        elif match_a and match_na:
            pass

    return pd.Series({
        "n_american": len(set(american)),
        "n_non_american": len(set(non_american))
    })

# Apply matching
df[[
    "n_american",
    "n_non_american"
]] = df.apply(match_origin, axis=1)


#--------------------------------------------
# 9. MATCH RATE
#--------------------------------------------

total = sum(
    len(lst)
    for lst in df["ingredients_clean"]
)

matched = (
    df["n_american"].sum()
    + df["n_non_american"].sum()
)

print("Total ingredients:", total)
print("Matched ingredients:", matched)
print("Match rate:", matched / total)

#--------------------------------------------
# 10. SAVE FINAL OUTPUT
#--------------------------------------------

df.to_csv("${recipes}/recipes_america.csv", index=False, sep=";")

end


*--- Import database to check 
import delimited  "${recipes}/recipes_america.csv", delimiter(";") clear

drop numberofingredients
egen numberofingredients = rowtotal(n_american n_non_american)

gen prop_native_american = n_american/numberofingredients
gen prop_native_non_american = n_non_american/numberofingredients

gen perc_native_american = prop_native_american*100
gen perc_native_non_american = prop_native_non_american*100

save "${recipes}/recipes_native_american.dta", replace 

preserve

drop if n_american == 0 & n_non_american == 0
collapse perc_native_american* perc_native_non_american*, by(country adm0)
tempfile  native_america
save `native_america'

restore

grmap, activate
cd "$rawdata/world_admin_shp"

*--- Import shapefile to Stata
	spshape2dta ne_10m_admin_0_countries_lakes, replace saving(countries)

	use "$rawdata/world_admin_shp/countries.dta", replace
	
	*- Organize variable for merging
	tab ADMIN if ISO_A3 == "-99"
	
	replace ISO_A3 = "XKX" if ADMIN == "Kosovo"
	replace ISO_A3 = "FRA" if ADMIN == "France"
	replace ISO_A3 = "NOR" if ADMIN == "Norway"
	
	drop if ISO_A3 == "-99"
	rename ISO_A3 adm0
	
	keep adm0 _ID _CX _CY

merge 1:1 adm0 using `native_america', nogen 

drop if missing(_ID)

* Steve: we can decide on the clbreaks later, but this looked pretty decent, since it seems capped below 50: clbreaks(0 10 20 30 40 50 )
* old clbreaks: clbreaks(0 10 20 30 40 50 60 70)
grmap perc_native_american using "$rawdata/world_admin_shp/countries_shp_noATA.dta", ///
id(_ID) clnumber(7)  clmethod(custom) ///
title("Average of the proportion of American ingredients in each recipe") ///
clbreaks(0 15 20 25 35 ) ndfcolor(gs14) ndsize(vvvthin) ///
line(data("$rawdata/world_admin_shp/countries_shp_noATA.dta") size(vvvthin) color(gs0)) ///
osize(0.05) ocolor(gs0)
	
	graph export "$figures/american_heat_map.pdf", replace
	
* Steve: very little variation between 50 and 70 so I tried: clbreaks(50 70 80 90 100)
* old clbreaks: clbreaks(30 40 60 70 80 90 100)
grmap perc_native_non_american using "$rawdata/world_admin_shp/countries_shp_noATA.dta", ///
id(_ID) clnumber(6)  clmethod(custom) ///
title("Average of the proportion of non american ingredients in each recipe") ///
clbreaks(50 70 80 90 100) ndfcolor(gs14) ndsize(vvvthin) ///
line(data("$rawdata/world_admin_shp/countries_shp_noATA.dta") size(vvvthin) color(gs0)) ///
osize(0.05) ocolor(gs10)
	
	graph export "$figures/non_american_heat_map.pdf", replace

/*
	
use "$rawdata/world_admin_shp/countries.dta", clear
list _ID ISO_A3 if ISO_A3 == "ATA"

use "$rawdata/world_admin_shp/countries_shp.dta", clear
drop if _ID == 176
save "$rawdata/world_admin_shp/countries_shp_noATA.dta", replace