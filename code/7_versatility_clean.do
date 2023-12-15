   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *      This dofile creates files to generate versatility variables 	  *
   *																	  *
   * - Inputs: "${versatility}/cuisine_ciat_suit.dta"	  	 			  *
   *           "${versatility}/median_suitability.dta"        			  *
   *		   "${versatility}/cuisine_suit.dta"			  			  *
   * - Output: "${versatility}/native/native_clean_`var'.dta"			  *
   *		   "${versatility}/imported/imported_`var'.dta"	  			  *
   *		   "${versatility}/common_flavor.dta"             			  *
   *		   "${versatility}/common_flavor_3ing.csv"		  			  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       
   ** Last date modified: Nov 28, 2023

****************************************
* Data cleaning for versatility data
****************************************

// Limit ingredients to only suitable ingredients: = 1 if >= p0/p10/p25/... of suitability for region that's native for the ingredient

* prep for native versatility **************************

 use  "${versatility}/cuisine_ciat_suit.dta", clear
 merge m:1 ingredient using "${versatility}/median_suitability.dta"
 tab _merge
 assert _merge == 3
 drop _merge
 
 gen p0 = 0
 foreach var of varlist p0 p10 p25 p50 p60 p70{
 	
	preserve
 	gen aboveCutoff = (suitability > `var') & (!missing(suitability))
	keep if aboveCutoff == 1
	
	** save to csv file
	outsheet using "${versatility}/native/native_`var'.csv", replace
	
	* Save native ingredients files based on cutoff
	keep adm0 country ingredient
	rename adm0 nativeadm0
	rename country nativecountry
	
	save "${versatility}/native/native_clean_`var'.dta", replace
	
	restore
 	
 }

* prep for imported versatility **************************

 use "${versatility}/cuisine_ciat_suit.dta", clear
 keep adm0 ingredient
 rename ingredient nativeIng
 duplicates drop
 tempfile native
 save `native', replace
 
 use  "${versatility}/cuisine_suit.dta", clear
 merge m:1 ingredient using "${versatility}/median_suitability.dta"
 tab _merge
 assert _merge == 3 | _merge == 1
 keep if _merge == 3
 drop _merge
 
 gen p0 = 0
 foreach var of varlist p0 p10 p25 p50 p60 p70{
 
 preserve
 gen aboveCutoff = (suitability > `var') & (!missing(suitability))
 joinby adm0 using `native'
 
 keep if aboveCutoff == 1
 gen ifNative = (nativeIng == ingredient)

 * Drop info for native ingredients and keep only data for the imported ones
 drop if ifNative == 1
 drop nativeIng

** save to csv file
 outsheet using "${versatility}/imported/imported_`var'.csv", replace
 save "${versatility}/imported/imported_`var'.dta", replace
 
 restore
 
 }
 
// Calculate the number of common flavors

* 2 ingredients as a group **************************

** import data
 use  "${versatility}/cuisine_ciat_suit.dta", clear
 keep ingredient
 duplicates drop
 sort ingredient
 
** generate every combination of ingredients(group of 2)
 gen ingredient2 = ingredient
 fillin ingredient ingredient2
 drop if ingredient == ingredient2
 drop _fillin
 
 gen common = .
 
 outsheet using "${versatility}/common_flavor.csv", replace
 
** calculate number of common flavor componds
cd "${versatility}"

python

import pandas as pd
import json

common = pd.read_csv("common_flavor.csv", sep="\t")
common.head()

def getjson(ingredient): return json.load(open("../../precoded/flavor_profile/CIAT/{}.json".format(ingredient)))
def getflavor(ingredient): return [i["common_name"] for i in getjson(ingredient)["molecules"]]
def calCommon(ingredient, ingredient2): return len(list(set(getflavor(ingredient)).intersection(getflavor(ingredient2))))

common["common"] = common.apply(lambda row: calCommon(row["ingredient"],row["ingredient2"]), axis=1)
common["common"].describe()

common.to_stata("common_flavor_clean.dta")

end

* 3 ingredients as a group **************************

** import data
 use  "${versatility}/cuisine_ciat_suit.dta", clear
 keep ingredient
 duplicates drop
 sort ingredient
 
** generate every combination of ingredients(group of 3)
 gen ingredient2 = ingredient
 gen ingredient3 = ingredient
 fillin ingredient ingredient2 ingredient3
 drop if _fillin == 0
 drop _fillin
 
 gen common = .
 
 outsheet using "${versatility}/common_flavor_3ing.csv", replace
 
** calculate number of common flavor componds
cd "${versatility}"

python

import pandas as pd
import json

common = pd.read_csv("common_flavor_3ing.csv", sep="\t")
common.head()

def getjson(ingredient): return json.load(open("../../precoded/flavor_profile/CIAT/{}.json".format(ingredient)))
def getflavor(ingredient): return [i["common_name"] for i in getjson(ingredient)["molecules"]]
def calCommon(ingredient, ingredient2, ingredient3): return len(list(set(getflavor(ingredient)).intersection(getflavor(ingredient2)).intersection(getflavor(ingredient3))))

common["common"] = common.apply(lambda row: calCommon(row["ingredient"],row["ingredient2"], row["ingredient3"]), axis=1)
common["common"].describe()

common.to_stata("common_flavor_3ing_clean.dta")

end
 