use "${recipes}/recipe_all_countries_web.dta", clear

foreach var of varlist _all {

    capture confirm string variable `var'

    if !_rc {

        replace `var' = subinstr(`var', ";", ",", .)
        replace `var' = subinstr(`var', char(10), " ", .)
        replace `var' = subinstr(`var', char(13), " ", .)
        replace `var' = subinstr(`var', char(9), " ", .)

        replace `var' = subinstr(`var', "–", "-", .)
        replace `var' = subinstr(`var', "—", "-", .)
        replace `var' = subinstr(`var', "Â", "", .)
        replace `var' = subinstr(`var', "â€™", "'", .)

    }
}

* Rename ingredient variable for clarity
rename coreingredient ingredients

* Export to CSV to process in Python
export delimited using "${recipes}/recipes_ing_countries.csv", replace 
/*
*--- Native ingredients database
use "${versatility}/native/native_clean_p50_m_c.dta", clear

rename nativeadm0 adm0

keep ingredient adm0

save "${versatility}/native/native_clean_p50_m_c_clean.dta", replace

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
import csv

#--------------------------------------------
# 3. Import datasets
#--------------------------------------------

# Load recipes dataset (exported from Stata)
df = pd.read_csv("${recipes}/recipes_ing_countries.csv")

# Load native ingredients dataset
df_native = pd.read_stata("${versatility}/native/native_clean_p50_m_c_clean.dta")

# Keep only necessary columns
df_native = df_native[["ingredient", "adm0"]]

#--------------------------------------------
# 4. Define cleaning function
#--------------------------------------------

def clean_ingredient(text):
    """
    Standardize ingredient text:
    - lowercase
    - remove irrelevant descriptors
    - remove special characters
    - normalize spaces
    """
    text = str(text).lower()
    
    remove_words = [
        "fresh", "dried", "ground", "chopped", "minced",
        "large", "small", "medium", "sized", "premium",
        "real", "extra", "virgin"
    ]
    
    for w in remove_words:
        text = re.sub(r"\b" + w + r"\b", "", text)
    
    text = re.sub(r"[^a-z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

#--------------------------------------------
# 5. Parse and clean recipe ingredients
#--------------------------------------------

def parse_list(x):
    """
    Convert string representation of list into actual Python list
    """
    try:
        return ast.literal_eval(x)
    except:
        return []

#--------------------------------------------
# 6. Create ingredient source with fallback
#--------------------------------------------

def safe_parse(x):
    try:
        val = ast.literal_eval(x)
        return val if isinstance(val, list) else []
    except:
        return []

# Parse ambas variables
df["ingredients_list_main"] = df["ingredients"].apply(safe_parse)
def extract_ingredient(x):
    try:
        val = ast.literal_eval(x)
        if isinstance(val, list):
            cleaned = []
            for item in val:
                if isinstance(item, list) and len(item) > 1:
                    cleaned.append(item[1])  # <-- SOLO ingrediente
                elif isinstance(item, str):
                    cleaned.append(item)
            return cleaned
        return []
    except:
        return []

df["ingredients_list_alt"] = df["listofingredients_eng"].apply(extract_ingredient)

# Usar main si sirve, si no usar alternativa
df["ingredients_list"] = df.apply(
    lambda row: row["ingredients_list_main"] 
    if len(row["ingredients_list_main"]) > 0 
    else row["ingredients_list_alt"],
    axis=1
)

df["ingredients_clean"] = df["ingredients_list"].apply(
    lambda lst: [clean_ingredient(i) for i in lst]
)

df_native["ingredient"] = (
    df_native["ingredient"]
    .astype(str)
    .str.lower()
    .str.replace("_", " ", regex=False)
)

df_native["ingredient"] = df_native["ingredient"].apply(clean_ingredient)

#--------------------------------------------
# 7. Create dictionary of native ingredients by country
#--------------------------------------------

native_dict = (
    df_native.groupby("adm0")["ingredient"]
    .apply(set)
    .to_dict()
)

#-------------------------------------------
# 8. Count + track matches
#--------------------------------------------

def match_native(row):
    """
    For each recipe:
    - count native ingredients
    - store which ingredients matched
    - store which native ingredient they matched to
    """
    natives = native_dict.get(row["adm0"], set())
    
    count = 0
    matched_ings = []
    matched_native = []
    
    for ing in row["ingredients_clean"]:
        words = ing.split()
        
        for n in natives:
            if n == ing or n in words:
                count += 1
                matched_ings.append(ing)
                matched_native.append(n)
                break   # avoid multiple matches per ingredient
    
    return pd.Series([count, matched_ings, matched_native])

# Apply function
df[["n_native", "native_ingredients_list", "matched_native_ingredient"]] = df.apply(match_native, axis=1)

#--------------------------------------------
# 9. Convert lists to strings for CSV export
#--------------------------------------------

df["native_ingredients_list"] = df["native_ingredients_list"].apply(lambda x: ", ".join(x))
df["matched_native_ingredient"] = df["matched_native_ingredient"].apply(lambda x: ", ".join(x))

#--------------------------------------------
# 10. Save output
#--------------------------------------------

df.to_csv(
    "${recipes}/recipes_out.csv",
    index=False,
    sep=";",
    encoding="utf-8",
    quoting=csv.QUOTE_ALL
)

end


*--- Import database to check 
import delimited  "${recipes}/recipes_out.csv",  delimiter(";") clear

br if n_native != 0
gsort matched_native_ingredient

split matched_native_ingredient, parse(",") gen(item)

foreach v of varlist item* {
    replace `v' = trim(`v')
}

unab items: item*

local n : word count `items'

forvalues i = 1/`n' {
    local vi : word `i' of `items'
    
    forvalues j = `=`i'+1'/`n' {
        local vj : word `j' of `items'
        
        replace `vj' = "" if `vj' == `vi'
    }
}

egen cleaned = concat(item*), punct(", ")

replace cleaned = subinstr(cleaned, ", , , , , , , , , , ,", "", .)
replace cleaned = subinstr(cleaned, ", , , , , , , , , ,", "", .)
replace cleaned = subinstr(cleaned, ", , , , , , , , ,", "", .)
replace cleaned = subinstr(cleaned, ", , , , , , , ,", "", .)
replace cleaned = subinstr(cleaned, ", , , , , , ,", "", .)
replace cleaned = subinstr(cleaned, ", , , , , ,", "", .)
replace cleaned = subinstr(cleaned, ", , , , ,", "", .)
replace cleaned = subinstr(cleaned, ", , , ,", "", .)
replace cleaned = subinstr(cleaned, ", , ,", "", .)
replace cleaned = subinstr(cleaned, ", ,", ",", .)

gen temp = subinstr(cleaned, ", ", ",", .)
gen n_ingredients = 1 + length(temp) - length(subinstr(temp, ",", "", .))
replace n_ingredients = 0 if temp == ""

drop temp item*

rename ingredients coreingredient

gen prop_native = n_ingredients/numberofingredients
gen prop_percent = prop_native*100

save "${recipes}/recipes_native.dta", replace 

cd "$tables"
asdoc tabstat prop_percent, by(country) stat(count mean sd min p50 max) ///
dec(1) save(desc_native_recipes.doc) replace

preserve

collapse prop_percent, by(country adm0)
tempfile  native
save `native'

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

merge 1:1 adm0 using `native', nogen 

drop if missing(_ID)

grmap prop_percent, clnumber(9)  clmethod(custom) ///
title("Average of the proportion of native ingredients in each recipe") ///
clbreaks(0 1 2 4 6 8 10 12 14 16) ndfcolor(gs14)
	
	graph export "$figures/native_heat_map.pdf", replace

*duplicates drop

