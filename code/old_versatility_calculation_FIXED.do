* **************************************************************************** *
*                                                                      		   *
*            	Cuisine Complexity and Female Labor Force Participation	       *
*               Author: Varun C
* 				Last date modified: April 14, 2025 						   	   *
*				Old Versatility Calculations
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
	global github "C:\Users\wb641362\Dropbox\food4thought\analysis23"
	global files "C:\Users\wb641362\OneDrive - WBG\Documents\Food4Thought"
	
	* Creating the World Map Shape File
	* cd "C:\Users\wb641362\OneDrive - WBG\Documents\WB_countries_Admin0_10m"
	* spshape2dta WB_countries_Admin0_10m, replace saving(world)
	}

	** Project folder globals
	
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
	global outputs				"$projectfolder/outputs"
	
	* ***************************************************** *
	
	local x "p50"
	****************************************************************************
	****************** IMPORT VERSATILITY CALCULATION (FIXED) ******************
	****************************************************************************
	if $run == 0 {
	
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
	
	use "$outputs/2ingredient.dta",replace
	duplicates drop adm0 country ingredient ingredient2, force
	drop country suitability
	merge m:1 adm0 ingredient using `all', gen(suit1_merge)
	tab ifnative
	drop suit1_merge
	
	
	* generate suitability of ingredient2
	gen suitability2 = .

	levelsof ingredient, local(ing)
	foreach i of local ing{
		sum suitability if ingredient == "`i'"
		local s = r(mean)
		replace suitability2 = `s' if ingredient2 == "`i'"
	}
	
	
	* We do this to make sure that native ingredient pairs are not kept
	merge m:1 adm0 ingredient2 using `ifnative', gen(ifnative_merge)
	drop if ifnative == 1 & ifnative2 == 1
	drop ifnative_merge _fillin
	
	
	* Drop pairs where both ingredients are native 
	drop if ingredient == ingredient2
	
	
	merge m:1 ingredient ingredient2 using "${versatility}/common_flavor_clean.dta"
	count if _merge == 3
	if r(N) == 0{
		continue
	}
	keep if _merge == 3
	drop _merge index

	* generate weight
	gen weight = .
	replace weight = 1 if ifnative2 == 1

	** calculate the distance between the country and origin of the ingredient2
	rename (ingredient ingredient2) (ingredientrow ingredient)
	joinby ingredient using "${versatility}/native/native_clean_`x'.dta"
	joinby adm0 nativeadm0 using "${versatility}/distance_capital.dta"

	count 

	if r(N) == 0{
	continue
	
	}

	** keep the nearest distance
	sort ingredientrow ingredient distance
	bysort ingredientrow ingredient: gen num = _n
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
	rename mean_commondistance importVersatility
	keep adm0 country importVersatility
	
	* drop duplicates
	duplicates drop adm0 importVersatility, force
	
	save "${versatility}/imported/importbycountry_v2_`x'.dta", replace
	}

	****************************************************************************
	****************** NATIVE VERSATILITY CALCULATION (FIXED) ******************
	****************************************************************************
	
	* import data
	import delimited "${versatility}/native/native_`x'.csv", clear 

	* keep variables
	keep adm0 ingredient suitability country

	tempfile all
	save `all'
	
	use "$outputs/2ingredient.dta",replace
	duplicates drop adm0 country ingredient ingredient2, force
	drop country suitability
	merge m:1 adm0 ingredient using `all', gen(suit1_merge)
	tab ifnative
	drop suit1_merge
	
		* generate suitability of ingredient2
	gen suitability2 = .

	levelsof ingredient, local(ing)
	foreach i of local ing{
		sum suitability if ingredient == "`i'"
		local s = r(mean)
		replace suitability2 = `s' if ingredient2 == "`i'"
	}
	
	* get common flavors 
	merge m:1 ingredient ingredient2 using "${versatility}/common_flavor_clean.dta"
	count if _merge == 3
	dis "`l'"

	
	keep if _merge == 3
	drop _merge index
	
	* calculate native flavor versatility
	gen commonSuit2 = common * suitability2
	
	bys adm0 ingredient: egen mean_suitability = mean(suitability)
	bys adm0 ingredient: egen mean_commonSuit2 = mean(commonSuit2)
	

	gen commonSuit2Suit = mean_commonSuit2 * mean_suitability
	bys adm0: egen mean_commonSuit2Suit = mean(commonSuit2Suit)
	drop if mean_commonSuit2Suit == .
	
	keep adm0 country mean_commonSuit2Suit
	
	rename mean_commonSuit2Suit nativeVersatility
	duplicates drop adm0 nativeVersatility, force
	
	
	* save
	save "${versatility}/native/nativebycountry_`x'_g2weight.dta", replace
	
	
	
	
	
	