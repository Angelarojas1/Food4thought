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
	
	
	
	****************************
	****************************
	* New formula starts here
	****************************
	** calculate the distance between the country and origin of the ingredient2
	rename (ingredient ingredient2) (ingredientrow ingredient)
	joinby ingredient using "${versatility}/native/native_clean_p50.dta"
	joinby adm0 nativeadm0 using "${versatility}/distance_capital.dta"
	
	
	** Calculate the nearest distance
	sort ingredientrow ingredient distance
	bysort ingredientrow ingredient: gen num = _n
	
	
	** Calculate distance weight
	bys country ingredient: egen total_distance = sum(distance)
	
	gen relative_distance = distance/total_distance
	replace weight = 1 - relative_distance
	
	gen ingredient_versatility = weight * common 
	summ weight
	bys adm0: egen versatility = mean(ingredient_versatility)
	keep adm0 versatility
	duplicates drop
	save "$outputs/clean_versatility.dta", replace
	
	