   * ******************************************************************** *
   *                                                                      *
   *        Cuisine Complexity and Female Labor Force Participation	      *
   *        This dofile create suitability data for all ingredients 	  *
   *																	  *
   * - Inputs: "${precodedata}/suitability/staple_suitability.dta"		  *
   *           "${precodedata}/suitability/spices_suitability.dta"        *
   *		   "${precodedata}/suitability/spices_suitability_10nov23.dta"*
   *		   "${precodedata}/suitability/crop_suitability.dta"		  *
   *           "${versatility}/cuisine_ciat.dta"         	 			  *
   * - Output: "${versatility}/cuisine_ciat_suit.dta"     	 			  *
   *		   "${versatility}/median_suitability.dta"		 			  *
   *		   "${versatility}/cuisine_suit.dta"		     			  *
   * ******************************************************************** *

   ** IDS VAR:          adm0        // Uniquely identifies countries 
   ** NOTES:
   ** WRITTEN BY:       Xinyu Ren
   ** EDITTED BY:       Angela Rojas
   ** Last date modified: Dec 29, 2023

****************************************
* Data cleaning for suitability data
****************************************

***** Create suitability data for all ingredients  *****

** import staple suitability data
use "${precodedata}/suitability/staple_suitability.dta", clear
rename admin0_name country
keep adm0 country ingredient suitability

cap noisily assert !missing(adm0)
list adm0 country ingredient suitability if missing(adm0)
assert country == "Rest of World" if missing(adm0)

tempfile staple
save `staple', replace

** import spices suitability data
use "${precodedata}/suitability/spices_suitability.dta", clear
isid adm0
merge 1:1 adm0 using "${precodedata}/suitability/spices_suitability_10nov23.dta"
tab _merge
assert inlist(_merge, 2, 3)
drop _merge
isid adm0
reshape long ap_, i(adm0) j(ingredient, string)
rename ap_ suitability

assert !missing(adm0)

tempfile spices
save `spices', replace

* import crop suitability data
use "${precodedata}/suitability/crop_suitability.dta", clear
reshape long ap_, i(adm0) j(ingredient, string)
rename ap_ suitability

assert !missing(adm0)

* append all suitability data
append using `staple'
append using `spices'
replace ingredient = strlower(ingredient)

tab ingredient

** correct names for ingredients
 replace ingredient = "anise" if ingredient == "anise_seed"
 replace ingredient = "cabbages" if ingredient == "cabbage"
 replace ingredient = "carrots" if ingredient == "carrot"
 replace ingredient = "chickpeas" if ingredient == "chickpea"
 replace ingredient = "chillies&peppers" if ingredient == "chillies_peppers"
 replace ingredient = "cocoa beans" if ingredient == "cocoa"
 replace ingredient = "cottonseed oil" if ingredient == "cotton"
 replace ingredient = "cowpeas" if ingredient == "cowpea"
 replace ingredient = "faba beans" if ingredient == "faba_beans"
 replace ingredient = "lentils" if ingredient == "lentiles"
 replace ingredient = "macadamia nut" if ingredient == "macadamia_nut"
 replace ingredient = "mustard seed" if ingredient == "mustard_seed"
 replace ingredient = "peppermint" if ingredient == "mint" // 62 more observations merge after adding this. We added this because peppermint doesn't exist in suitability data, but it does in recipe database (AR: Dec 20,2023).
 replace ingredient = "nutmeg and mace" if ingredient == "nutmeg_mace"
 replace ingredient = "oats" if ingredient == "oat"
 replace ingredient = "palm oil" if ingredient == "oil palm"
 replace ingredient = "olives" if ingredient == "olive"
 replace ingredient = "onions" if ingredient == "onion"
 replace ingredient = "pigeonpeas" if ingredient == "pigeonpea"
 replace ingredient = "rape&mustard seed" if ingredient == "rape_mustard_seed"
 replace ingredient = "seasame" if ingredient == "sesame"
 replace ingredient = "sugar beet" if ingredient == "sugarbeet"
 replace ingredient = "sweet potatoes" if ingredient == "sweet potato"
 replace ingredient = "tomatoes" if ingredient == "tomato"
 replace ingredient = "yams" if ingredient == "yam"
 replace ingredient = "beans" if ingredient == "phaseolus bean"
 replace ingredient = "peas" if ingredient == "dry pea"
 replace ingredient = "rice" if ingredient == "dryland rice"
 replace ingredient = "millets" if ingredient == "foxtail millet"
 replace ingredient = "millets" if ingredient == "pearl millet"
 replace ingredient = "potatoes" if ingredient == "white potato"

 * Join repeated information
 bysort adm0 ingredient (suitability): keep if _n == 1
 keep adm0 country ingredient suitability
 isid adm0 ingredient, missok

 * Fill country information
 bys adm0 (country ingredient): replace country = country[_N]
 cap noisily assert !missing(country)
 tab adm0 if missing(country)

 tempfile suit
 save `suit', replace
 
 preserve
 keep if country == "Rest of World"
 isid ingredient
 rename suitability suitability_rest
 tempfile rest
 save `rest', replace
 restore
 
 * Merge with cuisine database 
 merge 1:1 adm0 ingredient using "${versatility}/cuisine_ciat.dta"
 assert inlist(_merge, 1, 2, 3)
 drop if _merge == 1
 rename _merge _merge1
 
 ** if missing suitability, use the suitability from the rest of the world
 merge m:1 ingredient using `rest'
 assert inlist(_merge, 1, 2, 3)
 drop if _merge == 2 
 tab _merge1 _merge
 assert !missing(suitability_rest) if _merge1 == 2 & _merge == 3
 assert missing(suitability_rest) if _merge1 == 2 & _merge == 1 //For these ing we definetly don't have information
 replace suitability = suitability_rest if _merge1 == 2 & _merge == 3 
 drop _merge1 _merge suitability_rest
 
 sort adm0 ingredient
 isid adm0 ingredient
 
 cap noisily assert !missing(country)
 bys adm0 (country ingredient): replace country = country[_N]
 replace country = "Tuvalu" if adm0 == "TUV"
 assert !missing(country)
 
 unique adm0
 assert `r(sum)' == 136
 
 ** drop ingredients that we don't have suitability data at all
 gen flag = 0
 bys ingredient(suitability adm0): replace flag = 1 if suitability[1] == suitability[_N] & suitability[1] == .
 assert missing(suitability) if flag == 1
 tab ingredient if flag == 1 //identify ingredients without suitability information
 drop if flag == 1
 drop flag
 
 sort adm0 ingredient
 
 unique adm0
 assert `r(sum)' == 136 // we have 136 countries with suitability information
 
 save "${versatility}/cuisine_ciat_suit.dta", replace

*** Find median of suitability for native ingredients  ***
 collapse (p10) p10 = suitability (p25) p25 = suitability (p33) p33 = suitability (median) p50 = suitability (p60) p60 = suitability (p66) p66 = suitability (p70) p70 = suitability, by(ingredient)
 isid ingredient // there's information for 64 ingredients
 save "${versatility}/median_suitability.dta", replace
  
  
  **NO ENTIENDO ESTA PARTE PARA QUÉ ES
*** limit to suitability data of all ingredients that are from CIAT map  ***
 use "${versatility}/cuisine_ciat.dta", clear

 * Keep country names information
 preserve
 keep adm0 country
 duplicates drop 
 isid adm0
 tempfile adm0
 save `adm0', replace
 restore
 
 * Keep only ingredients in recipe data
 preserve
 keep ingredient
 duplicates drop
 isid ingredient
 tempfile ing
 save `ing', replace
 restore
 
 use `rest', clear
 merge 1:1 ingredient using `ing'
 keep if _merge == 3 // 34 ingredients
 drop _merge
 rename suitability_rest suitability
 tempfile rest_suit
 save `rest_suit', replace
 
 use `suit', clear
 merge m:1 adm0 using `adm0'
 assert inlist(_merge, 1, 2, 3)
 drop if _merge == 1
 rename _merge _merge1
 
 merge m:1 ingredient using `ing'
 assert inlist(_merge, 1, 2, 3)
 drop if _merge1 == 3 & _merge == 1
 list if _merge == 2
 drop if _merge == 2
 tab adm0 if _merge1 == 2 & _merge == 1
 assert inlist(adm0, "ABW", "MDV", "MLT", "SGP", "XXK") if _merge1 == 2 & _merge == 1
 tab country if _merge1 == 2 & _merge == 1
 assert inlist(country, "Aruba", "Maldives", "Malta", "Singapore", "Kosovo") if _merge1 == 2 & _merge == 1
 drop if _merge1 == 2 & _merge == 1
 assert _merge1 == 3 & _merge == 3
 drop _merge1 _merge

 append using `rest_suit'
 replace country = "Aruba" if missing(adm0)
 replace adm0 = "ABW" if missing(adm0)
 
  append using `rest_suit'
 replace country = "Kosovo" if missing(adm0)
 replace adm0 = "XXK" if missing(adm0)
 
 append using `rest_suit'
 replace country = "Maldives" if missing(adm0)
 replace adm0 = "MDV" if missing(adm0)
 
 append using `rest_suit'
 replace country = "Malta" if missing(adm0)
 replace adm0 = "MLT" if missing(adm0)
 
 append using `rest_suit'
 replace country = "Singapore" if missing(adm0)
 replace adm0 = "SGP" if missing(adm0)
 
 sort adm0 ingredient
 isid adm0 ingredient
 
 save "${versatility}/cuisine_suit.dta", replace

 notes
 
 