   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *              This dofile creates common flavor files 	        	  *
   *																	  *
   * - Inputs: "${versatility}/cuisine_ciat_suit.dta"	  	 			  *
   *		   "${precodedata}/flavor_profile/CIAT/{}.json"
   * - Output: "${versatility}/common_flavor.dta"             			  *
   *		   "${versatility}/common_flavor_3ing.csv"		  			  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       
   ** Last date modified: Nov 28, 2023

*********************************************************************************
* Calculate the number of common flavors between ingredients in Milla data + CIAT
*********************************************************************************

**** Between 2 ingredients as a group ****

** import data
 use  "${versatility}/Milla_CIAT_ing_origin.dta", clear
 keep ingredient
 duplicates drop
 sort ingredient
 
** generate every combination of ingredients(group of 2)
 gen ingredient2 = ingredient
 fillin ingredient ingredient2
 drop if ingredient == ingredient2
 drop _fillin
 
 gen common = .
 
 outsheet using "${versatility}/common_flavor_m_c.csv", replace
 
** calculate number of common flavor componds
cd "${versatility}"

python

import pandas as pd
import json
import os

common = pd.read_csv("common_flavor_m_c.csv", sep="\t")

# List ingredients for which we have compounds data
def has_json(ingredient):
    return os.path.exists(f"../../precoded/flavor_profile/flavor_cleaned/{ingredient}.json")

valid_ingredients = {ing for ing in common["ingredient"].unique() if has_json(ing)}

# Filter dataset to keep ingredients with compounds info
common = common[common["ingredient"].isin(valid_ingredients) & 
                common["ingredient2"].isin(valid_ingredients)].copy()

def getjson(ingredient):
    with open(f"../../precoded/flavor_profile/flavor_cleaned/{ingredient}.json", "r") as f:
        return json.load(f)

def getflavor(ingredient):
    return [i["common_name"] for i in getjson(ingredient).get("molecules", [])]

def calCommon(ingredient, ingredient2):
    return len(set(getflavor(ingredient)).intersection(getflavor(ingredient2)))

# Get common compounds
common["common"] = common.apply(lambda row: calCommon(row["ingredient"], row["ingredient2"]), axis=1)

print(common["common"].describe())
common.to_stata("common_flavor_clean_m_c.dta", write_index=False)

end