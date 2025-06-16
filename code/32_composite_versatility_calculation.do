* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: June 16, 2025 						   	   *
*				New Versatility Calculation
* **************************************************************************** *
	
	

	clear all
	set more off
	global run = 1

	* ***************************************************** *
	
	** Root folder globals 

	if "`c(username)'" == "stell" {
	global projectfolder "C:/Users/stell/Dropbox/food4thought/analysis23"
	global github "C:\Users\stell\Dropbox\food4thought\analysis23"
	}
	
	if "`c(username)'" == "wb641362" { // Varun
	global projectfolder "C:\Users\wb641362\Dropbox\food4thought\analysis23"
	global github "C:\Users\wb641362\OneDrive - WBG\Documents\GitHub\Food4thought"
	}
	
	if "c(username)" == "mgafargo" { // Margarita
	global projectfolder "C:\Users\mgafargo\Dropbox\food4thought"
	}

	** Project folder globals
	global files "$projectfolder\data\coded"
	
	* Dofile sub-folder globals
	global code					"$github/code"
	
	* Python codes folder
	global precode				"$github/precode" 
	global recipe_code          "$precode/recipes"	
	
	* Dataset sub-folder globals
	global precodedata			"$projectfolder/data/precoded"
	global rawdata				"$projectfolder/data/raw"
	global codedata				"$projectfolder/data/coded"
	
	global recipes              "$codedata/recipes"
	global flfp             	"$codedata/FLFP"
	global versatility          "$codedata/iv_versatility"
	global cookpad              "$codedata/cookpad"
	global fao_suit             "$codedata/FAO_suitability"

	
	* Output sub-folder globals
	global outputs				"$files/Outputs"
	global tables				"$projectfolder\outputs\Tables"
	
	* ***************************************************** *
	
	local x "p50"
	
	* imported data
	import delimited "${versatility}/imported/imported_`x'_v2.csv", clear 

	* keep variables
	keep adm0 ingredient suitability country ifnative
	duplicates drop adm0 ingredient suitability, force
	
	preserve 
	keep if ifnative == 1
	keep adm0 ingredient ifnative
	ren ingredient ingredient2 
	ren ifnative ifnative2
	tempfile ifnative
	save `ifnative'
	restore
	
	tempfile all
	save `all'
	
	if $run == 0 {
	preserve
	keep if country == "zzz"
	tempfile bycountry
	save `bycountry', emptyok
	restore
	
	
	* Generating every combination of ingredients
	levelsof adm0, local(country)
	* initialize the output data
	foreach c of local country {
		preserve
	keep if adm0 == "`c'"

	gen ingredient2 = ingredient
	fillin ingredient ingredient2
	replace adm0 = "`c'" if adm0 == ""
	append using `bycountry', force
	save `bycountry', replace
	restore
	}
	use `bycountry', replace
	save "$outputs/2ingredient.dta", replace
	}
	
	use "$outputs/2ingredient.dta",replace
	duplicates drop adm0 country ingredient ingredient2, force
	drop country suitability
	merge m:1 adm0 ingredient using `all', gen(suit1_merge)
	tab ifnative
	drop suit1_merge
	
	gen suitability2 = .
	levelsof ingredient, local(ing)
	foreach i of local ing{
		sum suitability if ingredient == "`i'"
		local s = r(mean)
		replace suitability2 = `s' if ingredient2 == "`i'"
	}
	
	* We do this to make sure that native ingredient pairs are not kept
	merge m:1 adm0 ingredient2 using `ifnative', gen(ifnative_merge)
	*drop if ifnative == 1 & ifnative2 == 1
	drop ifnative_merge _fillin
	
	* get common flavors 
	merge m:1 ingredient ingredient2 using "${versatility}/common_flavor_clean.dta"
	count if _merge == 3
		dis "`l'"
		

	keep if _merge == 3
	drop _merge index

	* generate weight
	gen weight = .
	replace weight = 1 if ifnative2 == 1

	** calculate the distance between the country and origin of the ingredient2
	rename (ingredient ingredient2) (ingredientrow ingredient)
	joinby ingredient using "${versatility}/native/native_clean_p50.dta"
	joinby adm0 nativeadm0 using "${versatility}/distance_capital.dta"

	** keep the nearest distance
	sort ingredientrow ingredient distance
	bysort ingredientrow ingredient: gen num = _n
	
	
	************* 1. COMPOSITE VERSATILITY - MIN DISTANCE - NO SUITABILTY WEIGHT
	preserve
	keep if num == 1
	drop num

	replace weight = 1/distance if missing(weight)

	** generate normalized weight
	qui sum weight
	gen norm_weight = (weight - r(min))/(r(max) - r(min))


	* generate weighted average
	gen weightcommon = norm_weight * common
	drop common
	rename (weightcommon ingredientrow ingredient) (common ingredient ingredient2)

	*collapse (first)adm0 (first)country (mean)common (mean)ifnative, by(ingredient)
	bys adm0 ingredient: egen mean_common = mean(common)
	bys adm0 ingredient: egen mean_ifnative = mean(ifnative)
	
	* calculate the distance between the country and origin of the ingredient
	joinby ingredient using "${versatility}/native/native_clean_`x'.dta"
	dis "`l'"
	joinby adm0 nativeadm0 using "${versatility}/distance_capital.dta"

	* calculate imported versatility
	** keep the nearest distance
	sort ingredient distance
	bysort adm0 ingredient: gen num = _n
	keep if num == 1
	drop num

	gen commondistance = 1/distance * mean_common if ifnative != 1
	replace commondistance = mean_common if ifnative==1
	bys adm0: egen mean_commondistance = mean(commondistance)
	rename mean_commondistance Versatility_mindist
	keep adm0 country Versatility_mindist
	
	
	* drop duplicates
	duplicates drop adm0 Versatility_mindist, force
	
	save "$outputs/composite_versatility_mindist.dta", replace
	restore
	****************************************************************************
	
	************ 2.  COMPOSITE VERSATILITY - NO SUITABILTY WEIGHT***************
	preserve
	
	drop num

	replace weight = 1/distance if missing(weight)

	** generate normalized weight
	qui sum weight
	gen norm_weight = (weight - r(min))/(r(max) - r(min))


	* generate weighted average
	gen weightcommon = norm_weight * common
	drop common
	rename (weightcommon ingredientrow ingredient) (common ingredient ingredient2)

	*collapse (first)adm0 (first)country (mean)common (mean)ifnative, by(ingredient)
	bys adm0 ingredient: egen mean_common = mean(common)
	bys adm0 ingredient: egen mean_ifnative = mean(ifnative)
	
	* calculate the distance between the country and origin of the ingredient
	joinby ingredient using "${versatility}/native/native_clean_`x'.dta"
	dis "`l'"
	joinby adm0 nativeadm0 using "${versatility}/distance_capital.dta"

	* calculate imported versatility
	** keep the nearest distance
	sort ingredient distance
	bysort adm0 ingredient: gen num = _n
	keep if num == 1
	drop num

	gen commondistance = 1/distance * mean_common if ifnative != 1
	replace commondistance = mean_common if ifnative==1
	bys adm0: egen mean_commondistance = mean(commondistance)
	rename mean_commondistance Versatility
	keep adm0 country Versatility
	
	* drop duplicates
	duplicates drop adm0 Versatility, force
	
	save "$outputs/composite_versatility.dta", replace
	restore
	****************************************************************************

	************ 3.  COMPOSITE VERSATILITY - SUITABILTY WEIGHT******************
	preserve
	gen inverse_suit = 1 - suitability // Since suitability is a score and higher is better whereas for distance lower is better. (1 - suitability) gives us the inverse to lower is better.
	gen suit_weight = num*inverse_suit
	
	bys ingredientrow ingredient: gen suit_num = _n
	
	keep if suit_num == 1 // We now account for suitability along with distance to give a more believable metric for trade
	drop num suit_num
	
	replace weight = suitability/distance if missing(weight)

	** generate normalized weight
	qui sum weight
	gen norm_weight = (weight - r(min))/(r(max) - r(min))


	* generate weighted average
	gen weightcommon = norm_weight * common
	drop common
	rename (weightcommon ingredientrow ingredient) (common ingredient ingredient2)
	bys adm0 ingredient: egen mean_common = mean(common)
	bys adm0 ingredient: egen mean_ifnative = mean(ifnative)
	
	* calculate the distance between the country and origin of the ingredient
	joinby ingredient using "${versatility}/native/native_clean_`x'.dta"
	dis "`l'"
	joinby adm0 nativeadm0 using "${versatility}/distance_capital.dta"

	* calculate imported versatility
	** keep the nearest distance
	sort ingredient distance
	bysort adm0 ingredient: gen num = _n
	keep if num == 1
	drop num

	gen commondistance = 1/distance * mean_common if ifnative != 1
	replace commondistance = mean_common if ifnative==1
	bys adm0: egen mean_commondistance = mean(commondistance)
	rename mean_commondistance Versatility_weighted
	keep adm0 country Versatility_weighted
	
	* drop duplicates
	duplicates drop adm0 Versatility_weighted, force
	
	save "$outputs/composite_versatility_weighted.dta", replace
	restore
	****************************************************************************